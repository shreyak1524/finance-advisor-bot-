"""
Application configuration.

All settings are read from environment variables (loaded from a .env file
by python-dotenv). This keeps secrets out of source code and makes it easy
to switch between SQLite (default, zero setup) and MySQL (production).
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Expose BASE_DIR as a class attribute too, so app.py can reference
    # Config.BASE_DIR consistently wherever it needs the project root.
    BASE_DIR = BASE_DIR

    # Used by Flask to sign session cookies. Falls back to a dev-only value
    # so the app still runs if the developer forgot to set it, but a real
    # value should always be used in .env.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # SQLite by default -> file lives in instance/finance.db and requires
    # no extra installation. Can be swapped for MySQL by changing the
    # DATABASE_URL environment variable, e.g.:
    #   mysql+pymysql://user:password@localhost/finance_db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "finance.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI service configuration. If AI_API_KEY is empty, the app automatically
    # falls back to the local rule-based recommendation engine.
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "").strip().lower()
    AI_API_KEY = os.environ.get("AI_API_KEY", "").strip()
