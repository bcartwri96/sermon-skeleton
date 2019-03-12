from celery import Celery
import configparser as cfg
from src.scripts import index as sc

config = cfg.ConfigParser()
config.read('config.ini')


cel = Celery(config['MAIN']['APP_NAME'], \
broker=config['MAIN']['CELERY_BROKER_URL'], \
backend=config['MAIN']['CELERY_RESULT_BACKEND'], \
redis_max_connections=10)

cel.conf.update(config)
