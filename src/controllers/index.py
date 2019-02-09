from flask_login import current_user
import flask as fl
import src.podbean.index as podbean
import src.scripts.index as scripts
from src.models.models import Sermons
from src.conf import config
import requests as r

cl_id = scripts.get_env_variable('CLIENT_ID')
cl_sc = scripts.get_env_variable('CLIENT_SEC')

p = podbean.init(cl_id, cl_sc)

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
    sermon_db = Sermons.query.all()
    all = p.get_sermons(100)['episodes']

    # get the image link too
    podcast = p.get_podcasts()
    def_img = podcast['podcasts'][0]['logo']

    # replace with the def_img if there isn't an uploaded image
    for i in range(0, len(all), 1):
        if all[i]['logo'] == None:
            all[i]['logo'] = def_img

    # retrieve the number of rows and columns for client side
    cols = int(config['MAIN']['COLUMNS_VIEW_ALL'])

    return fl.render_template('view_all.html', sermons=sermon_db, eps=all, cols=cols)

def load_sermon(id):
    sermon_db = Sermons.query.get(id)
    pod = p.read_sermon(sermon_db.pod_id)['episode']

    if sermon_db.pod_logo_url == None:
        podcast = p.get_podcasts()
        sermon_db.pod_logo_url = podcast['podcasts'][0]['logo']

    med = r.get(sermon_db.pod_media_url)

    if sermon_db != None:
        if fl.request.method == 'GET':
            return fl.render_template('load_sermon.html', sermon=sermon_db, pod=pod, med=med)
        else:
            pass
        return fl.render_template('search.html')


def search():
    from src.forms.index import Search
    form = Search()
    if fl.request.method == 'GET':
        return fl.render_template("search.html", form=form)
    else:
        res = fl.request.form['query']
        Sermons.query.search(u''+res+'').all()
        return fl.render_template('search.html', form=form, res=res)
