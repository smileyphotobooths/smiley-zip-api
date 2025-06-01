from flask import Flask, request, jsonify
import boto3
import os
import zipfile
import tempfile

app = Flask(__name__)

S3_BUCKET = 'smiley-photo-galleries'
S3_REGION = 'us-east-2'
BASE_PREFIX = 'galleries'

s3 = boto3.client('s3')

@app.route('/create-zip', methods=['POST'])
def create_zip():
    data = request.get_json()
    event_id = data.get('eventID')
    if not event_id:
        return jsonify({'error': 'Missing eventID'}), 400

    prefix = f'{BASE_PREFIX}/{event_id}/'
    zip_filename = f'{event_id}_gallery.zip'

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if key.endswith('/'):
                        continue
                    tmp_file_path = os.path.join(tmpdir, os.path.basename(key))
                    s3.download_file(S3_BUCKET, key, tmp_file_path)
                    zipf.write(tmp_file_path, arcname=os.path.relpath(key, prefix))

        zip_key = f'zips/{zip_filename}'
        s3.upload_file(zip_path, S3_BUCKET, zip_key, ExtraArgs={'ACL': 'public-read'})

    public_url = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{zip_key}'
    return jsonify({'zip_url': public_url})
