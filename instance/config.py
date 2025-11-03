# ==============================================
# instance/config.py
# Flask app configuration settings
# ==============================================
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret keys and database configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'portfolio.db')}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwtsecret")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}