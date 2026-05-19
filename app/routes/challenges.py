from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.challenge import Challenge, WeeklyChallenge
from app.schemas import challenge_schema, challenges_schema, weekly_schema

challenges_bp = Blueprint("challenges", __name__, url_prefix="/api/challenges")

# -------------------------
# GET ALL CHALLENGES
# -------------------------
@challenges_bp.route("/", methods=["GET"])
@jwt_required()
def get_challenges():
    difficulty = request.args.get("difficulty")
    query = Challenge.query

    if difficulty:
        if difficulty not in ["Easy", "Medium", "Hard"]:
            return jsonify({"error": "difficulty must be Easy, Medium, or Hard"}), 400
        query = query.filter_by(difficulty=difficulty)

    challenges = query.order_by(Challenge.created_at.desc()).all()

    return jsonify(challenges_schema.dump(challenges)), 200


# -------------------------
# PRACTICE
# -------------------------
@challenges_bp.route("/practice", methods=["GET"])
@jwt_required()
def get_practice():
    challenges = (
        Challenge.query
        .filter_by(is_practice=True)
        .order_by(Challenge.created_at.desc())
        .all()
    )

    return jsonify(challenges_schema.dump(challenges)), 200


# -------------------------
# WEEKLY
# -------------------------
@challenges_bp.route("/weekly", methods=["GET"])
@jwt_required()
def get_weekly():
    weekly = WeeklyChallenge.query.filter_by(is_active=True).first()

    if not weekly:
        return jsonify({"error": "No active weekly challenge"}), 404

    return weekly_schema.jsonify(weekly), 200


# -------------------------
# SINGLE CHALLENGE
# -------------------------
@challenges_bp.route("/<int:challenge_id>", methods=["GET"])
@jwt_required()
def get_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    return challenge_schema.jsonify(challenge), 200