# ==========================================
#  auth_routes.py
#  Handles Admin/SuperAdmin authentication
#  - Login
#  - Change Password
#  - JWT Token handling
# ==========================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt_identity
)
from datetime import timedelta
from app.models import Admin
from app.database import db
from flask_bcrypt import check_password_hash, generate_password_hash

# Blueprint setup
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')


# -----------------------------
# 🟣 LOGIN ROUTE
# -----------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    admin = Admin.query.filter_by(username=username).first()

    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT Token valid for 1 day
    access_token = create_access_token(
        identity={"id": admin.id, "role": admin.role, "username": admin.username},
        expires_delta=timedelta(days=1)
    )

    return jsonify({
        "access_token": access_token,
        "role": admin.role,
        "username": admin.username
    }), 200


# -----------------------------
# 🟣 CHANGE PASSWORD
# -----------------------------
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    admin = Admin.query.get(current_user['id'])

    if not admin or not check_password_hash(admin.password_hash, old_password):
        return jsonify({"error": "Incorrect current password"}), 401

    admin.password_hash = generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200


# -----------------------------
# 🟣 TEST TOKEN (Optional utility)
# -----------------------------
@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    current_user = get_jwt_identity()
    return jsonify({"user": current_user}), 200