from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
# from flask_login import UserMixin
import jwt
from app import db
from hashlib import md5
from time import time
from flask import current_app

# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    tmp_password = db.Column(db.String(100), nullable=False, server_default='')
    reinitialise = db.Column('reset_by_user', db.Boolean(), nullable=False, server_default='0')

   # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')

    # def __init__(self, username=None, email=None, password=None, roles=None, tmp_password=None, active=True, reinitialise=False):
    #     if not username or not email:
    #         raise Exception("User must have username and email")
    #
    #     self.username = username
    #     self.email = email.lower()
    #     self.active = active
    #
    #     if password:
    #         self.tmp_password = ''
    #         self.set_password(tmp_password)
    #         self.reinitialise = True
    #     else:
    #         # make tmp password
    #         if not tmp_password:
    #             tmp_password = get_random_password()
    #         self.tmp_password = tmp_password
    #         self.set_password(tmp_password)
    #         self.reinitialise = False
    #
    #     # Be sure to call the UserMixin's constructor in your class constructor
    #     UserMixin.__init__(self, roles)

    def __repr__(self): #print username
        return '<User: {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    @property
    def is_admin(self):
        for role in self.roles:
            if role.name == 'Admin':
                return True
        return False

        # self.roles.query.filter('Admin').count()

#### for resetting passwords via email
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
####

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

# db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(None, db, User)
