from flask import Flask, request, jsonify
import boto3
import tempfile
import zipfile
import os

app = Flask(__name__)

# AWS credentials (these should be set as environment variables in Render)
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
REGION = 'us-east-2'
BUCKET = 'smiley-photo-galleries'

# Route to confirm deployment
@app.route('/')
def home():
    return 'Smiley ZIP API is live!'

@app.route('/zip', methods=['POST'])
def generate_zip():
    event_id = request.json.get('event_id')
    gallery_type = request.json.get('type')

    if not event_id or not gallery_type:
        return jsonify({'error': 'Missing event_id or type'}), 400

    prefix = f'galleries/{event_id}/{gallery_type}/'

    # Create a temporary directory to hold the zip file
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, f'{event_id}-{gallery_type}.zip')

        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=REGION
        )

        # List files in the target prefix
        try:
            response = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
            if 'Contents' not in response:
                return jsonify({'error': 'No files found in this gallery'}), 404

            # Create the ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('/'):
                        continue  # Skip folder keys

                    filename = os.path.basename(key)
                    temp_file = os.path.join(tmpdir, filename)
                    s3.download_file(BUCKET, key, temp_file)
                    zipf.write(temp_file, arcname=filename)

            # Upload the ZIP file to /zips/ folder in the bucket
            zip_key = f'zips/{event_id}-{gallery_type}.zip'
            s3.upload_file(zip_path, BUCKET, zip_key)

            # Generate a presigned download URL (valid for 7 days)
            download_url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': BUCKET, 'Key': zip_key},
                ExpiresIn=604800  # 7 days in seconds
            )

            return jsonify({'url': download_url})

        except Exception as e:
            return jsonify({'error': str(e)}), 500
