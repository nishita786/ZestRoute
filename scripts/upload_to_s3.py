"""
Upload ZestRoute datasets to an AWS S3 data lake bucket.

Usage:
  export AWS_REGION=ap-south-1
  export S3_BUCKET=your-zestroute-data-lake-bucket
  python scripts/upload_to_s3.py

Requires AWS credentials via environment variables, shared credentials file,
or an IAM role. Never hard-code secrets in this script.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "orders.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "clean_orders.csv"

UPLOAD_MAP = {
    RAW_PATH: "raw/orders.csv",
    PROCESSED_PATH: "processed/clean_orders.csv",
}


def get_bucket_name() -> str:
    bucket = os.getenv("S3_BUCKET", "").strip()
    if not bucket:
        print(
            "Missing S3_BUCKET environment variable.\n"
            "Example: export S3_BUCKET=your-zestroute-data-lake-bucket"
        )
        sys.exit(1)
    return bucket


def upload_file(client, bucket: str, local_path: Path, key: str) -> None:
    if not local_path.exists():
        raise FileNotFoundError(f"Local file not found: {local_path}")
    print(f"Uploading {local_path} -> s3://{bucket}/{key}")
    client.upload_file(str(local_path), bucket, key)


def main() -> None:
    bucket = get_bucket_name()
    region = os.getenv("AWS_REGION", "ap-south-1")
    client = boto3.client("s3", region_name=region)

    try:
        for local_path, key in UPLOAD_MAP.items():
            upload_file(client, bucket, local_path, key)
    except (BotoCoreError, ClientError, FileNotFoundError) as exc:
        print(f"Upload failed: {exc}")
        sys.exit(1)

    print("S3 upload completed successfully.")


if __name__ == "__main__":
    main()
