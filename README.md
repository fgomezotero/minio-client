# MinIO Client

A simple Python client for MinIO object storage operations.

## Features

- Bucket management (create, delete, list, check existence)
- File operations (upload, download, list, remove)
- Object listing with prefix filtering
- Simple and intuitive API

## Installation

```bash
pip install minio
```

## Quick Start

```python
from src.minio_client.main import MinioClient

# Initialize client
client = MinioClient(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Create bucket and upload file
client.make_bucket("my-bucket")
client.upload_file("my-bucket", "example.txt", "/path/to/local/file.txt")

# List objects
objects = client.list_objects("my-bucket")
print(objects)

# Download file
client.download_file("my-bucket", "example.txt", "/path/to/download/file.txt")
```

## API Reference

### MinioClient(endpoint, access_key, secret_key, secure=True)

Initialize MinIO client.

**Parameters:**
- `endpoint` (str): MinIO server endpoint
- `access_key` (str): Access key for authentication
- `secret_key` (str): Secret key for authentication
- `secure` (bool): Use HTTPS if True, HTTP if False

### Methods

#### Bucket Operations

- `bucket_exists(bucket_name)` - Check if bucket exists
- `make_bucket(bucket_name)` - Create bucket if it doesn't exist
- `remove_bucket(bucket_name)` - Delete bucket
- `list_buckets()` - List all buckets

#### Object Operations

- `upload_file(bucket_name, object_name, file_path)` - Upload file to bucket
- `download_file(bucket_name, object_name, file_path)` - Download file from bucket
- `list_objects(bucket_name, prefix="", recursive=True)` - List objects in bucket
- `remove_object(bucket_name, object_name)` - Remove object from bucket

## Environment Variables

Set these environment variables for configuration:

```bash
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="your-access-key"
export MINIO_SECRET_KEY="your-secret-key"
```

## Testing

Run integration tests with a running MinIO server:

```bash
python -m unittest tests/test_minio_client.py
```

Or with pytest:

```bash
pytest tests/test_minio_client.py -v
```

## Requirements

- Python 3.6+
- minio >= 7.0.0

## License

MIT License