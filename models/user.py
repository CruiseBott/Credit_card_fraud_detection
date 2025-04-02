import bcrypt
from models.database import users

def register_user(username, password, role="user"):  # Default role = "user"
    if users.find_one({"username": username}):
        return {"error": "User already exists"}

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users.insert_one({"username": username, "password": hashed_pw, "role": role})  # Store role in DB

    return {"message": "User registered successfully!", "role": role}

def verify_user(username, password):
    user = users.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return None
    return user  # Now includes "role"
