import os
if not os.getenv("DATABASE_URL"):
    raise ValueError("No DATABASE_URL Available")

from app.extensions import db
from .models import (
    User,
    Challenge,
    Submission,
    Institution,
    TestCase,
    Group,
    GroupMember,
    FriendRequest,
    WeeklyChallenge,
    Notification,
)
