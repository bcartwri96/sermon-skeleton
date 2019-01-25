from src.celery import cel

@cel.task
def add_task(x, y):
    # here is a task we'll need to upload the stuff after we return the user
    # their webpage and then we can continually update them via a neat JSON
    # API called `upload_progress` or something
    import time
    time.sleep(2)
    print("dome some sleeping")
