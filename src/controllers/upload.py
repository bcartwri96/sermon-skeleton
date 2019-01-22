import flask as fl
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from src.forms.index import Upload
import os
import configparser as cp
import src.podbean.index as pod
from src.models.models import Sermons
from datetime import datetime as dt
from src.models.db import session

# get conf
cfg = cp.ConfigParser()
cfg.read('config.ini') # read it in.
upload_loc = cfg['MAIN']['PROJ_ROOT']+ \
             cfg['MAIN']['UPLOADS_FOLDER']

def up():
    form = Upload()
    if fl.request.method == 'POST':
        if form.validate_on_submit():
            # upload media to server
            f = fl.request.files['thumb']
            filename = secure_filename(f.filename)
            fname_thumb = os.path.join(upload_loc, filename)
            # todo: pls ensure this gracefully fails!
            f.save(fname_thumb)

            # upload to server first
            f = fl.request.files['sermon']
            filename = secure_filename(f.filename)
            fname_media = os.path.join(upload_loc, filename)
            # todo: ensure this gracefully fails!
            f.save(fname_media)


            # write this to the database
            title_given = fl.request.form['title']
            date_given = fl.request.form['date_given'] # get the date, format it so it's server ready
            date_given = dt.strptime(date_given, '%d/%m/%Y')
            new_sermon = Sermons(title=title_given, \
                                 date_given=date_given, \
                                 tmp_media=fname_media, \
                                 tmp_thumbnail = fname_thumb)

            session.add(new_sermon)
            try:
                session.commit()

                # init the workers which upload the content to drive and
                # podcast distro
                pass
                
            except KeyError:
                fl.flash("Key error?")

            return fl.render_template('upload.html', form=form, loc=fname_media)
        else:
            fl.flash("Unsuccessful validation")
            fl.flash(str(form.errors))
            return fl.render_template('upload.html', form=form)
    else:
        fl.flash(str(upload_loc))
        return fl.render_template('upload.html', form=form)
