import os
import json
import logging
import boto3

logger = logging.getLogger("tasks")

AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
sns_client = boto3.client("sns", region_name=AWS_REGION) if AWS_SNS_TOPIC_ARN else None

def lambda_handler(event, context=None):
    try:
        task_id = event.get("task_id")
        task_title = event.get("title")
        task_status = event.get("status")

        if not all([task_id, task_title, task_status]):
            logger.error("Missing required task details in event: %s", event)
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing task details (task_id, title, status)."})
            }

        if task_status.lower() == "completed":
            message = f"Task '{task_title}' (ID: {task_id}) has been marked as completed."
            logger.info(message)
            if sns_client and AWS_SNS_TOPIC_ARN:
                try:
                    sns_client.publish(
                        TopicArn=AWS_SNS_TOPIC_ARN,
                        Message=message,
                        Subject="Task Completed Notification"
                    )
                    logger.info("SNS notification sent for task ID: %s", task_id)
                except Exception as sns_error:
                    logger.error("SNS notification failed: %s", str(sns_error))
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Notification processed successfully."})
            }

        logger.debug("Task ID %s status is %s; no action needed.", task_id, task_status)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No action needed."})
        }

    except Exception as e:
        logger.error("Lambda processing failed: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal error: {str(e)}"})
        }