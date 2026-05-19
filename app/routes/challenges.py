from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.challenge import Challenge, WeeklyChallenge
from app.schemas import (
    challenge_schema,
    challenges_schema,
    weekly_schema
)

# FIX: Removed url_prefix
challenges_bp = Blueprint("challenges", __name__)

@challenges_bp.route("/", methods=["GET"])
def get_challenges():
    try:
        difficulty = request.args.get("difficulty")
        query = Challenge.query

        if difficulty:
            allowed = ["Easy", "Medium", "Hard"]
            if difficulty not in allowed:
                return jsonify({
                    "error": "difficulty must be Easy, Medium, or Hard"
                }), 400
            query = query.filter_by(difficulty=difficulty)

        challenges = (
            query
            .order_by(Challenge.created_at.desc())
            .all()
        )

        return jsonify({
            "success": True,
            "count": len(challenges),
            "data": challenges_schema.dump(challenges)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@challenges_bp.route("/practice", methods=["GET"])
def get_practice():
    try:
        challenges = (
            Challenge.query
            .filter_by(is_practice=True)
            .order_by(Challenge.created_at.desc())
            .all()
        )

        return jsonify({
            "success": True,
            "count": len(challenges),
            "data": challenges_schema.dump(challenges)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@challenges_bp.route("/weekly", methods=["GET"])
def get_weekly():
    try:
        weekly = (
            WeeklyChallenge.query
            .filter_by(is_active=True)
            .first()
        )

        if not weekly:
            return jsonify({
                "success": False,
                "error": "No active weekly challenge"
            }), 404

        return jsonify({
            "success": True,
            "data": weekly_schema.dump(weekly)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@challenges_bp.route("/<int:challenge_id>", methods=["GET"])
def get_challenge(challenge_id):
    try:
        challenge = Challenge.query.get(challenge_id)

        if not challenge:
            return jsonify({
                "success": False,
                "error": f"Challenge with ID {challenge_id} not found"
            }), 404

        return jsonify({
            "success": True,
            "data": challenge_schema.dump(challenge)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500