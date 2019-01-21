from flask_login import current_user
import flask as fl

def main():
    text = "Hello, "+current_user.name+"!"
    return fl.render_template('index.html', txt=text, current_user=current_user)
