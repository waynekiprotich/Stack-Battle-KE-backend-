from flask import Blueprint, request, jsonify
from app.models.challenge import Challenge, WeeklyChallenge
from app.schemas import challenge_schema, challenges_schema, weekly_schema

challenges_bp = Blueprint("challenges", __name__)

@challenges_bp.route("/", methods=["GET"])
def get_challenges():
    try:
        difficulty = request.args.get("difficulty")
        query = Challenge.query

        if difficulty:
            if difficulty not in ["Easy", "Medium", "Hard"]:
                return jsonify({"error": "Invalid difficulty"}), 400
            query = query.filter_by(difficulty=difficulty)

        challenges = query.order_by(Challenge.created_at.desc()).all()

        return jsonify({
            "success": True,
            "count": len(challenges),
            "data": challenges_schema.dump(challenges)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@challenges_bp.route("/practice", methods=["GET"])
def get_practice():
    try:
        challenges = Challenge.query.filter_by(is_practice=True).all()

        return jsonify({
            "success": True,
            "count": len(challenges),
            "data": challenges_schema.dump(challenges)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@challenges_bp.route("/weekly", methods=["GET"])
def get_weekly():
    try:
        weekly = WeeklyChallenge.query.filter_by(is_active=True).first()

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
        return jsonify({"success": False, "error": str(e)}), 500

@challenges_bp.route("/<int:challenge_id>", methods=["GET"])
def get_challenge(challenge_id):
    try:
        challenge = Challenge.query.get(challenge_id)

        if not challenge:
            return jsonify({
                "success": False,
                "error": "Challenge not found"
            }), 404

        return jsonify({
            "success": True,
            "data": challenge_schema.dump(challenge)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
