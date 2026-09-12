import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def extract_pdf_text(pdf_file):
    text = ""

    reader = PdfReader(pdf_file)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def create_vector_store(pdf_file):
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing from .env")

    text = extract_pdf_text(pdf_file)

    if not text.strip():
        raise ValueError("No readable text found in the PDF.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_text(text)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    vector_store = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    return vector_store


def ask_question(vector_store, question):
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing from .env")

    documents = vector_store.similarity_search(
        question,
        k=4
    )

    if not documents:
        return "I could not find relevant information in the document."

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
You are Sentinel Secure's document analysis assistant.

Answer the user's question using only the information provided
in the document context below.

If the answer cannot be found in the context, clearly say:
"I could not find that information in the uploaded document."

Do not invent facts.

Document Context:
{context}

User Question:
{question}

Answer:
"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )

    response = llm.invoke(prompt)

    return response.content