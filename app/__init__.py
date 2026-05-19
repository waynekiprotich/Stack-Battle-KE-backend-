from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate, jwt, ma
from app.config import get_config


def create_app(env="development"):
    app = Flask(__name__)

    # ------------------------------------------------------------
    # FIX 1: Avoid strict slash redirect issues (308 errors)
    # ------------------------------------------------------------
    app.url_map.strict_slashes = False

    # ------------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------------
    app.config.from_object(get_config(env))

    # ------------------------------------------------------------
    # FIX 2: CORS (MAIN FIX FOR YOUR ERROR)
    # ------------------------------------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    # ------------------------------------------------------------
    # EXTENSIONS INIT
    # ------------------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # ------------------------------------------------------------
    # LOAD MODELS (ensures SQLAlchemy registers everything)
    # ------------------------------------------------------------
    with app.app_context():
        from app.models import (
            User, Institution, Challenge, TestCase,
            WeeklyChallenge, Submission, Group,
            GroupMember, FriendRequest, Notification,
        )

    # ------------------------------------------------------------
    # REGISTER BLUEPRINTS
    # ------------------------------------------------------------
    from app.routes import register_blueprints
    register_blueprints(app)

    # ------------------------------------------------------------
    # ERROR HANDLERS
    # ------------------------------------------------------------
    from app.errors.handlers import register_error_handlers
    register_error_handlers(app)

    # ------------------------------------------------------------
    # MIDDLEWARE
    # ------------------------------------------------------------
    from app.middleware import register_middleware
    register_middleware(app)

    # ------------------------------------------------------------
    # FIX 3: GLOBAL OPTIONS HANDLER (IMPORTANT FOR PRE-FLIGHT)
    # ------------------------------------------------------------
    @app.before_request
    def handle_preflight():
        from flask import request

        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            headers = response.headers

            headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
            headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
            headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"

            return response

    return app