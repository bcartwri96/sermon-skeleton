#!/bin/bash/
export PROJ_ROOT=~/projects/sermon_skeleton/
export CONFIG_LOC=PROJ_ROOT+config.cfg
export FLASK_ENV=development
export FLASK_DEBUG=True
export FLASK_APP=src/main.py
redis-server --daemonize yes
flask run
