import boto3
import json

# Initialize AWS clients
sqs = boto3.client('sqs')
dynamodb = boto3.client('dynamodb')

# Define the SQS queue URL and DynamoDB table name
QUEUE_URL = 'https://sqs.<region>.amazonaws.com/<account-id>/<queue-name>'
TABLE_NAME = '<dynamodb-table-name>'

def send_task_to_queue(text: str) -> str:
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({'text': text})
    )
    return response['MessageId']

def retrieve_task_result(task_id: str) -> str:
    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={'task_id': {'S': task_id}}
    )
    
    if 'Item' in response:
        return response['Item']['result']['S']
    else:
        return None
