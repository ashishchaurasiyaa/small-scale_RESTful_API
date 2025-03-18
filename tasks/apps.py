from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'


class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        import myapp.signals