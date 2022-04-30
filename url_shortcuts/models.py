from url_shortcuts import db
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin


class Shortcuts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortcut_id = db.Column(db.String(80), unique=True, nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    session_id = db.Column(db.String(40), unique=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<Shortcut id:{} link:{}>'.format(self.shortcut_id, self.url)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passUserword_hash, password)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User name: {} email: {}>'.format(self.name, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
