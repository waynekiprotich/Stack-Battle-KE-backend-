from flask import Blueprint, jsonify
from app.models.users import Institution
from app.schemas import institutions_schema

# FIX: Removed url_prefix
institutions_bp = Blueprint("institutions", __name__)

@institutions_bp.get("/")
def get_institutions():
    institutions = Institution.query.order_by(Institution.name).all()
    return institutions_schema.jsonify(institutions), 200