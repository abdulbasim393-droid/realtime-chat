from time import sleep
from app.celery_app import celery_app


@celery_app.task
def long_task():
    print("Starting task...")
    sleep(10)
    print("Finished task!")

    return "Done!"