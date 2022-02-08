__version__ = '0.2.0'


from flask import Flask, url_for
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import session
from flask import g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
import os


SECRET_KEY = os.environ.get('SECRET_KEY') or uuid.uuid4().hex
DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shortcuts.db'
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True

db  = SQLAlchemy(app)
migrate = Migrate(app, db)


from url_shortcuts.models import Shortcuts


def generate_shortcut_id():
    return uuid.uuid4().hex[:8]


def generate_session_id():
    return uuid.uuid4().hex


@app.before_request
def load_session_id():
    session_id = session.get("session_id")

    if session_id:
        g.session_id = session_id
    else:
        g.session_id = generate_session_id()
        session['session_id'] = g.session_id


@app.route('/', methods=['GET', 'POST'])
def index():
    message = None

    if request.method == 'POST':
        url = request.form.get('url')

        if not url:
            message = 'URL must be filled'
        else:
            shortcut_id = generate_shortcut_id()
            new_item = Shortcuts(url=url, shortcut_id=shortcut_id, session_id=g.session_id)
            db.session.add(new_item)
            db.session.commit()
            message = 'Shortcut created'
            
    shortcuts = Shortcuts.query.filter_by(session_id=g.session_id).order_by(Shortcuts.created.desc()).all()
    shortcuts = [request.host_url + sh.shortcut_id for sh in shortcuts]

    if message:
        flash(message)

    return render_template('index.html', shortcuts=shortcuts)


@app.route('/<shortcut_id>')
def redirect_url(shortcut_id):
    shortcut = Shortcuts.query.filter_by(shortcut_id=shortcut_id).first()
    print(shortcut) # debug

    if shortcut:
        return redirect(shortcut.url)

    else:
        flash('Invalid link')
        return redirect(url_for('index'))


@app.route('/clear')
def clear():
    if session['session_id']:
        del session['session_id']
    return redirect(url_for('index'))