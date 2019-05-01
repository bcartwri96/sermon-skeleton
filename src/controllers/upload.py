import flask as fl
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from src.forms.index import Upload, get_series, get_bb_opts, get_author_opts
import os
import configparser as cp
from src.controllers.podbean import index as pod
from src.models.models import Sermons
from datetime import datetime as dt
from src.models.db import session
from src.scripts.index import get_env_variable
from src.controllers.tasks import upload_podbean, upload_aws
from flask_login import current_user

# get conf
cfg = cp.ConfigParser()
cfg.read('config.ini') # read it in.
upload_loc = cfg['MAIN']['UPLOADS_FOLDER']

def get_presigned(name, type):
    # we need to calculate a presigned url using AWS and then send it back to
    # the client as JSON

    import src.controllers.aws.index as aws
    profile_name = cfg['MAIN']['AWS_PROFILE_NAME']
    bucket_name = cfg['MAIN']['AWS_BUCKET_NAME']

    a = aws.Aws(profile_name, bucket_name)

    return fl.jsonify({'url':a.generate_presigned_upload_url(name, type)})

def post_upload():
    files = fl.request.files['file']
    print("Files: "+str(files))

    return "hello"

def up():
    form = Upload()
    if fl.request.method == 'POST':
        print(fl.request.form)
        if form.validate_on_submit():
            title_given = fl.request.form['title']
            date_given = fl.request.form['date_given']
            ss = fl.request.form['sermon_series']
            description = fl.request.form['description']
            author = fl.request.form['author']
            book_bible = fl.request.form['book_bible']
            chapter_book = fl.request.form['chapter_book']
            sermon_link = fl.request.form['sermon_link']
            thumb_link = fl.request.form['thumb_link']
            length = fl.request.form['size_sermon']

            # check that filename is not taken, otherwise continue.
            q = Sermons.query.filter(Sermons.title == title_given).all()
            if len(q) > 0:
                fl.flash("Title already taken")
                return fl.render_template('upload.html', form=form)

            # save_to_disk.delay(filename, fname_media)
            upload_a = upload_aws.apply_async(args=[sermon_link, title_given, \
            description, author, date_given, thumb_link, ss, current_user.id, \
            book_bible, chapter_book, length])

            return fl.render_template('upload.html', form=form, task_id=upload_a.id)
        else:
            fl.flash("Unsuccessful validation")
            fl.flash(str(form.errors))
            return fl.render_template('upload.html', form=form)
    else:
        # force the form to refresh the options in the database
        form.author.choices =get_author_opts()
        form.sermon_series.choices = get_series()
        form.book_bible.chices = get_bb_opts()

        return fl.render_template('upload.html', form=form, task_id=0)
