from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError
from datetime import date
from src.models.models import Sermon_Series

def content_len_check(form, field):
    try:
        if len(field.data) < 5:
            raise ValidationError("Lenth of description must be >= 5")
    except TypeError:
        raise ValidationError("Cannot be empty")

class Login(FlaskForm):
    pw = PasswordField('pw', validators=[DataRequired()])

class Upload(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    date_given = DateField('date',default=date.today(), \
    format='%d/%m/%Y', \
    validators=[DataRequired(message="You need to enter the start date")])
    sermon_series = SelectField('sermon_series', coerce=int, choices=[(ss.id, ss.name) for ss in Sermon_Series.query.all()])
    description = TextAreaField('description', validators=[content_len_check])
    thumb = FileField('thumb', validators=[
        FileAllowed(['jpg', 'png'], 'Only image uploading is permitted.')])
    sermon = FileField('sermon', validators=[
        FileAllowed(['mp3', 'wav'], 'Only mp3 and wav files accepted!')])

class AddSermonSeries(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

class Search(FlaskForm):
    query = StringField('query', validators=[DataRequired()])
    sub = SubmitField("Search")
