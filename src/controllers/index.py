from flask_login import current_user
import flask as fl
import src.podbean.index as podbean
import src.scripts.index as scripts

def main():
    try:
        text = "Hello, "+current_user.name+"!"
    except AttributeError:
        text = "Hello anon!"
    return fl.render_template('index.html', txt=text, current_user=current_user)


def show_eps():
    cl_id = scripts.get_env_variable('CLIENT_ID')
    cl_sc = scripts.get_env_variable('CLIENT_SEC')

    p = podbean.init(cl_id, cl_sc)
    all = p.get_sermons(100)['episodes']

    # get the image link too, because it's missing!
    podcast = p.get_podcasts()
    def_img = podcast['podcasts'][0]['logo']

    # replace with the def_img if there isn't an uploaded image
    for i in range(0, len(all), 1):
        if all[i]['logo'] == None:
            all[i]['logo'] = def_img
    return fl.render_template('view_all.html', eps=all)
