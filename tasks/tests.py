from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task
from django.core.cache import cache

class TaskAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(
            title="Test Task",
            description="Test description",
            status="pending",
            assigned_to=self.user
        )

    def test_create_task(self):
        data = {"title": "New Task", "description": "New task", "status": "pending"}
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_get_task_list(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_status(self):
        response = self.client.get("/api/tasks/?status=pending")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mark_task_completed(self):
        response = self.client.post(f"/api/tasks/{self.task.id}/mark_completed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")

class RateLimitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def test_rate_limiting(self):
        for _ in range(5):
            response = self.client.get("/api/tasks/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)