import flask as fl
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from src.forms.index import Upload
import os
# from src.main import app

def up():
    form = Upload()
    if fl.request.method == 'POST':
        if form.validate_on_submit():
            f = fl.request.files['thumb']
            filename = secure_filename(f.filename)
            fname = os.path.join('uploads/', filename)
            print("saving to... "+str(fname))
            f.save(fname)
            return fl.redirect(fl.url_for('upload'), loc=fname)
        else:
            fl.flash("Unsuccessful validation")
            fl.flash(str(form.errors))
            return fl.render_template('upload.html', form=form)
    else:
        return fl.render_template('upload.html', form=form)
