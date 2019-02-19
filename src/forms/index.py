from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, \
SelectField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError
from datetime import date
from src.models.models import Sermon_Series, Authors, Books_Bible

def content_len_check(form, field):
    try:
        if len(field.data) < 5:
            raise ValidationError("Lenth of description must be >= 5")
    except TypeError:
        raise ValidationError("Cannot be empty")

def select_field_filled(form, field):
    try:
        if field.data == 0 or field.data == "0":
            raise ValidationError("The field cannot be left empty")
    except TypeError:
        raise ValidationError("Cannot be empty")

# we need to be able to have a select option
res = [(0, "Select")]
for ss in Sermon_Series.query.all():
    res.append((ss.id, ss.name))

class Login(FlaskForm):
    pw = PasswordField('pw', validators=[DataRequired()])

class Upload(FlaskForm):
    title = StringField('title', validators=[DataRequired(), content_len_check])
    date_given = DateField('date',default=date.today(), \
    format='%d/%m/%Y', \
    validators=[DataRequired(message="You need to enter the start date")])
    sermon_series = SelectField('sermon_series', coerce=int, choices=res)
    author = SelectField('author', coerce=int, choices=[(auth.id, \
    auth.name) for auth in Authors.query.all()])
    description = TextAreaField('description', validators=[content_len_check, \
    select_field_filled])
    thumb = FileField('thumb', validators=[
        FileAllowed(['jpg', 'png'], 'Only image uploading is permitted.')])
    sermon = FileField('sermon', validators=[
        FileAllowed(['mp3', 'wav'], 'Only mp3 and wav files accepted!')])
    book_bible = SelectField('book_bible', coerce=int, \
    choices=[(bb.id, bb.nickname) for bb in Books_Bible.query.all()])

class Settings(FlaskForm):
    add_ss_name = StringField('add_ss_name')
    add_author_name = StringField('add_author_name')

class Search(FlaskForm):
    query = StringField('query', validators=[DataRequired()])
    author = SelectField('author', coerce=int, choices=res)
    sub = SubmitField("Search")
