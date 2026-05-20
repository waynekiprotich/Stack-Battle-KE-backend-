from marshmallow import fields, validate, EXCLUDE
from app.extensions import ma
from app.models.users import User, Institution
from app.models.challenge import Challenge, TestCase, WeeklyChallenge
from app.models.submission import Submission
from app.models.group import Group, GroupMember
from app.models.friend import FriendRequest
from app.models.notification import Notification

# Institution
class InstitutionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Institution
        load_instance = True
        unknown = EXCLUDE

# User
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password_hash",)
        include_fk = True
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    name = fields.Str(required=True)

    institution = ma.Nested(
        InstitutionSchema,
        only=("id", "name", "type"),
        dump_only=True
    )


# Test Case
class TestCaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TestCase
        load_instance = True
        exclude = ("expected_output",)
        unknown = EXCLUDE

# Challenge 
class ChallengeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Challenge
        load_instance = True
        include_fk = True
        unknown = EXCLUDE

    difficulty = fields.Str(
        validate=validate.OneOf(["Easy", "Medium", "Hard"])
    )

    desc = fields.String(attribute="description", dump_only=True)
    points = fields.Integer(attribute="points_reward", dump_only=True)
    time = fields.Method("format_time", dump_only=True)

    boilerplate = fields.Method("get_boilerplate", dump_only=True)
    examples = fields.Method("get_examples", dump_only=True)
    hiddenTests = fields.Method("get_hidden_tests_count", dump_only=True)

    def format_time(self, obj):
        return f"{obj.time_limit}ms" if obj.time_limit else "5000ms"

    def get_boilerplate(self, obj):
        return {
            "python": obj.starter_code_python or "",
            "javascript": obj.starter_code_javascript or ""
        }

    def get_examples(self, obj):
        try:
            cases = obj.test_cases.all() if hasattr(obj.test_cases, "all") else []
        except Exception:
            cases = []

        visible = [c for c in cases if not c.is_hidden]

        return [
            {
                "input": c.input_data or "",
                "output": c.expected_output or "",
                "explanation": ""
            }
            for c in visible
        ]

    def get_hidden_tests_count(self, obj):
        try:
            cases = obj.test_cases.all() if hasattr(obj.test_cases, "all") else []
        except Exception:
            return 0

        return sum(1 for c in cases if c.is_hidden)
        
# Weekly Challenge
class WeeklyChallengeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WeeklyChallenge
        load_instance = True
        unknown = EXCLUDE
    challenge_id = fields.Integer()

# Submission
class SubmissionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Submission
        load_instance = True
        unknown = EXCLUDE

    language = fields.Str(
        validate=validate.OneOf(["python", "javascript"])
    )
    code = fields.Str(required=True)

    user = ma.Nested(UserSchema, only=("id", "name", "rank_tier"), dump_only=True)
    challenge = ma.Nested(ChallengeSchema, only=("id", "title", "difficulty"), dump_only=True)

# Group
class GroupMemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GroupMember
        load_instance = True
        unknown = EXCLUDE

    user = ma.Nested(UserSchema, only=("id", "name", "points", "rank_tier"), dump_only=True)


class GroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Group
        load_instance = True
        unknown = EXCLUDE

    members = ma.Nested(GroupMemberSchema, many=True, dump_only=True)
    admin = ma.Nested(UserSchema, only=("id", "name"), dump_only=True)

# Friend Request
class FriendRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FriendRequest
        load_instance = True
        unknown = EXCLUDE

    sender = ma.Nested(UserSchema, only=("id", "name"), dump_only=True)
    receiver = ma.Nested(UserSchema, only=("id", "name"), dump_only=True)

# Notification
class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True
        unknown = EXCLUDE

# INSTANCES
institution_schema = InstitutionSchema()
institutions_schema = InstitutionSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

challenge_schema = ChallengeSchema()
challenges_schema = ChallengeSchema(many=True)

weekly_schema = WeeklyChallengeSchema()

submission_schema = SubmissionSchema()
submissions_schema = SubmissionSchema(many=True)

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)

friend_schema = FriendRequestSchema()
friends_schema = FriendRequestSchema(many=True)

notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
