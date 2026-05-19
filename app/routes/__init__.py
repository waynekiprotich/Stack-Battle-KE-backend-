from app.routes.auth import auth_bp
from app.routes.user import users_bp
from app.routes.institutions import institutions_bp
from app.routes.challenges import challenges_bp
from app.routes.submissions import submissions_bp
from app.routes.groups import groups_bp
from app.routes.friends import friends_bp
from app.routes.leaderboard import leaderboard_bp
from app.routes.notifications import notifications_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(institutions_bp, url_prefix="/api/institutions")
    app.register_blueprint(challenges_bp, url_prefix="/api/challenges")
    app.register_blueprint(submissions_bp, url_prefix="/api/submissions")
    app.register_blueprint(groups_bp, url_prefix="/api/groups")
    app.register_blueprint(friends_bp, url_prefix="/api/friends")
    app.register_blueprint(leaderboard_bp, url_prefix="/api/leaderboard")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")