import json
import os
from dotenv import load_dotenv
from constants import DATA_DIR, IS_VERCEL

load_dotenv()

USERS_FILE = DATA_DIR / 'users.json'
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Load users
def load_users():
    try:
        if not USERS_FILE.exists():
            return {}
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    if IS_VERCEL:
        # Vercel filesystem is read-only. In production, a database like Upstash Redis, 
        # Supabase, or Vercel KV should be used.
        print("Warning: Attempted to save users on Vercel's read-only filesystem.")
        return False
        
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
