import io
from typing import Optional
import pandas as pd
import boto3

class S3Uploader:
    """Upload DataFrame to S3 as parquet."""

    def __init__(self, bucket: str, prefix: str = "raw") -> None:
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.s3 = boto3.client("s3")

    def upload_parquet(self, df: pd.DataFrame, date: pd.Timestamp, key_prefix: Optional[str] = None) -> str:
        """Upload dataframe partitioned by date."""
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        partition = date.strftime("date=%Y-%m-%d")
        key = f"{self.prefix}/{partition}/data.parquet"
        if key_prefix:
            key = f"{self.prefix}/{partition}/{key_prefix}.parquet"
        self.s3.upload_fileobj(buffer, self.bucket, key)
        return key