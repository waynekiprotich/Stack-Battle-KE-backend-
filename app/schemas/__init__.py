# Functional use of schema
# Convert database objects
# Validate incoming user data
# Control what fields are exposed or hidden

from marshmallow import fields, validate, validates, ValidationError, EXCLUDE
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

    type = fields.Str(validate=validate.OneOf(["University", "Bootcamp"]))


# User 
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password_hash",)
        
        # Allows institution_id to pass through and ignores unknown fields
        include_fk = True       
        unknown = EXCLUDE       

    # Input validation
    email = fields.Email(required=True, error_messages={"required": "Email is required."})
    password = fields.Str(
        load_only=True,  
        required=True,
        validate=validate.Length(min=8, error="Password must be at least 8 characters."),
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=80, error="Name must be 2–80 characters."),
    )

    institution = ma.Nested(InstitutionSchema, only=("id", "name", "type"), dump_only=True)


# Test Case 
class TestCaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TestCase
        load_instance = True
        exclude = ("expected_output",)


class TestCaseAdminSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TestCase
        load_instance = True


# Challenge
class ChallengeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Challenge
        load_instance = True
        unknown = EXCLUDE
        include_fk = True

    difficulty = fields.Str(
        validate=validate.OneOf(
            ["Easy", "Medium", "Hard"],
            error="Difficulty must be Easy, Medium, or Hard.",
        )
    )
    
    # 1. Map backend columns to the exact keys the React frontend expects
    desc = fields.String(attribute="description", dump_only=True)
    points = fields.Integer(attribute="points_reward", dump_only=True)
    time = fields.Method("format_time", dump_only=True)
    
    # 2. Combine the individual starter code columns into the nested object React wants
    boilerplate = fields.Method("get_boilerplate", dump_only=True)
    
    # 3. Split the test cases into visible 'examples' and a 'hiddenTests' counter
    examples = fields.Method("get_examples", dump_only=True)
    hiddenTests = fields.Method("get_hidden_tests_count", dump_only=True)

    def format_time(self, obj):
        # React expects a string like "5000s" or "5000ms"
        return f"{obj.time_limit}ms" if obj.time_limit else "5000ms"

    def get_boilerplate(self, obj):
        return {
            "python": obj.starter_code_python or "# Write your solution here\npass",
            "javascript": obj.starter_code_javascript or "// Write your solution here"
        }

    def get_examples(self, obj):
            # FIX: Because the model uses lazy="dynamic", we MUST call .all() to get the list
            cases = obj.test_cases.all() if hasattr(obj.test_cases, 'all') else obj.test_cases
            
            if not cases:
                return []
                
            # Filter out hidden tests
            visible_tests = [tc for tc in cases if not tc.is_hidden]
            return [
                {
                    "input": tc.input_data or "",
                    "output": tc.expected_output or "",
                    "explanation": "" 
                } for tc in visible_tests
        ]

    def get_hidden_tests_count(self, obj):
        # FIX: Call .all() here as well
        cases = obj.test_cases.all() if hasattr(obj.test_cases, 'all') else obj.test_cases
        
        if not cases:
            return 0
        return sum(1 for tc in cases if tc.is_hidden)


# Weekly Challenge
class WeeklyChallengeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WeeklyChallenge
        load_instance = True

    challenge = ma.Nested(ChallengeSchema, dump_only=True)


# Submission 
class SubmissionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Submission
        load_instance = True

    language = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["python", "javascript"],
            error="Only Python or JavaScript is supported.",
        ),
    )
    code = fields.Str(required=True, validate=validate.Length(min=1, error="Code cannot be empty."))

    # Nested references 
    user = ma.Nested(UserSchema, only=("id", "name", "rank_tier"), dump_only=True)
    challenge = ma.Nested(ChallengeSchema, only=("id", "title", "difficulty"), dump_only=True)


# Group
class GroupMemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GroupMember
        load_instance = True

    user = ma.Nested(UserSchema, only=("id", "name", "points", "rank_tier"), dump_only=True)


class GroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Group
        load_instance = True
        
        # Add this line to prevent the 422 crash!
        unknown = EXCLUDE 

    name = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100, error="Group name must be 3–100 characters."),
    )
    members = ma.Nested(GroupMemberSchema, many=True, dump_only=True)
    admin = ma.Nested(UserSchema, only=("id", "name"), dump_only=True)


# Friend Request
class FriendRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FriendRequest
        load_instance = True

    sender = ma.Nested(UserSchema, only=("id", "name", "avatar_url"), dump_only=True)
    receiver = ma.Nested(UserSchema, only=("id", "name", "avatar_url"), dump_only=True)
    status = fields.Str(validate=validate.OneOf(["Pending", "Accepted", "Rejected"]))


# Notification  
class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True


# Single instances in routes
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