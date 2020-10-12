from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from application.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Používateľské meno', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    confirm_password = PasswordField('Potvrďte heslo', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zaregistrovať sa')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Používateľské meno je obsadené. Vyberte si iné.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email je obsadený. Vyberte si iný.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    remember = BooleanField('Zapamätať prihlásenie')
    submit = SubmitField('Prihlásiť sa')


class UpdateAccountForm(FlaskForm):
    username = StringField('Používateľské meno', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Zmeniť profilovú fotografiu', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Uložiť zmeny')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Používateľské meno je obsadené. Vyberte si iné.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email je obsadený. Vyberte si iný.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Chcem si zmeniť heslo')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('S týmto e-mailom neevidujeme žiadny účet. Najprv sa musíte zaregistrovať.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nové heslo', validators=[DataRequired()])
    confirm_password = PasswordField('Potvrďte nové heslo', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Obnoviť heslo')
