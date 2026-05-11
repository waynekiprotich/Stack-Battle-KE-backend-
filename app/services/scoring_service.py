from app.extensions import db

def calculate_and_award_points(user, challenge, submission_status):
    """
    Awards points to the user if the submission is Accepted.
    Updates their rank tier.
    """
    if submission_status != "Accepted":
        return 0 # No points for failing

    points_awarded = challenge.points_reward

    # Check if it's a weekly challenge (Simulated check)
    # If a WeeklyChallenge record exists and is active, give bonus
    # (Leaving this simple for MVP purposes)
    # points_awarded += 50 

    # Update User Points
    user.points += points_awarded
    
    # Recalculate rank tier based on new points
    user.calculate_rank()
    
    db.session.commit()
    return points_awarded