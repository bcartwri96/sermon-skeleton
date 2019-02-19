import flask as fl
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from src.forms.index import Upload
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
upload_loc = cfg['MAIN']['PROJ_ROOT']+ \
             cfg['MAIN']['UPLOADS_FOLDER']

def up():
    form = Upload()
    if fl.request.method == 'POST':
        if form.validate_on_submit():
            title_given = fl.request.form['title']
            date_given = fl.request.form['date_given']
            ss = fl.request.form['sermon_series']
            description = fl.request.form['description']
            author = fl.request.form['author']

            # check that filename is not taken, otherwise continue.
            q = Sermons.query.filter(Sermons.title == title_given).all()
            if len(q) > 0:
                fl.flash("Title already taken")
                return fl.render_template('upload.html', form=form)

            # upload media to server
            f = fl.request.files['thumb']
            filename = secure_filename(f.filename)
            fname_thumb = os.path.join(upload_loc, filename)
            # todo: pls ensure this gracefully fails!
            f.save(fname_thumb)

            # JSON can't serialise a file object, so convert to bytes
            # save_to_disk.delay(filename, fname_thumb)

            # upload to server first
            f = fl.request.files['sermon']
            filename = secure_filename(f.filename)
            fname_media = os.path.join(upload_loc, filename)
            # todo: ensure this gracefully fails!
            f.save(fname_media)
            # save_to_disk.delay(filename, fname_media)
            upload_a = upload_aws.apply_async(args=[fname_media, title_given, description, author, date_given, fname_thumb, ss, current_user.id])
            print(fname_media, title_given, description, date_given, fname_thumb, ss)
            # upload = upload_podbean.apply_async(args=[fname_media, title_given, description, date_given, fname_thumb, ss])
            # init the workers which upload the content to drive and
            # podcast distro

            return fl.render_template('upload.html', form=form, loc=fname_media, task_id=upload_a.id)
        else:
            fl.flash("Unsuccessful validation")
            fl.flash(str(form.errors))
            return fl.render_template('upload.html', form=form)
    else:


        return fl.render_template('upload.html', form=form, task_id=0)
