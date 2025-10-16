import cv2
import os
import math

def split_video_to_images(video_path, interval_seconds):
    # Check if video exists
    if not os.path.exists(video_path):
        print("❌ Video file not found.")
        return

    # Extract base name (without extension)
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Create output folder
    output_folder = f"{video_name}_frames"
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Could not open video.")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps

    print(f"🎞 Video: {video_name}")
    print(f"⏱ Duration: {duration_seconds:.2f}s ({total_frames} frames)")
    print(f"⚙️ FPS: {fps:.2f}")

    # Calculate frame interval
    frame_interval = int(fps * interval_seconds)
    print(f"📸 Extracting frame every {interval_seconds}s ({frame_interval} frames apart)...")

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            saved_count += 1
            filename = f"{saved_count:03d}_{video_name}.png"
            filepath = os.path.join(output_folder, filename)
            cv2.imwrite(filepath, frame)
            print(f"✅ Saved: {filename}")

        frame_count += 1

    cap.release()
    print(f"\n✅ Done! {saved_count} frames saved in '{output_folder}'.")


if __name__ == "__main__":
    # --- USER INPUTS ---
    video_path = input("🎥 Enter path to video file: ").strip()

    print("\nSelect split interval (seconds):")
    print("1. 5s\n2. 10s\n3. 20s\n4. 30s\n5. 60s")
    choice = input("Enter choice (1–5): ").strip()

    interval_map = {"1": 5, "2": 10, "3": 20, "4": 30, "5": 60}
    interval_seconds = interval_map.get(choice, 10)  # Default 10s

    split_video_to_images(video_path, interval_seconds)