from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, \
SelectField, TextAreaField, HiddenField
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
series_opts = [(0, "Select")]
for ss in Sermon_Series.query.all():
    series_opts.append((ss.id, ss.name))

books_bible_opts = [(0, "Select")]
for bb in Books_Bible.query.all():
    books_bible_opts.append((bb.id, bb.name))

author_opts = [(0, "Select")]
for a in Authors.query.all():
    author_opts.append((a.id, a.name))


class Login(FlaskForm):
    pw = PasswordField('Password', validators=[DataRequired()])

class Upload(FlaskForm):
    title = StringField('title', validators=[DataRequired(), content_len_check])
    date_given = DateField('date', default=date.today(), \
    format='%d-%m-%Y', \
    validators=[DataRequired(message="You need to enter the sermon date")])
    sermon_series = SelectField('sermon_series', coerce=int, choices=series_opts)
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
    add_ss_name = StringField('Add a Sermon Series')
    add_author_name = StringField('Add an Author Name')
    org_name = StringField('org_name')

class Search(FlaskForm):
    query = StringField('Search term', validators=[DataRequired()])
    author = SelectField('Author', coerce=int, choices=author_opts)
    books_bible = SelectField('Bible Books', coerce=int, choices=books_bible_opts)
    sermon_series = SelectField('Sermon Series', coerce=int, choices=series_opts)
    sub = SubmitField("Search")
