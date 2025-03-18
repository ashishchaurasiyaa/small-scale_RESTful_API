import os
import json
import boto3

# Read environment variables from AWS Lambda
AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

# Initialize AWS SNS client
sns_client = boto3.client('sns', region_name=AWS_REGION)

def lambda_handler(event, context):
    """
    AWS Lambda function to send an SNS notification when a task is marked as completed.
    """
    try:
        # Parse the event data safely
        task_data = json.loads(event.get('body', '{}'))
        task_id = task_data.get('task_id')
        task_name = task_data.get('task_name')
        task_status = task_data.get('task_status')

        if not task_id or not task_name or not task_status:
            return {"statusCode": 400, "body": json.dumps({"message": "Missing task details."})}

        # Check if the task is completed
        if task_status.lower() == "completed":
            message = f"Task '{task_name}' (ID: {task_id}) has been marked as completed."

            # Send SNS notification
            sns_client.publish(
                TopicArn=AWS_SNS_TOPIC_ARN,
                Message=message,
                Subject="Task Completed Notification"
            )

            return {"statusCode": 200, "body": json.dumps({"message": "Notification sent successfully."})}

        return {"statusCode": 200, "body": json.dumps({"message": "No action needed."})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

# Local Testing (Optional)
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "task_id": "123",
            "task_name": "Complete Report",
            "task_status": "completed"
        })
    }
    print(lambda_handler(test_event, None))
