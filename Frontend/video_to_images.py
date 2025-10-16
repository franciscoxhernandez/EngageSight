import cv2
import os
import boto3

def split_video_to_images(video_path, interval_seconds=10):
    """
    Splits a video into .png images every N seconds and uploads them to S3.
    Args:
        video_path (str): Path to the video file
        interval_seconds (int): Time interval between frames to extract
    Returns:
        uploaded_files (list): List of S3 URLs of uploaded frames
    """

    # --- AWS CONFIG ---
    S3_BUCKET = "engagesight-images"       # ✅ make sure this matches your bucket
    S3_PREFIX = "uploads/"                 # ✅ target folder in S3
    s3 = boto3.client("s3")

    if not os.path.exists(video_path):
        print("❌ Video file not found:", video_path)
        return []

    # Extract video name (without extension)
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Create temp output folder in same directory
    output_folder = os.path.join(os.path.dirname(video_path), f"{video_name}_frames")
    os.makedirs(output_folder, exist_ok=True)

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Could not open video:", video_path)
        return []

    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps if fps > 0 else 0

    print(f"🎞 Video: {video_name}")
    print(f"⏱ Duration: {duration_seconds:.2f}s ({total_frames} frames)")
    print(f"⚙️ FPS: {fps:.2f}")

    # Calculate interval in frames
    frame_interval = int(fps * interval_seconds)
    print(f"📸 Extracting frame every {interval_seconds}s ({frame_interval} frames apart)...")

    frame_count = 0
    saved_count = 0
    uploaded_files = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            saved_count += 1
            filename = f"{saved_count:03d}_{video_name}.png"
            local_path = os.path.join(output_folder, filename)
            cv2.imwrite(local_path, frame)

            # --- Upload to S3 ---
            s3_key = f"{S3_PREFIX}{filename}"
            s3.upload_file(local_path, S3_BUCKET, s3_key)
            s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
            uploaded_files.append(s3_url)
            print(f"✅ Uploaded: {s3_url}")

            # Optionally remove local copy to save space
            os.remove(local_path)

        frame_count += 1

    cap.release()
    print(f"\n✅ Done! {saved_count} frames uploaded to s3://{S3_BUCKET}/{S3_PREFIX}")
    return uploaded_files


# --- Optional Standalone Test ---
if __name__ == "__main__":
    test_video = "uploads/test_meeting.mp4"
    split_video_to_images(test_video, 10)