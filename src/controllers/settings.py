from src.models.models import Sermon_Series, Authors, User
import flask as fl
from src.forms.index import Settings
from src.models.db import session
import configparser as cp
from werkzeug.utils import secure_filename
import os
from src.controllers.aws import index as aws
import bcrypt
from flask_login import current_user

def main():
    fm = Settings()
    if fl.request.method == 'GET':
        return fl.render_template('settings.html', form=fm)

    else:
        # get conf
        cfg = cp.ConfigParser()
        cfg.read('config.ini') # read it in.
        upload_loc = cfg['MAIN']['UPLOADS_FOLDER']
        bn = cfg['MAIN']['aws_bucket_name']
        pn = cfg['MAIN']['aws_profile_name']
        a = aws.Aws(bn, pn)

        # process form
        if fm.validate_on_submit():
            ss_name = ""
            auth_name = ""
            thumb_podcast = ""
            pw = ""
            pw_c = ""
            try:
                ss_name = fl.request.form['add_ss_name']
                auth_name = fl.request.form['add_author_name']
                thumb_podcast = fl.request.files['thumb_podcast']
                pw = fl.request.form['pw']
                pw_c = fl.request.form['pw_c']

                print("ss:"+ss_name+".")
                if ss_name == '':
                    print("trigger thing")
                print("an:"+auth_name+".")
            except Exception:
                if not ss_name:
                    ss_name = ""
                if not auth_name:
                    auth_name = ""
                if not thumb_podcast:
                    thumb_podcast = None

            # organisation_name = fl.request.form['org_name']

            # do we need to reset the password?
            if pw != "" and pw_c != "":
                if pw == pw_c:
                    # hash it
                    hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt( 12 ))
                    # get the current user
                    cu = User.query.get(current_user.id)
                    cu.pw = hashed.decode('ascii') # in src/models/db learn about why it
                    # needs to be decoded for ascii before injected into DB
                    session.add(cu)
                else:
                    fl.flash("Passwords provided don't match")

            # any with same name?
            if len(ss_name) != 0:
                same_name = Sermon_Series.query.filter(Sermon_Series.name == ss_name).all()

                res = Sermon_Series(name=ss_name)
                session.add(res)
                print("in here with length ss_name == "+str(len(ss_name)))

            if len(auth_name) != 0:
                same_name = Authors.query.filter(Authors.name == auth_name).all()

                res = Authors(name=auth_name)
                session.add(res)

            if thumb_podcast.filename != '':
                # we got a new file to upload to server
                from PIL import Image

                # save it locally
                filename = secure_filename(thumb_podcast.filename)
                fname_thumb = os.path.join(upload_loc, filename)
                # todo: pls ensure this gracefully fails!
                thumb_podcast.save(fname_thumb)

                img = Image.open(fname_thumb)
                if img.size[0]>= 1400 and img.size[0] <= 3000 and \
                img.size[1] >= 1400 and img.size[1] <= 3000:
                    # save it
                    uploaded = a.upload_resource(fname_thumb, 'png', 'index.png')
                    if not uploaded:
                        old = a.get_obj('index.png')
                        a.rm_objs([old])
                        a.upload_resource(fname_thumb, 'png', 'index.png')
                        os.unlink(fname_thumb) #finished with it, so delete.
                else:
                    # respond to client with failure to upload
                    fl.flash("Couldn't upload this. Size dimensions are not at\
                    least 1400x1400")

            # commit
            try:
                session.commit()
                session.flush()
                fl.flash("Success")
            except IOError:
                fl.flash("Failed to submit to database")

            return fl.redirect(fl.url_for('settings'))
        else:
            fl.flash("Failed")
            return fl.redirect(fl.url_for('settings'))
