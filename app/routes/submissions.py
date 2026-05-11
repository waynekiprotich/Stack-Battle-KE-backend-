from flask import Blueprint, request, jsonify
from extensions import db
from models import Submission, Challenge, TestCase, User
from services.piston_service import execute_code_against_tests
from services.scoring_service import calculate_and_award_points
from flask_jwt_extended import jwt_required, get_jwt_identity

submission_bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')

@submission_bp.route('/submit', methods=['POST'])
@jwt_required() # Protect this route
def submit_code():
    data = request.get_json()
    
    # 1. Extract request data
    challenge_id = data.get('challenge_id')
    language = data.get('language')
    code = data.get('code')
    current_user_id = get_jwt_identity() # Get ID from token

    # 2. Validate Challenge exists
    challenge = Challenge.query.get_or_404(challenge_id)
    user = User.query.get_or_404(current_user_id)
    test_cases = TestCase.query.filter_by(challenge_id=challenge_id).all()

    if not test_cases:
        return jsonify({"error": "No test cases found for this challenge."}), 400

    # 3. Create a Pending Submission
    submission = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        language=language,
        code=code,
        status='Pending'
    )
    db.session.add(submission)
    db.session.commit() # Save to DB to get an ID

    # 4. Send code to Piston API (Business Logic Layer)
    evaluation_result = execute_code_against_tests(code, language, test_cases)

    # 5. Update submission with results
    submission.status = evaluation_result.get('status')
    submission.passed_tests = evaluation_result.get('passed_tests')
    submission.total_tests = evaluation_result.get('total_tests')
    submission.stdout = evaluation_result.get('stdout')
    submission.stderr = evaluation_result.get('stderr')

    # 6. Apply Scoring Logic if Accepted
    points_earned = calculate_and_award_points(user, challenge, submission.status)
    submission.score = points_earned

    # 7. Save final state
    db.session.commit()

    # 8. Return response
    return jsonify({
        "message": "Execution complete.",
        "submission_id": submission.id,
        "status": submission.status,
        "passed_tests": submission.passed_tests,
        "total_tests": submission.total_tests,
        "points_earned": points_earned,
        "new_total_points": user.points,
        "current_rank": user.rank_tier,
        "stdout": submission.stdout,
        "stderr": submission.stderr
    }), 200