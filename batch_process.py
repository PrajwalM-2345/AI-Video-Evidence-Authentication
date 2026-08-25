import os
import sys
import asyncio
from io import BytesIO
# batch_process.py
from backend.database import SessionLocal
from backend.services import run_forensic_analysis

async def process_all():
    db = SessionLocal()
    for filename in os.listdir(DATASET_PATH):
        with open(os.path.join(DATASET_PATH, filename), "rb") as f:
            await run_forensic_analysis(f.read(), filename, db)
    db.close()

if __name__ == "__main__":
    asyncio.run(process_all())

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.main import verify_video

# 1. Create a helper to satisfy FastAPI's UploadFile interface
class MockUploadFile:
    def __init__(self, filename, file_content):
        self.filename = filename
        self.file = BytesIO(file_content)
    async def read(self):
        return self.file.read()

DATASET_PATH = "/Users/prajwalm/Desktop/AI-Video-Evidence-Authentication/kaggle_data/test"

def batch_process():
    db = SessionLocal()
    # Ensure folders exist
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Path not found: {DATASET_PATH}")
        return

    files = [f for f in os.listdir(DATASET_PATH) if f.endswith((".mp4", ".mov", ".avi", ".mkv"))]
    print(f"🚀 Found {len(files)} files. Starting batch analysis...")
    
    for filename in files:
        file_path = os.path.join(DATASET_PATH, filename)
        print(f"🔍 Analyzing: {filename}")
        
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                # Create the mock
                upload_file = MockUploadFile(filename=filename, file_content=content)
                
                # Execute the async verify_video
                asyncio.run(verify_video(file=upload_file, db=db))
                
            print(f"✅ Successfully processed: {filename}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    db.close()
    print("✨ Batch processing complete.")

if __name__ == "__main__":
    batch_process()