from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action, api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle
from django.core.exceptions import ObjectDoesNotExist
from .models import Task
from .serializers import TaskSerializer
import logging

logger = logging.getLogger("tasks")

class TaskRateThrottle(UserRateThrottle):
    rate = "5/min"

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [TaskRateThrottle]

    def get_queryset(self):
        queryset = self.queryset
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.filter(assigned_to=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assigned_to=request.user)
            logger.info("Task created: %s by user %s", serializer.data["title"], request.user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Task creation failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            task = self.get_object()
            serializer = self.get_serializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Task ID %s not found for user %s", pk, request.user.username)
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            task = self.get_object()
            serializer = self.get_serializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info("Task ID %s updated by user %s", pk, request.user.username)
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error("Task update failed for ID %s: %s", pk, serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Task ID %s not found for update by user %s", pk, request.user.username)
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            task = self.get_object()
            task.delete()
            logger.info("Task ID %s deleted by user %s", pk, request.user.username)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            logger.error("Task ID %s not found for deletion by user %s", pk, request.user.username)
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def mark_completed(self, request, pk=None):
        try:
            task = self.get_object()
            task.status = "completed"
            task.save()
            logger.info("Task ID %s marked as completed by user %s", pk, request.user.username)
            return Response({"message": "Task marked as completed"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Task ID %s not found for completion by user %s", pk, request.user.username)
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@throttle_classes([TaskRateThrottle])
def rate_limited_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    serializer = TaskSerializer(tasks, many=True)
    logger.info("User %s accessed rate-limited tasks endpoint", request.user.username)
    return Response(serializer.data, status=status.HTTP_200_OK)