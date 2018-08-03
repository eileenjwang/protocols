from flask_wtf import Form
# from flask.ext.admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla import ModelView

from app.models import Role, UserRoles


class MyForm(Form):
    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        self._obj = obj
        super(MyForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

# class MyModelView(ModelView):

class SecureModelView(ModelView):
    # Make Flask-Admin use Flask-WTF
    form_base_class = MyForm
    def is_accessible(self):
        return current_user.is_authenticated

def setup_admin(app):
    admin = Admin(app, template_mode='bootstrap3')
    # Flask and Flask-SQLAlchemy initialization here
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Role, db.session))
    admin.add_view(SecureModelView(UserRoles, db.session))
