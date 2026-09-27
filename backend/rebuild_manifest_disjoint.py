import json
import random
from pathlib import Path
from collections import defaultdict

MANIFEST = Path("kaggle_data/video_manifest_balanced.jsonl")
OUTPUT   = Path("kaggle_data/video_manifest_disjoint.jsonl")
SEED     = 42

random.seed(SEED)

def identity_of(path):
    for part in path.split("/"):
        if part.startswith("id") and len(part) > 2 and part[2:].isdigit():
            return part
    return "unknown_" + path.split("/")[-2] if "/" in path else "unknown"

records = []
with open(MANIFEST) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        r["identity"] = identity_of(r["path"])
        records.append(r)

print("Total records:", len(records))

# Group by identity
by_identity = defaultdict(list)
for r in records:
    by_identity[r["identity"]].append(r)

identities = sorted(by_identity.keys())
random.shuffle(identities)

n = len(identities)
n_test = int(0.15 * n)
n_val  = int(0.15 * n)
n_train = n - n_test - n_val

test_ids  = set(identities[:n_test])
val_ids   = set(identities[n_test:n_test + n_val])
train_ids = set(identities[n_test + n_val:])

print("Train identities:", len(train_ids))
print("Val identities  :", len(val_ids))
print("Test identities :", len(test_ids))
print("Overlap train/test:", len(train_ids & test_ids))

out_records = []
for r in records:
    if r["identity"] in test_ids:
        r["split"] = "test"
    elif r["identity"] in val_ids:
        r["split"] = "val"
    else:
        r["split"] = "train"
    r.pop("identity", None)
    out_records.append(r)

with open(OUTPUT, "w") as f:
    for r in out_records:
        f.write(json.dumps(r) + "\n")

# Report balance
def count(records, split):
    sub = [r for r in records if r["split"] == split]
    real = sum(1 for r in sub if r["label"] == 0)
    fake = sum(1 for r in sub if r["label"] == 1)
    return len(sub), real, fake

for split in ("train", "val", "test"):
    total, real, fake = count(out_records, split)
    print(f"{split}: {total} (real={real}, fake={fake})")

print("Wrote:", OUTPUT)
