// src/components/TimelineScrubber.jsx
// ============================================================
// NEW FEATURE — Timeline Scrubber
// An interactive, draggable scrubber over the REAL per-frame
// `timeline` array already returned in analysisResult (the same
// array the existing "Frame Timeline" list renders). Dragging the
// playhead selects a frame and shows its real frame_number,
// timestamp, and status — no synthetic frame data is introduced.
//
// Usage:
//   <TimelineScrubber timeline={analysisResult?.timeline} />
// ============================================================
import React, { useRef, useState, useMemo } from 'react';
import { Film, ChevronLeft, ChevronRight } from 'lucide-react';

export default function TimelineScrubber({ timeline = [] }) {
  const trackRef = useRef(null);
  const [index, setIndex] = useState(0);
  const [dragging, setDragging] = useState(false);

  const frames = timeline || [];
  const hasFrames = frames.length > 0;
  const clampedIndex = Math.min(index, Math.max(frames.length - 1, 0));
  const current = hasFrames ? frames[clampedIndex] : null;

  const tamperedRanges = useMemo(() => {
    if (!hasFrames) return [];
    const ranges = [];
    let start = null;
    frames.forEach((f, i) => {
      const isTampered = f.status === 'Tampered';
      if (isTampered && start === null) start = i;
      if (!isTampered && start !== null) { ranges.push([start, i - 1]); start = null; }
    });
    if (start !== null) ranges.push([start, frames.length - 1]);
    return ranges;
  }, [frames, hasFrames]);

  const setFromClientX = (clientX) => {
    const track = trackRef.current;
    if (!track || !hasFrames) return;
    const rect = track.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    setIndex(Math.round(pct * (frames.length - 1)));
  };

  const onPointerDown = (e) => { setDragging(true); setFromClientX(e.clientX); };
  const onPointerMove = (e) => { if (dragging) setFromClientX(e.clientX); };
  const onPointerUp = () => setDragging(false);

  if (!hasFrames) {
    return (
      <div className="glass-surface rounded-[22px] p-4">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5 uppercase font-mono tracking-wide mb-2">
          <Film size={13} className="text-[#4FD1E8]" /> Timeline Scrubber
        </span>
        <div className="text-center text-[11px] font-mono text-slate-600 py-8 italic">
          No frame timeline yet. Run a video audit to enable scrubbing.
        </div>
      </div>
    );
  }

  const playheadPct = (clampedIndex / Math.max(frames.length - 1, 1)) * 100;

  return (
    <div className="glass-surface rounded-[22px] p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5 uppercase font-mono tracking-wide">
          <Film size={13} className="text-[#4FD1E8]" /> Timeline Scrubber
        </span>
        <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-lg ${current?.status === 'Tampered' ? 'bg-[#FF4757]/10 text-[#FF4757]' : 'bg-[#34E5A8]/10 text-[#34E5A8]'}`}>
          {current?.status}
        </span>
      </div>

      <div
        ref={trackRef}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
        className="relative h-8 rounded-xl bg-black/30 border border-white/[0.06] cursor-pointer select-none"
      >
        {tamperedRanges.map(([s, e], i) => (
          <div
            key={i}
            className="absolute top-0 bottom-0 bg-[#FF4757]/25"
            style={{
              left: `${(s / Math.max(frames.length - 1, 1)) * 100}%`,
              width: `${((e - s + 1) / Math.max(frames.length - 1, 1)) * 100}%`,
            }}
          />
        ))}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]"
          style={{ left: `${playheadPct}%` }}
        />
        <div
          className="absolute -top-1 w-3 h-3 rounded-full bg-white border-2 border-[#34E5A8] shadow-lg"
          style={{ left: `calc(${playheadPct}% - 6px)` }}
        />
      </div>

      <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
        <button onClick={() => setIndex((i) => Math.max(0, i - 1))} className="flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-white/[0.05] transition-colors">
          <ChevronLeft size={12} /> Prev
        </button>
        <span className="tabular-nums text-slate-300">
          Frame {current?.frame_number} · {current?.timestamp}
        </span>
        <button onClick={() => setIndex((i) => Math.min(frames.length - 1, i + 1))} className="flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-white/[0.05] transition-colors">
          Next <ChevronRight size={12} />
        </button>
      </div>
    </div>
  );
}
