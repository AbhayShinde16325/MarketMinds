import os
import json

def lambda_handler(event, context):
    company = event.get('company', '')
    s3_bucket = os.environ.get('S3_BUCKET', 'your-s3-bucket-name')
    s3_key = f"{company}_earnings.pdf"
    file_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"
    return {
        "statusCode": 200,
        "body": json.dumps({
            "company": company,
            "report_url": file_url
        })
    }
