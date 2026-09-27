"""Budget management routes: page, CRUD API, and automatic budget generation."""

from datetime import date

from flask import Blueprint, render_template, jsonify, request

from models import db
from models.budget import Budget
from decorators import login_required, get_current_user
from constants import EXPENSE_CATEGORIES
from services import finance_service as fs

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/budget")
@login_required
def budget_page():
    return render_template("budget.html", categories=EXPENSE_CATEGORIES)


@budget_bp.route("/api/budget", methods=["GET"])
@login_required
def get_budget():
    user = get_current_user()
    today = date.today()
    year = request.args.get("year", type=int, default=today.year)
    month = request.args.get("month", type=int, default=today.month)

    statuses = fs.budget_status(user.id, year, month)
    return jsonify({"budget_status": statuses, "year": year, "month": month})


@budget_bp.route("/api/budget", methods=["POST"])
@login_required
def save_budget():
    """
    Accepts a list of {category, amount} entries for a given month/year and
    creates/updates each one (upsert), so the user can save their whole
    budget form in a single request.
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])
    year = data.get("year")
    month = data.get("month")

    if not year or not month:
        return jsonify({"error": "Year and month are required."}), 400
    if not isinstance(items, list) or not items:
        return jsonify({"error": "No budget items were provided."}), 400

    try:
        year = int(year)
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid month or year."}), 400

    saved = []
    for item in items:
        category = (item.get("category") or "").strip()
        try:
            amount = float(item.get("amount", 0))
        except (TypeError, ValueError):
            continue
        if not category or amount < 0:
            continue

        existing = Budget.query.filter_by(
            user_id=user.id, category=category, month=month, year=year
        ).first()
        if existing:
            existing.amount = amount
        else:
            existing = Budget(user_id=user.id, category=category, amount=amount, month=month, year=year)
            db.session.add(existing)
        saved.append(category)

    db.session.commit()
    return jsonify({"message": f"Budget saved for {len(saved)} categories.", "categories": saved})


@budget_bp.route("/api/budget/generate", methods=["GET"])
@login_required
def generate_budget():
    user = get_current_user()
    today = date.today()
    year = request.args.get("year", type=int, default=today.year)
    month = request.args.get("month", type=int, default=today.month)
    savings_target = request.args.get("savings_target", type=int, default=20)

    suggestion = fs.generate_budget_suggestion(user.id, year, month, savings_target)
    return jsonify(suggestion)
