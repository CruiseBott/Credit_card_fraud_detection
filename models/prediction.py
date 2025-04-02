import joblib
import pandas as pd
from models.database import transactions

# Load XGBoost model and encoders
try:
    model_data = joblib.load("fraud_detection_pipeline_xgb.pkl")
    model = model_data["model"]
    encoders = model_data.get("encoders", {})
    print("✅ Model and encoders loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    encoders = None

def safe_encode(label, encoder):
    """Safely encode a label. If unseen, assign -1."""
    try:
        if label in encoder.classes_:
            return encoder.transform([label])[0]  # Normal encoding
        else:
            print(f"⚠️ Warning: Label '{label}' not seen before. Assigning -1.")
            return -1  # Assign -1 for unseen labels
    except Exception as e:
        print(f"❌ Encoding error: {e}")
        return -1

def predict_fraud(username, data):
    if not model:
        return {"error": "Model not loaded"}

    df = pd.DataFrame([data])

    # Ensure correct data types
    numerical_cols = ["amt", "trans_hour", "trans_day"]
    categorical_cols = ["merchant", "category", "gender"]

    try:
        # Convert numerical columns explicitly to float64
        for col in numerical_cols:
            df[col] = df[col].astype("float64")  

        # Encode categorical features
        for col in categorical_cols:
            if col in encoders:
                df[col] = df[col].apply(lambda x: safe_encode(x, encoders[col]))

        # Debugging: Print DataFrame and its types before prediction
        print("🔍 Final DataFrame before Prediction:")
        print(df)
        print("🛠 Data Types Before Prediction:")
        print(df.dtypes)

        # Run prediction (Ensure output is in native Python types)
        prediction = int(model.predict(df)[0])  # ✅ Convert to native Python int
        probability = float(model.predict_proba(df)[0][1])  # ✅ Convert to float64

        # Save transaction to MongoDB
        transactions.insert_one({
            "username": username,
            "transaction": data,
            "fraudulent": bool(prediction),
            "fraud_probability": round(probability, 4)
        })

        return {"fraudulent": bool(prediction), "fraud_probability": round(probability, 4)}

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {"error": "Prediction failed", "details": str(e)}
