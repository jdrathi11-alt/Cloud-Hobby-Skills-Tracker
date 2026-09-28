import os, uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED = {'image/jpeg','image/png','image/webp','application/pdf'}

def save_local(file, user_id):
    if not file or not file.filename: raise ValueError('No file supplied')
    if file.content_type not in ALLOWED: raise ValueError('Unsupported file type')
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    key = f'users/{user_id}/{uuid.uuid4().hex}{ext}'
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    return key

def delete_local(key):
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], key)
    if os.path.exists(path): os.remove(path)
