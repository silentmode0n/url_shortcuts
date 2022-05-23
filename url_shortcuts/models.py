from url_shortcuts import db
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin


class Shortcuts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortcut_id = db.Column(db.String(80), unique=True, nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)
    last_visited = db.Column(db.DateTime, index=True)
    visits = db.Column(db.Integer, default=0, index=True)
    session_id = db.Column(db.String(40), unique=False)
    password_hash = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return '<Shortcut id:{} link:{}>'.format(self.shortcut_id, self.url)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def mark_visit(self):
        self.last_visited = datetime.now()
        self.visits += 1
        db.session.add(self)
        db.session.commit()

    def switch_on(self):
        if not self.is_active:
            self.is_active = True
            db.session.add(self)
            db.session.commit()

    def switch_off(self):
        if self.is_active:
            self.is_active = False
            db.session.add(self)
            db.session.commit()


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    shortcuts = db.relationship('Shortcuts', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User name: {} email: {}>'.format(self.name, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
