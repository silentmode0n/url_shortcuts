__version__ = '0.1.0'

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

app.config['SECRET_KEY'] = 'very very secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortcuts.db'

db  = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    return render_template('index.html')

