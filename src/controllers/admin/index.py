# dedicated to controller code that only the admin can use!

import flask as fl
from flask_login import current_user

# index (direct admin to either add and remove users with preset passwords)
def index():
    from src.models.models import User
    from src.models.db import session

    # get all the users who aren't admins
    us = User.query.all()
    print(us)
    if current_user.is_admin(): 
        return fl.render_template('admin/index.html', us=us)
    else:
        fl.flash("Only admins can access this page.")
        return fl.redirect(fl.url_for('index'))

def remove_user(i):
    from src.models.models import User
    from src.models.db import session

    u = User.query.get(i)
    if u:
        session.delete(u)
        try:
            session.commit()
        except KeyError:
            fl.flash("Failed to delete!")
        return fl.redirect(fl.url_for('admin'))
    else:
        return fl.redirect(fl.url_for('admin'))


def add_user():
    from src.models.models import User
    from src.models.db import session
    from src.forms.index import Add_User
    import bcrypt

    fm = Add_User()

    if fl.request.method == 'GET':
        return fl.render_template('admin/add_user.html', fm=fm)
    else:
        if fm.validate_on_submit():
            name = fl.request.form['name']
            email = fl.request.form['email']
            pw = fl.request.form['pw']
            role = fl.request.form['role']

            if len(User.query.filter(User.email == email).all()) < 1:
                pw_hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt(12))
                us = User(name=name, email=email, pw = pw_hashed.decode('ascii'), role=str(role))
                session.add(us)
                try:
                    session.commit()
                    fl.flash("Successfully added new user")
                    return fl.redirect(fl.url_for('admin'))
                except KeyError:
                    fl.flash("Failed to add!")
                    return fl.render_template('admin/add_user.html', fm=fm)
            else:
                fl.flash("Email already used!")
                return fl.render_template('admin/add_user.html', fm=fm)
        else:
            fl.flash("Errors")
            fl.flash(fl.request.form)
            fl.flash(str(fm.errors))
            return fl.render_template('admin/add_user.html', fm=fm)