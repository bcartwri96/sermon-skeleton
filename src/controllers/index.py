from flask_login import current_user
import flask as fl
import src.scripts.index as scripts
from src.models.models import Sermons
from src.conf import config
import requests as r
import src.conf as conf
from src.controllers.aws import index as aws_lib
import random
from src.models.db import session

# get the aws details

aws_bucket_name = conf.read_config("MAIN", "aws_bucket_name")
aws_profile_name = conf.read_config("MAIN", 'aws_profile_name')

aws = aws_lib.Aws(aws_bucket_name, aws_profile_name)
client = aws.init_client()

def main():
    try:
        text = "Hello, "+current_user.name+"!"
    except AttributeError:
        text = "Hello anon!"
    return fl.render_template('index.html', txt=text, current_user=current_user)


def show_eps():
    # show all the episodes (seen in the view_all page.)
    data = {}
    sermon_db = Sermons.query.all()

    for sermon in sermon_db:
        # dict the sermon id with the urls required so we can
        # fetch client side
        data[sermon.id] = [aws.get_obj_url(sermon.aws_key_media), \
        aws.get_obj_url(sermon.aws_key_thumb)]

    # retrieve the number of rows and columns for client side
    cols = conf.read_config("MAIN", "columns_view_all")
    if cols != False:
        cols = int(cols)

    return fl.render_template('view_all.html', sermons=sermon_db, eps=data, cols=cols)

def load_sermon(id):
    sermon_db = Sermons.query.get(id)

    media_url = aws.get_obj_url(sermon_db.aws_key_media)
    thumb_url = aws.get_obj_url(sermon_db.aws_key_thumb)

    # increment the sermon view count
    sermon_db.views = sermon_db.views+1
    session.add(sermon_db)
    session.commit()

    if sermon_db != None:
        if fl.request.method == 'GET':
            return fl.render_template('load_sermon.html', sermon=sermon_db, \
            media_url=media_url, thumb_url=thumb_url)
        else:
            pass
        return fl.render_template('search.html')


def search():
    from src.forms.index import Search
    from src.controllers.search import search_master
    form = Search()
    cols = int(config['MAIN']['COLUMNS_VIEW_ALL'])

    if fl.request.method == 'GET':
        return fl.render_template("search.html", form=form, cols=cols)
    else:
        res = fl.request.form['query']
        all = search_master(res, False, True, False, False)
        if all == []:
            fl.flash("No results found")

        data = {}
        for sermon in all:
            # dict the sermon id with the urls required so we can
            # fetch client side
            data[sermon.id] = [aws.get_obj_url(sermon.aws_key_media), \
            aws.get_obj_url(sermon.aws_key_thumb)]


        return fl.render_template('search.html', form=form, res=all, media=data, cols=cols)


def find_unique_id(u_id):
    # get a unique ID for upload to S3
    from sqlalchemy import or_
    # necessary because _or is not passed from Sermons alone.
    import sys

    found = False
    while not found:
        max_int = int(sys.maxsize)
        id = str(u_id) + "/" + str(random.randint(0, max_int-1))
        
        if len(Sermons.query.filter(or_(Sermons.aws_key_media == id, Sermons.aws_key_thumb == id)).all()) == 0:
            return id

    return False
