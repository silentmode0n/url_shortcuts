__version__ = '0.1.0'


from flask import Flask, url_for
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
import os


SECRET_KEY = os.environ.get('SECRET_KEY') or uuid.uuid4().hex
DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shortcuts.db'


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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')

        if not url:
            flash('URL must be filled')
        else:
            shortcut_id = generate_shortcut_id()
            print('shortcut_id ', shortcut_id) # debug
            new_item = Shortcuts(url=url, shortcut_id=shortcut_id)
            db.session.add(new_item)
            db.session.commit()
            shortcut_url = request.host_url + shortcut_id
            print('shortcut_url ', shortcut_url) # debug
            flash('Shortcut created')

            return render_template('index.html', shortcut_url=shortcut_url)

    return render_template('index.html')

@app.route('/<shortcut_id>')
def redirect_url(shortcut_id):
    shortcut = Shortcuts.query.filter_by(shortcut_id=shortcut_id).first()
    print(shortcut) # debug

    if shortcut:
        return redirect(shortcut.url)

    else:
        flash('Invalid link')
        return redirect(url_for('index'))
