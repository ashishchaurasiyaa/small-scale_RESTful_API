import time
from django.db.models import Count
from .models import Task
import logging

logger = logging.getLogger("tasks")

def monitor_task_volume(threshold=100, min_threshold=20, interval=60):
    while True:
        start_time = time.time()
        initial_count = Task.objects.count()
        time.sleep(interval)
        end_time = time.time()
        final_count = Task.objects.count()

        tasks_per_minute = (final_count - initial_count) * (60 / (end_time - start_time))
        logger.info("Tasks created per minute: %d", tasks_per_minute)

        if tasks_per_minute > threshold:
            logger.info("Scaling up: Adding 1 instance")
        elif tasks_per_minute < min_threshold:
            logger.info("Scaling down: Removing 1 instance")

if __name__ == "__main__":
    monitor_task_volume()