__version__ = '0.6.3'
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
from flask import abort

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
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
csrf = CSRFProtect(app)

from url_shortcuts.models import Shortcuts
from url_shortcuts.forms import PasswordForm


def generate_shortcut_id():
    return uuid.uuid4().hex[:8]


def generate_session_id():
    return uuid.uuid4().hex


def check_link(view):

    @functools.wraps(view)
    def wrapped(shortcut_id):
        shortcut = Shortcuts.query.filter_by(shortcut_id=shortcut_id).first()
        if not shortcut:
            abort(404)
        g.shortcut = shortcut
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

        errors = False

        if not url:
            errors = True
            push_message('Укажите адрес ссылки.', type='worning')
        if custom_on and not custom_id:
            errors = True
            push_message(
                'Введите желаемое имя ярлыка или отключите переключатель.',
                type='worning')
        if password_on and not password:
            errors = True
            push_message(
                'Введите пароль или отключите переключатель.',
                type='worning')
        if not errors:
            shortcut_id = custom_id if custom_on else generate_shortcut_id()
            try:
                add_record_to_shortcuts(url, shortcut_id, password)
                push_message('Ярлык успешно создан. Можете поделить им.', type='success')
                return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                push_message(
                    'Имя ярлыка должно быть уникальным. Попробуйте снова.',
                    type='error')


    shortcuts = Shortcuts.query.filter_by(
        session_id=g.session_id).order_by(Shortcuts.created.desc()).all()

    return render_template('index.html', shortcuts=shortcuts)


@app.route('/<shortcut_id>', methods=['GET', 'POST'])
@check_link
def redirect_url(shortcut_id):
    if not g.shortcut.password_hash:
            return render_template('redirect.html', link=g.shortcut.url)
            
    form = PasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        if g.shortcut.check_password(password):
            return render_template('redirect.html', link=g.shortcut.url)
        push_message('Пароль не верный!', type='error')

    return render_template('get_pass.html', form=form)


@app.route('/clear')
def clear():
    if session.get('session_id'):
        del session['session_id']
    return redirect(url_for('index'))


@app.route('/qr/<shortcut_id>')
@check_link
def get_qr(shortcut_id):
    return send_file(
        get_qr_file_buffer(url_for('redirect_url', shortcut_id=shortcut_id, _external=True)),
        download_name=f'{shortcut_id}.jpg',
        mimetype='image/jpeg',
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404