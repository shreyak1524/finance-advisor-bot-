"""Financial goals routes: page + CRUD API."""

from datetime import datetime

from flask import Blueprint, render_template, jsonify, request

from models import db
from models.goal import Goal
from decorators import login_required, get_current_user
from constants import GOAL_TYPES

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/goals")
@login_required
def goals_page():
    return render_template("goals.html", goal_types=GOAL_TYPES)


def _parse_goal_payload(data):
    name = (data.get("name") or "").strip()
    if not name:
        raise ValueError("Please provide a goal name.")

    try:
        target_amount = float(data.get("target_amount"))
    except (TypeError, ValueError):
        raise ValueError("Target amount must be a valid number.")
    if target_amount <= 0:
        raise ValueError("Target amount must be greater than zero.")

    try:
        current_amount = float(data.get("current_amount", 0) or 0)
    except (TypeError, ValueError):
        raise ValueError("Saved amount must be a valid number.")
    if current_amount < 0:
        raise ValueError("Saved amount cannot be negative.")

    target_date = None
    date_str = (data.get("target_date") or "").strip()
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Please provide a valid target date.")

    description = (data.get("description") or "").strip()
    return name, target_amount, current_amount, target_date, description


@goals_bp.route("/api/goals", methods=["GET"])
@login_required
def list_goals():
    user = get_current_user()
    goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.created_at.desc()).all()
    return jsonify({"goals": [g.to_dict() for g in goals]})


@goals_bp.route("/api/goals", methods=["POST"])
@login_required
def add_goal():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    try:
        name, target_amount, current_amount, target_date, description = _parse_goal_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    goal = Goal(
        user_id=user.id, name=name, target_amount=target_amount,
        current_amount=current_amount, target_date=target_date, description=description,
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({"message": "Goal created successfully.", "goal": goal.to_dict()}), 201


@goals_bp.route("/api/goals/<int:goal_id>", methods=["PUT"])
@login_required
def update_goal(goal_id):
    user = get_current_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found."}), 404

    data = request.get_json(silent=True) or {}
    try:
        name, target_amount, current_amount, target_date, description = _parse_goal_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    goal.name = name
    goal.target_amount = target_amount
    goal.current_amount = current_amount
    goal.target_date = target_date
    goal.description = description
    db.session.commit()
    return jsonify({"message": "Goal updated successfully.", "goal": goal.to_dict()})


@goals_bp.route("/api/goals/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id):
    user = get_current_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found."}), 404

    db.session.delete(goal)
    db.session.commit()
    return jsonify({"message": "Goal deleted successfully."})
