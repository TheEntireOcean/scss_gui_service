# gui-service/app/utils/database.py

# Not necessary since SQLAlchemy handles it, but for custom utils if needed
from app import db

def init_db():
    db.create_all()