import requests as r
from requests.auth import HTTPBasicAuth
import json
import configparser as cp
import os
from src.models.db import session
import flask as fl
import boto3 as aws #the AWS python HTTP wrapper lib

# get conf
cfg = cp.ConfigParser()
cfg.read('config.ini') # read it in.
upload_loc = cfg['MAIN']['PROJ_ROOT']+ \
             cfg['MAIN']['UPLOADS_FOLDER']


class Aws:
    # define the class which contacts and uses AWS to store data, and retreive
    # resources from

    def __init__(self, bucket_name, profile_name):
        self.bucket_name = bucket_name
        self.profile_name = profile_name
        self.connection = None
        self.client = None

    def init(self):

        # this is going to assume you've already done the config work which
        # is normal in any AWS operation (say, with AWSCLI)

        aws.setup_default_session(profile_name=self.profile_name)
        con = aws.resource('s3')
        self.connection = con
        client = aws.client('s3')
        self.client = client

        return client

    def upload_resource(self, resource, type):
        try:
            data = open(resource, 'rb')
        except IOError:
            print("Resource doesn't exist")
            return False

        new_obj = self.connection.Bucket(self.bucket_name).put_object(Key=data.name, \
        Body=data)
        if not new_obj:
            print("Resource failed to upload")
            return False
        else:
            return True

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

    def get_podcasts(self):
        url = "https://api.podbean.com/v1/podcasts"

        payload = {}
        payload['access_token'] = self.access_token

        res = r.get(url, params=payload)

        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False

    def get_sermons(self, limit):
        url = "https://api.podbean.com/v1/episodes"

        payload = {}
        payload['access_token'] = self.access_token
        payload['limit'] = limit
        payload['offset'] = 0

        resp = r.get(url, params=payload)

        if resp.status_code == 200:
            # we've got them! parse as json
            eps = resp.json()
            return eps
        else:
            print(resp.text)
            return False

    def auth_upload(self, resource, type):
        # uploads the sermon to the podbean temporarily!
        # NOTE: NOT the publishing of a new episode!
        # returns only *temporary* file_key

        payload = {}
        payload['access_token'] = self.access_token
        payload['content_type'] = "audio/mpeg"
        payload['filename'] = resource

        # get the file
        file_loc = resource #upload_loc+audio
        with open(file_loc, 'rb+') as file:
            #note, os.stat returns bytes
            payload['filesize'] = os.stat(file_loc).st_size

        file.close()

        # upload
        url = "https://api.podbean.com/v1/files/uploadAuthorize"
        req = r.get(url, params=payload)

        # NOTE HERE: the actual docs say to submit a GET request to upload the
        # sermon (which is obviously strange given it's an upload) and regardless
        # it didn't work like that so I submitted it as a POST and it worked :)

        resp = req.json()
        if req.status_code == 200:
            file_key = resp["file_key"]
            presigned_url = resp["presigned_url"]
            print(req.text)
            return [presigned_url, file_key]

        else:
            return False
            print(req.text)
            #TODO: deal with errors gracefully

    def upload_resource(self, url, media_key, type):
        head = {'Content-Type': 'audio/mpeg'}
        # files = {'file': open(media_key, 'rb')}
        files = {'file': str(media_key)}
        with open(media_key, 'rb') as data:
            res = r.put(url, headers=head, data=data)
            print(res.text)

            if res.status_code == 200:
                return True
            else:
                return False
        return False

    def publish_sermon(self, title, content, media_key, logo_key):
        # this takes the temp file uploaded and binds it with important
        # metadata to produce an actual podcast
        url = "https://api.podbean.com/v1/episodes"
        payload = {}

        # fill the payload
        payload['access_token'] = str(self.access_token)
        payload['title'] = str(title)
        payload['content'] = str(content)
        payload['status'] = "publish"
        payload['type'] = "public"
        payload['media_key'] = str(media_key)
        if logo_key:
            payload['logo_key'] = str(logo_key)

        # make the request
        resp = r.post(url, data=payload)
        print(resp.text)

        # receive the episode object and then store the episode in
        # with the database
        if resp.status_code == 200:
            resp = resp.json()['episode'] # is sent as an 'episode' obj, so
            # just filter out garbage

            pod_id = resp["id"]
            pod_media_url = resp["media_url"]
            pod_logo_url = resp["logo"]

            try:
                return [pod_id, pod_media_url, pod_logo_url]
            except KeyError:
                return [False]
            return [False]
        else:
            return [False]

    def read_sermon(self, id):
        payload = {
            'access_token': self.access_token
        }

        url = "https://api.podbean.com/v1/episodes/"+str(id)

        res = r.get(url, params=payload)

        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False

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
