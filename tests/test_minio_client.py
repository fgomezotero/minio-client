"""A module for integration tests of the MinioClient.

This module contains a suite of integration tests for the MinioClient class,
ensuring that it correctly interacts with a live MinIO server. These tests
cover bucket and file operations, including creation, deletion, listing,
uploading, and downloading.

Note: These tests require a running MinIO server instance and credentials
provided via environment variables.
"""

import unittest
import os
import tempfile
from minio.error import S3Error
from src.minio_client.main import MinioClient


class TestMinioClient(unittest.TestCase):
    """Defines the integration test suite for the MinioClient.

    This class sets up a connection to a MinIO server and a dedicated test
    bucket, which is cleaned up before and after each test to ensure test
    isolation.
    """

    @classmethod
    def setUpClass(cls):
        """Initializes the MinIO client and configuration for all tests.

        This method is run once per class, setting up the connection
        details from environment variables and creating a client instance
        that will be reused across all tests.
        """
        cls.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        cls.access_key = os.getenv("MINIO_ACCESS_KEY", "accesskey")
        cls.secret_key = os.getenv("MINIO_SECRET_KEY", "secretkey")
        cls.client = MinioClient(
            cls.endpoint, cls.access_key, cls.secret_key, secure=False
        )
        cls.test_bucket = "test-bucket-integration"

    def setUp(self):
        """Ensures the test bucket is clean before each test run.

        This method removes the test bucket and all its contents to prevent
        interference between tests. It runs before every single test method.
        """
        try:
            if self.client.bucket_exists(self.test_bucket):
                objects = self.client.list_objects(self.test_bucket)
                for obj in objects:
                    self.client.remove_object(self.test_bucket, obj)
                self.client.remove_bucket(self.test_bucket)
        except S3Error:
            pass  # Ignore errors if the bucket is already gone

    def tearDown(self):
        """Cleans up resources after each test run.

        This method ensures the test bucket and its contents are deleted
        after each test, maintaining a clean state for subsequent tests.
        """
        try:
            if self.client.bucket_exists(self.test_bucket):
                objects = self.client.list_objects(self.test_bucket)
                for obj in objects:
                    self.client.remove_object(self.test_bucket, obj)
                self.client.remove_bucket(self.test_bucket)
        except S3Error:
            pass  # Ignore errors if cleanup fails

    def test_bucket_operations(self):
        """Tests the full lifecycle of bucket management.

        This test verifies the following sequence:
        1. A new bucket does not exist initially.
        2. The bucket can be created successfully.
        3. The new bucket appears in the list of all buckets.
        4. The bucket can be removed successfully.
        """
        # 1. Verify bucket does not exist initially
        self.assertFalse(self.client.bucket_exists(self.test_bucket))

        # 2. Create the bucket
        self.client.make_bucket(self.test_bucket)
        self.assertTrue(self.client.bucket_exists(self.test_bucket))

        # 3. Verify the bucket is in the list of all buckets
        buckets = self.client.list_buckets()
        self.assertIn(self.test_bucket, buckets)

        # 4. Remove the bucket
        self.client.remove_bucket(self.test_bucket)
        self.assertFalse(self.client.bucket_exists(self.test_bucket))

    def test_file_operations(self):
        """Tests the full lifecycle of file management within a bucket.

        This test verifies the following sequence:
        1. A file can be uploaded to a bucket.
        2. The uploaded file appears in the object list.
        3. The file can be downloaded correctly.
        4. The downloaded file's content matches the original.
        5. The file can be removed from the bucket.
        """
        # Create a temporary file with content for testing
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.txt'
        ) as f:
            f.write("Test content for MinIO")
            test_file_path = f.name

        try:
            # 1. Upload the file
            self.client.upload_file(self.test_bucket, "test.txt", test_file_path)

            # 2. Verify the object is listed in the bucket
            objects = self.client.list_objects(self.test_bucket)
            self.assertIn("test.txt", objects)

            # 3. Download the file to a new temporary path
            download_path = tempfile.NamedTemporaryFile(suffix=".txt").name
            self.client.download_file(
                self.test_bucket, "test.txt", download_path
            )

            # 4. Verify the content of the downloaded file
            with open(download_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "Test content for MinIO")

            # 5. Remove the object from the bucket
            self.client.remove_object(self.test_bucket, "test.txt")
            objects = self.client.list_objects(self.test_bucket)
            self.assertNotIn("test.txt", objects)

        finally:
            # Clean up local temporary files
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
            if os.path.exists(download_path):
                os.unlink(download_path)

    def test_list_objects_with_prefix(self):
        """Tests filtering objects in a bucket by a specific prefix.

        This test uploads multiple files into simulated subdirectories and
        verifies that the `list_objects` method correctly returns only the
        files matching the specified prefix.
        """
        # Create a temporary file to upload multiple times
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.txt'
        ) as f:
            f.write("Test content")
            test_file_path = f.name

        try:
            # Upload files with different prefixes
            self.client.upload_file(
                self.test_bucket, "docs/file1.txt", test_file_path
            )
            self.client.upload_file(
                self.test_bucket, "docs/file2.txt", test_file_path
            )
            self.client.upload_file(
                self.test_bucket, "images/pic1.jpg", test_file_path
            )

            # Test filtering with the 'docs/' prefix
            docs_objects = self.client.list_objects(
                self.test_bucket, prefix="docs/"
            )
            self.assertEqual(len(docs_objects), 2)
            self.assertIn("docs/file1.txt", docs_objects)
            self.assertIn("docs/file2.txt", docs_objects)

            # Test filtering with the 'images/' prefix
            images_objects = self.client.list_objects(
                self.test_bucket, prefix="images/"
            )
            self.assertEqual(len(images_objects), 1)
            self.assertIn("images/pic1.jpg", images_objects)

        finally:
            # Clean up the local temporary file
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)

    @unittest.skipIf(
        not os.getenv("MINIO_ENDPOINT"), "MinIO server not available"
    )
    def test_connection(self):
        """Tests that a basic connection to the MinIO server can be made.

        This test attempts to list buckets and fails if an exception occurs,
        verifying that the client can communicate with the server. It is
        skipped if the MINIO_ENDPOINT environment variable is not set.
        """
        try:
            buckets = self.client.list_buckets()
            self.assertIsInstance(buckets, list)
        except Exception as e:
            self.fail(f"Failed to connect to MinIO server: {e}")


if __name__ == "__main__":
    unittest.main()