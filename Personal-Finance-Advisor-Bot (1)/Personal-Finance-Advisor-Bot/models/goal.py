"""Goal model: a savings target the user is tracking progress towards."""

from datetime import datetime
from models import db


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def progress_percent(self):
        if not self.target_amount:
            return 0
        pct = (self.current_amount / self.target_amount) * 100
        return round(min(pct, 100), 1)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "remaining": max(self.target_amount - self.current_amount, 0),
            "progress_percent": self.progress_percent(),
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "description": self.description or "",
        }
