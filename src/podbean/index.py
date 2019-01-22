import requests as r
from requests.auth import HTTPBasicAuth
import json
import configparser as cp
import os
from src.models.db import session
import flask as fl

# get conf
cfg = cp.ConfigParser()
cfg.read('config.ini') # read it in.
upload_loc = cfg['MAIN']['PROJ_ROOT']+ \
             cfg['MAIN']['UPLOADS_FOLDER']

class Podbean:
    # record information which is useful for any interaction with
    # podbean and then the user can pass it whenever we need it.

    def __init__(self, access_token, expires, scope):
        self.access_token = access_token
        self.expires = expires
        self.scope = scope

    # have a method in the
    def refresh_token(self):
        self.access_token = 'abcd'
        return True

    def upload_sermon(self, audio):
        # uploads the sermon to the podbean temporarily!
        # NOTE: NOT the publishing of a new episode!
        # returns only *temporary* file_key

        payload = {}
        payload['access_token'] = self.access_token
        payload['content_type'] = "audio/mpeg"
        payload['filename'] = audio

        # get the file
        file_loc = upload_loc+audio
        with open(file_loc, 'rb+') as file:
            #note, os.stat returns bytes
            payload['filesize'] = os.stat(file_loc).st_size

        file.close()

        # upload
        url = "https://api.podbean.com/v1/files/uploadAuthorize"
        req = r.post(url, params=payload)

        # NOTE HERE: the actual docs say to submit a GET request to upload the
        # sermon (which is obviously strange given it's an upload) and regardless
        # it didn't work like that so I submitted it as a POST and it worked :)

        resp = req.json()
        if req.status_code == 200:
            file_key = resp["file_key"]
            return file_key
        else:
            return req.text
            #TODO: deal with errors gracefully

    def publish_sermon(self, file_key, title, content, logo_key):
        # this takes the temp file uploaded and binds it with important
        # metadata to produce an actual podcast
        url = "https://api.podbean.com/v1/episodes"
        payload = {}

        # fill the payload
        payload["access_token"] = self.access_token
        payload["title"] = title
        payload["content"] = content
        payload["status"] = "publish"
        payload["type"] = "public"
        payload["media_key"] = file_key
        if logo_key:
            payload["logo_key"] = logo_key

        # make the request
        resp = r.post(url, data=payload)
        print(resp.text)

        # receive the episode object and then store the episode in
        # with the database
        if resp.status_code == 200:
            resp = resp.json()

            pod_id = resp["id"]
            pod_media_url = resp["media_url"]
            pod_logo_url = resp["logo"]

            sermon = Sermons(title=title, \
            pod_id=pod_id, \
            pod_media_url=pod_media_url, \
            pod_logo_url=pod_logo_url)

            session.add(sermon)
            try:
                session.commit()
                fl.flash("Successfully published the new episode!")
            except KeyError:
                fl.flash("We were unable to publish at the episode at this\
                 time.")
            return fl.redirect(fl.url_for('upload'))
        else:
            fl.flash("unable to publish the episode.")
            return fl.redirect(fl.url_for('upload'))

def init(client_id, secret):
    # provide client id and secret, authenticate you with your app
    # returns the access_token to carry around for all the rest of the
    # interactions with podbean.

    payload = {
        'grant_type' : 'client_credentials'
    }
    response = r.post("https://api.podbean.com/v1/oauth/token", \
    auth=HTTPBasicAuth(client_id, secret), data=payload)

    if response.status_code == 200:
        res = response.json()
        pod = Podbean(access_token=res["access_token"], expires=res["expires_in"],\
        scope=res['scope'])

        return pod
    else:
        return response.text
