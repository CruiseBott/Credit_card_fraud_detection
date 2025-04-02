from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import register_user, verify_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    # Assign a default role (all new users are "user" unless changed manually)
    role = data.get("role", "user")

    result = register_user(username, password, role)
    return jsonify(result)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = verify_user(data["username"], data["password"])

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(
    identity=data["username"],  # Only store username as identity
    additional_claims={"role": user["role"]}  # Store role in additional claims
    )

    return jsonify({"access_token": access_token, "role": user["role"]})
