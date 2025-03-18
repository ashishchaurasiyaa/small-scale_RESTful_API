from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, TaskLog


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    - id: Unique identifier of the user.
    - username: Username of the user.
    - email: Email address of the user.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    - id: Unique identifier for the task.
    - title: Name of the task.
    - description: Details about the task.
    - assigned_to: The user assigned to complete the task.
    - status: Status of the task ('pending', 'in_progress', 'completed', 'overdue').
    - priority: Priority level ('low', 'medium', 'high').
    - due_date: Deadline for completing the task.
    - created_at: Timestamp when the task was created.
    - updated_at: Timestamp when the task was last updated.
    - is_overdue: Read-only field indicating if the task is overdue.
    """

    assigned_to = UserSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assigned_to",
            "status",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
            "is_overdue",
        ]

    def get_is_overdue(self, obj):
        """
        Custom method to determine if a task is overdue.
        - Returns True if the due date has passed and the task is not completed.
        """
        return obj.is_overdue()


class TaskLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the TaskLog model.

    - id: Unique identifier of the log entry.
    - task: The task associated with the log.
    - user: The user who made the change.
    - action: Description of the action performed.
    - timestamp: When the action occurred.
    """

    user = UserSerializer(read_only=True)
    task = serializers.StringRelatedField()  # Returns the task title instead of ID

    class Meta:
        model = TaskLog
        fields = ["id", "task", "user", "action", "timestamp"]
