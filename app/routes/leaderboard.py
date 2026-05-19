from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.schemas import user_schema, users_schema, group_schema
# FIX: Import get_weekly_leaderboard
from app.services.leaderboard_service import get_global_leaderboard, get_weekly_leaderboard
from app.utils.pagination import paginate
from app.models.group import Group

# FIX: Removed url_prefix
leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.get("/")
@jwt_required()
def global_leaderboard():
    try:
        query = get_global_leaderboard()
        return jsonify(paginate(query, users_schema)), 200

    except Exception as e:
        print("GLOBAL LEADERBOARD ERROR:", str(e))
        return jsonify({"data": [], "error": "global leaderboard failed"}), 200


@leaderboard_bp.get("/groups")
@jwt_required()
def groups_leaderboard():
    try:
        groups = Group.query.all()
        results = []

        for group in groups:
            members = getattr(group, "members", []) or []

            total_points = 0
            member_count = 0

            for m in members:
                user = getattr(m, "user", None)
                if user:
                    total_points += getattr(user, "points", 0) or 0
                    member_count += 1

            results.append({
                "group": group_schema.dump(group),
                "total_points": total_points,
                "member_count": member_count
            })

        results.sort(key=lambda x: x["total_points"], reverse=True)
        return jsonify({"data": results}), 200

    except Exception as e:
        print("GROUP LB ERROR:", str(e))
        return jsonify({"data": [], "error": "failed"}), 200


@leaderboard_bp.get("/weekly/<int:week_number>")
@jwt_required()
def weekly_leaderboard(week_number):
    try:
        # FIX: Call the correct function
        results, weekly = get_weekly_leaderboard(week_number)

        data = []
        for user, best_score in results:
            try:
                data.append({
                    "user": user_schema.dump(user),
                    "best_score": int(best_score or 0),
                })
            except Exception:
                continue

        return jsonify({
            "week_number": getattr(weekly, "week_number", week_number),
            "challenge_id": getattr(weekly, "challenge_id", None),
            "data": data,
        }), 200

    except Exception as e:
        print("WEEKLY LEADERBOARD CRASH:", str(e))
        return jsonify({"data": [], "error": "weekly leaderboard failed"}), 200