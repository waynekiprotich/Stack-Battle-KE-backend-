from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.users import User
from app.schemas import user_schema

# FIX: Removed url_prefix
users_bp = Blueprint("users", __name__)


@users_bp.get("/profile")
@jwt_required()
def get_profile():
    # FIX: Cast to int
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return user_schema.jsonify(user), 200


@users_bp.put("/profile")
@jwt_required()
def update_profile():
    # FIX: Cast to int
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = data["name"].strip()
        if len(name) < 2 or len(name) > 80:
            return jsonify({"error": "Name must be 2–80 characters."}), 400
        user.name = name

    if "bio" in data:
        user.bio = data["bio"].strip()

    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"].strip()

    if "institution_id" in data:
        user.institution_id = data["institution_id"]

    db.session.commit()
    return user_schema.jsonify(user), 200


@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "points": user.points,
        "rank_tier": user.rank_tier,
        "institution": {
            "id": user.institution.id,
            "name": user.institution.name,
        } if user.institution else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }), 200