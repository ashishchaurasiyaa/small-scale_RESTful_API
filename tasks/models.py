from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Task(models.Model):
    """
    Task model representing a task in the system.

    - title: Name of the task.
    - description: Details of the task.
    - assigned_to: The user assigned to complete the task.
    - status: Status of the task ('pending', 'in_progress', 'completed', 'overdue').
    - priority: Importance level of the task ('low', 'medium', 'high').
    - due_date: Deadline for completing the task.
    - created_at: Timestamp for task creation.
    - updated_at: Timestamp for last update.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("overdue", "Overdue"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_overdue(self):
        """
        Check if the task is overdue.

        - Returns True if the task is not completed and the due date has passed.
        """
        return self.status != "completed" and self.due_date < now()

    def __str__(self):
        return f"{self.title} - {self.status}"


class TaskLog(models.Model):
    """
    TaskLog model tracking changes made to tasks.

    - task: The task associated with the log entry.
    - user: The user who performed the action.
    - action: Description of the change.
    - timestamp: When the change occurred.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task: {self.task.title} | Action: {self.action} | By: {self.user.username}"


class RateLimitTracker(models.Model):
    """
    RateLimitTracker model tracking API usage per user.

    - user: The user associated with the rate limit.
    - last_request: Timestamp of the last API request.
    - request_count: Number of API requests made within the rate limit window.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_request = models.DateTimeField(auto_now=True)
    request_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"RateLimit: {self.user.username} - {self.request_count} requests"
