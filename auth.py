import json
import os

USERS_FILE = "database/users.json"


# ==========================================
# Create users file if not exists
# ==========================================
if not os.path.exists("database"):
    os.makedirs("database")

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)


# ==========================================
# Load Users
# ==========================================
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


# ==========================================
# Save Users
# ==========================================
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ==========================================
# Register User
# ==========================================
def register_user(username, password, role, college_id):

    users = load_users()

    if username in users:
        return False, "Username already exists"

    users[username] = {
        "password": password,
        "role": role,
        "college_id": college_id
    }

    save_users(users)

    return True, "Registration Successful"


# ==========================================
# Authenticate User
# ==========================================
def authenticate(username, password):

    users = load_users()

    if username in users:

        user = users[username]

        if user["password"] == password:
            return True, user

    return False, None
