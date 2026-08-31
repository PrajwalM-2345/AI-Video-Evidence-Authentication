import base64
import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from .temporal_video_model import TemporalVideoEvidenceAI

TRANSFORM = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])


def _device():
    if torch.backends.mps.is_available(): return torch.device("mps")
    if torch.cuda.is_available(): return torch.device("cuda")
    return torch.device("cpu")


def load_temporal_model(path):
    dev=_device()
    model=TemporalVideoEvidenceAI(pretrained=False).to(dev)
    ckpt=torch.load(path,map_location=dev)
    state=ckpt.get("model",ckpt)
    model.load_state_dict(state,strict=True)
    model.eval()
    return model,dev


def _smooth(values, window=3):
    if len(values)<2:return values
    out=[]
    for i in range(len(values)):
        lo=max(0,i-window//2); hi=min(len(values),i+window//2+1)
        out.append(float(np.median(values[lo:hi])))
    return out


def _intervals(records, threshold=0.65, min_consecutive=2):
    intervals=[]; start=None; last=None; run=0
    for r in records:
        if r["tampering_probability"] >= threshold:
            run += 1
            if run == 1: start=r["timestamp_seconds"]
            last=r["timestamp_seconds"]
        else:
            if run >= min_consecutive:
                intervals.append({"start_seconds":start,"end_seconds":last})
            run=0; start=None; last=None
    if run >= min_consecutive:
        intervals.append({"start_seconds":start,"end_seconds":last})
    return intervals


def analyze_video(path, model, device, samples=48, threshold=0.65):
    cap=cv2.VideoCapture(path)
    if not cap.isOpened(): raise RuntimeError(f"Cannot open video: {path}")
    fps=float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    positions=np.linspace(0,max(0,total-1),min(samples,max(1,total))).astype(int)
    tensors=[]; originals=[]; times=[]
    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(pos)); ok,frame=cap.read()
        if not ok: continue
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        tensors.append(TRANSFORM(rgb)); originals.append(frame); times.append(pos/max(fps,1e-6))
    cap.release()
    if not tensors: raise RuntimeError("No decodable frames")

    x=torch.stack(tensors).unsqueeze(0).to(device)
    with torch.no_grad():
        vlogits, frame_logits=model(x)
        video_p=float(torch.softmax(vlogits,1)[0,1].cpu())
        frame_p=torch.softmax(frame_logits[0],1)[:,1].cpu().numpy().tolist()

    frame_p=_smooth(frame_p,3)
    timeline=[]
    for t,p,frame in zip(times,frame_p,originals):
        timeline.append({
            "frame_number":int(round(t*fps)),
            "timestamp":f"{t:.2f}s",
            "timestamp_seconds":round(float(t),3),
            "tampering_probability":round(float(p)*100,2),
            "status":"Tampered" if p>=threshold else "Original",
        })
    intervals=_intervals(timeline,threshold,min_consecutive=2)
    suspicious=[r for r in timeline if r["status"]=="Tampered"]
    gallery=[]
    ranked=sorted([(i,p) for i,p in enumerate(frame_p)], key=lambda z:z[1], reverse=True)
    for i,p in ranked[:10]:
        if p < threshold:
            break
        frame=originals[i]
        ok,buf=cv2.imencode(".jpg",cv2.resize(frame,(320,320)))
        if ok:
            b64=base64.b64encode(buf.tobytes()).decode("utf-8")
            gallery.append({"frame_id":int(round(times[i]*fps)),"timestamp":f"{times[i]:.2f}s","confidence":round(float(p)*100,2),"thumbnail_b64":b64,"original_frame_b64":b64})

    # Robust aggregate: a single anomalous frame cannot flip the whole video.
    pvals=np.array(frame_p,dtype=np.float32)
    robust=float(0.6*video_p + 0.4*np.percentile(pvals,75))
    if len(suspicious) < 2:
        robust=min(robust,0.49)
    verdict="Synthetic/Deepfake Tampering Detected" if robust>=threshold else "Authentic Match"
    confidence=(robust if verdict!="Authentic Match" else 1-robust)*100
    return {
        "verdict":verdict,
        "confidence":round(float(confidence),2),
        "tampering_probability":round(float(robust)*100,2),
        "timeline":timeline,
        "tampering_intervals":intervals,
        "gallery":gallery,
        "frame_statistics":{
            "total_frames":total,"evaluated_frames":len(timeline),
            "tampered_frames":len(suspicious),
            "original_frames":len(timeline)-len(suspicious),
            "tampering_ratio":round(100*len(suspicious)/max(1,len(timeline)),2),
        },
        "video_info":{"width":width,"height":height,"fps":round(fps,3),"duration_seconds":round(total/max(fps,1e-6),3)},
        "model":"TemporalVideoEvidenceAI / EfficientNet-B0 + temporal Transformer",
        "label_policy":"0=authentic/original, 1=tampered/fake",
    }
