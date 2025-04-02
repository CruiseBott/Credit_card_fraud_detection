from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.prediction import predict_fraud  # ✅ Use prediction.py instead of loading model again

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
@jwt_required()  # Ensure user is authenticated
def predict():
    data = request.get_json()
    print("Received data:", data)

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Fetch username from JWT token instead of request body
        username = get_jwt_identity()
        if not username:
            return jsonify({"error": "User identity not found"}), 401

        # Run fraud prediction
        response = predict_fraud(username, data)
        print("API Response:", response)
        return jsonify(response)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
