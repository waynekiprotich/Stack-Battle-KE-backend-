import secrets
from datetime import datetime
from app.extensions import db

def generate_invite_code():
    """Generates an 8-character random hex string (e.g., '1a2b3c4d')"""
    return secrets.token_hex(4)

# This represents the group 
class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Auto-generates a unique code if one isn't provided
    invite_code = db.Column(
        db.String(12), 
        unique=True, 
        nullable=False,
        default=generate_invite_code 
    )
    
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # many-to-one relationship
    admin = db.relationship("User", foreign_keys=[admin_id], back_populates="created_groups")
    # one-to-many relationship
    members = db.relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Group {self.name}>"

# This is the connector User to a Group
class GroupMember(db.Model):
    __tablename__ = "group_members"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships back to both sides
    user = db.relationship("User", back_populates="groups")
    group = db.relationship("Group", back_populates="members")

    def __repr__(self):
        return f"<GroupMember user={self.user_id} group={self.group_id}>"