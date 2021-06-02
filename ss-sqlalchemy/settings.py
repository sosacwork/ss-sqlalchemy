import os


class Config(object):
    """Base configuration"""
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DATABASE_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'sqlitedb'))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + DATABASE_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
