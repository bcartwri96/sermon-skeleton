from src.celery import cel
from src.models.models import Sermons, Sermon_Series
from src.models.db import session
from src.scripts.index import get_env_variable
import configparser as cp
import flask as fl
from datetime import datetime as dt
import time

@cel.task
def add_task(x, y):
    # here is a task we'll need to upload the stuff after we return the user
    # their webpage and then we can continually update them via a neat JSON
    # API called `upload_progress` or something
    import time
    time.sleep(2)
    print("dome some sleeping")

@cel.task(bind=True)
def upload_aws(self, filename, title_given, content_given, date_given, fname_thumb, ss):
    # init aws platform
    import src.controllers.aws.index as aws

    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status':'Authenticating with server'})
    # get the profile name and bucket name from config

    # get conf
    cfg = cp.ConfigParser()
    cfg.read('config.ini') # read it in.

    bucket_name = cfg['MAIN']['AWS_BUCKET_NAME']
    profile_name = cfg['MAIN']['AWS_PROFILE_NAME']
    a = aws.Aws(profile_name, bucket_name)
    client = a.init_client()

    # simpler process for this side of things... just upload directly to the
    # server.
    self.update_state(state='PROGRESS', meta={'current':20, 'total':100, 'status':'Authorising upload'})
    res = a.upload_resource(filename, 'audio/mpeg')
    self.update_state(state='PROGRESS', meta={'current':70, 'total':100, 'status':'Authorising upload of image'})
    res_thumb = a.upload_resource(fname_thumb, 'image/png')
    import time
    time.sleep(2)
    if res_thumb != False and res != False:
        # we've uploaded successfully
        self.update_state(state='PROGRESS', meta={'current':90, 'total':100, 'status':'Uploaded. Publishing'})

        date_given = dt.strptime(date_given, '%d/%m/%Y')

        # get the object for the sermon series
        ss = Sermon_Series.query.get(int(ss))

        # ensure that the title is unique
        unique = Sermons.query.filter(Sermons.title == title_given).all()
        print(res)
        print(res_thumb)
        if len(unique) == 0:
            new_sermon = Sermons(title=title_given, \
                                 date_given=date_given, \
                                 tmp_media=filename, \
                                 tmp_thumbnail = fname_thumb, \
                                 sermon_series = ss, \
                                 aws_key_media = res, \
                                 aws_key_thumb = res_thumb)

            session.add(new_sermon)
            try:
                session.commit()
                self.update_state(state='PROGRESS', meta={'current':100, 'total':100, 'status':'Done'})
            except KeyError:
                self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Error with database'})
                # return False
        else:
            self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Filename not unique'})
    else:
        self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Failed to upload'})



@cel.task(bind=True)
def upload_podbean(self, filename, title_given, content_given, date_given, fname_thumb, ss):
    import src.controllers.podbean.index as pod

    # send to podbean now
    client_id = get_env_variable('CLIENT_ID')
    client_sec = get_env_variable('CLIENT_SEC')
    p = pod.init(client_id, client_sec)
    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status':'Authenticating with server'})
    res_up = p.auth_upload(filename, "audio/mpeg")
    self.update_state(state='PROGRESS', meta={'current':20, 'total':100, 'status':'Authorising upload'})
    res_up_thumb = p.auth_upload(fname_thumb, "image/png")
    self.update_state(state='PROGRESS', meta={'current':30, 'total':100, 'status':'Authorising upload of image'})
    # deal with the thumbnail first
    if res_up_thumb[0] != False:
        thumb_url = res_up_thumb[0]
        thumb_key = res_up_thumb[1]
        # now upload the img, if there.
        if p.upload_resource(thumb_url, thumb_key, "image/png"):
            self.update_state(state='PROGRESS', meta={'current':40, 'total':100, 'status':'Image uploaded. Publishing'})
        else:
            self.update_state(state='PROGRESS', meta={'current':40, 'total':100, 'status':'Image upload failed. Continuing.'})
    else:
        self.update_state(state='PROGRESS', meta={'current':30, 'total':100, 'status':'Image upload failed. Continuing.'})

    # upload the audio
    if res_up[0] != False:
        url = res_up[0]
        key = res_up[1]
        if p.upload_resource(url, key, "audio/mpeg"):
            self.update_state(state='PROGRESS', meta={'current':70, 'total':100, 'status':'File uploaded. Publishing'})
            res = p.publish_sermon(title_given, content_given, \
            key, thumb_key)
            self.update_state(state='PROGRESS', meta={'current':95, 'total':100, 'status':'Publishing and saving'})
            if res[0] != False:
                # fl.flash("Successfully published sermon!")

                pod_id = res[0]
                pod_media_url = res[1]
                pod_logo_url = res[2]
                # write this to the database

                # get the object for the sermon series
                ss = Sermon_Series.query.get(int(ss))

                # ensure that the title is unique
                unique = Sermons.query.filter(Sermons.title == title_given).all()
                # get the date, format it so it's server ready
                date_given = dt.strptime(date_given, '%d/%m/%Y')
                if len(unique) == 0:
                    new_sermon = Sermons(title=title_given, \
                                         date_given=date_given, \
                                         tmp_media=filename, \
                                         pod_id=pod_id, \
                                         pod_media_url=pod_media_url, \
                                         pod_logo_url=pod_logo_url, \
                                         tmp_thumbnail = fname_thumb, \
                                         sermon_series = ss)
                else:
                    self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Filename not unique'})
                print(title_given, date_given, filename, pod_id, pod_media_url, pod_logo_url, fname_thumb, ss)

                session.add(new_sermon)
                try:
                    session.commit()
                    self.update_state(state='SUCCESS', meta={'current':100, 'total':100, 'status':'Done'})
                except KeyError:
                    self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Error with database'})
                    # return False

                # return True
            else:
                self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Error publishing'})
                # fl.flash("FAILURE to publish")
                # return False
        else:
            self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Error uploading'})
            # fl.flash("FAILURE to upload")
            # return False
    else:
        self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Error authorising upload'})
        # fl.flash("FAILURE to authorise the upload")
        # return False

def t_stat(t_id):
    task = cel.AsyncResult(t_id)
    response = {}
    if task.state != 'PENDING' and task.state != 'FAILURE':
        if task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'current': 100,
                'total':100,
                'status':'Success'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'current': task.info['current'],
                'total':100,
                'status':task.info['status']
            }
        else:
            response = {
                'state': task.state,
                'current':0,
                'total':100,
                'status':task.info['status']
                }
    else:
        response = {
        'state': task.state,
        'current': 0,
        'total': 100,
        'status':str(task.info)
        }
    return fl.jsonify(response)
