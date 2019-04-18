#defines the logging in and out process
import flask as fl
from django.utils.http import is_safe_url
from src.forms.index import Login
from flask_login import login_user, logout_user
from src.models.models import User
import bcrypt

def auth():
    # login
    form = Login()
    if fl.request.method == "GET":
        return fl.render_template("login/in.html", form=form)
    else:
        print(str(form.data))
        if form.validate_on_submit():

            # THERE IS ONLY ONE USER, SO SIMPLY GRAB THEIR DETAILS
            attempt = fl.request.form['pw']
            pw = User.query.get(1).pw.encode('utf-8')
            if bcrypt.checkpw(attempt.encode('utf-8'), pw.decode('ascii').encode('utf-8')):
                login_user(User.query.get(1))
                fl.flash("Successfully logged in!")

            # a = User.query.filter(bcrypt.checkpw(str(User.pw).encode('utf-8'), pw.decode('ascii').encode('utf-8'))).all()
            # if a != None and len(a) == 1:
                # login_user(a[0])
                # fl.flash("Successfully logged in!")
                # next = fl.request.args.get('next')
                # if not is_safe_url(next):
                #     return fl.abort(400)

                return fl.redirect(fl.url_for('index')) #or next
            else:
                fl.flash("Admin password not correct :( !")
                return fl.render_template("login/in.html", form=form)
        else:
            fl.flash(str(form.errors))
            return fl.render_template("login/in.html", form=form)

def out():
    logout_user()
    fl.flash("Successfully logged out!")
    return fl.redirect(fl.url_for('index'))
