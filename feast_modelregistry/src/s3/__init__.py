import os


def init():
    """
    Initialize the MinIO S3 environment
    """
    # MinIO username
    os.environ['accesskey'] = 'minio'
    # MinIO password
    os.environ['secretkey'] = 'minio123'
    # MinIO API endpoint
    os.environ['AWS_S3_ENDPOINT'] = 'http://minio-service.feast.svc.cluster.local:9000'
    # Bucket name
    os.environ['AWS_S3_BUCKET'] = 'feast'
    # MinIO region
    os.environ['AWS_DEFAULT_REGION'] = 'default'
    print(f"Initialized MinIO S3 environment served by {os.environ['AWS_S3_ENDPOINT']}")


init()