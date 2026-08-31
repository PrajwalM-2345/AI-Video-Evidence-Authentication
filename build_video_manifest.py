from pathlib import Path
import json
from train_video_temporal import discover

ROOTS=[Path("backend/kaggle_data/Celeb-DF-v2"),Path("backend/kaggle_data/FakeAVCeleb_v1.2")]
out=Path("backend/kaggle_data/video_manifest_all.jsonl")
records=[]
for root in ROOTS:
    if root.exists():
        found=discover(root); print(root,len(found)); records.extend(found)
seen=set(); unique=[]
for r in records:
    if r['path'] not in seen: seen.add(r['path']); unique.append(r)
with out.open('w') as f:
    for r in unique: f.write(json.dumps(r)+'\n')
print('TOTAL',len(unique))
print('AUTHENTIC',sum(r['label']==0 for r in unique))
print('TAMPERED',sum(r['label']==1 for r in unique))
print(out)
