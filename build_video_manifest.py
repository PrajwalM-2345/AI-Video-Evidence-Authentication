from pathlib import Path
import json
import random
from collections import Counter

from train_video_temporal import discover


ROOTS = [
    Path("backend/kaggle_data/Celeb-DF-v2"),
    Path("backend/kaggle_data/FakeAVCeleb_v1.2"),
]

OUTPUT = Path("backend/kaggle_data/video_manifest_balanced.jsonl")

SEED = 42

# Use all authentic videos and the same number of tampered videos.
# This creates a balanced dataset.
MAX_PER_CLASS = None

VAL_RATIO = 0.15
TEST_RATIO = 0.15


def main():

    print("=" * 60)
    print("BUILDING BALANCED VIDEO MANIFEST")
    print("=" * 60)

    records = []

    for root in ROOTS:
        if root.exists():
            found = discover(root)
            print(f"{root}: {len(found)} labeled videos")
            records.extend(found)
        else:
            print(f"WARNING: missing {root}")

    # Remove duplicate paths
    unique = {}
    for r in records:
        unique[r["path"]] = r

    records = list(unique.values())

    authentic = [r for r in records if r["label"] == 0]
    tampered = [r for r in records if r["label"] == 1]

    print()
    print("Before balancing:")
    print("Authentic :", len(authentic))
    print("Tampered  :", len(tampered))

    # --------------------------------------------------------
    # BALANCE CLASSES
    # --------------------------------------------------------

    random.seed(SEED)

    n = min(len(authentic), len(tampered))

    if MAX_PER_CLASS is not None:
        n = min(n, MAX_PER_CLASS)

    random.shuffle(authentic)
    random.shuffle(tampered)

    authentic = authentic[:n]
    tampered = tampered[:n]

    print()
    print("After balancing:")
    print("Authentic :", len(authentic))
    print("Tampered  :", len(tampered))
    print("Total     :", len(authentic) + len(tampered))

    # --------------------------------------------------------
    # VIDEO-LEVEL SPLIT
    # --------------------------------------------------------

    def split_class(items):

        random.shuffle(items)

        total = len(items)

        n_test = int(total * TEST_RATIO)
        n_val = int(total * VAL_RATIO)

        test = items[:n_test]
        val = items[n_test:n_test + n_val]
        train = items[n_test + n_val:]

        return train, val, test

    train0, val0, test0 = split_class(authentic)
    train1, val1, test1 = split_class(tampered)

    train = train0 + train1
    val = val0 + val1
    test = test0 + test1

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    # --------------------------------------------------------
    # VERIFY NO PATH LEAKAGE
    # --------------------------------------------------------

    train_paths = {r["path"] for r in train}
    val_paths = {r["path"] for r in val}
    test_paths = {r["path"] for r in test}

    assert train_paths.isdisjoint(val_paths)
    assert train_paths.isdisjoint(test_paths)
    assert val_paths.isdisjoint(test_paths)

    # --------------------------------------------------------
    # WRITE MANIFEST
    # --------------------------------------------------------

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w") as f:

        for split_name, items in [
            ("train", train),
            ("val", val),
            ("test", test),
        ]:

            for r in items:

                row = {
                    "split": split_name,
                    "path": r["path"],
                    "label": r["label"],
                }

                f.write(json.dumps(row) + "\n")

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FINAL MANIFEST")
    print("=" * 60)

    for name, items in [
        ("TRAIN", train),
        ("VAL", val),
        ("TEST", test),
    ]:

        counts = Counter(r["label"] for r in items)

        print(
            f"{name:5s}: "
            f"total={len(items):5d} | "
            f"authentic={counts[0]:5d} | "
            f"tampered={counts[1]:5d}"
        )

    print()
    print("Total videos :", len(train) + len(val) + len(test))
    print("Output       :", OUTPUT)
    print("Seed         :", SEED)

    print()
    print("✓ Balanced")
    print("✓ Video-disjoint")
    print("✓ Train/validation/test splits created")


if __name__ == "__main__":
    main()
