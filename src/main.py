from flask import Flask
import sqlalchemy as sa
import src.controllers as cn
import src.models.db as db
import flask_login as login
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config.from_pyfile('config.cfg')

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
