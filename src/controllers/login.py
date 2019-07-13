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

            email_attempt = fl.request.form['email']
            pw_attempt = fl.request.form['pw']

            # check for email in emails
            print("EMAIL",email_attempt)
            ems = User.query.filter(User.email.contains(email_attempt)).all()
            if len(ems) == 1:
                pw = ems[0].pw.encode('utf-8')
                if bcrypt.checkpw(pw_attempt.encode('utf-8'), pw.decode('ascii').encode('utf-8')):
                    login_user(ems[0])
                    fl.flash("Successfully logged in!")
                else:
                    fl.flash("Admin password not correct :( !")
                    return fl.render_template("login/in.html", form=form)
            else:
                fl.flash("Login not found (email)")
                return fl.render_template("login/in.html", form=form)

            return fl.redirect(fl.url_for('index')) #or next
        else:
            fl.flash(str(form.errors))
            return fl.render_template("login/in.html", form=form)

def out():
    logout_user()
    fl.flash("Successfully logged out!")
    return fl.redirect(fl.url_for('index'))
