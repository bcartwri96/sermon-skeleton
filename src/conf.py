import configparser as cfg

# config
config = cfg.ConfigParser()
config.sections()
config['MAIN'] = {'UPLOADS_FOLDER': 'uploads/',
                  'PROJ_ROOT': '/Users/bencartwright/projects/sermon-skeleton/',
                  'CELERY_BROKER_URL': 'redis://localhost:6379/0',
                  'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0',
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
