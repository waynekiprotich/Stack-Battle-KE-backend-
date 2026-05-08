from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# For representing universities and bootcamps
class Institution(db.Model):
    __tablename__ = "institutions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50)) 
    # relation to (one to many with users)
    users = db.relationship("User", backref="institution")

#Students account (track points, rank, school )
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=0)
    rank_tier = db.Column(db.String(50), default="Beginner")

    institution_id = db.Column(
        db.Integer,
        db.ForeignKey("institutions.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    submissions = db.relationship("Submission", backref="user")

#Storing coding questions
class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50))
    is_practice = db.Column(db.Boolean, default=True)
    points = db.Column(db.Integer, default=50)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    test_cases = db.relationship(
        "TestCase",
        backref="challenge"
    )

    submissions = db.relationship(
        "Submission",
        backref="challenge"
    )

# Used for validating submissions done
class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id")
    )

    input_data = db.Column(db.Text)
    expected_output = db.Column(db.Text)
    is_hidden = db.Column(
        db.Boolean,
        default=False
    )

# Storing code submission
class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id")
    )

    language = db.Column(db.String(50))
    code = db.Column(db.Text)
    status = db.Column(db.String(50)) 
    score = db.Column(db.Integer)
    execution_time = db.Column(db.String(50))
    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

#Student groups 
class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    invite_code = db.Column(db.String(20), unique=True)

    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# Many-to-many relationship between users and groups
class GroupMember(db.Model):
    __tablename__ = "group_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.id")
    )
    joined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class FriendRequest(db.Model):
    __tablename__ = "friend_requests"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )
    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )
    status = db.Column(
        db.String(20),
        default="Pending"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

#Tracking weekly challenge
class WeeklyChallenge(db.Model):
    __tablename__ = "weekly_challenges"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id")
    )

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    bonus_points = db.Column(db.Integer, default=100)

# For friend requests 
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )
    message = db.Column(db.Text)
    is_read = db.Column(
        db.Boolean,
        default=False
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

