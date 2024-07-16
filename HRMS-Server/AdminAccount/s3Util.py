import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings


def upload_to_s3(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        return True
    except FileNotFoundError:
        return False
    except NoCredentialsError:
        return False