from enum import unique
from url_shortcuts import db
from datetime import datetime


class Shortcuts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortcut = db.Column(db.String(80), unique=True, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.now(), nullable=False)



