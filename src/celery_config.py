from celery import Celery
import configparser as cfg
from src.scripts import index as sc

import src.conf as cf
try:
    bro = back = sc.get_env_variable('REDIS_URL')
except Exception:
    bro = cf.read_config('MAIN', 'CELERY_BROKER_URL')
    back = cf.read_config('MAIN', 'CELERY_RESULT_BACKEND')
    
cel = Celery(cf.read_config('MAIN', 'APP_NAME'), \
broker = bro, \
backend = back, \
redis_max_connections = 10)
