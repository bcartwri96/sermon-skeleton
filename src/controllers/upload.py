import flask as fl
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from src.forms.index import Upload
import os
import configparser as cp

# get conf
cfg = cp.ConfigParser()
cfg.read('config.ini') # read it in.
upload_loc = cfg['MAIN']['PROJ_ROOT']+ \
             cfg['MAIN']['UPLOADS_FOLDER']

def up():
    form = Upload()
    if fl.request.method == 'POST':
        if form.validate_on_submit():
            f = fl.request.files['thumb']
            filename = secure_filename(f.filename)
            fname = os.path.join(upload_loc, filename)
            f.save(fname)
            return fl.render_template('upload.html', form=form, loc=fname)
        else:
            fl.flash("Unsuccessful validation")
            fl.flash(str(form.errors))
            return fl.render_template('upload.html', form=form)
    else:
        fl.flash(str(upload_loc))
        return fl.render_template('upload.html', form=form)
