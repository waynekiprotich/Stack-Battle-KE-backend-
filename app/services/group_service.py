from app.extensions import db
from app.models.group import Group, GroupMember
from app.utils.helpers import generate_invite_code


def create_group(admin_id, data):
    """
    Creates a new group and automatically adds
    the creator as the first member.
    """

    # Create the group with a unique invite code
    new_group = Group(
        name=data.get("name", "").strip(),
        description=data.get("description", "").strip(),
        invite_code=generate_invite_code(),
        admin_id=admin_id
    )

    db.session.add(new_group)

    # Flush sends pending changes to the database
    # without committing, which lets us access new_group.id
    db.session.flush()

    # The group creator should also be part of the group
    creator_membership = GroupMember(
        user_id=admin_id,
        group_id=new_group.id
    )

    db.session.add(creator_membership)
    db.session.commit()

    return new_group


def join_group(user_id, invite_code):
    """
    Adds a user to an existing group using
    the group's invite code.
    """

    # Normalize invite code in case user types lowercase
    cleaned_code = invite_code.upper().strip()

    group = Group.query.filter_by(
        invite_code=cleaned_code
    ).first_or_404(
        description=f"No group found with invite code '{invite_code}'."
    )

    # Prevent duplicate memberships
    existing_membership = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group.id
    ).first()

    if existing_membership:
        raise ValueError("You are already a member of this group.")

    new_member = GroupMember(
        user_id=user_id,
        group_id=group.id
    )

    db.session.add(new_member)
    db.session.commit()

    return group


def get_user_groups(user_id):
    """
    Returns all groups that a user belongs to.
    """

    # Get all membership records for this user
    memberships = GroupMember.query.filter_by(
        user_id=user_id
    ).all()

    # Extract group IDs from the membership table
    group_ids = [membership.group_id for membership in memberships]

    # Fetch actual group details
    user_groups = Group.query.filter(
        Group.id.in_(group_ids)
    ).all()

    return user_groups