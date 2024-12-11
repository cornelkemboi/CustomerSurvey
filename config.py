# config.py
import os
from datetime import timedelta
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy object
db = SQLAlchemy()


class Config:
    # Database URI for MySQL using pymysql
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:admin@localhost:3307/customer_survey"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional: Disable track modifications to save resources
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function
