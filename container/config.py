import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    TEMPLATES_AUTO_RELOAD = True
    JSON_AS_ASCII=True

    PROTOCOLS_DB_FN = os.path.join(basedir, 'data', 'repertoire.db')
    PROTOCOLS_DB_URI = 'sqlite:///' + PROTOCOLS_DB_FN
    CONFIG_JSON_FILENAME = os.path.join(basedir, 'data', 'config.json')
    ROOT_DIR = basedir

    # Flask-User settings
    USER_APP_NAME = "Radiologie CHUM"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True    # False to simplify register form
