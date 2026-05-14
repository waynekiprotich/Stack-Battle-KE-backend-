from app.services.piston_service import run_code
from app.extensions import db

def evaluate_submission(submission, challenge, test_cases):
    """
    This function runs the student's code against the test cases using Piston.
    It updates the submission in the database and returns the final results.
    """
    passed = 0
    total = len(test_cases)
    last_stdout = ""
    last_stderr = ""
    last_time = 0.0
    per_test_results = []

    # Loop through every test case one by one
    for tc in test_cases:
        # Send the code to Piston to get the output
        output = run_code(
            language=submission.language,
            code=submission.code,
            stdin=tc.input_data or "",
        )

        # Clean up the output to compare it easily
        actual = output["stdout"].strip()
        expected = tc.expected_output.strip()
        
        # Keep track of the latest output and time
        last_stdout = output["stdout"]
        last_stderr = output["stderr"]
        if output.get("time", 0) > last_time:
            last_time = output.get("time", 0)

        # Check what the result of this specific test was
        if output["stderr"]:
            tc_status = "Runtime Error"
        elif actual == expected:
            tc_status = "Accepted"
            passed += 1
        else:
            tc_status = "Wrong Answer"

        # Save the result for this test case to show the user later
        per_test_results.append({
            "test_case_id": tc.id,
            "passed": tc_status == "Accepted",
            "status": tc_status,
            "is_hidden": tc.is_hidden,
            # If the test is hidden, we don't show the expected/actual output
            "expected": expected if not tc.is_hidden else None,
            "actual": actual if not tc.is_hidden else None,
        })

    # Step 1: Calculate the base score 
    if total > 0:
        ratio = passed / total
    else:
        ratio = 0
    
    score = int(ratio * challenge.points_reward)

    # Step 2: Check for the Weekly Challenge bonus 
    from app.models.challenge import WeeklyChallenge
    # Look for an active weekly challenge that matches this one
    is_weekly = WeeklyChallenge.query.filter_by(
        challenge_id=challenge.id, is_active=True
    ).first()
    
    # If it's a weekly challenge and they got 100%, give 50 extra points
    if is_weekly and passed == total and total > 0:
        score += 50

    # Step 3: Figure out the final status 
    if last_stderr:
        final_status = "Runtime Error"
    elif passed == total and total > 0:
        final_status = "Accepted"
    else:
        final_status = "Wrong Answer"

    # Step 4: Update the submission object with the new data 
    submission.status = final_status
    submission.score = score
    submission.passed_tests = passed
    submission.total_tests = total
    submission.stdout = last_stdout
    submission.stderr = last_stderr
    submission.execution_time = round(last_time, 4)

    # Return the summary of everything that happened
    return {
        "status": final_status,
        "score": score,
        "passed_tests": passed,
        "total_tests": total,
        "results": per_test_results,
    }


def update_user_points(user, score):
    """
    Adds points to the user's account and updates their rank.
    """
    if score > 0:
        # Add the points from this submission
        user.points += score
        
        # Check if the user's rank (Beginner, Elite, etc.) needs to change
        user.calculate_rank()
        
        # Save changes to the database
        db.session.commit()