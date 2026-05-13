from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Initialize SQLAlchemy and Migrate with no app bound yet
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()