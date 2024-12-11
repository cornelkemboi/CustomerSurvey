# app/models.py
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from config import db  # Import the db object from config

# Role and On-Behalf mappings
role = {"1": "Private", "2": "Public", "3": "Supplier", "4": "Others"}
on_behalf = {"1": "Personnal", "2": "Organization"}


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=True)

    # Relationships to user activities
    created_activities = db.relationship("UserActivity", foreign_keys='UserActivity.create_uid',
                                         back_populates="created_by")
    updated_activities = db.relationship("UserActivity", foreign_keys='UserActivity.write_uid',
                                         back_populates="updated_by")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False


class UserActivity(db.Model):
    __tablename__ = 'user_activity'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    create_uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    write_uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships to users
    created_by = db.relationship("User", foreign_keys=[create_uid], back_populates="created_activities")
    updated_by = db.relationship("User", foreign_keys=[write_uid], back_populates="updated_activities")


class Survey(db.Model):
    __tablename__ = "survey"
    id = db.Column(db.Integer, primary_key=True)
    formdef_version = db.Column(db.String(50))
    formdef_id = db.Column(db.String(50))
    instanceID = db.Column(db.String(100), unique=True)
    key = db.Column("KEY", db.String(100))
    submission_url = db.Column(db.String(255))
    submissionDate = db.Column(db.DateTime)

    responses = db.relationship("SurveyResponse", back_populates="survey")
    category_values = db.relationship("SurveyCategoryValue", back_populates="survey")


class SurveyResponse(db.Model):
    __tablename__ = "survey_responses"
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, ForeignKey("survey.id"), nullable=False)
    appr_comm = db.Column(db.String(255))
    other_appr_comm = db.Column(db.String(255))  # Added
    kippra_interaction = db.Column(db.String(255))
    start_interaction = db.Column(db.String(255))
    overall_satisfaction = db.Column(db.String(255))
    like_most_abt_kippra = db.Column(db.String(255))
    not_like_abt_kippra = db.Column(db.String(255))
    as_ceo_advice = db.Column(db.String(255))
    suggestions = db.Column(db.String(255))
    onbehalf = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    role = db.Column(db.String(50))
    age = db.Column(db.String(10))
    disability = db.Column(db.String(50))
    disability_true = db.Column(db.Boolean)  # Updated type for true/false
    education = db.Column(db.String(50))
    other_education = db.Column(db.String(255))
    kwldg_abt_kippra = db.Column(db.String(255))
    respondents_name = db.Column(db.String(255))
    org_name = db.Column(db.String(255))
    org_category = db.Column(db.String(255))
    note24 = db.Column(db.String(255))  # Added
    note25 = db.Column(db.String(255))  # Added

    survey = db.relationship("Survey", back_populates="responses")


class SurveyCategoryValue(db.Model):
    __tablename__ = "survey_category_values"
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, ForeignKey("survey.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)

    survey = db.relationship("Survey", back_populates="category_values")
