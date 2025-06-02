from flask import Flask, request, jsonify
import redis
import os
import json

app = Flask(__name__)

# Redis connection
REDIS_URL = os.environ.get("REDIS_URL")  # You'll add this to Render
r = redis.Redis.from_url(REDIS_URL)

@app.route("/")
def home():
    return "Smiley ZIP API with Redis is live!"

@app.route("/zip", methods=["POST"])
def queue_zip_job():
    data = request.get_json()

    event_id = data.get("event_id")
    gallery_type = data.get("type")
    email = data.get("email")

    if not event_id or not gallery_type or not email:
        return jsonify({"error": "Missing event_id, type, or email"}), 400

    # Queue the job
    job = {
        "event_id": event_id,
        "type": gallery_type,
        "email": email
    }

    r.rpush("zip_jobs", json.dumps(job))  # Push to Redis queue
    return jsonify({"message": "Job queued"}), 202
