from django.urls import path
from . import views

urlpatterns = [
    path("tasks/ratelimited/", views.rate_limited_tasks, name="rate_limited_tasks"),
]