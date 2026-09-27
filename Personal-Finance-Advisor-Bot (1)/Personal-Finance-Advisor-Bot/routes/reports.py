"""Monthly reports routes: page + API combining all financial data for a month."""

from datetime import date

from flask import Blueprint, render_template, jsonify, request

from decorators import login_required, get_current_user
from services import finance_service as fs
from services import recommendation_service as rs
from constants import MONTH_NAMES

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports_page():
    return render_template("reports.html", month_names=MONTH_NAMES)


@reports_bp.route("/api/reports/<int:year>/<int:month>")
@login_required
def monthly_report(year, month):
    user = get_current_user()
    if month < 1 or month > 12:
        return jsonify({"error": "Invalid month."}), 400

    summary = fs.savings_summary(user.id, year, month)
    breakdown = fs.category_breakdown(user.id, year, month)
    total_exp = summary["expenses"] or 1  # avoid divide-by-zero
    category_analysis = [
        {
            "category": cat,
            "amount": round(amt, 2),
            "percent_of_total": round((amt / total_exp) * 100, 1),
        }
        for cat, amt in sorted(breakdown.items(), key=lambda x: -x[1])
    ]

    budget_statuses = fs.budget_status(user.id, year, month)
    within_budget = [b for b in budget_statuses if b["status"] == "on_track"]
    approaching = [b for b in budget_statuses if b["status"] == "warning"]
    exceeded = [b for b in budget_statuses if b["status"] == "exceeded"]

    recommendations = rs.generate_recommendations(user.id, year, month)
    summary_text = fs.monthly_summary_text(user.id, year, month)
    variability = fs.income_variability(user.id)

    return jsonify({
        "year": year,
        "month": month,
        "month_name": MONTH_NAMES[month - 1],
        "summary": summary,
        "category_analysis": category_analysis,
        "budget_performance": {
            "within_budget": within_budget,
            "approaching": approaching,
            "exceeded": exceeded,
        },
        "recommendations": recommendations,
        "summary_text": summary_text,
        "income_variability": variability,
    })
