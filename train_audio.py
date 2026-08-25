from pathlib import Path
from sklearn.model_selection import train_test_split

REAL_DIR = "backend/kaggle_data/audio_dataset/real"
FAKE_DIR = "backend/kaggle_data/audio_dataset/fake"

real_files = list(Path(REAL_DIR).glob("*.wav"))
fake_files = list(Path(FAKE_DIR).glob("*.wav"))

files = real_files + fake_files
labels = [1] * len(real_files) + [0] * len(fake_files)

train_files, val_files, train_labels, val_labels = train_test_split(
files,
labels,
test_size=0.2,
random_state=42,
stratify=labels
)

print("=" * 60)
print("AUDIO DATASET SUMMARY")
print("=" * 60)

print(f"Real Audio Files : {len(real_files)}")
print(f"Fake Audio Files : {len(fake_files)}")
print(f"Total Files      : {len(files)}")

print()

print(f"Train Files      : {len(train_files)}")
print(f"Validation Files : {len(val_files)}")

print()

print(f"Train Real       : {sum(train_labels)}")
print(f"Train Fake       : {len(train_labels) - sum(train_labels)}")

print()

print(f"Val Real         : {sum(val_labels)}")
print(f"Val Fake         : {len(val_labels) - sum(val_labels)}")

print("=" * 60)
from pathlib import Path
from sklearn.model_selection import train_test_split

REAL_DIR = "backend/kaggle_data/audio_dataset/real"
FAKE_DIR = "backend/kaggle_data/audio_dataset/fake"

real_files = list(Path(REAL_DIR).glob("*.wav"))
fake_files = list(Path(FAKE_DIR).glob("*.wav"))

files = real_files + fake_files
labels = [1] * len(real_files) + [0] * len(fake_files)

train_files, val_files, train_labels, val_labels = train_test_split(
files,
labels,
test_size=0.2,
random_state=42,
stratify=labels
)

print("=" * 60)
print("AUDIO DATASET SUMMARY")
print("=" * 60)

print(f"Real Audio Files : {len(real_files)}")
print(f"Fake Audio Files : {len(fake_files)}")
print(f"Total Files      : {len(files)}")

print()

print(f"Train Files      : {len(train_files)}")
print(f"Validation Files : {len(val_files)}")

print()

print(f"Train Real       : {sum(train_labels)}")
print(f"Train Fake       : {len(train_labels) - sum(train_labels)}")

print()

print(f"Val Real         : {sum(val_labels)}")
print(f"Val Fake         : {len(val_labels) - sum(val_labels)}")

print("=" * 60)

