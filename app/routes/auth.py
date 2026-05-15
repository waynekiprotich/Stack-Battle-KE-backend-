from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request data is required"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    institution_id = data.get("institution_id")

    if not all([name, email, password]):
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    user_exists = User.query.filter_by(email=email).first()

    if user_exists:
        return jsonify({
            "message": "Email is already in use"
        }), 400

    new_user = User(
        name=name,
        email=email,
        institution_id=institution_id
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request data is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "message": "Account not found"
        }), 404

    if not user.check_password(password):
        return jsonify({
            "message": "Incorrect password"
        }), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "points": user.points,
            "rank": user.rank_tier
        }
    }), 200