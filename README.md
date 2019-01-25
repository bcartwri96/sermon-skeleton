# sermon-skeleton
This little web app was paid for by Crossroads Christian Church in Canberra, Australia. It aims to provide a means by which church-goers can easily access talks from their local church by wrapping it in a neat Podcast distribution service (Podbean).


We're using redis (a low-memory, in-memory data structure store), so make sure
you _separately_ install the **redis server**.

We also use Celery, which allows us to run tasks in a neat little queue. To do
this, of course Celery needs installation (which should happen in `pipenv install`)
and then to run, we:
1. start our python flask server `pipenv run sh run.sh` and then;
2. start our celery server with `pipenv run celery -A src.main.celery`
