from flask_login import current_user
import flask as fl

def main():
    try:
        text = "Hello, "+current_user.name+"!"
    except AttributeError:
        text = "Hello anon!"
    return fl.render_template('index.html', txt=text, current_user=current_user)
