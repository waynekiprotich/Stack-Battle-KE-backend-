from extensions import db
from datetime import datetime
from sqlalchemy.orm import validates

class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) 
    starter_code_python = db.Column(db.Text, nullable=True)
    starter_code_javascript = db.Column(db.Text, nullable=True)
    is_practice = db.Column(db.Boolean, default=True)
    points_reward = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Float, default=2.0) # Seconds
    memory_limit = db.Column(db.Integer, default=128) # MB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    test_cases = db.relationship('TestCase', backref='challenge', lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship('Submission', backref='challenge', lazy=True)

    @validates('difficulty')
    def validate_difficulty(self, key, difficulty):
        if difficulty not in ['Easy', 'Medium', 'Hard']:
            raise ValueError("Difficulty must be Easy, Medium, or Hard")
        return difficulty

class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeeklyChallenge(db.Model):
    __tablename__ = 'weekly_challenges'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)