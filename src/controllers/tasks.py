from src.celery import cel
from src.models.models import Sermons
from src.models.db import session
from src.scripts.index import get_env_variable
import src.podbean.index as pod
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

@cel.task
def save_to_disk(file, name):
    try:
        file.save(name)
        # return True
    except IOError:
        # return False
        pass


@cel.task(bind=True)
def upload_podbean(self, filename, title_given, content_given, date_given, fname_thumb):
    # send to podbean now
    print(self)
    client_id = get_env_variable('CLIENT_ID')
    client_sec = get_env_variable('CLIENT_SEC')
    p = pod.init(client_id, client_sec)
    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status':'Authenticating with server'})
    time.sleep(30)
    res_up = p.auth_upload(filename)
    self.update_state(state='PROGRESS', meta={'current':10, 'total':100, 'status':'Authorising upload'})
    if res_up[0] != False:
        url = res_up[0]
        key = res_up[1]
        if p.upload_sermon(url, key):
            self.update_state(state='PROGRESS', meta={'current':70, 'total':100, 'status':'File uploaded. Publishing'})
            res = p.publish_sermon(title_given, 'content for now', \
            key, '')
            self.update_state(state='PROGRESS', meta={'current':95, 'total':100, 'status':'Publishing and saving'})
            if res[0] != False:
                # fl.flash("Successfully published sermon!")

                pod_id = res[0]
                pod_media_url = res[1]
                pod_logo_url = res[2]
                # write this to the database

                # get the date, format it so it's server ready
                date_given = dt.strptime(date_given, '%d/%m/%Y')
                new_sermon = Sermons(title=title_given, \
                                     date_given=date_given, \
                                     tmp_media=filename, \
                                     pod_id=pod_id, \
                                     pod_media_url=pod_media_url, \
                                     pod_logo_url=pod_logo_url, \
                                     tmp_thumbnail = fname_thumb)

                session.add(new_sermon)
                try:
                    session.commit()
                    self.update_state(state='PROGRESS', meta={'current':100, 'total':100, 'status':'Done'})
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
        'status':task.info['status']
        }
    return fl.jsonify(response)
