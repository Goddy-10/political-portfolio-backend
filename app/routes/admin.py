from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Admin
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")

# 🟣 Get all admins (Super Admin only)
@admin_bp.route("/all", methods=["GET"])
@jwt_required()
def get_all_admins():
    current_admin = get_jwt_identity()
    print("JWT identity:", current_admin)
    admin = Admin.query.filter_by(username=current_admin).first()
    print("Fetched admin:", admin)
    # current_admin_identity = get_jwt_identity()
    # username = current_admin_identity["username"]
    # admin = Admin.query.filter_by(username=username).first()

    if not admin or not admin.is_super:
        return jsonify({"error": "Unauthorized"}), 403

    admins = Admin.query.all()
    data = [{"id": a.id, "username": a.username, "is_super": a.is_super} for a in admins]
    return jsonify(data), 200


# 🟣 Add new admin
@admin_bp.route("/add", methods=["POST"])
@jwt_required()
def add_admin():
    current_admin = get_jwt_identity()
    
    admin = Admin.query.filter_by(username=current_admin).first()

    if not admin or not admin.is_super:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    is_super = data.get("is_super", False)

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    if Admin.query.filter_by(username=username).first():
        return jsonify({"error": "Admin already exists"}), 400

    hashed_pw = generate_password_hash(password)
    role="superadmin" if is_super else "admin"
    new_admin = Admin(username=username, password=password, role=role)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({"message": f"Admin '{username}' added successfully."}), 201


# 🟣 Remove an admin (Super Admin only)
@admin_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def remove_admin(id):
    current_admin = get_jwt_identity()
    admin = Admin.query.filter_by(username=current_admin).first()

    if not admin or not admin.is_super:
        return jsonify({"error": "Unauthorized"}), 403

    target = Admin.query.get(id)
    if not target:
        return jsonify({"error": "Admin not found"}), 404

    db.session.delete(target)
    db.session.commit()
    return jsonify({"message": f"Admin '{target.username}' removed successfully."}), 200


# 🟣 Change Password (Any admin)
# @admin_bp.route("/change-password", methods=["PATCH"])
# @jwt_required()
# def change_password():
#     current_admin = get_jwt_identity()
#     admin = Admin.query.filter_by(username=current_admin).first()

#     data = request.get_json()
#     old_pw = data.get("old_password")
#     new_pw = data.get("new_password")

#     if not all([old_pw, new_pw]):
#         return jsonify({"error": "Both fields required"}), 400

#     if not check_password_hash(admin.password, old_pw):
#         return jsonify({"error": "Incorrect current password"}), 400

#     admin.password = generate_password_hash(new_pw)
#     db.session.commit()

#     return jsonify({"message": "Password changed successfully."}), 200










@admin_bp.route("/change-password", methods=["PATCH"])
@jwt_required()
def change_password():
    current_admin = get_jwt_identity()
    # ✅ If identity is a dict, use current_admin["username"]
    username = current_admin if isinstance(current_admin, dict) else current_admin
    admin = Admin.query.filter_by(username=username).first()

    data = request.get_json()
    old_pw = data.get("old_password")
    new_pw = data.get("new_password")

    if not all([old_pw, new_pw]):
        return jsonify({"error": "Both fields required"}), 400

    # ✅ Use the model's helper for password verification
    if not admin.check_password(old_pw):
        return jsonify({"error": "Incorrect current password"}), 400

    # ✅ Use helper method to set new password
    admin.set_password(new_pw)
    db.session.commit()

    return jsonify({"message": "Password changed successfully."}), 200