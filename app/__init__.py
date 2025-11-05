# ==============================================
# app/__init__.py
# Flask application factory setup
# ==============================================

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .database import db
import os


# Initialize Flask extensions (defined globally)
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    """App factory function to create and configure the Flask app"""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from instance/config.py
    app.config.from_pyfile("../instance/config.py", silent=False)

    # Enable CORS for the frontend (React)
    # CORS(app, resources={r"/*":{"origins":["http://localhost:5173"]}})
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app import models


    # Register blueprints
    from .routes.hero import hero_bp
    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.feedback import feedback_bp
    from .routes.slideshow import slideshow_bp
    from .routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(slideshow_bp, url_prefix="/api/slides")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(hero_bp, url_prefix="/api/hero")

    # Simple health route
    @app.route("/")
    def home():
        return {"message": "Political Portfolio API running successfully"}

    return app