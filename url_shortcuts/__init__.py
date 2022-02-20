__version__ = '0.5.1'
__author__ = 'silentmode0n'


import functools
import uuid
import os
import io
import qrcode

from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import session
from flask import g
from flask import send_file

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError


SECRET_KEY = os.environ.get('SECRET_KEY') or uuid.uuid4().hex
DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shortcuts.db'
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from url_shortcuts.models import Shortcuts


def generate_shortcut_id():
    return uuid.uuid4().hex[:8]


def generate_session_id():
    return uuid.uuid4().hex


def check_link(view):

    @functools.wraps(view)
    def wrapped(shortcut_id):
        shortcut = Shortcuts.query.filter_by(shortcut_id=shortcut_id).first()
        if not shortcut:
            push_message('Invalid link', type='error')
            return redirect(url_for('index'))
        g.shortcut = shortcut
        return view(shortcut_id)

    return wrapped


def check_link_pass(view):

    @functools.wraps(view)
    def wrapped(shortcut_id):
        if request.method == 'POST':
            password = request.form.get('password')

            if not g.shortcut.check_password(password):
                push_message('Invalid password', type='error')
                return redirect(url_for(view.__name__, shortcut_id=shortcut_id))

        elif g.shortcut.password_hash:
            return render_template('get_pass.html')

        return view(shortcut_id)

    return wrapped


def add_record_to_shortcuts(url, shortcut_id, password=None):
    new_item = Shortcuts(
        url=url,
        shortcut_id=shortcut_id,
        session_id=g.session_id)
    if password:
        new_item.set_password(password)
    db.session.add(new_item)
    db.session.commit()


def push_message(message, type='worning'):
    types = {
        'worning': 'toast toast-worning',
        'success': 'toast toast-success',
        'error': 'toast toast-error',
    }
    category = types[type] if type in types else types['worning']
    flash(message, category)


def get_qr_file_buffer(data):
    qr = qrcode.QRCode()
    qr.add_data(data)
    buf = io.BytesIO()
    qr.make_image().save(buf, format='JPEG')
    buf.seek(0)
    return buf


@app.template_filter('datetime')
def _jinja2_filter_datetime(date, format=None):
    format = format if format else '%d.%m.%Y %H:%M:%S'
    return date.strftime(format)


@app.before_request
def load_session_id():
    session_id = session.get("session_id", None)

    if session_id:
        g.session_id = session_id
    else:
        g.session_id = generate_session_id()
        session['session_id'] = g.session_id


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        custom_id = request.form.get('custom')
        custom_on = request.form.get('custom_on')
        password_on = request.form.get('password_on')
        password = request.form.get('password')

        if not url:
            push_message('URL must be filled.', type='worning')
        elif custom_on and not custom_id:
            push_message(
                'Input custom shortcut ID or disable the checkbox.',
                type='worning')
        elif password_on and not password:
            push_message(
                'Input password or disable the checkbox.',
                type='worning')
        else:
            shortcut_id = custom_id if custom_on else generate_shortcut_id()
            try:
                add_record_to_shortcuts(url, shortcut_id, password)
                push_message('Shortcut created.', type='success')
            except IntegrityError:
                db.session.rollback()
                push_message(
                    'Shortcut ID is already taken, please try again.',
                    type='error')

        return redirect(url_for('index'))

    shortcuts = Shortcuts.query.filter_by(
        session_id=g.session_id).order_by(Shortcuts.created.desc()).all()

    return render_template('index.html', shortcuts=shortcuts)


@app.route('/<shortcut_id>', methods=['GET', 'POST'])
@check_link
@check_link_pass
def redirect_url(shortcut_id):
    return redirect(g.shortcut.url)


@app.route('/clear')
def clear():
    if session.get('session_id'):
        del session['session_id']
    return redirect(url_for('index'))


@app.route('/qr/<shortcut_id>', methods=['GET', 'POST'])
@check_link
@check_link_pass
def get_qr(shortcut_id):
    return send_file(
        get_qr_file_buffer(g.shortcut.url),
        download_name=f'{shortcut_id}.jpg',
        mimetype='image/jpeg',
    )
