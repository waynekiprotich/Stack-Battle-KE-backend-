from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.auth_service import check_email_exists, register_user, login_user
from app.models.users import User
from app.schemas import user_schema

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/check-email")
def check_email():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    email = email.strip().lower()
    try:
        exists = check_email_exists(email)
        return jsonify({"exists": exists}), 200
    except Exception as e:
        return jsonify({"error": "Server error", "message": str(e)}), 500

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    try:
        result = register_user(data)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 422
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": "Unexpected server error", "message": str(e)}), 500

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    try:
        result = login_user(data)
        if "token" not in result:
            return jsonify({"error": "Login failed - no token generated"}), 500
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Unexpected server error", "message": str(e)}), 500

@auth_bp.get("/me")
@jwt_required()
def me():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return user_schema.jsonify(user), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch user", "message": str(e)}), 500
