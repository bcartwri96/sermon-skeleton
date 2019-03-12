import configparser as cfg
import src.scripts.index as scripts
import os

try:
    cel_det = scripts.get_env_variable('REDIS_URL')
    # we want to use the heroku set add-on redis server if it's available,
    # but if we can't find it, then it isn't set and we must be running
    # the dev server, so we connect to it instead
except Exception:
    cel_det = 'redis://localhost:6379/0'
    # we run redis automatically from the /dev.sh screen, which means we
    # should have an existing server running which we can connect to.

cel_det = scripts.get_env_variable('REDIS_URL')

# config
config = cfg.ConfigParser()

def init():
    try:
        with open('config.ini', 'r+') as f:
            config.read_file(f)

    except IOError:
        print("Can't open the config file. Writing a default")
        config['MAIN'] = {'UPLOADS_FOLDER': '/tmp',
                          'PROJ_ROOT': os.getcwd()+"/",
                          'CELERY_BROKER_URL': cel_det,
                          'CELERY_RESULT_BACKEND': cel_det,
                          'COLUMNS_VIEW_ALL':'3',
                          'AWS_BUCKET_NAME': 'sermon-skeleton',
                          'AWS_PROFILE_NAME': 'sermon-skeleton',
                          'ORG_NAME': 'Crossroads Christian Church',
                          'ORG_EMAIL': 'itmanager@crossroads.asn.au',
                          'ORG_LINK': 'https://crossroads.org.au'}

def write_config():
    try:
        with open('config.ini', 'w') as conf:
            config.write(conf)
        return True
    except IOError:
        return False


def read_config(section, option):
    # get the aws details
    config = cfg.ConfigParser()
    config.read('config.ini')

    try:
        return config.get(section, option)
    except cfg.NoOptionError as error:
        print("Failed to get option "+option)
    except cfg.NoSectionError as error:
        print("Failed to get section "+section)
    return False
