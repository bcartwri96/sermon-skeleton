from flask import Flask, request
import src.conf as config
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# update config
config.init()
config.config.set('MAIN', 'APP_NAME', app.name)
config.write_config()

import sqlalchemy as sa
import src.models.db as db
import flask_login as login
import os
import src.celery_config as cel
import src.controllers as cn
# note that atm, controllers needs config already set up before it can
# do anything, so we exclude the line -> run so config is written, then we
# allow it back in so controllers can use it.


# security key
SECRET_KEY = "helllo here is a secure key/scds/e/fv/ad/vf/fewefvnwfinaekfnvalk"
app.config['SECRET_KEY'] = SECRET_KEY
# app.config['SERVER_NAME'] = ""

# produce the login manager
lm = login.LoginManager()
lm.init_app(app)
lm.login_view = '/login'

@app.route("/")
# @login.login_required
def index():
    return cn.index.main()

@app.route("/view")
def view():
    return cn.index.show_eps()

@app.route("/upload", methods=['GET', 'POST'])
@login.login_required
def upload():
    return cn.upload.up()

@app.route("/get_presigned")
@login.login_required
def get_presigned():
    name = request.args.get('file')
    ty = request.args.get('type')
    return cn.upload.get_presigned(name, ty)

@app.route("/upload_file", methods=["POST"])
@login.login_required
def upload_file():
    return cn.upload.post_upload()

# settings
@app.route("/settings", methods=["GET", "POST"])
@login.login_required
def settings():
    return cn.settings.main()

@app.route("/admin", methods=["GET", "POST"])
@login.login_required
def admin():
    return cn.admin.index.index()

@app.route("/task_status/<t_id>")
@login.login_required
def task_status(t_id):
    return cn.tasks.t_stat(t_id)

@app.route("/sermon/<int:id>")
@cross_origin(origin="*")
def sermon(id):
    return cn.index.load_sermon(id)

@app.route("/sermon/edit/<int:id>", methods=['GET', 'POST'])
@login.login_required
def edit_sermon(id):
    return cn.upload.edit_sermon(id)

@app.route("/sermon/delete/<int:id>", methods=['GET'])
@login.login_required
def delete_sermon(id):
    return cn.upload.delete_sermon(id)

@app.route("/test")
@login.login_required
def test():
    return cn.index.produce_feeds()

# login/out

@app.route("/login", methods=["GET", "POST"])
def login():
    return cn.login.auth()

@app.route("/logout")
def logout():
    return cn.login.out()

#searching
@app.route("/search/", methods=["GET", "POST"])
def search():
    return cn.index.search()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@lm.user_loader
def load_user(user_id):
    from src.models.models import User
    return User.query.get(user_id)

@app.context_processor
def inject_globals():
    import datetime as dt
    return dict(
        org_name = config.read_config('MAIN', 'ORG_NAME'),
        cc_year = dt.datetime.now().year
    )
