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
    # MySQL configuration using environment variables
    MYSQL_DB = os.getenv('MYSQL_DB', 'customer_survey')  # Default to 'customer_survey' if not set
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')  # Default to 'localhost' if not set
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')  # Default to 'root' if not set
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')  # Default to '3306' if not set
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin')  # Default to 'admin' if not set

    # Build the database URI dynamically
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional: Disable track modifications to save resources

    # Flask session and security configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Default secret key if not set
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Session time


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function
