from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.group import Group, GroupMember

groups_bp = Blueprint("groups", __name__)

@groups_bp.post("/")
@jwt_required()
def create_group_route():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        is_public = data.get("isPublic", True)

        if not name:
            return jsonify({"success": False, "error": "Group name is required"}), 400

        group = Group(
            name=name,
            description=description,
            is_public=is_public,
            admin_id=user_id
        )

        db.session.add(group)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "is_public": group.is_public,
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@groups_bp.get("/")
@jwt_required()
def list_groups():
    try:
        groups = Group.query
