"""AI Financial Advisor routes: chat-style page + API with automatic fallback."""

from datetime import date

from flask import Blueprint, render_template, jsonify, request

from decorators import login_required, get_current_user
from services import finance_service as fs
from services import recommendation_service as rs
from services import ai_service

advisor_bp = Blueprint("advisor", __name__)


@advisor_bp.route("/advisor")
@login_required
def advisor_page():
    return render_template("advisor.html")


@advisor_bp.route("/api/advisor", methods=["POST"])
@login_required
def ask_advisor():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    today = date.today()
    year = data.get("year", today.year)
    month = data.get("month", today.month)

    # Build the financial context that gets sent to the AI (or used by the
    # rule-based fallback) so the answer is personalized to this user.
    summary = fs.savings_summary(user.id, year, month)
    context = {
        "income": summary["income"],
        "expenses": summary["expenses"],
        "savings": summary["savings"],
        "savings_rate": summary["savings_rate"],
        "category_breakdown": fs.category_breakdown(user.id, year, month),
        "budget_status": fs.budget_status(user.id, year, month),
        "goals": [],
    }
    from models.goal import Goal
    context["goals"] = [g.to_dict() for g in Goal.query.filter_by(user_id=user.id).all()]

    answer = None
    used_ai = False
    try:
        answer = ai_service.get_ai_response(context, question)
        if answer:
            used_ai = True
    except Exception:
        answer = None

    if not answer:
        answer = rs.answer_question_fallback(user.id, year, month, question)

    return jsonify({
        "answer": answer,
        "used_ai": used_ai,
        "disclaimer": (
            "AI-generated suggestions are for educational and planning purposes "
            "only and should not be considered professional financial advice."
        ),
    })
