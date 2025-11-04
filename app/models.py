# ==============================================
# app/models.py
# Defines all database models: Admin, Feedback, Slideshow
# ==============================================

from datetime import datetime
from .database import db
from flask_bcrypt import generate_password_hash, check_password_hash

# 🧑‍💼 ADMIN MODEL (for both Super Admin and Candidate Admin)
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="admin")  # "admin" or "super_admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    @property
    def is_super(self):
        return self.role == "superadmin"

    # 🟣 Initialize Admin with password hashing
    def __init__(self, username, password, role="admin"):
        self.username = username
        self.set_password(password)
        self.role = role

    # 🟣 Set password (hashed)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 🟣 Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 🟣 For debugging / admin display
    def __repr__(self):
        return f"<Admin {self.username} ({self.role})>"


# 🗳️ FEEDBACK MODEL (for storing voter responses)
class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    subcounty = db.Column(db.String(100), nullable=False)
    ward = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    age_bracket = db.Column(db.String(20), nullable=False)
    will_vote = db.Column(db.Boolean, nullable=False)  # True for Yes, False for No
    reason = db.Column(db.Text, nullable=True)  # If 'No', the reason or suggestion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.subcounty} - {'Yes' if self.will_vote else 'No'}>"


# 🖼️ SLIDESHOW MODEL (for admin-managed slideshow images)
class Slideshow(db.Model):
    __tablename__ = "slides"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("admins.id"))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)  # 🟣 NEW FIELD

    admin = db.relationship("Admin", backref="slides")

    def __repr__(self):
        return f"<Slide {self.caption or 'No Caption'}>"
    


class HeroImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))