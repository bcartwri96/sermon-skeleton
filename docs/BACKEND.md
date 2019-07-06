## The Backend

This is an outline of the backend of the services which we use to make this *fast*.
Basically there is a thing called `Celery` which is a backend task queue service
which makes use of `redis` to enable Python code to be run either on a schedule
or in parallel while the frontend serves page requests. In laymens terms, this means
you can have a user request a complex operation to run without needing to wait for it
to complete before we return a page to the user, which we can later fill with information
as the task is slowly completed by querying the web worker for updates later.

### How do we set it up?
I've been slightly sneaky and included celery in the venv install you already did, but you'll also
need another low memory queue service like redis (there are others, but I used redis and it was easy 
so I recommend you use it too.)

#### How do I install `redis`?
For MacOS users, just run `brew install redis` and then you can have a redis server running as easily
as running `brew services start redis` (for the background task) or simply `redis-server` (which I recommend,
because, again, I did this and it worked)

For Linux users, a very similar process.
```bash
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
```
Then just `redis-server` again.

Now, in the run command (`sh run.sh`) we actually have all these services daemonised (NOTE: built to daemonize 
on mac) so we can simply run the command and assuming you have
1. Supervisor and;
2. Redis

installed, you should be fine. Errors will pop up if the run command fails!