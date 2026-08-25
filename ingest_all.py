import os
import zipfile
import shutil
import random

# Ensure all 8 are mapped correctly
DATASETS = {
    "real-and-fake-face-detection": "ciplab/real-and-fake-face-detection",
    "celeb-df": "yuezunli/celeb-df",
    "dfdc": "metadefense/dfdc-preview",
    # ... add remaining slugs here
}

def connect_datasets():
    base_dir = "kaggle_data"
    for name, slug in DATASETS.items():
        zip_path = os.path.join(base_dir, f"{name}.zip")
        
        if not os.path.exists(zip_path):
            print(f"⚠️ Missing {name}.zip. Please download manually and place in kaggle_data/")
            continue
            
        print(f"🔗 Connecting {name} to pipeline...")
        # Extract and move files to standard /train and /test folders
        # [Your existing logic here]
        print(f"✅ {name} connected.")

if __name__ == "__main__":
    connect_datasets()