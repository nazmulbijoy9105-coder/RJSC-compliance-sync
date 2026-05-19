import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

# Initialize the S3 client configured for Cloudflare R2
s3_client = boto3.client(
    's3',
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name='auto'
)

def upload_file_to_storage(file_bytes: bytes, file_name: str, content_type: str) -> str:
    """
    Uploads a file to Cloudflare R2 and returns the public URL.
    """
    try:
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"
    except ClientError as e:
        print(f"Failed to upload to R2: {e}")
        raise Exception("File upload failed")
