# ================================================
# feedback_routes.py
# Handles feedback submission and summaries
# Aligned with the Feedback model (uses will_vote: Boolean)
# ================================================

from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Feedback

feedback_bp = Blueprint("feedback_bp", __name__, url_prefix="/api/feedback")


# 🟣 Submit Feedback
@feedback_bp.route("/submit", methods=["POST"])
def submit_feedback():
    """
    Accepts a JSON payload with:
    {
      "subcounty": "Muthara",
      "ward": "Kathwana",
      "village": "Kanyuru",
      "age_bracket": "18-28",
      "will_vote": "Yes",      # or "No"
      "reason": "optional"
    }
    """

    data = request.get_json()

    # Extract fields safely
    subcounty = data.get("subcounty")
    ward = data.get("ward")
    village = data.get("village")
    age_bracket = data.get("age_bracket")
    vote_input = data.get("will_vote")  # Expecting 'Yes' or 'No'
    reason = data.get("reason", None)

    # Validate required fields
    if not all([subcounty, ward, village, age_bracket, vote_input]):
        return jsonify({"error": "All fields are required"}), 400

    # Convert 'Yes'/'No' to Boolean
    will_vote = True if vote_input.lower() == "yes" else False

    # Create and save feedback entry
    feedback = Feedback(
        subcounty=subcounty,
        ward=ward,
        village=village,
        age_bracket=age_bracket,
        will_vote=will_vote,
        reason=reason
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({"message": "Feedback submitted successfully"}), 201


# 🟣 Get Summary Totals
@feedback_bp.route("/summary", methods=["GET"])
def get_summary():
    """
    Returns total counts of Yes/No votes and total responses
    """
    total_yes = Feedback.query.filter_by(will_vote=True).count()
    total_no = Feedback.query.filter_by(will_vote=False).count()
    total = Feedback.query.count()

    return jsonify({
        "total_yes": total_yes,
        "total_no": total_no,
        "total_responses": total
    }), 200


# 🟣 Get Breakdown by Region (Subcounty)
@feedback_bp.route("/by-region", methods=["GET"])
def get_by_region():
    """
    Returns breakdown of feedback by subcounty:
    [
      {"subcounty": "Muthara", "total": 10, "yes_count": 8, "no_count": 2},
      {"subcounty": "Tigania East", "total": 5, "yes_count": 3, "no_count": 2}
    ]
    """
    results = (
        db.session.query(
            Feedback.subcounty,
            db.func.count(Feedback.id).label("total"),
            db.func.sum(db.case((Feedback.will_vote == True, 1), else_=0)).label("yes_count"),
            db.func.sum(db.case((Feedback.will_vote == False, 1), else_=0)).label("no_count"),
        )
        .group_by(Feedback.subcounty)
        .all()
    )

    data = []
    for r in results:
        data.append({
            "subcounty": r.subcounty,
            "total": r.total,
            "yes_count": int(r.yes_count or 0),
            "no_count": int(r.no_count or 0),
        })

    return jsonify(data), 200