from flask import Blueprint, request, jsonify
from app.database import db
from app.models import HeroImage

hero_bp = Blueprint("hero_bp", __name__)

@hero_bp.route("/", methods=["GET"])
def get_hero():
    hero = HeroImage.query.first()
    return jsonify({"image_url": hero.image_url if hero else None})

@hero_bp.route("/", methods=["POST"])
def set_hero():
    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "Image URL required"}), 400

    hero = HeroImage.query.first()
    if hero:
        hero.image_url = image_url
    else:
        db.session.add(HeroImage(image_url=image_url))
    db.session.commit()

    return jsonify({"message": "Hero image updated successfully!"}), 200