"""Expense management routes: page + CRUD API with filter/search support."""

from datetime import datetime

from flask import Blueprint, render_template, jsonify, request

from models import db
from models.expense import Expense
from decorators import login_required, get_current_user
from constants import EXPENSE_CATEGORIES, PAYMENT_METHODS

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/expenses")
@login_required
def expenses_page():
    return render_template("expenses.html", categories=EXPENSE_CATEGORIES, payment_methods=PAYMENT_METHODS)


def _parse_expense_payload(data):
    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number.")
    if amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")

    category = (data.get("category") or "").strip()
    if not category:
        raise ValueError("Please select a category.")

    date_str = (data.get("date") or "").strip()
    try:
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Please provide a valid date (YYYY-MM-DD).")

    description = (data.get("description") or "").strip()
    payment_method = (data.get("payment_method") or "Cash").strip()
    return amount, category, entry_date, description, payment_method


@expenses_bp.route("/api/expenses", methods=["GET"])
@login_required
def list_expenses():
    user = get_current_user()
    query = Expense.query.filter_by(user_id=user.id)

    category = request.args.get("category")
    if category and category != "all":
        query = query.filter(Expense.category == category)

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    if year and month:
        from services import finance_service as fs
        first_day, last_day = fs.month_bounds(year, month)
        query = query.filter(Expense.date >= first_day, Expense.date <= last_day)

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    if date_from:
        query = query.filter(Expense.date >= datetime.strptime(date_from, "%Y-%m-%d").date())
    if date_to:
        query = query.filter(Expense.date <= datetime.strptime(date_to, "%Y-%m-%d").date())

    search = request.args.get("search")
    if search:
        query = query.filter(Expense.description.ilike(f"%{search}%"))

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = round(sum(e.amount for e in expenses), 2)
    return jsonify({"expenses": [e.to_dict() for e in expenses], "total": total})


@expenses_bp.route("/api/expenses", methods=["POST"])
@login_required
def add_expense():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    try:
        amount, category, entry_date, description, payment_method = _parse_expense_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    entry = Expense(
        user_id=user.id, amount=amount, category=category, date=entry_date,
        description=description, payment_method=payment_method,
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "Expense added successfully.", "expense": entry.to_dict()}), 201


@expenses_bp.route("/api/expenses/<int:expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id):
    user = get_current_user()
    entry = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
    if not entry:
        return jsonify({"error": "Expense not found."}), 404

    data = request.get_json(silent=True) or {}
    try:
        amount, category, entry_date, description, payment_method = _parse_expense_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    entry.amount = amount
    entry.category = category
    entry.date = entry_date
    entry.description = description
    entry.payment_method = payment_method
    db.session.commit()
    return jsonify({"message": "Expense updated successfully.", "expense": entry.to_dict()})


@expenses_bp.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    user = get_current_user()
    entry = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
    if not entry:
        return jsonify({"error": "Expense not found."}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Expense deleted successfully."})
