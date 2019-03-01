from celery import Celery
import configparser as cfg

config = cfg.ConfigParser()
config.read('config.ini')

cel = Celery(config['MAIN']['APP_NAME'], broker=config['MAIN']['CELERY_BROKER_URL'], backend=config['MAIN']['CELERY_RESULT_BACKEND'])
cel.conf.update(config)
