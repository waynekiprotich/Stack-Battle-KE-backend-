from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.auth_service import (
    check_email_exists,
    register_user,
    login_user
)

from app.models.users import User
from app.schemas import user_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ------------------------------------------------
# CHECK EMAIL
# ------------------------------------------------
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
        return jsonify({
            "error": "Server error",
            "message": str(e)
        }), 500


# ------------------------------------------------
# REGISTER
# ------------------------------------------------
@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    try:
        result = register_user(data)

        # 🔥 ENSURE token identity is string-safe (if service returns token here)
        if "token" in result:
            result["token"] = result["token"]

        return jsonify(result), 201

    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.messages
        }), 422

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 409

    except Exception as e:
        return jsonify({
            "error": "Unexpected server error",
            "message": str(e)
        }), 500


# ------------------------------------------------
# LOGIN
# ------------------------------------------------
@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    try:
        result = login_user(data)

        # 🔥 IMPORTANT: ensure token exists
        if "token" not in result:
            return jsonify({
                "error": "Login failed - no token generated"
            }), 500

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    except Exception as e:
        return jsonify({
            "error": "Unexpected server error",
            "message": str(e)
        }), 500


# ------------------------------------------------
# CURRENT USER
# ------------------------------------------------
@auth_bp.get("/me")
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()

        # 🔥 FIX: JWT identity comes back as STRING → convert safely
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({"error": "User not found"}), 404

        return user_schema.jsonify(user), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch user",
            "message": str(e)
        }), 500