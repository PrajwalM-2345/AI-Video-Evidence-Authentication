// src/components/EnhancedHeatmap.jsx
// ============================================================
// NEW FEATURE — Enhanced Heatmap
// An upgrade layer over the existing single-row ThreatHeatmap
// strip already in App.jsx (which this file does NOT modify or
// remove). This adds a second, richer 2D read of the SAME real
// `timeline` array: frames bucketed into a grid with a hover
// tooltip showing exact frame_number / timestamp / status, plus
// a running tampered-density sparkline beneath it. No fabricated
// per-frame values — buckets simply group the real frame objects
// already returned by the backend.
//
// Usage — render this ALONGSIDE the existing <ThreatHeatmap />,
// not instead of it:
//   <ThreatHeatmap timeline={analysisResult?.timeline} />
//   <EnhancedHeatmap timeline={analysisResult?.timeline} />
// ============================================================
import React, { useMemo, useState } from 'react';
import { Grid3x3 } from 'lucide-react';

const COLS = 20;

export default function EnhancedHeatmap({ timeline = [] }) {
  const [hovered, setHovered] = useState(null);
  const frames = timeline || [];

  const rows = useMemo(() => {
    if (frames.length === 0) return [];
    const rowCount = Math.ceil(frames.length / COLS);
    const grid = [];
    for (let r = 0; r < rowCount; r++) {
      grid.push(frames.slice(r * COLS, r * COLS + COLS));
    }
    return grid;
  }, [frames]);

  const densityByRow = useMemo(
    () => rows.map((row) => row.filter((f) => f.status === 'Tampered').length / Math.max(row.length, 1)),
    [rows]
  );

  if (frames.length === 0) {
    return (
      <div className="glass-surface rounded-[28px] p-5">
        <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-2 flex items-center gap-1.5">
          <Grid3x3 size={14} className="text-[#FF4757]" /> Enhanced Confidence Grid
        </h3>
        <div className="text-center text-[11px] font-mono text-slate-600 py-8 italic">
          No frame data yet. Run a video audit to populate this grid.
        </div>
      </div>
    );
  }

  return (
    <div className="glass-surface rounded-[28px] p-5">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-1 flex items-center gap-1.5">
        <Grid3x3 size={14} className="text-[#FF4757]" /> Enhanced Confidence Grid
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-3">
        Same frame data as the heatmap strip, gridded {COLS}-wide with hover detail and per-row density
      </p>

      <div className="space-y-1">
        {rows.map((row, r) => (
          <div key={r} className="flex items-center gap-1.5">
            <div className="flex gap-[2px] flex-1">
              {row.map((frame, c) => {
                const isTampered = frame.status === 'Tampered';
                const isHovered = hovered && hovered.frame_number === frame.frame_number;
                return (
                  <div
                    key={c}
                    onMouseEnter={() => setHovered(frame)}
                    onMouseLeave={() => setHovered(null)}
                    className="flex-1 aspect-square rounded-[3px] cursor-pointer transition-transform"
                    style={{
                      backgroundColor: isTampered ? '#FF4757' : '#34E5A8',
                      opacity: isTampered ? 0.65 : 0.35,
                      transform: isHovered ? 'scale(1.4)' : 'scale(1)',
                      outline: isHovered ? '1px solid white' : 'none',
                    }}
                  />
                );
              })}
            </div>
            <div className="w-14 h-2.5 rounded-full bg-black/30 overflow-hidden flex-shrink-0">
              <div
                className="h-full bg-[#FF4757]"
                style={{ width: `${densityByRow[r] * 100}%`, opacity: 0.7 }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 pt-3 border-t border-white/[0.05] min-h-[32px] flex items-center">
        {hovered ? (
          <span className="text-[11px] font-mono text-slate-300">
            Frame <span className="tabular-nums text-white font-bold">{hovered.frame_number}</span> · {hovered.timestamp} ·{' '}
            <span className={hovered.status === 'Tampered' ? 'text-[#FF4757]' : 'text-[#34E5A8]'}>{hovered.status}</span>
          </span>
        ) : (
          <span className="text-[10px] font-mono text-slate-600 italic">Hover a cell for exact frame detail</span>
        )}
      </div>
    </div>
  );
}
