import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

from database import (
    initialize_database,
    save_transaction,
    get_user_transactions
)

from auth import (
    register_user,
    login_user
)

from card_service import get_bin_info

from fraud_engine import calculate_fraud_risk

from rag_engine import (
    create_vector_store,
    ask_question
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="Sentinel Secure",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "document_name" not in st.session_state:
    st.session_state.document_name = ""


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #d9dee7;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .brand {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .brand-subtitle {
        font-size: 13px;
        color: #667085;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .section-description {
        color: #667085;
        margin-bottom: 25px;
    }

    .security-box {
        border: 1px solid #d9dee7;
        border-radius: 10px;
        padding: 18px;
        margin-top: 20px;
    }

    .login-box {
        max-width: 600px;
        margin: 50px auto;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN / REGISTRATION
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="login-box">',
        unsafe_allow_html=True
    )

    st.title("Sentinel Secure")
    st.caption("Financial security and intelligence platform")

    st.divider()

    login_tab, register_tab = st.tabs(
        ["Sign In", "Create Account"]
    )

    # --------------------------------------------------------
    # SIGN IN
    # --------------------------------------------------------

    with login_tab:

        st.subheader("Sign in")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Sign In",
            type="primary",
            use_container_width=True
        ):

            if not login_email or not login_password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                success, user, message = login_user(
                    login_email,
                    login_password
                )

                if success:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.email = user["email"]
                    st.session_state.page = "Overview"

                    st.success("Login successful.")

                    st.rerun()

                else:

                    st.error(message)

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    with register_tab:

        st.subheader("Create account")

        register_username = st.text_input(
            "Username",
            key="register_username"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        register_confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if register_password != register_confirm:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    register_username,
                    register_email,
                    register_password
                )

                if success:

                    st.success(message)
                    st.info(
                        "You can now sign in using your account."
                    )

                else:

                    st.error(message)

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">Sentinel Secure</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-subtitle">Financial Security Platform</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Signed in as **{st.session_state.username}**"
    )

    st.divider()

    st.caption("NAVIGATION")

    if st.button(
        "Overview",
        use_container_width=True
    ):
        st.session_state.page = "Overview"
        st.rerun()

    if st.button(
        "Card Intelligence",
        use_container_width=True
    ):
        st.session_state.page = "Card Intelligence"
        st.rerun()

    if st.button(
        "Fraud Risk",
        use_container_width=True
    ):
        st.session_state.page = "Fraud Risk"
        st.rerun()

    if st.button(
        "Document Intelligence",
        use_container_width=True
    ):
        st.session_state.page = "Document Intelligence"
        st.rerun()

    if st.button(
        "Transaction History",
        use_container_width=True
    ):
        st.session_state.page = "Transaction History"
        st.rerun()

    st.divider()

    st.caption("ACCOUNT")

    if st.button(
        "Sign Out",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.session_state.email = ""
        st.session_state.page = "Overview"

        st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

if st.session_state.page == "Overview":

    st.markdown(
        '<div class="section-title">Financial Security Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Monitor transaction risk, card intelligence, and financial documents.'
        '</div>',
        unsafe_allow_html=True
    )

    transactions = get_user_transactions(
        st.session_state.user_id
    )

    total_transactions = len(transactions)

    high_risk = 0
    medium_risk = 0
    low_risk = 0

    total_amount = 0

    for transaction in transactions:

        total_amount += transaction["amount"]

        if transaction["risk_level"] == "High":
            high_risk += 1

        elif transaction["risk_level"] == "Medium":
            medium_risk += 1

        else:
            low_risk += 1

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Transactions",
            total_transactions
        )

    with col2:

        st.metric(
            "Total Amount",
            f"₹{total_amount:,.2f}"
        )

    with col3:

        st.metric(
            "High Risk",
            high_risk
        )

    with col4:

        st.metric(
            "Medium Risk",
            medium_risk
        )

    st.divider()

    # --------------------------------------------------------
    # SECURITY STATUS
    # --------------------------------------------------------

    st.subheader("Security Status")

    if high_risk > 0:

        st.error(
            f"{high_risk} high-risk transaction(s) detected."
        )

    elif medium_risk > 0:

        st.warning(
            f"{medium_risk} medium-risk transaction(s) detected."
        )

    else:

        st.success(
            "No significant transaction risk detected."
        )

    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("Risk Distribution")

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    with risk_col1:

        st.metric(
            "Low Risk",
            low_risk
        )

    with risk_col2:

        st.metric(
            "Medium Risk",
            medium_risk
        )

    with risk_col3:

        st.metric(
            "High Risk",
            high_risk
        )

    st.divider()

    # --------------------------------------------------------
    # RECENT TRANSACTIONS
    # --------------------------------------------------------

    st.subheader("Recent Transactions")

    if not transactions:

        st.info(
            "No transaction analysis has been recorded yet."
        )

    else:

        recent_transactions = transactions[:5]

        table_data = []

        for transaction in recent_transactions:

            table_data.append(
                {
                    "Date": transaction["created_at"][:19],
                    "Amount": f"₹{transaction['amount']:,.2f}",
                    "Risk Score": transaction["risk_score"],
                    "Risk Level": transaction["risk_level"]
                }
            )

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# CARD INTELLIGENCE
# ============================================================

elif st.session_state.page == "Card Intelligence":

    st.markdown(
        '<div class="section-title">Card Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Validate card numbers locally and retrieve public BIN metadata.'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "For testing, use a public test card number such as "
        "4242 4242 4242 4242. Do not enter real payment-card numbers."
    )

    st.subheader("Card Analysis")

    card_number = st.text_input(
        "Card Number",
        type="password",
        placeholder="Enter card number"
    )

    if st.button(
        "Analyze Card",
        type="primary",
        use_container_width=True
    ):

        if not card_number:

            st.error(
                "Please enter a card number."
            )

        else:

            with st.spinner(
                "Analyzing card..."
            ):

                result = get_bin_info(
                    card_number
                )

            if not result["success"]:

                st.error(
                    result["message"]
                )

            else:

                st.success(
                    "Card validation successful."
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Card",
                        result["card"]
                    )

                    st.metric(
                        "Scheme",
                        result["scheme"]
                    )

                with col2:

                    st.metric(
                        "Type",
                        result["type"]
                    )

                    st.metric(
                        "Brand",
                        result["brand"]
                    )

                with col3:

                    st.metric(
                        "Bank",
                        result["bank"]
                    )

                    st.metric(
                        "Country",
                        result["country"]
                    )

                st.divider()

                st.subheader("BIN Information")

                bin_data = [
                    {
                        "Field": "BIN",
                        "Value": result["bin"]
                    },
                    {
                        "Field": "Scheme",
                        "Value": result["scheme"]
                    },
                    {
                        "Field": "Card Type",
                        "Value": result["type"]
                    },
                    {
                        "Field": "Brand",
                        "Value": result["brand"]
                    },
                    {
                        "Field": "Bank",
                        "Value": result["bank"]
                    },
                    {
                        "Field": "Country",
                        "Value": result["country"]
                    },
                    {
                        "Field": "Country Code",
                        "Value": result["country_code"]
                    },
                    {
                        "Field": "Currency",
                        "Value": result["currency"]
                    },
                    {
                        "Field": "Prepaid",
                        "Value": result["prepaid"]
                    }
                ]

                st.dataframe(
                    bin_data,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# FRAUD RISK
# ============================================================

elif st.session_state.page == "Fraud Risk":

    st.markdown(
        '<div class="section-title">Fraud Risk Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Evaluate transaction risk using explainable security indicators.'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "This prototype uses a rule-based risk engine. "
        "It is not a machine-learning fraud detector."
    )

    # --------------------------------------------------------
    # TRANSACTION DETAILS
    # --------------------------------------------------------

    st.subheader("Transaction Details")

    col1, col2 = st.columns(2)

    with col1:

        amount = st.number_input(
            "Transaction Amount",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )

        transaction_count = st.number_input(
            "Recent Transaction Count",
            min_value=1,
            value=1,
            step=1
        )

    with col2:

        international = st.checkbox(
            "International Transaction"
        )

        unusual_hour = st.checkbox(
            "Unusual Transaction Hour"
        )

        new_device = st.checkbox(
            "New Device"
        )

    st.divider()

    if st.button(
        "Analyze Transaction",
        type="primary",
        use_container_width=True
    ):

        result = calculate_fraud_risk(
            amount=amount,
            transaction_count=transaction_count,
            international=international,
            unusual_hour=unusual_hour,
            new_device=new_device
        )

        score = result["score"]
        risk_level = result["risk_level"]
        reasons = result["reasons"]

        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        save_transaction(
            user_id=st.session_state.user_id,
            amount=amount,
            transaction_count=transaction_count,
            international=international,
            unusual_hour=unusual_hour,
            new_device=new_device,
            risk_score=score,
            risk_level=risk_level
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        st.subheader("Risk Assessment")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Risk Score",
                f"{score}/100"
            )

        with col2:

            st.metric(
                "Risk Level",
                risk_level
            )

        st.progress(
            score / 100
        )

        # ----------------------------------------------------
        # RISK MESSAGE
        # ----------------------------------------------------

        if risk_level == "High":

            st.error(
                "High-risk transaction. Additional verification is recommended."
            )

        elif risk_level == "Medium":

            st.warning(
                "Medium-risk transaction. Review the detected indicators."
            )

        else:

            st.success(
                "Low-risk transaction."
            )

        # ----------------------------------------------------
        # REASONS
        # ----------------------------------------------------

        st.subheader("Risk Indicators")

        for reason in reasons:

            st.write(
                f"- {reason}"
            )

        st.success(
            "Transaction analysis saved to your account history."
        )


# ============================================================
# DOCUMENT INTELLIGENCE
# ============================================================

elif st.session_state.page == "Document Intelligence":

    st.markdown(
        '<div class="section-title">Document Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Upload a PDF and ask questions using retrieval-augmented generation.'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "The document is processed into text chunks, embedded, "
        "stored in a FAISS vector index, and retrieved for question answering."
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if (
            st.session_state.document_name
            != uploaded_file.name
        ):

            st.session_state.vector_store = None
            st.session_state.document_name = uploaded_file.name

        st.write(
            f"Selected document: **{uploaded_file.name}**"
        )

        if st.button(
            "Process Document",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Processing document..."
                ):

                    st.session_state.vector_store = (
                        create_vector_store(
                            uploaded_file
                        )
                    )

                st.success(
                    "Document processed successfully."
                )

            except Exception as error:

                st.error(
                    f"Document processing failed: {error}"
                )

        if st.session_state.vector_store is not None:

            st.divider()

            st.subheader(
                "Ask Questions"
            )

            question = st.text_input(
                "Question",
                placeholder="Ask something about the document"
            )

            if st.button(
                "Ask Question",
                type="primary",
                use_container_width=True
            ):

                if not question.strip():

                    st.warning(
                        "Please enter a question."
                    )

                else:

                    try:

                        with st.spinner(
                            "Searching document..."
                        ):

                            answer = ask_question(
                                st.session_state.vector_store,
                                question
                            )

                        st.subheader(
                            "Answer"
                        )

                        st.write(
                            answer
                        )

                    except Exception as error:

                        st.error(
                            f"Question answering failed: {error}"
                        )


# ============================================================
# TRANSACTION HISTORY
# ============================================================

elif st.session_state.page == "Transaction History":

    st.markdown(
        '<div class="section-title">Transaction History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Review previous transaction risk assessments associated with your account.'
        '</div>',
        unsafe_allow_html=True
    )

    transactions = get_user_transactions(
        st.session_state.user_id
    )

    if not transactions:

        st.info(
            "No transaction history available."
        )

    else:

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        total = len(transactions)

        high = 0
        medium = 0
        low = 0

        for transaction in transactions:

            if transaction["risk_level"] == "High":
                high += 1

            elif transaction["risk_level"] == "Medium":
                medium += 1

            else:
                low += 1

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total",
                total
            )

        with col2:

            st.metric(
                "Low",
                low
            )

        with col3:

            st.metric(
                "Medium",
                medium
            )

        with col4:

            st.metric(
                "High",
                high
            )

        st.divider()

        # ----------------------------------------------------
        # HISTORY TABLE
        # ----------------------------------------------------

        history_data = []

        for transaction in transactions:

            history_data.append(
                {
                    "Date": transaction["created_at"][:19],
                    "Amount": f"₹{transaction['amount']:,.2f}",
                    "Recent Transactions": transaction[
                        "transaction_count"
                    ],
                    "International": (
                        "Yes"
                        if transaction["international"]
                        else "No"
                    ),
                    "Unusual Hour": (
                        "Yes"
                        if transaction["unusual_hour"]
                        else "No"
                    ),
                    "New Device": (
                        "Yes"
                        if transaction["new_device"]
                        else "No"
                    ),
                    "Risk Score": transaction[
                        "risk_score"
                    ],
                    "Risk Level": transaction[
                        "risk_level"
                    ]
                }
            )

        st.dataframe(
            history_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"Sentinel Secure | Signed in as {st.session_state.username} | "
    f"{datetime.now().strftime('%Y-%m-%d')}"
)
