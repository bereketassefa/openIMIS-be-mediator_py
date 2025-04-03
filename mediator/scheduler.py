# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .job import fetch_data_from_server

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")  # Store jobs in database

    scheduler.add_job(
        fetch_data_from_server,
        trigger='interval',  # Can also use 'cron' for cron-like syntax
        minutes=5,           # Runs every 5 minutes
        id='fetch_data',     # Unique ID for the job
        replace_existing=True,
    )

    register_events(scheduler)  # Optional: for job execution logging
    scheduler.start()
    print("Scheduler started!")