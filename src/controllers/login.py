#defines the logging in and out process
import flask as fl
from src.forms.index import Login
from flask_login import login_user
from src.models.models import User

def auth():
    # login
    form = Login()
    if fl.request.method == "GET":
        return fl.render_template("login/in.html", form=form)
    else:
        if form.validate_on_submit():
            a = User.query.filter(User.pw == fl.request.form['pw']).all()
            if a != None and len(a) == 1:
                login_user(a[0])
                return fl.redirect(fl.url_for('index'))
            else:
                fl.flash("Admin password not correct :( !")
                return fl.render_template("login/in.html", form=form)
        else:
            fl.flash(str(form.errors))
            return fl.render_template("login/in.html", form=form)
