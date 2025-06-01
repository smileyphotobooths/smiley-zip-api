from flask import Flask, request, jsonify

app = Flask(__name__)

# ✅ Home route for testing
@app.route('/')
def home():
    return "Smiley ZIP API is live!"

# 🧪 Optional test endpoint for now
@app.route('/zip', methods=['POST'])
def create_zip():
    data = request.get_json()
    event_id = data.get('event_id')
    image_type = data.get('type')  # "singles" or "prints"

    # In a future step we'll actually create the ZIP here

    # For now, just return a dummy response
    return jsonify({
        "status": "success",
        "message": f"Simulated ZIP for {image_type} of event {event_id}",
        "download_url": f"https://smiley-photo-galleries.s3.amazonaws.com/zips/{event_id}-{image_type}.zip"
    })
