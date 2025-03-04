import boto3
import os
import dotenv

dotenv.load_dotenv()

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


def get_number_of_files(path):
    """
    Get the number of files in an S3 bucket's folder.
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
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=path)
        return len(response['Contents'])
    except Exception as e:
        print(f"Error getting number of files in S3: {e}")
        return 0
