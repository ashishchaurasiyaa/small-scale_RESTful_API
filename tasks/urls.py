from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet,rate_limited_tasks

# Create a router for the TaskViewSet
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/ratelimited/', rate_limited_tasks, name='rate_limited_tasks'),
]
