# app/create_tables.py
from config import db
from app import create_app

app = create_app()

# Create tables
with app.app_context():
    db.create_all()
