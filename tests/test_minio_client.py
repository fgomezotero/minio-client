"""Integration tests for MinioClient"""

import unittest
import os
import tempfile
from minio.error import S3Error
from src.minio_client.main import MinioClient


class TestMinioClient(unittest.TestCase):
    """Integration test cases for MinioClient class"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the class"""
        cls.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        cls.access_key = os.getenv("MINIO_ACCESS_KEY", "accesskey")
        cls.secret_key = os.getenv(
            "MINIO_SECRET_KEY", "secretkey"
        )
        cls.client = MinioClient(cls.endpoint, cls.access_key, cls.secret_key, secure=False)
        cls.test_bucket = "test-bucket-integration"

    def setUp(self):
        """Clean up before each test"""
        try:
            if self.client.bucket_exists(self.test_bucket):
                objects = self.client.list_objects(self.test_bucket)
                for obj in objects:
                    self.client.remove_object(self.test_bucket, obj)
                self.client.remove_bucket(self.test_bucket)
        except S3Error:
            pass

    def tearDown(self):
        """Clean up after each test"""
        try:
            if self.client.bucket_exists(self.test_bucket):
                objects = self.client.list_objects(self.test_bucket)
                for obj in objects:
                    self.client.remove_object(self.test_bucket, obj)
                self.client.remove_bucket(self.test_bucket)
        except S3Error:
            pass

    def test_bucket_operations(self):
        """Test bucket creation, existence check, and removal"""
        # Test bucket doesn't exist initially
        self.assertFalse(self.client.bucket_exists(self.test_bucket))

        # Test bucket creation
        self.client.make_bucket(self.test_bucket)
        self.assertTrue(self.client.bucket_exists(self.test_bucket))

        # Test bucket appears in list
        buckets = self.client.list_buckets()
        self.assertIn(self.test_bucket, buckets)

        # Test bucket removal
        self.client.remove_bucket(self.test_bucket)
        self.assertFalse(self.client.bucket_exists(self.test_bucket))

    def test_file_operations(self):
        """Test file upload, download, list, and removal"""
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for MinIO")
            test_file_path = f.name

        try:
            # Test upload
            self.client.upload_file(self.test_bucket, "test.txt", test_file_path)

            # Test list objects
            objects = self.client.list_objects(self.test_bucket)
            self.assertIn("test.txt", objects)

            # Test download
            download_path = tempfile.NamedTemporaryFile(suffix=".txt").name
            self.client.download_file(self.test_bucket, "test.txt", download_path)

            # Verify downloaded content
            with open(download_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "Test content for MinIO")

            # Test remove object
            self.client.remove_object(self.test_bucket, "test.txt")
            objects = self.client.list_objects(self.test_bucket)
            self.assertNotIn("test.txt", objects)

        finally:
            # Clean up files
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
            # if os.path.exists(download_path):
            #     os.unlink(download_path)

    def test_list_objects_with_prefix(self):
        """Test listing objects with prefix filter"""
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            test_file_path = f.name

        try:
            # Upload files with different prefixes
            self.client.upload_file(self.test_bucket, "docs/file1.txt", test_file_path)
            self.client.upload_file(self.test_bucket, "docs/file2.txt", test_file_path)
            self.client.upload_file(self.test_bucket, "images/pic1.jpg", test_file_path)

            # Test prefix filtering
            docs_objects = self.client.list_objects(self.test_bucket, prefix="docs/")
            self.assertEqual(len(docs_objects), 2)
            self.assertIn("docs/file1.txt", docs_objects)
            self.assertIn("docs/file2.txt", docs_objects)

            images_objects = self.client.list_objects(self.test_bucket, prefix="images/")
            self.assertEqual(len(images_objects), 1)
            self.assertIn("images/pic1.jpg", images_objects)

        finally:
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)

    @unittest.skipIf(not os.getenv("MINIO_ENDPOINT"), "MinIO server not available")
    def test_connection(self):
        """Test MinIO server connection"""
        try:
            buckets = self.client.list_buckets()
            self.assertIsInstance(buckets, list)
        except Exception as e:
            self.fail(f"Failed to connect to MinIO server: {e}")


if __name__ == "__main__":
    unittest.main()
