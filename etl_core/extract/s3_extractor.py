import logging
import boto3
import pandas as pd
from io import StringIO, BytesIO
from django.conf import settings

logger = logging.getLogger('pipeline')


class S3Extractor:
    """Extract raw data files from S3."""

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME

    def list_files(self, prefix: str) -> list[str]:
        paginator = self.client.get_paginator('list_objects_v2')
        keys = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            keys.extend(obj['Key'] for obj in page.get('Contents', []))
        return keys

    def read_csv(self, key: str) -> pd.DataFrame:
        logger.info(f"Extracting s3://{self.bucket}/{key}")
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))

    def read_parquet(self, key: str) -> pd.DataFrame:
        logger.info(f"Extracting parquet s3://{self.bucket}/{key}")
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return pd.read_parquet(BytesIO(obj['Body'].read()))

    def upload_processed(self, df: pd.DataFrame, key: str) -> None:
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        self.client.put_object(
            Bucket=self.bucket,
            Key=f"{settings.S3_PROCESSED_PREFIX}{key}",
            Body=buffer.getvalue(),
        )
        logger.info(f"Uploaded processed file to s3://{self.bucket}/{settings.S3_PROCESSED_PREFIX}{key}")
