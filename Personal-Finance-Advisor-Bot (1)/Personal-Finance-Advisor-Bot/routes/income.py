"""Income management routes: page + CRUD API."""

from datetime import datetime

from flask import Blueprint, render_template, jsonify, request

from models import db
from models.income import Income
from decorators import login_required, get_current_user
from constants import INCOME_SOURCES
from services import finance_service as fs

income_bp = Blueprint("income", __name__)


@income_bp.route("/income")
@login_required
def income_page():
    return render_template("income.html", sources=INCOME_SOURCES)


def _parse_income_payload(data):
    """Validate and parse incoming income JSON. Raises ValueError on bad input."""
    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    source = (data.get("source") or "").strip()
    if not source:
        raise ValueError("Please select an income source.")

    date_str = (data.get("date") or "").strip()
    try:
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Please provide a valid date (YYYY-MM-DD).")

    description = (data.get("description") or "").strip()
    return amount, source, entry_date, description


@income_bp.route("/api/income", methods=["GET"])
@login_required
def list_income():
    user = get_current_user()
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    query = Income.query.filter_by(user_id=user.id)
    if year and month:
        first_day, last_day = fs.month_bounds(year, month)
        query = query.filter(Income.date >= first_day, Income.date <= last_day)

    incomes = query.order_by(Income.date.desc(), Income.id.desc()).all()
    total = round(sum(i.amount for i in incomes), 2)
    return jsonify({"incomes": [i.to_dict() for i in incomes], "total": total})


@income_bp.route("/api/income", methods=["POST"])
@login_required
def add_income():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    try:
        amount, source, entry_date, description = _parse_income_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    entry = Income(user_id=user.id, amount=amount, source=source, date=entry_date, description=description)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "Income added successfully.", "income": entry.to_dict()}), 201


@income_bp.route("/api/income/<int:income_id>", methods=["PUT"])
@login_required
def update_income(income_id):
    user = get_current_user()
    entry = Income.query.filter_by(id=income_id, user_id=user.id).first()
    if not entry:
        return jsonify({"error": "Income entry not found."}), 404

    data = request.get_json(silent=True) or {}
    try:
        amount, source, entry_date, description = _parse_income_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    entry.amount = amount
    entry.source = source
    entry.date = entry_date
    entry.description = description
    db.session.commit()
    return jsonify({"message": "Income updated successfully.", "income": entry.to_dict()})


@income_bp.route("/api/income/<int:income_id>", methods=["DELETE"])
@login_required
def delete_income(income_id):
    user = get_current_user()
    entry = Income.query.filter_by(id=income_id, user_id=user.id).first()
    if not entry:
        return jsonify({"error": "Income entry not found."}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Income deleted successfully."})
