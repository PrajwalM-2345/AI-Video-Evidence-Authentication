import os, sys, time
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

print("STEP 1: importing torch", flush=True)
import torch
print("  torch version:", torch.__version__, flush=True)
print("  mps available:", torch.backends.mps.is_available(), flush=True)
print("  cuda available:", torch.cuda.is_available(), flush=True)

print("STEP 2: checking dataset paths", flush=True)
from pathlib import Path
REAL_DIR = Path("backend/kaggle_data/audio_dataset/real")
FAKE_DIR = Path("backend/kaggle_data/audio_dataset/fake")
print("  REAL_DIR exists:", REAL_DIR.exists(), flush=True)
print("  FAKE_DIR exists:", FAKE_DIR.exists(), flush=True)
if REAL_DIR.exists():
    real_files = sorted(REAL_DIR.glob("*.wav"))
    print("  real .wav count:", len(real_files), flush=True)
if FAKE_DIR.exists():
    fake_files = sorted(FAKE_DIR.glob("*.wav"))
    print("  fake .wav count:", len(fake_files), flush=True)

print("STEP 3: reading one real audio file", flush=True)
import soundfile as sf
if REAL_DIR.exists() and len(real_files) > 0:
    t0 = time.time()
    wav, sr = sf.read(str(real_files[0]))
    print(f"  read ok, shape={wav.shape}, sr={sr}, took {time.time()-t0:.2f}s", flush=True)

print("STEP 4: checking model files", flush=True)
CONFIG_PATH = "backend/aasist/config/AASIST.conf"
PRETRAINED_MODEL = "backend/aasist/models/weights/AASIST.pth"
print("  config exists:", os.path.exists(CONFIG_PATH), flush=True)
print("  weights exist:", os.path.exists(PRETRAINED_MODEL), flush=True)
if os.path.exists(PRETRAINED_MODEL):
    print("  weights size (MB):", os.path.getsize(PRETRAINED_MODEL) / 1e6, flush=True)

print("STEP 5: loading pretrained weights to CPU", flush=True)
if os.path.exists(PRETRAINED_MODEL):
    t0 = time.time()
    state = torch.load(PRETRAINED_MODEL, map_location="cpu")
    print(f"  loaded ok, took {time.time()-t0:.2f}s", flush=True)

print("STEP 6: building model on CPU", flush=True)
sys.path.append("backend/aasist")
if os.path.exists(CONFIG_PATH):
    import json
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
    from models.AASIST import Model
    t0 = time.time()
    model = Model(cfg["model_config"]).to("cpu")
    print(f"  model built, took {time.time()-t0:.2f}s", flush=True)
    if os.path.exists(PRETRAINED_MODEL):
        model.load_state_dict(state)
        print("  state_dict loaded ok", flush=True)

print("STEP 7: one forward pass on CPU with dummy input", flush=True)
if 'model' in dir():
    model.eval()
    dummy = torch.zeros(2, 64600, dtype=torch.float32)
    t0 = time.time()
    with torch.no_grad():
        _, out = model(dummy)
    print(f"  forward pass ok, took {time.time()-t0:.2f}s, output shape={out.shape}", flush=True)

print("ALL STEPS COMPLETED — no hang found in isolated steps", flush=True)


