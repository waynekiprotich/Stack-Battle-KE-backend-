from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate


jwt = JWTManager()


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Enable CORS
    CORS(app)

    # Register routes
    from app.routes.submissions import submission_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(submission_bp)
    app.register_blueprint(auth_bp)

    @app.route("/health")
    def health():
        return {
            "status": "Stack-Battle KE API is running"
        }, 200

    return app