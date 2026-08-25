import os
import subprocess
from pathlib import Path

ROOT = "backend/kaggle_data/FakeAVCeleb_v1.2/FakeAVCeleb_v1.2"

REAL_DIR = "backend/kaggle_data/audio_dataset/real"
FAKE_DIR = "backend/kaggle_data/audio_dataset/fake"

os.makedirs(REAL_DIR, exist_ok=True)
os.makedirs(FAKE_DIR, exist_ok=True)

real_sources = [
    os.path.join(ROOT, "RealVideo-RealAudio"),
    os.path.join(ROOT, "FakeVideo-RealAudio"),
]

fake_sources = [
    os.path.join(ROOT, "RealVideo-FakeAudio"),
    os.path.join(ROOT, "FakeVideo-FakeAudio"),
]

def extract_audio(source_dirs, output_dir):
    count = 0

    for source in source_dirs:
        for mp4 in Path(source).rglob("*.mp4"):
            rel = mp4.relative_to(source)
            name = "_".join(rel.parts).replace(".mp4", ".wav")

            out_file = os.path.join(output_dir, name)

            if os.path.exists(out_file):
                continue

            cmd = [
                "ffmpeg",
                "-loglevel", "error",
                "-i", str(mp4),
                "-vn",
                "-ac", "1",
                "-ar", "16000",
                out_file
            ]

            subprocess.run(cmd)

            count += 1

            if count % 100 == 0:
                print(f"Processed {count} files")

    print(f"Finished {count} files")

print("Extracting REAL audio...")
extract_audio(real_sources, REAL_DIR)

print("Extracting FAKE audio...")
extract_audio(fake_sources, FAKE_DIR)

print("DONE")
