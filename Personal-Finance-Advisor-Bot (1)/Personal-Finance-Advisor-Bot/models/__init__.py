"""
Models package.

`db` is the single SQLAlchemy instance shared by the whole application.
It is created here (not in app.py) to avoid circular imports: models need
`db`, and app.py needs the models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so that they register themselves with SQLAlchemy's
# metadata. This must happen after `db` is defined above.
from models.user import User        # noqa: E402,F401
from models.income import Income    # noqa: E402,F401
from models.expense import Expense  # noqa: E402,F401
from models.budget import Budget    # noqa: E402,F401
from models.goal import Goal        # noqa: E402,F401
