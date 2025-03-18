from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task
from django.core.cache import cache
from django.utils.timezone import now

"""
Unit tests for the Task Management API.

- Tests CRUD operations for tasks.
- Verifies authentication and permission handling.
- Ensures rate-limiting works correctly.
- Tests marking a task as completed.
"""

class TaskAPITestCase(TestCase):
    """
    Test case for the Task API endpoints.
    """

    def setUp(self):
        """
        Set up test environment:
        - Creates a test user.
        - Generates an authentication token.
        - Initializes the API client.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticated requests

        # Create a test task
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            status="pending",
            assigned_to=self.user
        )

    def test_create_task(self):
        """
        Ensure a task can be created successfully.
        """
        data = {
            "title": "New Task",
            "description": "New task description",
            "status": "pending",
            "assigned_to": self.user.id
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.data["title"], "New Task")

    def test_get_task_list(self):
        """
        Ensure tasks can be retrieved.
        """
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should return one task

    def test_get_task_detail(self):
        """
        Ensure a single task can be retrieved.
        """
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Task")

    def test_update_task(self):
        """
        Ensure a task can be updated.
        """
        data = {"title": "Updated Task", "status": "completed"}
        response = self.client.patch(f'/api/tasks/{self.task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.status, "completed")

    def test_delete_task(self):
        """
        Ensure a task can be deleted.
        """
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_mark_task_completed(self):
        """
        Ensure a task can be marked as completed.
        """
        response = self.client.post(f'/api/tasks/{self.task.id}/mark_completed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")
        self.assertIsNotNone(self.task.completed_at)

    def test_mark_task_completed_not_found(self):
        """
        Ensure marking a non-existent task as completed returns 404.
        """
        response = self.client.post('/api/tasks/9999/mark_completed/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")


class RateLimitTestCase(TestCase):
    """
    Test case for API rate-limiting.
    """

    def setUp(self):
        """
        Set up test environment:
        - Creates a test user.
        - Initializes API client.
        - Clears cache to reset rate limits.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        cache.clear()  # Clear cache to reset rate limit

    def test_rate_limiting(self):
        """
        Ensure API requests are rate-limited.
        """
        for _ in range(5):  # Send 5 allowed requests
            response = self.client.get('/api/tasks/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6th request should be rate-limited
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)  # 429 Too Many Requests
