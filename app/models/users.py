from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

# This model represents the educational organizations that users be in
class Institution(db.Model):
    __tablename__ = "institutions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.Enum("University", "Bootcamp", name="institution_type"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    # one-to-many relationship with the User model
    users = db.relationship("User", back_populates="institution", lazy="dynamic")

    def __repr__(self):
        return f"<Institution {self.name}>"

# Model for the main users 
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(300))
    rank_tier = db.Column(db.String(20), default="Beginner")
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # many-to-one relationship
    institution = db.relationship("Institution", back_populates="users")
    # one-to-many relationship
    submissions = db.relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    # one-to-many relationship
    groups = db.relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    #one-to-many relationship
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    # one-to-many relationship
    sent_requests = db.relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    # one-to-many relationship
    recv_requests = db.relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    # Groups this user created (as admin)
    created_groups = db.relationship(
        "Group",
        foreign_keys="Group.admin_id",
        back_populates="admin",
    )

    #Password helpers
    #setting password
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)
    #Checking password
    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    # Rank calculation 
    def calculate_rank(self):
        if self.points <= 200:
            self.rank_tier = "Beginner"
        elif self.points <= 500:
            self.rank_tier = "Intermediate"
        elif self.points <= 1000:
            self.rank_tier = "Advanced"
        else:
            self.rank_tier = "Elite"

    def __repr__(self):
        return f"<User {self.email}>"