"""Dashboard routes: main overview page and its JSON data API."""

from datetime import date

from flask import Blueprint, render_template, jsonify, request

from decorators import login_required, get_current_user
from services import finance_service as fs
from services import recommendation_service as rs
from models.expense import Expense
from models.goal import Goal

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html")


@dashboard_bp.route("/api/dashboard")
@login_required
def dashboard_api():
    user = get_current_user()
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    summary = fs.savings_summary(user.id, year, month)
    breakdown = fs.category_breakdown(user.id, year, month)
    budget_statuses = fs.budget_status(user.id, year, month)

    recent_expenses = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.date.desc(), Expense.id.desc())
        .limit(5)
        .all()
    )
    goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.created_at.desc()).limit(3).all()

    recommendations = rs.generate_recommendations(user.id, year, month)
    exceeded = [b for b in budget_statuses if b["status"] == "exceeded"]

    # Last 6 months income vs expenses for the trend chart
    trend = []
    y, m = year, month
    for _ in range(6):
        trend.append({
            "label": f"{m:02d}/{y}",
            "income": fs.total_income(user.id, y, m),
            "expenses": fs.total_expenses(user.id, y, m),
        })
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    trend.reverse()

    return jsonify({
        "summary": summary,
        "category_breakdown": breakdown,
        "budget_status": budget_statuses,
        "recent_expenses": [e.to_dict() for e in recent_expenses],
        "goals": [g.to_dict() for g in goals],
        "recommendations": recommendations,
        "budget_warnings": [
            f"You have exceeded your {b['category']} budget by ₹{abs(b['remaining']):,.0f}."
            for b in exceeded
        ],
        "trend": trend,
        "year": year,
        "month": month,
    })
