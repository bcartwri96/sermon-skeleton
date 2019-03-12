from celery import Celery
import configparser as cfg
from src.scripts import index as sc

import src.conf as cf

cel = Celery(cf.read_config('MAIN', 'APP_NAME'), \
broker = cf.read_config('MAIN', 'CELERY_BROKER_URL'), \
backend = cf.read_config('MAIN', 'CELERY_RESULT_BACKEND'), \
redis_max_connections = 10)
