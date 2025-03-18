from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .lambda_function import lambda_handler

@receiver(post_save, sender=Task)
def task_completed(sender, instance, created, **kwargs):
    if instance.status == "completed" and not created:
        event = {"task_id": str(instance.id), "title": instance.title, "status": instance.status}
        lambda_handler(event)