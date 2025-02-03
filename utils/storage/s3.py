import boto3
import os

def upload_file(path, key):
    """
    Uploads a file to an S3 bucket.
    """
    try:
        bucket_name = "salesdeep-scrapped-data"
        aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
        )
        s3.upload_file(path, bucket_name, key)
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

