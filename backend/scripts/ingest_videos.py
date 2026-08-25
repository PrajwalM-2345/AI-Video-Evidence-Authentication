import cv2
import os
import shutil

# Directories
SOURCE_VIDEO_DIR = "kaggle_data/raw_videos" # Put your downloaded videos here
TARGET_DIR = "kaggle_data/train"

def ingest_video_dataset(dataset_name, label):
    # label = "authentic" or "fake"
    target_path = os.path.join(TARGET_DIR, label)
    os.makedirs(target_path, exist_ok=True)
    
    source_path = os.path.join(SOURCE_VIDEO_DIR, dataset_name)
    
    for video_file in os.listdir(source_path):
        if video_file.endswith((".mp4", ".avi", ".mov")):
            print(f"🎥 Processing: {video_file}")
            # Extraction logic: get 1 frame per second
            cap = cv2.VideoCapture(os.path.join(source_path, video_file))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_id = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                if frame_id % int(fps) == 0:
                    cv2.imwrite(f"{target_path}/{video_file}_{frame_id}.jpg", frame)
                frame_id += 1
            cap.release()

# Usage
# ingest_video_dataset("celeb_df_fake", "fake")