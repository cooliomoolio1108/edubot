# app.py
from flask import Flask
from flask_cors import CORS
from config import Config
from routes import register_routes
from rag.services.chroma_service import vector_store

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)  # Enable CORS for all routes

    register_routes(app)  # Registers all blueprints (flat)

    return app

if __name__ == "__main__":
    vector_db = vector_store  # If you need it early
    app = create_app()
    app.run(debug=True, host="localhost", port=5050)
