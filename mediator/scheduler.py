# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .job import fetch_data_from_server

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")  

    scheduler.add_job(
        fetch_data_from_server,
        trigger='interval',  
        minutes=0.6,           
        id='fetch_data',     
        replace_existing=True,
    )

    register_events(scheduler)  
    scheduler.start()
    print("Scheduler started!")