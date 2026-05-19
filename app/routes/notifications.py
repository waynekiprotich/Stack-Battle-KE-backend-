from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.notification import Notification
from app.schemas import notifications_schema, notification_schema
from app.services.notification_service import get_user_notifications, mark_read

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.get("/")
@jwt_required()
def get_notifications():
    """Return the last 50 notifications for the user."""
    user_id = int(get_jwt_identity())
    notifs = get_user_notifications(user_id)
    return notifications_schema.jsonify(notifs), 200


@notifications_bp.put("/<int:notification_id>/read")
@jwt_required()
def mark_as_read(notification_id):
    """Mark a single notification as read."""
    user_id = int(get_jwt_identity())
    try:
        notif = mark_read(notification_id=notification_id, user_id=user_id)
        return jsonify({"message": "Notification marked as read.", "id": notif.id}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@notifications_bp.put("/read-all")
@jwt_required()
def mark_all_read():
    """Mark all unread notifications for the user as read."""
    user_id = int(get_jwt_identity())
    
    # Find all unread notifications for this user
    unread_notifs = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    
    for notif in unread_notifs:
        notif.is_read = True
        
    db.session.commit()
    return jsonify({"message": f"{len(unread_notifs)} notifications marked as read."}), 200


@notifications_bp.delete("/<int:notification_id>")
@jwt_required()
def delete_notification(notification_id):
    """Deletes a notification."""
    user_id = int(get_jwt_identity())
    notif = Notification.query.get_or_404(notification_id)
    
    if notif.user_id != user_id:
        return jsonify({"error": "Forbidden — you can only delete your own notifications."}), 403
        
    db.session.delete(notif)
    db.session.commit()
    
    return jsonify({"message": "Notification deleted."}), 200