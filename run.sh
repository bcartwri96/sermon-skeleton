# NOTE THAT this is for DEVELOPMENT ONLY! 
# Heroku itself has a seperate 'prod' setup which involves a 
# redis server installed on it's own service, and a celery worker 
# which we run in another dyno.

export FLASK_APP=src.main
export FLASK_ENV=development

# write some important variables
# AWS keys
export AWS_ACCESS_KEY_ID=AKIASAWQPOH525BEGPX6
export AWS_SECRET_ACCESS_KEY=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

# DB connection
export POSTGRES_URL=localhost
export POSTGRES_DB=ss
export POSTGRES_USER=postgres
export POSTGRES_PW=1234

redis-server --daemonize yes
supervisord
flask run

# this point is where we can terminate the services.
echo "Shutting down Supervisor"
kill_supervisor=$(<supervisord.pid)
kill "$kill_supervisor"
echo "Shut down"

# redis has an inbuilt CLI (note: untested on Linux)
echo "Shutting down Redis server"
redis-cli shutdown
echo "Shut down"

echo "------------"
echo "--Finished--"
echo "------------"