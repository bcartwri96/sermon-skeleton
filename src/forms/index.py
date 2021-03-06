from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, \
SelectField, TextAreaField, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError
from datetime import date
from src.models.models import Sermon_Series, Authors, Books_Bible, Congregation

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
def get_series():
    series_opts = [(-1, "Select")]
    for ss in Sermon_Series.query.all():
        series_opts.append((ss.id, ss.name))
    return series_opts

def get_bb_opts():
    books_bible_opts = [(-1, "Select")]
    for bb in Books_Bible.query.all():
        books_bible_opts.append((bb.id, bb.name))
    return books_bible_opts

def get_author_opts():
    author_opts = [(-1, "Select")]
    for a in Authors.query.all():
        author_opts.append((a.id, a.name))
    return author_opts

def get_cong_opts():
    cong_opts = [(-1, "Select")]
    for c in Congregation.query.all():
        cong_opts.append((c.id, c.name))
    return cong_opts

class Login(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])

class Upload(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), content_len_check])
    date_given = DateField('Date', default=date.today(), \
    format='%d-%m-%Y', \
    validators=[DataRequired(message="You need to enter the sermon date")])
    sermon_series = SelectField('Sermon Series', coerce=int, choices=get_series(), validators=[DataRequired()])
    author = SelectField('Author', coerce=int, choices=get_author_opts(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[content_len_check, \
    select_field_filled])
    thumb = FileField('Thumbnail Upload', validators=[
        FileAllowed(['png'], 'Only image uploading is permitted.')])
    sermon_link = HiddenField('sermon_link')
    thumb_link = HiddenField('thumb_link')
    sermon = FileField('Sermon Upload', validators=[
        FileAllowed(['mp3', 'wav'], 'Only mp3 and wav files accepted!')])
    book_bible = SelectField('Book of the Bible', coerce=int, \
    choices=get_bb_opts(), validators=[DataRequired()])
    chapter_book = StringField('Chapter(/s) of Bible Preached Upon', validators=[DataRequired()])
    size_sermon = HiddenField('size_sermon')
    congregation = SelectField("Congregation", coerce=int, choices=get_cong_opts(), validators=[DataRequired()])

class Settings(FlaskForm):
    add_ss_name = StringField('Add a Sermon Series')
    add_author_name = StringField('Add an Author Name')
    org_name = StringField('org_name')
    thumb_podcast = FileField("Podcast Thumbnail")
    # changing the password to get into the admin interface here.
    pw = PasswordField('Password')
    pw_c = PasswordField('Confirm Password')

class Search(FlaskForm):
    query = StringField('Search term', validators=[DataRequired()])
    author = SelectField('Author', coerce=int, choices=get_author_opts())
    books_bible = SelectField('Bible Books', coerce=int, choices=get_bb_opts())
    sermon_series = SelectField('Sermon Series', coerce=int, choices=get_series())
    sub = SubmitField("Search")

class Edit_Sermon(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), content_len_check])
    date_given = DateField('Date', default=date.today(), \
    format='%d-%m-%Y', \
    validators=[DataRequired(message="You need to enter the sermon date")])
    sermon_series = SelectField('Sermon Series', coerce=int, choices=get_series())
    author = SelectField('Author', coerce=int, choices=get_author_opts(), default=0)
    description = TextAreaField('Description', validators=[content_len_check, \
    select_field_filled])
    book_bible = SelectField('Book of the Bible', coerce=int, \
    choices=get_bb_opts())
    chapter_book = StringField('Chapter(/s) of Bible Preached Upon', validators=[DataRequired()])
    size_sermon = HiddenField('size_sermon')
    congregation = SelectField("Congregation", coerce=int, choices=get_cong_opts())


class Add_User(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', coerce=str, choices=[["0", "User"], ["1", "Admin"]], default=0)