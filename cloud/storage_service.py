"""Production storage adapter sketch. Keep credentials server-side.
Use an S3-compatible provider (AWS S3, Supabase Storage through its compatible APIs,
or another object store) and return short-lived signed URLs rather than public keys.
"""
import os, boto3

def client():
    return boto3.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL') or None, aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'), region_name=os.getenv('S3_REGION','us-east-1'))

def upload(path, object_key, content_type):
    client().upload_file(path, os.environ['S3_BUCKET'], object_key, ExtraArgs={'ContentType':content_type})

def signed_url(object_key, expires=900):
    return client().generate_presigned_url('get_object', Params={'Bucket':os.environ['S3_BUCKET'],'Key':object_key}, ExpiresIn=expires)

def delete(object_key):
    client().delete_object(Bucket=os.environ['S3_BUCKET'], Key=object_key)
