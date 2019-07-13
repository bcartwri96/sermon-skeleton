# dedicated to controller code that only the admin can use!

import flask as fl
from flask_login import current_user

# index (direct admin to either add and remove users with preset passwords)
def index():
    if current_user.is_admin():
        return fl.render_template('admin/index.html')
    else:
        fl.flash("Only admins can access this page.")
        return fl.redirect(fl.url_for('index'))