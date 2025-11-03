from flask import Blueprint, jsonify
from sqlalchemy import func,case
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Feedback, Slideshow,Admin

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api/dashboard")

# ✅ Summary route (Total responses, Yes, No)
@dashboard_bp.route("/summary", methods=["GET"])
def get_summary():
    total = Feedback.query.count()
    total_yes = Feedback.query.filter_by(will_vote=True).count()
    total_no = Feedback.query.filter_by(will_vote=False).count()

    return jsonify({
        "total_feedback": total,
        "total_yes": total_yes,
        "total_no": total_no
    }), 200


# ✅ Breakdown by Subcounty
@dashboard_bp.route("/by-subcounty", methods=["GET"])
def get_by_subcounty():
    results = db.session.query(
        Feedback.subcounty,
        func.count(Feedback.id).label("total"),
        func.sum(case((Feedback.will_vote == True, 1), else_=0)).label("yes_count"),
        func.sum(case((Feedback.will_vote == False, 1), else_=0)).label("no_count")
    ).group_by(Feedback.subcounty).all()

    data = []
    for row in results:
        data.append({
            "subcounty": row.subcounty,
            "total": row.total,
            "yes_count": int(row.yes_count or 0),
            "no_count": int(row.no_count or 0)
        })

    return jsonify(data), 200




# 🟣 Breakdown by Ward
@dashboard_bp.route("/by-ward", methods=["GET"])
def get_by_ward():
    results = (
        db.session.query(
            Feedback.ward,
            db.func.count(Feedback.id).label("total"),
            db.func.sum(db.case((Feedback.will_vote == True, 1), else_=0)).label("yes_count"),
            db.func.sum(db.case((Feedback.will_vote == False, 1), else_=0)).label("no_count"),
        )
        .group_by(Feedback.ward)
        .all()
    )

    data = []
    for r in results:
        data.append({
            "ward": r.ward,
            "total": int(r.total),
            "yes_count": int(r.yes_count),
            "no_count": int(r.no_count)
        })
    return jsonify(data), 200






# 🟣 Breakdown by Village
@dashboard_bp.route("/by-village", methods=["GET"])
def get_by_village():
    results = (
        db.session.query(
            Feedback.village,
            db.func.count(Feedback.id).label("total"),
            db.func.sum(db.case((Feedback.will_vote == True, 1), else_=0)).label("yes_count"),
            db.func.sum(db.case((Feedback.will_vote == False, 1), else_=0)).label("no_count"),
        )
        .group_by(Feedback.village)
        .all()
    )

    data = []
    for r in results:
        data.append({
            "village": r.village,
            "total": int(r.total),
            "yes_count": int(r.yes_count),
            "no_count": int(r.no_count)
        })
    return jsonify(data), 200



# ✅ Quick Stats for Admin Overview
@dashboard_bp.route("/quick-stats", methods=["GET"])
def get_quick_stats():
    total_admins = Admin.query.count()
    total_feedback = Feedback.query.count()
    total_subcounties = db.session.query(Feedback.subcounty).distinct().count()
    latest_feedback = db.session.query(func.max(Feedback.created_at)).scalar()

    return jsonify({
        "total_admins": total_admins,
        "total_feedback": total_feedback,
        "total_subcounties": total_subcounties,
        "latest_feedback": latest_feedback.isoformat() if latest_feedback else None
    }), 200