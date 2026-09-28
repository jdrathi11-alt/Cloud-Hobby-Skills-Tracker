import os
import jwt

from functools import wraps
from datetime import datetime, timedelta, timezone

from flask import request, jsonify

from ..models.models import User
from .. import db


SECRET = os.getenv(
    "JWT_SECRET",
    os.getenv("SECRET_KEY", "dev-only-change-me")
)


def make_token(user_id):
    """
    Create a JWT access token for the authenticated user.

    The token is valid for 12 hours.
    """

    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=12),
        },
        SECRET,
        algorithm="HS256",
    )


def current_user():
    """
    Return the currently authenticated user.

    The client must send:

        Authorization: Bearer <token>

    Returns:
        User object if authentication succeeds.
        None if the token is missing, invalid, expired,
        or the user does not exist.
    """

    header = request.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return None

    try:
        token = header.split(" ", 1)[1]

        payload = jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
        )

        user_id = int(payload["sub"])

        # SQLAlchemy 2.x-compatible way of retrieving
        # a record by primary key.
        return db.session.get(User, user_id)

    except Exception:
        # Authentication failures are intentionally treated
        # as unauthenticated requests.
        return None


def login_required(fn):
    """
    Protect an API endpoint from unauthenticated users.

    If authentication succeeds, the current user object is
    passed as the first argument to the protected function.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()

        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401

        return fn(user, *args, **kwargs)

    return wrapper

