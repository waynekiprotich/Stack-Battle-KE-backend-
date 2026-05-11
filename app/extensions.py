from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy and Migrate with no app bound yet
db = SQLAlchemy()
migrate = Migrate()