import os
import boto3
import tempfile
import zipfile
from flask import Flask, request, jsonify

app = Flask(__name__)

# AWS config
S3_BUCKET = 'smiley-photo-galleries'
REGION = 'us-east-2'
s3 = boto3.client('s3', region_name=REGION)

@app.route('/')
def home():
    return 'Smiley ZIP API is live!'

@app.route('/zip', methods=['POST'])
def generate_zip():
    data = request.get_json()
    event_id = data.get('event_id')
    gallery_type = data.get('type')

    if not event_id or not gallery_type:
        return jsonify({'error': 'Missing event_id or type'}), 400

    prefix = f"galleries/{event_id}/{gallery_type}/"
    zip_filename = f"{event_id}-{gallery_type}.zip"
    zip_key = f"zips/{zip_filename}"

    try:
        # List files in S3 prefix
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        contents = response.get('Contents', [])

        if not contents:
            return jsonify({'error': 'No files found in gallery'}), 404

        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_path = os.path.join(tmpdirname, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for obj in contents:
                    key = obj['Key']
                    if key.endswith('/'):
                        continue  # skip folder keys
                    local_path = os.path.join(tmpdirname, os.path.basename(key))
                    s3.download_file(S3_BUCKET, key, local_path)
                    zipf.write(local_path, arcname=os.path.basename(key))

            # Upload back to S3
            s3.upload_file(zip_path, bucket, s3_key)

        zip_url = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{zip_key}"
        return jsonify({'url': zip_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
