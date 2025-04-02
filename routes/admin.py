from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import users, transactions

admin_bp = Blueprint("admin", __name__)

# ✅ Get All Users (Admin Only)
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    identity = get_jwt_identity()  # Now it's just the username
    claims = get_jwt()  # Get additional claims (role)

    print(f"🔍 Request Headers: {request.headers}")  # Debugging
    print(f"🆔 JWT Identity: {identity}")  # Debugging
    print(f"🔑 User Role: {claims.get('role')}")  # Debugging

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    user_list = list(users.find({}, {"_id": 0, "password": 0}))  # Hide sensitive info
    return jsonify(user_list)

# ✅ Update User Role (Admin Only)
@admin_bp.route("/update-role", methods=["POST"])
@jwt_required()
def update_role():
    identity = get_jwt_identity()  
    claims = get_jwt()  

    print(f"🔍 Admin Identity: {identity}")  # Debugging
    print(f"🔑 Admin Role: {claims.get('role')}")  # Debugging

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    username = data.get("username")
    new_role = data.get("role")

    if not username or not new_role:
        return jsonify({"error": "Missing username or role"}), 400

    update_result = users.update_one({"username": username}, {"$set": {"role": new_role}})

    if update_result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": f"Updated {username} to {new_role}!"})

# ✅ Get All Transactions (Admin Only)
@admin_bp.route("/fraud-transactions", methods=["GET"])
@jwt_required()
def get_fraud_transactions():
    identity = get_jwt_identity()
    claims = get_jwt()

    print(f"🔍 Request by: {identity}")  # Debugging
    print(f"🔑 User Role: {claims.get('role')}")  # Debugging

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    fraud_transactions = list(transactions.find({}, {"_id": 0}))
    return jsonify(fraud_transactions)
