from flask import Flask, render_template,request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.predict import predict_bp
from routes.admin import admin_bp  # ✅ Import Admin Routes
from routes.user import user_bp  # ✅ Import User Routes
from models.database import contact_collection
from flask import jsonify
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# ✅ Configurations
app.config.from_object(Config)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ✅ Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(predict_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api/admin")  # ✅ Admin Routes
app.register_blueprint(user_bp, url_prefix="/api/user")  # ✅ User Routes



# ✅ Frontend Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/predict")
def predict_page():
    return render_template("predict.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")  # ✅ Admin Dashboard

@app.route("/user")
def user_page():
    return render_template("user.html")  # ✅ User Dashboard

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/api/contact", methods=["POST"])
def save_contact():
    data = request.json
    if not all(key in data for key in ["name", "email", "message"]):
        return jsonify({"error": "Missing data"}), 400

    contact_collection.insert_one(data)
    return jsonify({"message": "Contact form submitted successfully!"})

@app.route("/api/admin/contacts", methods=["GET"])
def get_contacts():
    contacts = list(contact_collection.find({}, {"_id": 0}))  # Hide MongoDB _id
    print("Contacts from DB:", contacts)  # Debugging output
    return jsonify(contacts)


@app.route("/contact")
def contact_page():
    return render_template("contact.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 for local
    app.run(host="0.0.0.0", port=port)

