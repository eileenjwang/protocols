import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask_user import current_user, UserManager, SQLAlchemyAdapter
from flask import g

import sqlite3 as sql
import json
import datetime
from sqlalchemy import and_

db = SQLAlchemy()
migrate = Migrate()
# user_manager = UserManager(None, db, )

# login = LoginManager()
# login.login_view = 'auth.login'
# login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()
csrf = CSRFProtect()

# user_manager = None

# def init_db(app):
#     global db
#     db = SQLAlchemy(app)
#     from app.models import User
#     print('Creating models..')
#     db.create_all()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    csrf.init_app(app)

    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate.init_app(app, db)
    # login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.main.utils import get_json_data

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Protocols startup')


    # Create protocols database if it does not exist
    print(app.config.get('PROTOCOLS_DB_FN'))
    with sql.connect(app.config.get('PROTOCOLS_DB_FN')) as con:
        cur = con.cursor()
        sql_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';".format(table_name='Protocols')
        cur.execute(sql_query)
        rows = cur.fetchall()

        # if table does not exist or is empty, (create it and) populate it with init_data.json
        if len(rows) == 0 or get_json_data(app) is None:
            cur.execute('CREATE TABLE IF NOT EXISTS Protocols (version_id INTEGER PRIMARY KEY, user, timestamp, JSON_text TEXT)')

            json_data_fn = os.path.join(app.config.get('ROOT_DIR'), 'data', 'init_data.json')
            print(json_data_fn)
            if not os.path.exists(json_data_fn):
                print('Unable to populate db with initial json...')

            else:

                with open(json_data_fn, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                json_str = json.dumps(json_data)
                now = str(datetime.datetime.now())
                user = 'Original Data'

                cur.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
                    (user, now, json_str,))
                con.commit()

    # Setup Flask-User
    # from app.models import User
    # user_manager = UserManager(app, db, User)
    # g.user_manager = user_manager
    # app.config['user_manager'] = user_manager
    # user_manager.init(app)

    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager, current_user=current_user)
    # #
    from app.models import User
    from app.models import user_manager
    user_manager.init_app(app, db, User)
    # from flask_user import UserManager
    # global user_manager
    # user_manager = UserManager(app, db, User)

    # setup admin
    from app.admin import setup_admin
    with app.app_context():
        setup_admin(app, db)

    # make sure admins have admin roles
    with app.app_context():
        admin_role = Role.query.filter(Role.name == 'Admin').one_or_none()
        if not admin_role:
            admin_role = Role(name='Admin')
        for username in app.config['ADMIN_USERNAMES']:
            print(username)
            user = User.query.filter(User.username == username).one_or_none()
            if user:
                print('Found user')
                # user_is_admin = user.is_admin
                # UserRoles.query.filter(and_(UserRoles.user_id == user.id, UserRoles.role_id == admin_role.id))
                if not user.is_admin:
                    print('User is not admin')
                    user.roles.append(admin_role)
                    db.session.add(user)
                    db.session.commit()
    return app

from app import models
from app.models import User, Role, UserRoles
# user_manager = UserManager(app, db, User)
