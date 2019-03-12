from celery import Celery
import configparser as cfg
from src.scripts import index as sc

import src.conf as cf
bro = "redis://h:p33b23923fb4a76463b57ab4cb7ef9c04899975f22b3747b520db88255d41a4e1@ec2-3-209-60-144.compute-1.amazonaws.com:23849"
back = "redis://h:p33b23923fb4a76463b57ab4cb7ef9c04899975f22b3747b520db88255d41a4e1@ec2-3-209-60-144.compute-1.amazonaws.com:23849"

cel = Celery(cf.read_config('MAIN', 'APP_NAME'), \
broker = bro, \
backend = back, \
redis_max_connections = 10)
