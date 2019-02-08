from flask import Flask
import src.conf as config
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# update config
config.config.set('MAIN', 'APP_NAME', app.name)
config.write_config()

import sqlalchemy as sa
import src.models.db as db
import flask_login as login
import os
import src.celery as cel
import src.controllers as cn
# note that atm, controllers needs config already set up before it can
# do anything, so we exclude the line -> run so config is written, then we
# allow it back in so controllers can use it.


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# produce the login manager
lm = login.LoginManager()
lm.init_app(app)

@app.route("/")
# @login.login_required
def index():
    print("Working...")
    # add_task.delay(1,1)
    print("Done?")
    return cn.index.main()

@app.route("/view")
def view():
    return cn.index.show_eps()

@app.route("/upload", methods=['GET', 'POST'])
# @login.login_required
def upload():
    return cn.upload.up()

@app.route("/task_status/<t_id>")
def task_status(t_id):
    return cn.tasks.t_stat(t_id)

@app.route("/sermon/<int:id>")
@cross_origin(origin="*")
def sermon(id):
    return cn.index.load_sermon(id)

# login/out

@app.route("/login", methods=["GET", "POST"])
def login():
    return cn.login.auth()

@app.route("/logout")
def logout():
    return cn.login.out()

# settings

@app.route("/settings", methods=["GET", "POST"])
def settings():
    return cn.settings.main()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@lm.user_loader
def load_user(user_id):
    from src.models.models import User
    return User.query.get(user_id)
