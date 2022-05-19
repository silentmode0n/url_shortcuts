import os
import uuid


SECRET_KEY = os.environ.get('SECRET_KEY') or uuid.uuid4().hex
CSRF_ENABLED = True

DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shortcuts.db' #sqlite for debug from localhost
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1) # for deploy on heroku with postgres db

SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 299}

# CSS styles for flash message on frontend
FLASH_TYPES = {
        'worning': 'toast toast-worning',
        'success': 'toast toast-success',
        'error': 'toast toast-error',
    }
