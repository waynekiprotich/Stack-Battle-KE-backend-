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
                "is_public": group.is_public
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@groups_bp.get("/")
@jwt_required()
def list_groups():
    try:
        groups = Group.query.all()

        return jsonify({
            "success": True,
            "data": [
                {
                    "id": g.id,
                    "name": g.name,
                    "description": getattr(g, "description", ""),
                    "is_public": getattr(g, "is_public", True)
                }
                for g in groups
            ]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@groups_bp.post("/join")
@jwt_required()
def join_group_route():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True) or {}

        invite_code = data.get("invite_code", "").strip().upper()

        if not invite_code:
            return jsonify({"error": "invite_code is required"}), 400

        group = Group.query.filter_by(invite_code=invite_code).first()

        if not group:
            return jsonify({"error": "Invalid invite code"}), 404

        existing = GroupMember.query.filter_by(
            user_id=user_id,
            group_id=group.id
        ).first()

        if existing:
            return jsonify({"error": "Already a member"}), 409

        member = GroupMember(
            user_id=user_id,
            group_id=group.id
        )

        db.session.add(member)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "group_id": group.id,
                "message": "Joined successfully"
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
