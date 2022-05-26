import os
import uuid


SECRET_KEY = os.environ.get('SECRET_KEY') or uuid.uuid4().hex
CSRF_ENABLED = True

#sqlite for debug from localhost
# DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shortcuts.db' 
#mysql for debug from localhost
DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://user:userpassword@localhost/shortdb'

# for deploy on heroku with postgres db
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1) 

# config for SqlAlchemy
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 299}

# CSS styles for flash message on frontend
FLASH_TYPES = {
        'worning': 'toast toast-worning',
        'success': 'toast toast-success',
        'error': 'toast toast-error',
    }

LINKS_PER_PAGE = int(os.environ.get('LINKS_PER_PAGE')) or 5
