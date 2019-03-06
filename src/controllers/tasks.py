from src.celery_config import cel
from src.models.models import Sermons, Sermon_Series, Authors, Books_Bible
from src.models.db import session
from src.scripts.index import get_env_variable
import configparser as cp
import flask as fl
from datetime import datetime as dt
import time
from src.controllers.index import find_unique_id, strip_extension


@cel.task(bind=True)
def upload_aws(self, filename, title_given, description, author, date_given, fname_thumb, ss, u_id, book_bible, length):
    # init aws platform
    import src.controllers.aws.index as aws
    import os

    print("upload_aws begins...")
    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status':'Verifying uploads'})
    # get the profile name and bucket name from config

    # get conf
    cfg = cp.ConfigParser()
    cfg.read('config.ini') # read it in.

    bucket_name = cfg['MAIN']['AWS_BUCKET_NAME']
    profile_name = cfg['MAIN']['AWS_PROFILE_NAME']
    a = aws.Aws(profile_name, bucket_name)
    # simpler process for this side of things... just upload directly to the
    # server.

    # check the uploads went to the server
    print("approaching the object head construction stage")
    if a.get_obj_head(filename) and a.get_obj_head(fname_thumb):
        print("object phase is complete")
        self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status':'Verified. Processing...'})
        import time
        time.sleep(5)
        date_given = dt.strptime(date_given, '%d-%m-%Y')

        # get the object for the sermon series
        ss = Sermon_Series.query.get(int(ss))

        #get the object for the author
        author = Authors.query.get(int(author))

        # get the object for the bible book
        book_bible = Books_Bible.query.get(book_bible)

        # ensure that the title is unique
        unique = Sermons.query.filter(Sermons.title == title_given).all()

        # get the size of the file
        length = a.get_obj_size(filename)


        if len(unique) == 0:
            new_sermon = Sermons(title = title_given, \
                                 date_given = date_given, \
                                 description = description, \
                                 author = author, \
                                 sermon_series = ss, \
                                 aws_key_media = filename, \
                                 aws_key_thumb = fname_thumb, \
                                 book_bible = book_bible, \
                                 length = length)

            session.add(new_sermon)
            try:
                session.commit()
                self.update_state(state='SUCCESS')
            except KeyError:
                self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Error with database'})
                # return False
        else:
            self.update_state(state='FAILURE', meta={'current':0, 'total':100, 'status':'Failed to upload'})
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
