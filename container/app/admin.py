from flask_admin import Admin
# from flask_wtf import Form
from wtforms_alchemy import ModelForm
from flask_wtf import Form
from flask_admin.form import SecureForm


from app.models import User, Role, UserRoles
from flask_admin.contrib.sqla import ModelView

# from flask.ext.contrib.sqla import ModelView

class MyForm(Form):
    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        self._obj = obj
        super(MyForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

# class MyForm(ModelForm):
#     def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
#         self._obj = obj
#         super(MyForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

# class MyModelView(ModelView):


#
# class UserModelView(SecureModelView):
#     validators=[Unique(model= User, get_session=lambda : db)]
#
#     def get_pk_value(self, model):
#         """
#         Return the primary key value from a model object. If there are multiple primary keys, they’re encoded into string representation.
#         """


def setup_admin(app, db):
    from flask_user import current_user

    class SecureModelView(ModelView):
        # Make Flask-Admin use WTForms-Alchemy
        form_base_class = ModelForm
        def is_accessible(self):
            return current_user.is_authenticated

    class MyModelView(ModelView):
        # Make Flask-Admin use Flask-WTF
        form_base_class = SecureForm
        # form_base_class = ModelForm

    admin = Admin(app, template_mode='bootstrap3')
    # Flask and Flask-SQLAlchemy initialization here
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(SecureModelView(Role, db.session))
    admin.add_view(SecureModelView(UserRoles, db.session))
