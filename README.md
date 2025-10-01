# Simplified MinIO Client for Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python client providing a simplified interface for common object storage operations on a MinIO server or any S3-compatible service.

## Overview

This project wraps the official [`minio-py`](https://github.com/minio/minio-py) library to offer a more straightforward, high-level API for frequent tasks like bucket management and file handling. It is designed for developers who need to integrate basic object storage capabilities into their applications with minimal setup and boilerplate code.

The client automatically handles bucket creation on upload and provides clear, concise methods for all its operations.

## Features

- **Simplified API**: Intuitive methods for common object storage tasks.
- **Bucket Management**: Create, delete, list, and check for the existence of buckets.
- **File Operations**: Upload, download, and delete files.
- **Object Listing**: List objects within a bucket, with optional prefix filtering.
- **Idempotent Operations**: `make_bucket` and `upload_file` are safe to call multiple times.

## Prerequisites

- Python 3.7+
- [Poetry](https://python-poetry.org/) for dependency management.
- A running MinIO server instance. You can start one easily using Docker:
  ```bash
  docker run -p 9000:9000 -p 9001:9001 --name minio \
    -e "MINIO_ROOT_USER=minioadmin" \
    -e "MINIO_ROOT_PASSWORD=minioadmin" \
    minio/minio server /data --console-address ":9001"
  ```

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/minio-client.git
    cd minio-client
    ```

2.  **Set up environment variables:**
    The client is configured using environment variables. Create a `.env` file in the root directory or export them in your shell:
    ```bash
    export MINIO_ENDPOINT="localhost:9000"
    export MINIO_ACCESS_KEY="minioadmin"
    export MINIO_SECRET_KEY="minioadmin"
    ```

3.  **Install dependencies:**
    This project uses Poetry for dependency management.
    ```bash
    poetry install
    ```

## Quick Start

Here is a complete example demonstrating how to use the `MinioClient`.

```python
import os
from src.minio_client import MinioClient

# 1. Initialize the client
# The client automatically reads credentials from environment variables.
endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
access_key = os.getenv("MINIO_ACCESS_KEY", "accesskey")
secret_key = os.getenv("MINIO_SECRET_KEY", "secretkey")

client = MinioClient(endpoint, access_key, secret_key, secure=False)

# 2. Define bucket and file names
bucket_name = "my-test-bucket"
object_name = "my-document.txt"
file_path = "my-document.txt"
download_path = "downloaded_document.txt"

# 3. Create a dummy file for uploading
with open(file_path, "w") as f:
    f.write("Hello, MinIO!")

try:
    # 4. Upload the file
    # The bucket will be created automatically if it doesn't exist.
    print(f"Uploading '{file_path}' to bucket '{bucket_name}'...")
    client.upload_file(bucket_name, object_name, file_path)
    print("Upload successful.")

    # 5. List objects in the bucket
    objects = client.list_objects(bucket_name)
    print(f"Objects in '{bucket_name}': {objects}")
    assert object_name in objects

    # 6. Download the file
    print(f"Downloading '{object_name}' to '{download_path}'...")
    client.download_file(bucket_name, object_name, download_path)

    # 7. Verify its content
    with open(download_path, "r") as f:
        content = f.read()
        print(f"Downloaded content: '{content}'")
        assert content == "Hello, MinIO!"

finally:
    # 8. Clean up resources
    print("Cleaning up...")
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(download_path):
        os.remove(download_path)

    client.remove_object(bucket_name, object_name)
    client.remove_bucket(bucket_name)
    print("Cleanup complete.")

```

## Running Tests

To run the integration tests, ensure your MinIO server is running and the environment variables are set correctly. Then, run the following command:

```bash
poetry run pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.