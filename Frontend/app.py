from flask import Flask, render_template, request, jsonify, Response
import boto3
import os
import uuid
import csv
import io
from video_to_images import split_video_to_images

app = Flask(__name__)

# --- AWS CONFIG ---
S3_BUCKET_IMAGES = "engagesight-images"
S3_BUCKET_ANNOTATED = "engagesight-annotated"
S3_UPLOAD_PREFIX = "uploads/"
S3_ANNOTATED_PREFIX = "annotated/"
DYNAMODB_TABLE = "EngageSightParticipants"

s3 = boto3.client("s3", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

# --- ROUTES ---

@app.route('/')
def index():
    """Render EngageSight main upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Handle video upload and frame extraction."""
    try:
        # 1️⃣ Get uploaded file and interval
        file = request.files.get('file')
        if not file:
            return jsonify({"success": False, "error": "No file uploaded."}), 400

        interval = int(request.form.get('interval', 10))

        # 2️⃣ Save video temporarily on EC2
        os.makedirs("uploads", exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        video_path = os.path.join("uploads", filename)
        file.save(video_path)

        print(f"🎥 Received video: {filename}")
        print(f"⏱ Interval selected: {interval} seconds")

        # 3️⃣ Process video and upload frames to S3
        uploaded_files = split_video_to_images(video_path, interval)

        # 4️⃣ Clean up local video
        if os.path.exists(video_path):
            os.remove(video_path)

        # 5️⃣ Return response with uploaded frame URLs
        return jsonify({
            "success": True,
            "message": f"{len(uploaded_files)} frames uploaded successfully.",
            "uploaded_files": uploaded_files,
            "csv_url": "#"
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/download_images', methods=['GET'])
def download_images():
    """List all annotated images from S3."""
    try:
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET_ANNOTATED,
            Prefix=S3_ANNOTATED_PREFIX
        )

        if "Contents" not in response:
            return jsonify({"success": False, "message": "No annotated images found."})

        files = [
            f"https://{S3_BUCKET_ANNOTATED}.s3.amazonaws.com/{obj['Key']}"
            for obj in response["Contents"]
            if obj["Key"].lower().endswith((".png", ".jpg"))
        ]

        return jsonify({
            "success": True,
            "annotated_images": files,
            "count": len(files)
        })
    except Exception as e:
        print(f"❌ Error listing annotated images: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/download_csv', methods=['GET'])
def download_csv():
    """Generate and return a CSV file from DynamoDB."""
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.scan()
        items = response.get("Items", [])

        if not items:
            return jsonify({"success": False, "message": "No data found in DynamoDB."})

        # Create CSV in memory
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)

        # Return CSV as download
        return Response(
            csv_buffer.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=engagesight_results.csv"}
        )
    except Exception as e:
        print(f"❌ Error exporting DynamoDB data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# --- MAIN ENTRY POINT ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)


# Feature
# Description
# 🧩 Simplified logic
# All uploads handled by split_video_to_images()
# 🪣 Real URLs returned
# Flask sends list of S3 URLs back to frontend
# 🧼 Auto-clean
# Temporary video file deleted after upload
# 💬 Clear logs
# Prints video name, interval, and progress
# 🚨 Better error messages
# Clear responses for no file / processing issues
# Feature
# Description
# 🖼️ Download Annotated Images
# Lists all .png / .jpg files from s3://engagesight-annotated/annotated/
# 📊 Download Participant CSV
# Exports all DynamoDB entries to a downloadable CSV file
# 🧠 Better structure & logging
# Easier to maintain, all buckets clearly defined
# 🪣 Bucket-safe
# Uses S3_BUCKET_ANNOTATED instead of hardcoding replacements

