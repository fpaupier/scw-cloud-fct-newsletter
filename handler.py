import json
import logging

import boto3
import os
from datetime import datetime
import pytz
import csv
from io import StringIO

from scw_serverless import Serverless

REGION = "fr-par"
S3_URL = "https://s3.fr-par.scw.cloud"

SCW_ACCESS_KEY = os.environ["SCW_ACCESS_KEY"]
SCW_SECRET_KEY = os.environ["SCW_SECRET_KEY"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

app = Serverless(
    "s3-csv-email-writer",
    secret={
        "SCW_ACCESS_KEY": SCW_ACCESS_KEY,
        "SCW_SECRET_KEY": SCW_SECRET_KEY,
    },
    env={
        "BUCKET_NAME": BUCKET_NAME,
        "PYTHONUNBUFFERED": "1",
    },
)

logging.basicConfig(level=logging.INFO)


@app.func(memory_limit=512)
def handle(event, context):
    # Validate request method
    if event.get('method') != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'}),
            'headers': {'Content-Type': ['application/json']}
        }

    # Get email from request body
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        if not email:
            raise ValueError('Email is required')
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body'}),
            'headers': {'Content-Type': ['application/json']}
        }

    # Initialize S3 client
    s3 = boto3.client(
        's3',
        region_name='fr-par',
        endpoint_url='https://s3.fr-par.scw.cloud',
        aws_access_key_id=os.environ['SCW_ACCESS_KEY'],
        aws_secret_access_key=os.environ['SCW_SECRET_KEY']
    )

    bucket_name = os.environ['BUCKET_NAME']
    file_name = 'newsletter_register.csv'

    # Get current datetime in French format
    paris_tz = pytz.timezone('Europe/Paris')
    current_time = datetime.now(paris_tz)
    formatted_date = current_time.strftime('%a %b %d %H:%M:%S %Y')

    try:
        # Try to read existing file
        try:
            response = s3.get_object(Bucket=bucket_name, Key=file_name)
            existing_content = response['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            existing_content = 'datetime,email\n'  # Create header if file doesn't exist

        # Process CSV content
        output = StringIO()
        output.write(existing_content)
        if output.tell() > 0:
            output.seek(0, 2)  # Go to end of file
        else:
            output.write('datetime,email\n')  # Write header if empty file

        # Append new registration
        writer = csv.writer(output)
        writer.writerow([formatted_date, email])

        # Upload updated content back to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=output.getvalue()
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Successfully subscribed to newsletter'}),
            'headers': {'Content-Type': ['application/json']}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': ['application/json']}
        }


if __name__ == "__main__":
    from scaleway_functions_python import local
    local.serve_handler(handle)


