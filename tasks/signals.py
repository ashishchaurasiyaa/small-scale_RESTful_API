from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def task_completed(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        logger.info(f"Simulated AWS Lambda: Task {instance.id} marked as completed.")
        # Here, you can simulate calling the AWS Lambda function
        # For instance, you can log it or make an API call to simulate Lambda.
