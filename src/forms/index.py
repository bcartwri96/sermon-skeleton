from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from datetime import date

class Login(FlaskForm):
    pw = PasswordField('pw', validators=[DataRequired()])

class Upload(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    date_given = DateField('date',default=date.today(), format='%d/%m/%Y', validators=[DataRequired(message="You need to enter the start date")])
    thumb = FileField('thumb', validators=[
        FileAllowed(['jpg', 'png'], 'Only image uploading is permitted.')])
    sermon = FileField('sermon', validators=[
        FileAllowed(['mp3', 'wav'], 'Only mp3 and wav files accepted!')])
