"""Authentication routes: register, login, logout, and demo data loading."""

import random
from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models import db
from models.user import User
from models.income import Income
from models.expense import Expense
from models.budget import Budget
from models.goal import Goal
from constants import EXPENSE_CATEGORIES, INCOME_SOURCES
from decorators import login_required, get_current_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard_page"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        error = None
        if not name or not email or not password:
            error = "Please fill in all fields."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif password != confirm:
            error = "Passwords do not match."
        elif User.query.filter_by(email=email).first():
            error = "An account with this email already exists."

        if error:
            flash(error, "danger")
            return render_template("register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["user_name"] = user.name
        flash("Account created successfully! Welcome aboard.", "success")
        return redirect(url_for("dashboard.dashboard_page"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard_page"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user.id
        session["user_name"] = user.name
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for("dashboard.dashboard_page"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/demo-data", methods=["POST"])
@login_required
def load_demo_data():
    """
    Populate the current user's account with realistic sample data so they
    can explore the app immediately. Safe to call multiple times (it simply
    adds more sample rows).
    """
    user = get_current_user()
    today = date.today()
    random.seed(42)

    # --- Demo income: salary + occasional freelance work over last 3 months
    for months_ago in range(3):
        month = today.month - months_ago
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        salary_date = date(year, month, 1)
        db.session.add(Income(
            user_id=user.id, amount=30000, source="Salary",
            date=salary_date, description="Monthly salary",
        ))
        if random.random() > 0.4:
            freelance_date = date(year, month, min(15, 28))
            db.session.add(Income(
                user_id=user.id, amount=random.choice([2500, 4000, 6000]),
                source="Freelancing", date=freelance_date,
                description="Freelance project payment",
            ))

    # --- Demo expenses for current month across categories
    demo_expenses = [
        ("Rent", 8000, "Monthly rent"),
        ("Food", 4200, "Groceries and dining"),
        ("Transport", 2100, "Fuel and cab rides"),
        ("Bills & Utilities", 1800, "Electricity and internet"),
        ("Entertainment", 1500, "Movies and streaming"),
        ("Shopping", 2200, "Clothes and essentials"),
        ("Healthcare", 900, "Pharmacy"),
        ("Education", 1000, "Online course"),
        ("Travel", 1200, "Weekend trip"),
        ("Other", 600, "Miscellaneous"),
    ]
    for i, (cat, amt, desc) in enumerate(demo_expenses):
        exp_date = today.replace(day=min(28, max(1, today.day - i)))
        db.session.add(Expense(
            user_id=user.id, amount=amt, category=cat, date=exp_date,
            description=desc, payment_method=random.choice(["UPI", "Cash", "Debit Card"]),
        ))

    # --- Demo budgets for current month
    demo_budgets = {
        "Rent": 8000, "Food": 5000, "Transport": 2500, "Bills & Utilities": 2000,
        "Entertainment": 1500, "Shopping": 1500, "Healthcare": 1000,
        "Education": 1200, "Travel": 1500, "Other": 800,
    }
    for cat, amt in demo_budgets.items():
        existing = Budget.query.filter_by(
            user_id=user.id, category=cat, month=today.month, year=today.year
        ).first()
        if not existing:
            db.session.add(Budget(
                user_id=user.id, category=cat, amount=amt,
                month=today.month, year=today.year,
            ))

    # --- Demo goals
    if not Goal.query.filter_by(user_id=user.id).first():
        db.session.add(Goal(
            user_id=user.id, name="Emergency Fund", target_amount=60000,
            current_amount=25000, target_date=today + timedelta(days=180),
            description="6 months of essential expenses",
        ))
        db.session.add(Goal(
            user_id=user.id, name="New Laptop", target_amount=55000,
            current_amount=12000, target_date=today + timedelta(days=120),
            description="For work and studies",
        ))

    db.session.commit()
    flash("Demo data loaded successfully! Explore the dashboard, budget and reports.", "success")
    return redirect(url_for("dashboard.dashboard_page"))
