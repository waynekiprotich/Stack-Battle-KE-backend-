from flask import request, jsonify

def register_middleware(app):
    """Register before/after request hooks."""

    @app.before_request
    def log_request():
        """Log every incoming request method and path."""
        app.logger.info(f"→ {request.method} {request.path} from {request.remote_addr}")