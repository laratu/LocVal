from . import db
from flask_login import UserMixin




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), unique=True)
    survey_part2_answered = db.Column(db.Boolean)

class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    db_loaded = db.Column(db.Boolean)
   
