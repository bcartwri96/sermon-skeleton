from flask import Flask
import sqlalchemy as sa
import src.controllers as cn
# note that atm, controllers needs config already set up before it can
# do anything, so we exclude the line -> run so config is written, then we
# allow it back in so controllers can use it.
import src.models.db as db
import flask_login as login
import os
import configparser as cfg
import src.celery as cel

app = Flask(__name__)

# config
config = cfg.ConfigParser()
config.sections()
config['MAIN'] = {'UPLOADS_FOLDER': 'uploads/',
                  'PROJ_ROOT': '/Users/bencartwright/projects/sermon-skeleton/',
                  'CELERY_BROKER_URL': 'redis://localhost:6379/0',
                  'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0',
                  'APP_NAME': str(app.name)}
with open('config.ini', 'w') as conf:
    config.write(conf)

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
    return cn.index.show_eps()

@app.route("/upload", methods=['GET', 'POST'])
@login.login_required
def upload():
    return cn.upload.up()

# login/out

@app.route("/login", methods=["GET", "POST"])
def login():
    return cn.login.auth()

@app.route("/logout")
def logout():
    return cn.login.out()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@lm.user_loader
def load_user(user_id):
    from src.models.models import User
    return User.query.get(user_id)
