from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from app.extensions import db
from app.models.users import User
from app.schemas import user_schema


def check_email_exists(email):
    """
    Check whether this email is already in use.
    Emails are normalized first to avoid duplicates
    caused by casing or accidental spaces.
    """
    clean_email = email.lower().strip()

    existing_user = User.query.filter_by(
        email=clean_email
    ).first()

    return existing_user is not None


def register_user(data):
    """
    Handles new user registration:
    - validates input
    - prevents duplicate accounts
    - hashes password before saving
    - returns JWT token after successful signup
    """

    # Validate incoming request data
    validation_errors = user_schema.validate(data)

    if validation_errors:
        raise ValidationError(validation_errors)

    clean_email = data["email"].lower().strip()

    # Stop duplicate accounts
    if email_already_registered(clean_email):
        raise ValueError("An account with this email already exists.")

    # Create user object
    new_user = User(
        name=data["name"].strip(),
        email=clean_email,
        institution_id=data.get("institution_id"),
        bio=data.get("bio", ""),
        avatar_url=data.get("avatar_url", "")
    )

    # Hash password before storing it
    new_user.set_password(data["password"])

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    # Automatically log user in after signup
    access_token = create_access_token(identity=new_user.id)

    return {
        "token": access_token,
        "user": user_schema.dump(new_user)
    }


def login_user(data):
    """
    Handles user login by:
    - checking whether the account exists
    - verifying password
    - returning JWT token if successful
    """

    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    # Keep error generic for security reasons
    if not user or not user.check_password(password):
        raise ValueError("Invalid email or password.")

    access_token = create_access_token(identity=user.id)

    return {
        "token": access_token,
        "user": user_schema.dump(user)
    }