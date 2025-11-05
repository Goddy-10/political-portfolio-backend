

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Slideshow
import os
from werkzeug.utils import secure_filename

import cloudinary
import cloudinary.uploader

slideshow_bp = Blueprint('slideshow_bp', __name__, url_prefix='/api/slides')

# 🟣 Cloudinary Config (use env vars on Render)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 🟣 Upload Slide (Hybrid: Local + Cloudinary)
# @slideshow_bp.route('/upload', methods=['POST'])
# def upload_slide():
#     """
#     Handles both local and cloud uploads.
#     Accepts multipart/form-data:
#       - image: file
#       - caption: text
#       - uploaded_by: text
#     """

#     if 'image' not in request.files:
#         return jsonify({"error": "No image file provided"}), 400

#     image = request.files['image']
#     caption = request.form.get('caption')
#     uploaded_by = request.form.get('uploaded_by')

#     if not uploaded_by:
#         return jsonify({"error": "Uploader name is required"}), 400

#     if image.filename == '' or not allowed_file(image.filename):
#         return jsonify({"error": "Invalid or missing image file"}), 400

#     filename = secure_filename(image.filename)

#     try:
#         # 🟣 If running on Render (production), upload to Cloudinary
#         if os.getenv("RENDER") or os.getenv("CLOUDINARY_CLOUD_NAME"):
#             upload_result = cloudinary.uploader.upload(image)
#             image_url = upload_result.get('secure_url')
#         else:
#             # 🟣 Otherwise, save locally (development)
#             upload_folder = os.path.join(current_app.root_path, 'uploads', 'slides')
#             os.makedirs(upload_folder, exist_ok=True)
#             local_path = os.path.join(upload_folder, filename)
#             image.save(local_path)
#             image_url = f"/uploads/slides/{filename}"  # Served locally

#         # Save to DB
#         slide = Slideshow(
#             image_url=image_url,
#             caption=caption,
#             uploaded_by=uploaded_by
#         )
#         db.session.add(slide)
#         db.session.commit()
@slideshow_bp.route('/upload', methods=['POST'])
def upload_slide_json():
    data = request.get_json()
    image_url = data.get("image_url")
    caption = data.get("caption")
    uploaded_by = data.get("uploaded_by")

    if not image_url or not caption or not uploaded_by:
        return jsonify({"error": "Missing required fields"}), 400

    slide = Slideshow(image_url=image_url, caption=caption, uploaded_by=uploaded_by)
    db.session.add(slide)
    db.session.commit()

    return jsonify({"message": "Slide uploaded successfully", "image_url": image_url}), 201


        # return jsonify({
        #     "message": "Slide uploaded successfully",
        #     "image_url": image_url
        # }), 201

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500


# 🟣 Get All Slides
@slideshow_bp.route('/', methods=['GET'])
def get_slides():
    slides = Slideshow.query.all()
    return jsonify([
        {
            "id": s.id,
            "image_url": s.image_url,
            "caption": s.caption,
            "uploaded_by": s.uploaded_by,
            "is_active": s.is_active,
            "uploaded_at": s.uploaded_at.isoformat()
        } for s in slides
    ]), 200


# 🟣 Toggle Slide Active/Inactive
@slideshow_bp.route('/<int:id>/toggle', methods=['PATCH'])
def toggle_slide(id):
    slide = Slideshow.query.get_or_404(id)
    slide.is_active = not slide.is_active
    db.session.commit()
    return jsonify({"message": "Slide status updated", "is_active": slide.is_active}), 200


# 🟣 Get Active Slides for Homepage
@slideshow_bp.route('/active', methods=['GET'])
def get_active_slides():
    slides = Slideshow.query.filter_by(is_active=True).all()
    return jsonify([
        {
            "id": s.id,
            "image_url": s.image_url,
            "caption": s.caption
        } for s in slides
    ]), 200


# 🟣 Delete Slide
@slideshow_bp.route('/<int:id>', methods=['DELETE'])
def delete_slide(id):
    slide = Slideshow.query.get_or_404(id)
    db.session.delete(slide)
    db.session.commit()
    return jsonify({"message": "Slide deleted successfully"}), 200