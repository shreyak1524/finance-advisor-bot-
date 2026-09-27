"""
Personal Finance Advisor Bot - Application entry point.

Run with:  python app.py
Or:        python -m flask --app app run
"""

import os
from flask import Flask, render_template
from flask_cors import CORS

from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure the instance folder (holds the default SQLite file) exists.
    os.makedirs(os.path.join(Config.BASE_DIR, "instance"), exist_ok=True)

    db.init_app(app)
    CORS(app)  # Allows the frontend JS to call the API cleanly (safe for local/dev use)

    # --- Register blueprints -------------------------------------------------
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.income import income_bp
    from routes.expenses import expenses_bp
    from routes.budget import budget_bp
    from routes.goals import goals_bp
    from routes.reports import reports_bp
    from routes.ai_advisor import advisor_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(advisor_bp)

    # --- Friendly error pages (no raw stack traces for normal users) --------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("error.html", code=500, message="Something went wrong on our end."), 500

    # --- Automatic database initialization -----------------------------------
    # Creates all tables on first run if they don't already exist. This means
    # a brand-new SQLite database file is ready to use with zero manual setup.
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" allows other devices on the same Wi-Fi network to
    # connect using this computer's local IP address (see README).
    app.run(host="0.0.0.0", port=5000, debug=True)
