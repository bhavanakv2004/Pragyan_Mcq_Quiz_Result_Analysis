import sqlite3
import hashlib

# ---------------- DATABASE CONNECTION ---------------- #
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- CREATE TABLE ---------------- #
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()


# ---------------- PASSWORD HASHING ---------------- #
def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()


# ---------------- REGISTER USER ---------------- #
def register_user(username, password):

    try:

        hashed_password = hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        conn.commit()

        return True, "✅ Registration Successful"

    except:

        return False, "❌ Username already exists"


# ---------------- LOGIN USER ---------------- #
def login_user(username, password):

    hashed_password = hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_password)
    )

    user = cursor.fetchone()

    if user:
        return True

    return False
