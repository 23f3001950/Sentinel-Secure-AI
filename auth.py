import re
import bcrypt

from database import create_user, get_user_by_email


def validate_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, password_hash):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username:
        return False, "Username is required."

    if not validate_email(email):
        return False, "Enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    existing_user = get_user_by_email(email)

    if existing_user:
        return False, "An account with this email already exists."

    password_hash = hash_password(password)

    created = create_user(
        username,
        email,
        password_hash
    )

    if not created:
        return False, "Username or email is already registered."

    return True, "Account created successfully."


def login_user(email, password):
    email = email.strip().lower()

    user = get_user_by_email(email)

    if not user:
        return False, None, "Invalid email or password."

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return False, None, "Invalid email or password."

    return True, user, "Login successful."
