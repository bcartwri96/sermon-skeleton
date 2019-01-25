from celery import Celery
import configparser as cfg

config = cfg.ConfigParser()
config.read('config.ini')

cel = Celery(config['MAIN']['APP_NAME'], broker=config['MAIN']['CELERY_BROKER_URL'])
cel.conf.update(config)
