# app.py
from flask import Flask
from flask_cors import CORS
from config import Config
from routes import register_routes
from database import seed_courses, seed_users

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)  # Enable CORS for all routes
    with app.app_context():
        seed_courses()
        seed_users()
    register_routes(app)  # Registers all blueprints (flat)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5050)
