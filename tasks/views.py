from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action, api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from tasks.models import Task
from tasks.serializers import TaskSerializer
import logging

# Configure logging for debugging and error tracking
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TaskRateThrottle(UserRateThrottle):
    """Custom throttle class (5 requests per minute)"""
    rate = '5/min'

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.

    - Provides CRUD operations (Create, Retrieve, Update, Delete).
    - Requires authentication for all actions.
    - Allows marking tasks as completed.
    - Filters tasks based on status.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]  # Enforces JWT authentication
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of tasks.

        - Filters tasks based on query parameters.
        - Returns a paginated response.
        """
        queryset = self.get_queryset()

        # Optional filtering by status
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Create a new task.

        - Validates and saves task data.
        - Returns the created task details.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Task created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Task creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieve details of a specific task.

        - Returns 404 if task does not exist.
        """
        try:
            task = self.get_object()
            serializer = self.get_serializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error(f"Task with ID {pk} not found.")
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update an existing task.

        - Allows modifying task attributes.
        - Returns updated task details.
        """
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Task {pk} updated: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Task update failed for ID {pk}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Delete a task.

        - Returns 204 No Content if successful.
        - Returns 404 if task does not exist.
        """
        try:
            task = self.get_object()
            task.delete()
            logger.info(f"Task {pk} deleted successfully.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            logger.error(f"Task with ID {pk} not found for deletion.")
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def mark_completed(self, request, pk=None):
        """
        Custom action to mark a task as completed.

        - Changes task status to 'completed'.
        - Logs completion event.
        """
        try:
            task = self.get_object()
            task.status = "completed"
            task.completed_at = now()
            task.save()
            logger.info(f"Task {pk} marked as completed.")
            return Response({"message": "Task marked as completed"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error(f"Task with ID {pk} not found for completion.")
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@throttle_classes([TaskRateThrottle])
def rate_limited_tasks(request):
    """
    API endpoint with rate limiting (Max 5 requests per min per user)
    """
    tasks = Task.objects.filter(assigned_to=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
