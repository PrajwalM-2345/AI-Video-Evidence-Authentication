import cv2
import numpy as np

def generate_synthetic_fake_video(output_path="test_fake_video.mp4"):
    # Video Specifications
    width, height = 640, 480
    fps = 24
    duration_seconds = 5
    total_frames = fps * duration_seconds
    
    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"🎬 Generating synthetic video: {total_frames} frames total...")
    
    # Define a window where we inject the "fake/tampered" anomalies
    tamper_start_frame = 40
    tamper_end_frame = 80

    for frame_idx in range(total_frames):
        # 1. Create a baseline clean background (gradient look)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            frame[i, :] = [int(50 + (i * 0.2)), 30, 30] # Soft dark red gradient
            
        # 2. Simulate a moving object (acting like a tracking target/face location)
        # The center moves across the screen over time
        center_x = int(100 + (frame_idx * 2.5))
        center_y = int(240 + np.sin(frame_idx * 0.1) * 50)
        radius = 60
        
        # Draw a clean white/green tracking reference sphere
        cv2.circle(frame, (center_x, center_y), radius, (150, 242, 16), -1)
        cv2.circle(frame, (center_x, center_y), radius - 10, (200, 255, 200), -1)
        
        # 3. CRITICAL: Inject Artificial "Deepfake / Forgery" Artifacts
        if tamper_start_frame <= frame_idx <= tamper_end_frame:
            # We simulate a bad face-swap bounding box error or blending anomaly
            box_w, box_h = 160, 160
            box_x = center_x - (box_w // 2)
            box_y = center_y - (box_h // 2)
            
            # Make sure it stays within frame limits
            box_x = max(0, min(box_x, width - box_w))
            box_y = max(0, min(box_y, height - box_h))
            
            # Inject a high-contrast inverted noise patch directly over our target
            # This completely disrupts localized pixel textures and breaks ViT patch math
            noise_patch = np.random.randint(0, 255, (box_h, box_w, 3), dtype=np.uint8)
            
            # Blend the noise heavily to mimic a dirty GAN/inpainting replacement boundary
            frame[box_y:box_y+box_h, box_x:box_x+box_w] = cv2.addWeighted(
                frame[box_y:box_y+box_h, box_x:box_x+box_w], 0.3, 
                noise_patch, 0.7, 0
            )
            
            # Add a slight blur to simulate an app trying to cover its tracks
            frame[box_y:box_y+box_h, box_x:box_x+box_w] = cv2.GaussianBlur(
                frame[box_y:box_y+box_h, box_x:box_x+box_w], (15, 15), 0
            )

        # Write frame to container
        out.write(frame)

    out.release()
    print(f"✅ Success! Generated tampered test video saved to: {output_path}")

if __name__ == "__main__":
    generate_synthetic_fake_video()