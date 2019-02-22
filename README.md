# sermon-skeleton
This little web app was paid for by Crossroads Christian Church in Canberra, Australia.
It aims to provide a means by which church-goers can easily access talks from
their local church by wrapping it in a neat Podcast distribution service (Podbean).


We're using redis (a low-memory, in-memory data structure store), so make sure
you _separately_ install the **redis server**.

We also use Celery, which allows us to run tasks in a neat little queue. To do
this, of course Celery needs installation (which should happen in `pipenv install`)
and then to run, we:
1. start our python flask server `pipenv run sh run.sh` and then;
2. start our celery server with `pipenv run celery -A src.main.celery`


To remove the database, we want to do the following:
1. `pipenv run python` to open the Python shell
2. `import src.models.db as db`
3. `db.create_db()`

This completes the db deletion and re-creation, but we also need to remove all
the content currently sitting on our AWS server.
1. `pipenv run python`
2. `from src.controllers.aws.index import Aws`
3. `a = Aws(bucket name, profile name)`
4. `all = a.get_all_obj` and `a.rm_objs(all)` to wipe them all off AWS.
