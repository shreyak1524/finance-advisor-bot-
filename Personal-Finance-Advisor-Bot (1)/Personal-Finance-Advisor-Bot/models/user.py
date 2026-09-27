"""User model: stores account information and authentication data."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships - deleting a user cleans up all of their financial data.
    incomes = db.relationship("Income", backref="user", cascade="all, delete-orphan", lazy=True)
    expenses = db.relationship("Expense", backref="user", cascade="all, delete-orphan", lazy=True)
    budgets = db.relationship("Budget", backref="user", cascade="all, delete-orphan", lazy=True)
    goals = db.relationship("Goal", backref="user", cascade="all, delete-orphan", lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}
