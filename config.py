import os

_basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "mysecretkey"
    TEMPLATE_FOLDER = "templates"
    BCRYPT_LOG_ROUNDS = 12

    SQLALCHEMY_DATABASE_URI = 'postgresql://podcast:OkTest123@localhost/podcast'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER = 'pyamqp://guest@localhost//'

    CACHE_DIR = '/var/lib/podcast/cache/'
