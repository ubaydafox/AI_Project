import json
import os
from dotenv import load_dotenv

load_dotenv()

USERS_FILE = 'data/users.json'
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123") # Default if not set, but should be set in .env

# Load users
def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

# Register a user
def register_user(user_id, student_id, batch):
    users = load_users()
    users[str(user_id)] = {
        "student_id": student_id,
        "batch": batch,
        "role": "student"
    }
    return save_users(users)

# Get user info
def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def get_user_batch(user_id):
    user = get_user(user_id)
    if user:
        return user.get("batch")
    return None

# Admin Authentication
def authenticate_admin(user_id, password):
    if password == ADMIN_PASSWORD:
        users = load_users()
        if str(user_id) not in users:
            # Auto-register as admin if not exists, or just update role?
            # Let's just update role or create a simple admin profile
            users[str(user_id)] = {
                "role": "admin"
            }
        else:
            users[str(user_id)]["role"] = "admin"
        
        save_users(users)
        return True
    return False

def is_admin(user_id):
    user = get_user(user_id)
    return user and user.get("role") == "admin"
