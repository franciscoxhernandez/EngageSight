from flask import Flask, render_template, request, jsonify
import boto3
import os
import uuid
from video_to_images import split_video_to_images

app = Flask(__name__)

# --- AWS S3 CONFIG ---
S3_BUCKET = "engagesight-images"   # ✅ bucket name fixed (with dash)
S3_UPLOAD_PREFIX = "uploads/"      # ✅ defined uploads folder prefix
s3 = boto3.client("s3")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    try:
        # 1️⃣ Get uploaded file and interval from form
        file = request.files['file']
        interval = int(request.form.get('interval', 10))

        # 2️⃣ Save video temporarily on EC2
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        video_path = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(video_path)

        # 3️⃣ Process video locally (split into images)
        split_video_to_images(video_path, interval)

        # Folder where frames are saved (based on your script)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        frames_folder = f"{video_name}_frames"

        # 4️⃣ Upload results to S3 -> all inside s3://engagesight-images/uploads/
        uploaded_files = []
        for img in os.listdir(frames_folder):
            local_path = os.path.join(frames_folder, img)
            s3_key = f"{S3_UPLOAD_PREFIX}{img}"  # ✅ no new folder, all go under uploads/
            s3.upload_file(local_path, S3_BUCKET, s3_key)
            uploaded_files.append(f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}")

        # 5️⃣ Optional: create a ZIP or CSV link (placeholder)
        # You could later add CSV export or annotated video here

        # 6️⃣ Clean up local files to save space
        os.remove(video_path)

        # 7️⃣ Return JSON response for the frontend
        return jsonify({
            "success": True,
            "images_url": f"https://{S3_BUCKET}.s3.amazonaws.com/{S3_UPLOAD_PREFIX}",
            "csv_url": "#"
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)