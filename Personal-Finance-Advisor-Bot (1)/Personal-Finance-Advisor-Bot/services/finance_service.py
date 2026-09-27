"""
Finance service.

Pure calculation helpers that turn raw Income/Expense/Budget/Goal rows into
the numbers the dashboard, reports and AI advisor need. Keeping this logic
in one place means routes stay thin and every page shows numbers computed
the same way.
"""

import calendar
from collections import defaultdict
from datetime import date

from models import db
from models.income import Income
from models.expense import Expense
from models.budget import Budget
from constants import EXPENSE_CATEGORIES, NEED_CATEGORIES, WANT_CATEGORIES


def month_bounds(year, month):
    """Return (first_day, last_day) date objects for a given month/year."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day


def get_incomes_for_month(user_id, year, month):
    first_day, last_day = month_bounds(year, month)
    return (
        Income.query.filter(
            Income.user_id == user_id, Income.date >= first_day, Income.date <= last_day
        )
        .order_by(Income.date.desc())
        .all()
    )


def get_expenses_for_month(user_id, year, month):
    first_day, last_day = month_bounds(year, month)
    return (
        Expense.query.filter(
            Expense.user_id == user_id, Expense.date >= first_day, Expense.date <= last_day
        )
        .order_by(Expense.date.desc())
        .all()
    )


def total_income(user_id, year, month):
    return round(sum(i.amount for i in get_incomes_for_month(user_id, year, month)), 2)


def total_expenses(user_id, year, month):
    return round(sum(e.amount for e in get_expenses_for_month(user_id, year, month)), 2)


def category_breakdown(user_id, year, month):
    """Returns {category: amount_spent} for the given month."""
    breakdown = defaultdict(float)
    for e in get_expenses_for_month(user_id, year, month):
        breakdown[e.category] += e.amount
    return dict(breakdown)


def savings_summary(user_id, year, month):
    income = total_income(user_id, year, month)
    expenses = total_expenses(user_id, year, month)
    savings = round(income - expenses, 2)
    savings_rate = round((savings / income) * 100, 1) if income > 0 else 0.0
    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "savings_rate": savings_rate,
    }


def get_budgets_for_month(user_id, year, month):
    return Budget.query.filter_by(user_id=user_id, year=year, month=month).all()


def budget_status(user_id, year, month):
    """
    Combine budgets with actual spending for the month.
    Returns a list of dicts: category, budget, spent, remaining, percent_used, status
    """
    budgets = {b.category: b.amount for b in get_budgets_for_month(user_id, year, month)}
    spent_by_cat = category_breakdown(user_id, year, month)

    results = []
    all_categories = set(budgets.keys()) | set(spent_by_cat.keys())
    for cat in all_categories:
        budget_amt = budgets.get(cat, 0)
        spent = spent_by_cat.get(cat, 0)
        remaining = round(budget_amt - spent, 2)
        percent_used = round((spent / budget_amt) * 100, 1) if budget_amt > 0 else (100.0 if spent > 0 else 0.0)

        if budget_amt == 0:
            status = "no_budget"
        elif spent > budget_amt:
            status = "exceeded"
        elif percent_used >= 80:
            status = "warning"
        else:
            status = "on_track"

        results.append(
            {
                "category": cat,
                "budget": budget_amt,
                "spent": round(spent, 2),
                "remaining": remaining,
                "percent_used": percent_used,
                "status": status,
            }
        )
    # Sort so exceeded/warning categories show first (most useful to the user)
    order = {"exceeded": 0, "warning": 1, "on_track": 2, "no_budget": 3}
    results.sort(key=lambda r: (order.get(r["status"], 9), -r["spent"]))
    return results


def highest_spending_category(user_id, year, month):
    breakdown = category_breakdown(user_id, year, month)
    if not breakdown:
        return None, 0
    cat = max(breakdown, key=breakdown.get)
    return cat, round(breakdown[cat], 2)


def income_variability(user_id, months_back=6):
    """
    Look back over the last `months_back` months (including current) and
    compute total income per month, to support freelancers with variable
    income. Returns dict with average, highest, lowest, and per-month list.
    """
    today = date.today()
    monthly_totals = []
    y, m = today.year, today.month
    for _ in range(months_back):
        total = total_income(user_id, y, m)
        monthly_totals.append({"year": y, "month": m, "total": total})
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    monthly_totals.reverse()

    non_zero = [x["total"] for x in monthly_totals if x["total"] > 0]
    if not non_zero:
        return {"average": 0, "highest": 0, "lowest": 0, "months": monthly_totals, "variable": False}

    average = round(sum(non_zero) / len(non_zero), 2)
    highest = max(non_zero)
    lowest = min(non_zero)
    # Consider income "variable" if lowest is less than 70% of highest
    variable = len(non_zero) > 1 and (lowest < highest * 0.7)

    return {
        "average": average,
        "highest": highest,
        "lowest": lowest,
        "months": monthly_totals,
        "variable": variable,
    }


def generate_budget_suggestion(user_id, year, month, savings_target_percent=20):
    """
    Auto-generate a suggested monthly budget.

    Approach:
      1. Start from the user's average spending per category over the last
         3 months (their actual habits), if available.
      2. If no history exists, fall back to a 50/30/20 (needs/wants/savings)
         split of their income across common categories.
      3. Always leave room for the savings target.
    """
    income = total_income(user_id, year, month)
    if income <= 0:
        # No income recorded yet - use most recent month with income, else 0
        income = 0

    # Gather average spend per category over the last 3 months (excluding current)
    totals = defaultdict(float)
    months_counted = 0
    y, m = year, month
    for _ in range(3):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        month_data = category_breakdown(user_id, y, m)
        if month_data:
            months_counted += 1
            for cat, amt in month_data.items():
                totals[cat] += amt

    has_history = months_counted > 0
    savings_amount = round(income * (savings_target_percent / 100), 2)
    spendable = max(income - savings_amount, 0)

    suggestion = {}
    if has_history:
        avg_by_cat = {cat: amt / months_counted for cat, amt in totals.items()}
        total_avg_spend = sum(avg_by_cat.values()) or 1
        # Scale historical averages proportionally to fit within spendable income
        scale = spendable / total_avg_spend if total_avg_spend > 0 else 0
        for cat, amt in avg_by_cat.items():
            suggestion[cat] = round(amt * scale, 2) if scale < 5 else round(amt, 2)
        # Make sure every standard category at least appears if income allows
        remaining = spendable - sum(suggestion.values())
        if remaining > 0:
            suggestion["Other"] = round(suggestion.get("Other", 0) + remaining, 2)
    else:
        # No spending history at all: reasonable default split of "needs" income
        default_weights = {
            "Rent": 0.27,
            "Food": 0.15,
            "Transport": 0.09,
            "Bills & Utilities": 0.07,
            "Education": 0.08,
            "Healthcare": 0.05,
            "Entertainment": 0.06,
            "Shopping": 0.05,
            "Travel": 0.04,
            "Other": 0.04,
        }
        for cat, weight in default_weights.items():
            suggestion[cat] = round(spendable * weight, 2)

    suggestion["Savings"] = savings_amount
    return {
        "income": income,
        "savings_target_percent": savings_target_percent,
        "suggested_budget": suggestion,
        "based_on_history": has_history,
    }


def monthly_summary_text(user_id, year, month):
    """Build a human-readable natural-language monthly summary."""
    from constants import MONTH_NAMES

    data = savings_summary(user_id, year, month)
    income, expenses, savings, rate = (
        data["income"], data["expenses"], data["savings"], data["savings_rate"],
    )
    top_cat, top_amt = highest_spending_category(user_id, year, month)
    statuses = budget_status(user_id, year, month)
    exceeded = [s for s in statuses if s["status"] == "exceeded"]

    month_name = MONTH_NAMES[month - 1]
    lines = []
    lines.append(
        f"In {month_name} {year}, your total income was ₹{income:,.0f} and your total "
        f"expenses were ₹{expenses:,.0f}."
    )
    if savings >= 0:
        lines.append(f"You saved ₹{savings:,.0f}, giving you a savings rate of {rate}%.")
    else:
        lines.append(
            f"You spent ₹{abs(savings):,.0f} more than you earned this month "
            f"(savings rate of {rate}%)."
        )
    if top_cat:
        lines.append(f"Your highest spending category was {top_cat} at ₹{top_amt:,.0f}.")
    if exceeded:
        over_texts = [
            f"exceeded your {s['category']} budget by ₹{abs(s['remaining']):,.0f}" for s in exceeded[:2]
        ]
        lines.append("You " + " and ".join(over_texts) + ".")
    if rate < 15:
        lines.append("Based on your spending pattern, reducing discretionary spending could help increase next month's savings.")
    elif rate >= 20:
        lines.append("Great job — your savings rate this month is healthy. Keep it up!")

    return " ".join(lines)
