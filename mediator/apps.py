from django.apps import AppConfig


class MediatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mediator'
    def ready(self):
        from .scheduler import start
        print("Starting scheduler...")
        start()
