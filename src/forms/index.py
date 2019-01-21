from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email

class Login(FlaskForm):
    pw = PasswordField('pw', validators=[DataRequired()])

class Upload(FlaskForm):
    thumb = FileField('thumb', validators=[
        FileAllowed(['jpg', 'png'], 'Only image uploading is permitted.')])
