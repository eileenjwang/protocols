from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Courrier électronique', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField(
        'Retapez votre mot de passe', validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField('S\'incrire')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Le nom d\'utilisateur que vous avez entré est déjà pris. Veuillez utiliser un nom d\'utilisateur différent.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Le courrier électronique que vous avez entré est déjà pris. Merci d\'utiliser un autre courrier électronique')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Courrier électronique', validators=[DataRequired(), Email()])
    submit = SubmitField('Demande pour une réinitialisation de mot de passe')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Entrez votre nouveau mot de passe', validators=[DataRequired()])
    password2 = PasswordField(
        'Retapez votre nouveau mot de passe', validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField('Demande pour une réinitialisation de mot de passe')
