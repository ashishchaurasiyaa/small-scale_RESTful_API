import boto3
import os
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save method to send notification when task is completed."""
        if self.status == "completed":
            self.send_sns_notification()
        super().save(*args, **kwargs)

    def send_sns_notification(self):
        """Send a notification to AWS SNS when task is marked completed."""
        sns_client = boto3.client(
            "sns",
            region_name=os.getenv("AWS_REGION"),
        )

        message = f"Task '{self.title}' has been marked as COMPLETED."
        topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")

        sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="Task Completed Notification",
        )
