import cv2
import os

def process_video_to_frames(video_path, output_dir, sample_rate=15):
    """
    Extracts frames at a specific interval to capture motion 
    without overwhelming the disk.
    """
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    saved_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Save every 'sample_rate'-th frame
        if frame_id % sample_rate == 0:
            frame_name = f"{os.path.basename(video_path)}_f{frame_id}.jpg"
            cv2.imwrite(os.path.join(output_dir, frame_name), frame)
            saved_count += 1
            
        frame_id += 1
        
    cap.release()
    print(f"Extracted {saved_count} frames from {video_path}")