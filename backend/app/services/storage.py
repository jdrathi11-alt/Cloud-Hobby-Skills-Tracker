
import os
import uuid

from flask import current_app
from supabase import create_client
from werkzeug.utils import secure_filename


ALLOWED = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/pdf',
}


def get_storage():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    bucket = os.getenv('SUPABASE_BUCKET', 'uploads')

    if not url or not key:
        raise ValueError('Supabase Storage is not configured')

    client = create_client(url, key)
    return client.storage.from_(bucket)


def save_local(file, user_id):
    if not file or not file.filename:
        raise ValueError('No file supplied')

    if file.content_type not in ALLOWED:
        raise ValueError('Unsupported file type')

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    key = f'users/{user_id}/{uuid.uuid4().hex}{ext}'

    data = file.read()

    if not data:
        raise ValueError('Empty file')

    max_bytes = current_app.config.get(
        'MAX_CONTENT_LENGTH',
        5 * 1024 * 1024,
    )

    if len(data) > max_bytes:
        raise ValueError('File is too large')

    try:
        get_storage().upload(
            key,
            data,
            {
                'content-type': file.content_type,
                'upsert': False,
            },
        )
    except Exception as e:
        raise ValueError(f'Upload failed: {e}')

    return key


def delete_local(key):
    if not key:
        return

    try:
        get_storage().remove([key])
    except Exception:
        pass
