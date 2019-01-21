from flask import Flask
import sqlalchemy as sa
import src.controllers as cn
import src.models.db as db
import flask_login as login
import os
import configparser as cfg

app = Flask(__name__)

# config
config = cfg.ConfigParser()
config['MAIN'] = {'UPLOADS_FOLDER': 'uploads/',
                  'PROJ_ROOT': '/Users/bencartwright/projects/sermon-skeleton/'}
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
    return cn.index.main()

@app.route("/upload", methods=['GET', 'POST'])
# @login.login_required
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
