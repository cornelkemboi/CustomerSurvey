from flask import Flask
from flask_login import LoginManager

from app.controllers.manage_users import admin_bp
from app.models.models import User
from config import Config, db

# Initialize LoginManager
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    try:
        db.init_app(app)
    except Exception as e:
        print("Error initializing database:", e)

    # Initialize Flask-Login
    login_manager.init_app(app)

    # Set the login view (this is important for redirection when the user isn't logged in)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.controllers.survey_controller import survey_bp
    from app.controllers.webhook_controller import webhook_bp
    from app.controllers.api_controller import api_bp
    from app.controllers.manage_users import auth_bp

    app.register_blueprint(survey_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    return app


# Register the user_loader function with Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Assuming you're using SQLAlchemy and the user_id is an integer
