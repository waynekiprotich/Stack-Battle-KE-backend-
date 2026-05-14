from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.submission import Submission
from app.models.challenge import WeeklyChallenge


def get_global_leaderboard():
    """
    Returns all users ranked by total points.
    Highest scoring users appear first.
    """
    return User.query.order_by(User.points.desc())


def get_group_leaderboard():
    """
    Builds the group leaderboard by:
    1. Adding up points for all members in each group
    2. Counting how many members each group has
    3. Ranking groups from highest to lowest score
    """

    # First build a temporary query that calculates
    # each group's combined points and member count.
    group_stats = (
        db.session.query(
            GroupMember.group_id,
            func.sum(User.points).label("total_points"),
            func.count(User.id).label("member_count")
        )
        .join(User, User.id == GroupMember.user_id)
        .group_by(GroupMember.group_id)
        .subquery()
    )

    # Join the calculated stats back to the Group table
    # so we can access group details like name, id, etc.
    leaderboard = (
        db.session.query(
            Group,
            group_stats.c.total_points,
            group_stats.c.member_count
        )
        .join(group_stats, Group.id == group_stats.c.group_id)
        .order_by(group_stats.c.total_points.desc())
        .all()
    )

    return leaderboard


def get_weekly_leaderboard(week_number):
    """
    Returns rankings for a specific weekly challenge.

    Only accepted submissions within the active challenge
    time window are considered.
    Each user gets ranked using their highest score.
    """

    # Find the active challenge for the selected week
    active_week = WeeklyChallenge.query.filter_by(
        week_number=week_number,
        is_active=True
    ).first_or_404()

    # For each user, keep only their highest accepted score
    # during this challenge period.
    top_scores = (
        db.session.query(
            Submission.user_id,
            func.max(Submission.score).label("best_score")
        )
        .filter(
            Submission.challenge_id == active_week.challenge_id,
            Submission.created_at >= active_week.start_date,
            Submission.created_at <= active_week.end_date,
            Submission.status == "Accepted"
        )
        .group_by(Submission.user_id)
        .subquery()
    )

    # Join score data back to users and rank them
    leaderboard = (
        db.session.query(
            User,
            top_scores.c.best_score
        )
        .join(top_scores, User.id == top_scores.c.user_id)
        .order_by(top_scores.c.best_score.desc())
        .all()
    )

    return leaderboard, active_week