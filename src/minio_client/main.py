"""A module for a simplified MinIO client.

This module provides the MinioClient class, which wraps the official
`minio-py` library to offer a simpler interface for common S3-compatible
object storage operations, such as creating buckets, and uploading,
downloading, and deleting files.
"""

import os
from minio import Minio
from minio.error import S3Error


class MinioClient:
    """A simplified client for common MinIO operations.

    This client provides a straightforward interface for interacting with
    a MinIO or other S3-compatible object storage server.

    Attributes:
        client: An instance of the underlying `minio.Minio` client.
    """

    def __init__(self, endpoint, access_key, secret_key, secure=True):
        """Initializes the MinioClient.

        Args:
            endpoint (str): The URL of the MinIO server (e.g., 'localhost:9000').
            access_key (str): The access key for authentication.
            secret_key (str): The secret key for authentication.
            secure (bool, optional): If True, uses HTTPS. If False, uses HTTP.
                Defaults to True.
        """
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def bucket_exists(self, bucket_name):
        """Checks if a bucket with the specified name exists.

        Args:
            bucket_name (str): The name of the bucket to check.

        Returns:
            bool: True if the bucket exists, False otherwise.

        Raises:
            S3Error: If an S3-related error occurs during the operation.
        """
        return self.client.bucket_exists(bucket_name)

    def make_bucket(self, bucket_name):
        """Creates a new bucket if it does not already exist.

        This method is idempotent; it will not raise an error if the bucket
        already exists.

        Args:
            bucket_name (str): The name of the bucket to create.

        Raises:
            S3Error: If an S3-related error occurs, such as an invalid
                bucket name.
        """
        if not self.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def remove_bucket(self, bucket_name):
        """Deletes a bucket from the MinIO server.

        The bucket must be empty for it to be deleted.

        Args:
            bucket_name (str): The name of the bucket to delete.

        Raises:
            S3Error: If the bucket is not empty or another S3-related
                error occurs.
        """
        self.client.remove_bucket(bucket_name)

    def list_buckets(self):
        """Retrieves a list of all buckets.

        Returns:
            list[str]: A list of bucket names.

        Raises:
            S3Error: If an S3-related error occurs during the operation.
        """
        return [bucket.name for bucket in self.client.list_buckets()]

    def upload_file(self, bucket_name, object_name, file_path):
        """Uploads a local file to a specified bucket.

        If the target bucket does not exist, it will be created automatically
        before the upload.

        Args:
            bucket_name (str): The name of the destination bucket.
            object_name (str): The name to assign to the object in the bucket.
            file_path (str): The local path of the file to upload.

        Raises:
            S3Error: If an S3-related error occurs during the upload.
            FileNotFoundError: If the specified `file_path` does not exist.
        """
        self.make_bucket(bucket_name)
        self.client.fput_object(bucket_name, object_name, file_path)

    def download_file(self, bucket_name, object_name, file_path):
        """Downloads an object from a bucket to a local file.

        Args:
            bucket_name (str): The name of the source bucket.
            object_name (str): The name of the object to download.
            file_path (str): The local path where the file will be saved.

        Raises:
            S3Error: If the object does not exist or another S3-related
                error occurs.
        """
        self.client.fget_object(bucket_name, object_name, file_path)

    def list_objects(self, bucket_name, prefix="", recursive=True):
        """Lists objects in a bucket, optionally filtering by prefix.

        Args:
            bucket_name (str): The name of the bucket to list objects from.
            prefix (str, optional): A prefix to filter the objects.
                Defaults to "".
            recursive (bool, optional): If True, lists objects in all
                subdirectories. Defaults to True.

        Returns:
            list[str]: A list of object names matching the criteria.

        Raises:
            S3Error: If the bucket does not exist or another S3-related
                error occurs.
        """
        return [
            obj.object_name for obj in self.client.list_objects(
                bucket_name, prefix=prefix, recursive=recursive
            )
        ]

    def remove_object(self, bucket_name, object_name):
        """Removes a single object from a bucket.

        Args:
            bucket_name (str): The name of the bucket containing the object.
            object_name (str): The name of the object to remove.

        Raises:
            S3Error: If the object does not exist or another S3-related
                error occurs.
        """
        self.client.remove_object(bucket_name, object_name)


# Example usage (remove or adapt for production)
if __name__ == "__main__":
    # Note: This example requires a running MinIO server and a file
    # named 'example.txt' in the same directory.
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "accesskey")
    secret_key = os.getenv("MINIO_SECRET_KEY", "secretkey")

    # Create a dummy file for upload
    with open("example.txt", "w") as f:
        f.write("This is a test file.")

    client = MinioClient(endpoint, access_key, secret_key, secure=False)

    bucket = "test-bucket"
    file_path = "example.txt"
    object_name = "example.txt"

    try:
        print(f"Connecting to MinIO at {endpoint}...")
        # Check existing buckets
        bucket_list = client.list_buckets()
        print("Existing buckets:", bucket_list)

        # Upload file
        print(f"Uploading '{file_path}' to bucket '{bucket}' as '{object_name}'...")
        client.upload_file(bucket, object_name, file_path)
        print("Upload successful.")

        # List objects
        print(f"Objects in bucket '{bucket}':", client.list_objects(bucket))

        # Download file
        downloaded_path = f"downloaded_{object_name}"
        print(f"Downloading '{object_name}' to '{downloaded_path}'...")
        client.download_file(bucket, object_name, downloaded_path)
        print("Download successful.")

        # Verify content
        with open(downloaded_path, "r") as f:
            content = f.read()
            print(f"Downloaded file content: '{content}'")
        os.remove(downloaded_path)  # Clean up downloaded file

        # Remove object
        print(f"Removing object '{object_name}' from bucket '{bucket}'...")
        client.remove_object(bucket, object_name)
        print("Object removal successful.")

        # Remove bucket
        print(f"Removing bucket '{bucket}'...")
        client.remove_bucket(bucket)
        print("Bucket removal successful.")

    except S3Error as err:
        print("A MinIO S3 error occurred:", err)
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
    finally:
        # Clean up the dummy file
        if os.path.exists("example.txt"):
            os.remove("example.txt")