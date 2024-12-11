import os
from dotenv import load_dotenv

from flask import Blueprint, render_template

survey_bp = Blueprint("survey", __name__)
load_dotenv()


@survey_bp.route("/")
def index():
    survey_url = os.getenv("SURVEY_URL")  # Fetch the survey URL
    if not survey_url:
        return "SURVEY_URL not set in .env file", 500
    return render_template("index.html", survey_url=survey_url)


@survey_bp.route("/demographic")
def demographic_charts():
    return render_template("demographic_charts.html")


@survey_bp.route("/survey")
def survey_charts():
    return render_template("survey_graphs.html")

