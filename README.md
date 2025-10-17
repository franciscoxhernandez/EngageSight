# EngageSight — AI Engagement Recognition Tool | Version 1.0

## 🔎 Overview

**EngageSight** is an AI-powered tool that automatically analyzes participants’ engagement levels during online meetings.  
It combines **AWS Rekognition**, **Lambda**, **DynamoDB**, and **S3** in an event-driven architecture, with a web interface 
hosted on **AWS EC2** for intuitive video uploads and results visualization.

Originally developed, and currently being further refined, as part of the ongoing PhD research of **Francisco Hernández** 
at the [**Chair for Ergonomics and Innovation**](https://www.tu-chemnitz.de/mb/ArbeitsWiss/index.php), **Technische Universität Chemnitz**.

**EngageSight** explores how facial expressions and visual attention can be used to understand engagement during virtual meetings, **without 
tracking, or storing any biometric data**.

---

## 📦 About This Repository

This repository contains the **frontend application** for EngageSight — including the video upload, frame extraction, and results visualization logic (Flask + HTML/CSS/JS).

The backend components, such as **AWS Lambda** functions, **Rekognition** integration, and **Terraform** infrastructure, are part of a **proprietary research setup** developed for the PhD project.

A short **demo video** is available to illustrate how the system works in action 
- 🔗 [**Link to video**](https://engagesight-demo-video.s3.us-east-1.amazonaws.com/EngageSight_Video_GitHub.mp4 )

If you are interested in a **collaboration**, **demo**, or **research access**, please contact me directly:
 
- 🔗 [**LinkedIn**](https://www.linkedin.com/in/francisco-hernandez-col-ger/) 

### 🔄 How it works
1. **Video Upload**
- The user opens the EngageSight website (hosted on AWS EC2).
- A meeting video (.mp4, .mov, .avi) is uploaded using the web form.
- The user selects how often to extract frames — every 5, 10, 20, 30, or 60 seconds.
2.	**Frame Extraction**
- The Flask app calls the `video_to_images.py script
- OpenCV processes the video locally on the EC2 instance.
- Frames are saved temporarily and uploaded to the S3 bucket `engagesight-images`.
3. **AI Analysis (Automated via AWS)**
- Each uploaded frame automatically triggers the `EngageSightAnalysis` Lambda function.
- The Lambda function uses **AWS Rekognition** to detect:
  - Engagement indicators such as; 
    - Facial expressions and emotion intensity 
    - Attention (looking at camera)
    - Speaking activity and mood indicators
- Results are stored as .json files in S3 → `engagesight-results` and 
summary data in DynamoDB → `EngageSightParticipants`.
4. **Annotated Visualization**
- The `engagesight-annotator-trigger` Lambda function triggers the EC2 `engagesight-drawboxes` 
to draw bounding boxes and labels.
  - The draw boxes are classified in: 
    - 🟢 **GREEN**  → High Engagement 
    - 🟡 **YELLOW** → Medium Engagement 
    - 🔴 **RED** → Low Engagement 
    - `ADD HERE AND EXAMPLE OF GREEN YELLOW AND RED`
- Annotated images are uploaded to S3 → `engagesight-annotated`.
- The web app displays these annotated images directly in the browser.
5. **Results Download**
- Users can download:
  - 📸 Annotated Images from `engagesight-annotated`
  - 📊 Engagement CSV generated from `EngageSightParticipants` (DynamoDB)
    - This shows the Name of each participant
    - On how many frames was present 
    - Last engagement level 
    - Total Engagement
    - Average Engagement 
  - All downloads use pre-generated S3 URLs returned by Flask. 
- After download all files in the buckets and the dynamodb are deleted 

### ⚠️ Usage Recommendations
- Limit videos to **10 participants or fewer** for best performance.  
- Each participant must have a **unique name** — duplicate names will be merged.  
- **Only one screen** should be visible in the recording.  
- **No audio or facial tracking** is analyzed — only frame-by-frame visual data are processed locally. 

### 📝 Summary
EngageSight offers a **fully automated AI workflow** from video upload to engagement visualization.

### 🧩 Architecture Overview
```

```

## 🧮 Simplified Frontend Logic

| **Feature** | **Description** |
|--------------|-----------------|
| 🧩 **split_video_to_images()** | Handles all uploads and video-to-frame splitting. Each frame is uploaded to S3 automatically. |
| 🪣 **Real URLs returned** | Flask returns a JSON list of direct S3 URLs (public or presigned) back to the frontend. |
| 🧼 **Auto-clean** | After processing, temporary video files are automatically deleted from EC2 to save space. |
| 💬 **Clear logs** | Console logs show video name, duration, chosen interval, and progress. |
| 🚨 **Error handling** | The app returns structured error messages (missing file, invalid format, AWS issues, etc.). |
| 🖼️ **Download Annotated Images** | Lists all `.png` / `.jpg` files from `s3://engagesight-annotated/annotated/`. |
| 📊 **Download Participant CSV** | Exports all DynamoDB table entries into a downloadable CSV. |

----

## 📜 License

This repository is shared for **academic and research visibility** only.  
All rights to the EngageSight architecture, backend pipeline, and associated AWS infrastructure remain with **Francisco Hernández** and the **Chair of Ergonomics and Innovation Management, Technische Universität Chemnitz**.

You may **view, clone, and reference** this code for non-commercial purposes.  
Reproduction, distribution, or commercial use of the full EngageSight system (including backend and AI logic) requires **explicit written permission** from the author.

© 2025 Francisco Hernández. All rights reserved.