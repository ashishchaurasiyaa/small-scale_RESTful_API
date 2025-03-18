import json
import logging
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from tasks.models import Task
from django.utils.timezone import now

# Configure logging for the Lambda simulation
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context=None):
    """
    Simulated AWS Lambda function to process tasks.

    - event: Dictionary containing task-related data.
    - context: AWS Lambda execution context (not used in simulation).

    Functionality:
    - Checks if a task exists.
    - Updates task status if overdue.
    - Logs the operation.
    """

    try:
        # Extract task ID from event data
        task_id = event.get("task_id")
        if not task_id:
            logger.error("Task ID is missing in the event data.")
            return {"statusCode": 400, "body": json.dumps({"error": "Task ID is required"})}

        # Fetch the task from the database
        task = Task.objects.get(id=task_id)

        # Check if the task is overdue
        if task.due_date and task.due_date < now() and task.status != "completed":
            task.status = "overdue"
            task.save()
            logger.info(f"Task {task.id} marked as overdue.")

        return {"statusCode": 200, "body": json.dumps({"message": "Task processed successfully"})}

    except ObjectDoesNotExist:
        logger.error(f"Task with ID {task_id} does not exist.")
        return {"statusCode": 404, "body": json.dumps({"error": "Task not found"})}

    except Exception as e:
        logger.error(f"Error processing task: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": "Internal server error"})}
