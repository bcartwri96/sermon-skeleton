from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email

class Login(FlaskForm):
    pw = PasswordField('pw', validators=[DataRequired()])
    submit = SubmitField('Sign in')
