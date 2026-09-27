"""Reusable request decorators and helpers for authentication."""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from models.user import User


def login_required(view_func):
    """Redirect to login (HTML routes) or return 401 JSON (API routes)."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required. Please log in."}), 401
            return redirect(url_for("auth.login_page"))
        return view_func(*args, **kwargs)

    return wrapped


def get_current_user():
    """Return the logged-in User object, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)
