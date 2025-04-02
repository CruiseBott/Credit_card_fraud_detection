from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from models.database import users, transactions

user_bp = Blueprint("user", __name__)

# ✅ Get User Profile
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    print(f"JWT Identity: {identity}")  # Debugging line
    
    username = identity if isinstance(identity, str) else identity.get("username")
    
    user = users.find_one({"username": username}, {"_id": 0, "password": 0})  # Hide password
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user)

# ✅ Get User's Transaction History
@user_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    token = get_jwt()
    print(f"📢 Received JWT: {token}")  # Debugging

    identity = get_jwt_identity()
    username = identity if isinstance(identity, str) else identity.get("username")

    user_transactions = list(transactions.find({"username": username}, {"_id": 0, "username": 0}))
    
    return jsonify({"transactions": user_transactions})

# ✅ Update User Role (Admin Only)
@user_bp.route("/update-role", methods=["PUT"])
@jwt_required()
def update_role():
    identity = get_jwt_identity()
    if isinstance(identity, str) or "role" not in identity or identity["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    username = data.get("username")
    new_role = data.get("role", "user")
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    user = users.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    users.update_one({"username": username}, {"$set": {"role": new_role}})
    return jsonify({"message": f"User '{username}' role updated to '{new_role}'"})

# ✅ Delete User Account (User Only)
@user_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_user():
    identity = get_jwt_identity()
    username = identity if isinstance(identity, str) else identity.get("username")
    
    delete_result = users.delete_one({"username": username})
    if delete_result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    
    transactions.delete_many({"username": username})  # Remove user transactions too
    
    return jsonify({"message": "User account deleted successfully!"})
