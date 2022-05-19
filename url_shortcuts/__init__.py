__version__ = '0.8.0'
__author__ = 'silentmode0n'


import functools
import uuid
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

from werkzeug.urls import url_parse

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

from config import FLASH_TYPES


app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизируйтесь для полного доступа к ресурсу.'
login_manager.login_message_category = FLASH_TYPES.get('worning')

from url_shortcuts.models import Shortcuts
from url_shortcuts.models import Users

from url_shortcuts.forms import PasswordForm
from url_shortcuts.forms import LoginForm
from url_shortcuts.forms import RegistrationForm


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


def create_shortcut(url, id, user=None, password=None):
    shortcut = Shortcuts(url=url, shortcut_id=id)

    if password:
        shortcut.set_password(password)
    if user:
        shortcut.owner = user
    
    db.session.add(shortcut)
    db.session.commit()


def add_record_to_users(name, email, password):
    new_user = Users(
        name=name,
        email=email,
        )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()


def push_message(message, type='worning'):
    category = FLASH_TYPES[type] if type in FLASH_TYPES else FLASH_TYPES['worning']
    flash(message, category)


def get_qr_file_buffer(data):
    qr = qrcode.QRCode()
    qr.add_data(data)
    buf = io.BytesIO()
    qr.make_image().save(buf, format='JPEG')
    buf.seek(0)
    return buf


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Users': Users, 'Shortcuts': Shortcuts}


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
    

@app.template_filter('datetime')
def _jinja2_filter_datetime(date, format=None):
    format = format if format else '%d.%m.%Y'
    return date.strftime(format) if date else ''


@app.before_request
def load_session_id():
    session_id = session.get("session_id", None)

    if session_id:
        g.session_id = session_id
    else:
        g.session_id = generate_session_id()
        session['session_id'] = g.session_id


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            push_message('Почта или пароль не верные!', type='error')

    return render_template('login.html', form=form)
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registrarion', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        try:
            add_record_to_users(name, email, password)
            push_message('Вы успешно зарегистрировались. Теперь можете войти.', type='success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            push_message(
                'Произошла ошибка записи данных. Попробуйте снова.',
                type='error')

    return render_template('registration.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        url = request.form.get('url')

        errors = False

        if not url:
            errors = True
            push_message('Укажите адрес ссылки.', type='worning')

        if not errors:
            shortcut_id = generate_shortcut_id()
            try:
                add_record_to_shortcuts(url, shortcut_id)
                push_message('Ярлык успешно создан. Можете поделиться им.', type='success')
                return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                push_message(
                    'Произошла ошибка записи данных. Попробуйте снова.',
                    type='error')

    shortcuts = Shortcuts.query.filter_by(
        session_id=g.session_id).order_by(Shortcuts.created.desc()).all()

    return render_template('index.html', shortcuts=shortcuts)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
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
                create_shortcut(
                    url=url,
                    id=shortcut_id,
                    user=current_user,
                    password=password)

                push_message('Ярлык успешно создан. Можете поделиться им.', type='success')
                return redirect(url_for('dashboard'))

            except IntegrityError:
                db.session.rollback()
                push_message(
                    'Имя ярлыка должно быть уникальным. Попробуйте снова.',
                    type='error')

    shortcuts = Shortcuts.query.filter_by(
        owner=current_user).order_by(Shortcuts.created.desc()).all()

    return render_template('dashboard.html', shortcuts=shortcuts)


@app.route('/<shortcut_id>', methods=['GET', 'POST'])
@check_link
def redirect_url(shortcut_id):  # TODO refactoring
    if not g.shortcut.password_hash:
        g.shortcut.mark_visit()
        return render_template('redirect.html', link=g.shortcut.url)
            
    form = PasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        if g.shortcut.check_password(password):
            g.shortcut.mark_visit()
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


@app.route('/delete/<shortcut_id>')
@login_required
@check_link
def delete(shortcut_id):
    try:
        db.session.delete(g.shortcut)
        db.session.commit()
        push_message(
            'Ссылка <{}> удалена.'.format(g.shortcut.shortcut_id),
            type='warning')
    except IntegrityError:
        db.session.rollback()
        push_message(
            'Произошла ошибка записи данных. Попробуйте снова.',
            type='error')
    finally:
        return redirect(url_for('dashboard'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404