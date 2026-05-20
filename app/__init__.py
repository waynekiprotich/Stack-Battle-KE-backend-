import os
from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate, jwt, ma
from app.config import get_config


def create_app(env="development"):
    app = Flask(__name__)

    app.url_map.strict_slashes = False
    app.config.from_object(get_config(env))

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "https://op-woking-bske.vercel.app"
    )

    CORS(
        app,
        resources={r"/*": {"origins": [frontend_url, "http://localhost:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    with app.app_context():
        from app.models import (
            User, Institution, Challenge, TestCase,
            WeeklyChallenge, Submission, Group,
            GroupMember, FriendRequest, Notification,
        )

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
