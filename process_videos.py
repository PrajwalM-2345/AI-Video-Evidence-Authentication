# process_videos.py
import os
import cv2

def extract_frames_from_videos(source_dir, target_base_dir, sample_rate_fps=1):
    """
    Scans a source directory for videos, determines if they are 'authentic' or 'fake' 
    based on the folder paths, and extracts frames directly into the training structure.
    
    Args:
        source_dir (str): Path where your raw downloaded video datasets are stored.
        target_base_dir (str): Path to 'kaggle_data/train'
        sample_rate_fps (int): How many frames to extract per second of video.
    """
    # Define standard targets
    authentic_target = os.path.join(target_base_dir, "authentic")
    fake_target = os.path.join(target_base_dir, "fake")
    
    os.makedirs(authentic_target, exist_ok=True)
    os.makedirs(fake_target, exist_ok=True)
    
    video_extensions = (".mp4", ".avi", ".mov", ".mkv")
    
    print("🚀 Starting Video Frame Extraction Pipeline...")
    
    # Walk through all directories in the source video folder
    for root, _, files in os.walk(source_dir):
        # Determine label based on directory naming conventions
        root_lower = root.lower()
        if "fake" in root_lower or "forgery" in root_lower or "manipulated" in root_lower:
            current_target = fake_target
            label = "fake"
        elif "real" in root_lower or "authentic" in root_lower or "original" in root_lower:
            current_target = authentic_target
            label = "authentic"
        else:
            # Default fallback if folder name is ambiguous
            current_target = authentic_target
            label = "authentic"

        for file in files:
            if file.lower().endswith(video_extensions):
                video_path = os.path.join(root, file)
                print(f"🎬 Processing [{label.upper()}]: {video_path}")
                
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print(f"❌ Failed to open video: {video_path}")
                    continue
                
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0:
                    fps = 30  # Fallback standard
                
                # Calculate frame interval (e.g., if fps=30 and sample_rate=1, interval=30 frames)
                frame_interval = max(1, int(fps / sample_rate_fps))
                
                frame_count = 0
                extracted_count = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % frame_interval == 0:
                        # Clean filename prefix to prevent cross-dataset overwrites
                        dataset_prefix = os.path.basename(os.path.dirname(video_path))
                        clean_name = f"{dataset_prefix}_{os.path.splitext(file)[0]}_frame_{frame_count}.jpg"
                        output_path = os.path.join(current_target, clean_name)
                        
                        # Save frame
                        cv2.imwrite(output_path, frame)
                        extracted_count += 1
                        
                    frame_count += 1
                
                cap.release()
                print(f"✅ Extracted {extracted_count} frames.")

if __name__ == "__main__":
    # 1. Place your raw downloaded video folders inside 'kaggle_data/raw_videos/'
    # 2. Run this script: python3 process_videos.py
    
    SOURCE_VIDEOS = "kaggle_data/raw_videos"
    TARGET_TRAIN = "kaggle_data/train"
    
    if not os.path.exists(SOURCE_VIDEOS):
        os.makedirs(SOURCE_VIDEOS, exist_ok=True)
        print(f"📁 Created directory: '{SOURCE_VIDEOS}'. Place your raw video datasets inside it and rerun.")
    else:
        extract_frames_from_videos(
            source_dir=SOURCE_VIDEOS, 
            target_base_dir=TARGET_TRAIN, 
            sample_rate_fps=1
        )