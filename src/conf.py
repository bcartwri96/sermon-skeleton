import configparser as cfg

# config
config = cfg.ConfigParser()
config.sections()
config['MAIN'] = {'UPLOADS_FOLDER': 'uploads/',
                  'PROJ_ROOT': '/Users/bencartwright/projects/sermon-skeleton/',
                  'CELERY_BROKER_URL': 'redis://localhost:6379/0',
                  'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0',
                  'COLUMNS_VIEW_ALL':'3'}


def write_config():
    try:
        with open('config.ini', 'w') as conf:
            config.write(conf)
        return True
    except IOError:
        return False
