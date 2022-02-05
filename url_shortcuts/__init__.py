__version__ = '0.1.0'


from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid


app = Flask(__name__)

app.config['SECRET_KEY'] = 'very very secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortcuts.db'

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
            print('shortcut_id ', shortcut_id)
            new_item = Shortcuts(url=url, shortcut_id=shortcut_id)
            db.session.add(new_item)
            db.session.commit()
            shortcut_url = request.host_url + shortcut_id
            print('shortcut_url ', shortcut_url)
            flash('Shortcut created')

            return render_template('index.html', shortcut_url=shortcut_url)

    return render_template('index.html')

