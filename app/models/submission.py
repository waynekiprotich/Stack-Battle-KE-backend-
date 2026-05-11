from extensions import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False) # python or javascript
    code = db.Column(db.Text, nullable=False)
    
    # Execution results
    stdout = db.Column(db.Text, nullable=True)
    stderr = db.Column(db.Text, nullable=True)
    execution_time = db.Column(db.Float, nullable=True)
    memory_used = db.Column(db.Float, nullable=True)
    
    # Outcome
    status = db.Column(db.String(50), default='Pending') # Accepted, Wrong Answer, etc.
    score = db.Column(db.Integer, default=0)
    passed_tests = db.Column(db.Integer, default=0)
    total_tests = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)