"""
Recommendation service (rule-based fallback).

This module produces useful financial recommendations WITHOUT needing any
AI API. It is always available, and is used automatically whenever no
AI_API_KEY is configured, or if the AI service call fails for any reason.
"""

from services import finance_service as fs


def generate_recommendations(user_id, year, month):
    """
    Analyze a user's financial data for the given month and return a list
    of plain-English recommendation strings, based on simple, transparent
    rules.
    """
    recs = []

    summary = fs.savings_summary(user_id, year, month)
    income = summary["income"]
    expenses = summary["expenses"]
    savings_rate = summary["savings_rate"]

    breakdown = fs.category_breakdown(user_id, year, month)

    if income <= 0:
        recs.append(
            "You haven't recorded any income for this month yet. Add your income "
            "entries first so recommendations can be tailored to your situation."
        )
        return recs

    # Rule: expenses exceed income
    if expenses > income:
        over_by = expenses - income
        recs.append(
            f"Your expenses currently exceed your recorded income by ₹{over_by:,.0f}. "
            "Review non-essential spending first, such as entertainment or shopping."
        )

    # Rule: food spending
    food_spend = breakdown.get("Food", 0) + breakdown.get("Groceries", 0)
    if income > 0 and food_spend / income > 0.25:
        recs.append(
            "Your food spending is relatively high compared with your income. "
            "Consider setting a weekly food limit or planning meals in advance."
        )

    # Rule: entertainment spending
    entertainment_spend = breakdown.get("Entertainment", 0)
    if income > 0 and entertainment_spend / income > 0.15:
        recs.append(
            "Entertainment spending is taking a significant portion of your monthly "
            "income. Look for free or lower-cost alternatives a few times a month."
        )

    # Rule: shopping spending
    shopping_spend = breakdown.get("Shopping", 0)
    if income > 0 and shopping_spend / income > 0.15:
        recs.append(
            "Shopping expenses are relatively high this month. Try waiting 24 hours "
            "before non-essential purchases to reduce impulse buying."
        )

    # Rule: savings rate
    if savings_rate < 10:
        recs.append(
            "Your current savings rate is low. Consider identifying one or two "
            "discretionary categories to reduce so you can build a savings cushion."
        )
    elif savings_rate > 20:
        recs.append(
            "Your current savings rate is healthy. Consider maintaining this habit "
            "and setting a specific financial goal for the extra savings."
        )

    # Rule: budget overspending
    statuses = fs.budget_status(user_id, year, month)
    exceeded = [s for s in statuses if s["status"] == "exceeded"]
    for s in exceeded[:3]:
        recs.append(
            f"You have exceeded your {s['category']} budget by "
            f"₹{abs(s['remaining']):,.0f}. Consider adjusting the budget or cutting "
            f"back in this category next month."
        )

    warning = [s for s in statuses if s["status"] == "warning"]
    for s in warning[:2]:
        recs.append(
            f"You have used {s['percent_used']}% of your {s['category']} budget. "
            "Keep an eye on this category for the rest of the month."
        )

    # Rule: income variability (freelancers)
    variability = fs.income_variability(user_id)
    if variability["variable"]:
        recs.append(
            "Your income varies significantly between months. Consider building an "
            "emergency fund based on your average essential monthly expenses, so "
            "leaner months are easier to manage."
        )

    # Rule: no budgets set at all
    if not statuses or all(s["status"] == "no_budget" for s in statuses):
        recs.append(
            "You haven't set a budget for this month yet. Try the 'Generate My "
            "Budget' feature on the Budget page to get a personalized starting point."
        )

    if not recs:
        recs.append(
            "Your finances look balanced this month. Keep tracking your income and "
            "expenses to maintain good habits."
        )

    return recs


def answer_question_fallback(user_id, year, month, question):
    """
    Very simple rule-based responder for the AI Advisor chat page, used when
    no AI API key is configured. Looks for keywords in the question and
    returns the most relevant recommendation(s), plus a general summary.
    """
    question_lower = (question or "").lower()
    recs = generate_recommendations(user_id, year, month)
    summary = fs.savings_summary(user_id, year, month)

    if "save" in question_lower or "saving" in question_lower:
        return (
            f"You are currently saving ₹{summary['savings']:,.0f} this month "
            f"({summary['savings_rate']}% of your income). "
            + " ".join([r for r in recs if "sav" in r.lower()][:2] or recs[:1])
        )

    if "spend" in question_lower or "spending" in question_lower or "overspend" in question_lower:
        top_cat, top_amt = fs.highest_spending_category(user_id, year, month)
        base = (
            f"Your highest spending category this month is {top_cat} at ₹{top_amt:,.0f}."
            if top_cat else "You have not recorded any expenses yet this month."
        )
        return base + " " + " ".join(recs[:2])

    if "afford" in question_lower or "increase" in question_lower:
        if summary["savings_rate"] > 20:
            return (
                "Based on your current savings rate, you may have some room to "
                "increase discretionary spending slightly, but keep tracking your "
                "budget to stay on target."
            )
        return (
            "Your current savings rate suggests it may be better to hold off on "
            "increasing discretionary spending for now, and focus on your existing "
            "budget."
        )

    if "reduce" in question_lower or "cut" in question_lower or "unnecessary" in question_lower:
        return " ".join(recs[:3])

    if "how much should i save" in question_lower:
        return (
            "A common guideline is to aim for at least 20% of your income in "
            f"savings. You are currently saving {summary['savings_rate']}%. "
            + (recs[0] if recs else "")
        )

    # Default: general overview
    return (
        f"This month your income is ₹{summary['income']:,.0f}, expenses are "
        f"₹{summary['expenses']:,.0f}, and your savings rate is "
        f"{summary['savings_rate']}%. " + " ".join(recs[:2])
    )
