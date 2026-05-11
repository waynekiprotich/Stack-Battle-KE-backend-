from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate

# Initialize JWT outside the factory so it can be imported elsewhere
jwt = JWTManager()

def create_app(config_class=Config):
    """
    Application Factory: Creates and configures the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Enable CORS (Cross-Origin Resource Sharing)
    # This allows your React frontend to talk to this API
    CORS(app)

    # Register Blueprints
    from app.routes.submissions import submission_bp
    
    app.register_blueprint(submission_bp)

    # Simple health check route
    @app.route('/health')
    def health():
        return {"status": "Stack-Battle KE API is running"}, 200

    return app