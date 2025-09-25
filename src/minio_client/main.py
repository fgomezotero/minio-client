"""MinIO Client Module"""

import os
from minio import Minio
from minio.error import S3Error

class MinioClient:
    """A simple MinIO client for basic operations.

    Args:
        endpoint (str): MinIO server endpoint.
        access_key (str): Access key for MinIO.
        secret_key (str): Secret key for MinIO.
        secure (bool, optional): Use HTTPS if True, HTTP if False. Defaults to True.
    """
    def __init__(self, endpoint, access_key, secret_key, secure=True):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def bucket_exists(self, bucket_name):
        """Check if a bucket exists.

        Args:
            bucket_name (str): Name of the bucket.

        Returns:
            bool: True if bucket exists, False otherwise.
        """
        return self.client.bucket_exists(bucket_name)

    def make_bucket(self, bucket_name):
        """Create a new bucket if it doesn't exist.

        Args:
            bucket_name (str): Name of the bucket to create.
        """
        if not self.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def list_buckets(self):
        """List all buckets.

        Returns:
            list: List of bucket names.
        """
        return [bucket.name for bucket in self.client.list_buckets()]

    def upload_file(self, bucket_name, object_name, file_path):
        """Upload a file to a bucket.

        Args:
            bucket_name (str): Name of the bucket.
            object_name (str): Name of the object in the bucket.
            file_path (str): Path to the local file to upload.
        """
        self.make_bucket(bucket_name)
        self.client.fput_object(bucket_name, object_name, file_path)

    def download_file(self, bucket_name, object_name, file_path):
        """Download a file from a bucket.

        Args:
            bucket_name (str): Name of the bucket.
            object_name (str): Name of the object in the bucket.
            file_path (str): Path where the file will be saved.
        """
        self.client.fget_object(bucket_name, object_name, file_path)

    def list_objects(self, bucket_name, prefix="", recursive=True):
        """List objects in a bucket.

        Args:
            bucket_name (str): Name of the bucket.
            prefix (str, optional): Filter objects by prefix. Defaults to "".
            recursive (bool, optional): List recursively. Defaults to True.

        Returns:
            list: List of object names.
        """
        return [obj.object_name for obj in self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)]

    def remove_object(self, bucket_name, object_name):
        """Remove an object from a bucket.

        Args:
            bucket_name (str): Name of the bucket.
            object_name (str): Name of the object to remove.
        """
        self.client.remove_object(bucket_name, object_name)

# Example usage (remove or adapt for production)
if __name__ == "__main__":
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    client = MinioClient(endpoint, access_key, secret_key, secure=False)

    bucket = "test-bucket"
    file_path = "example.txt"
    object_name = "example.txt"

    try:
        client.upload_file(bucket, object_name, file_path)
        print("Uploaded:", object_name)
        print("Objects in bucket:", client.list_objects(bucket))
        client.download_file(bucket, object_name, f"downloaded_{object_name}")
        print("Downloaded:", object_name)
        client.remove_object(bucket, object_name)
        print("Removed:", object_name)
    except S3Error as err:
        print("MinIO error:", err)