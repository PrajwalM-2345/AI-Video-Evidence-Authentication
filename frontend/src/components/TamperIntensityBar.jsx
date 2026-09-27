// TamperIntensityBar.jsx — additive component, no existing code modified
import React, { useMemo } from 'react';
import { Activity } from 'lucide-react';

export default function TamperIntensityBar({ timeline = [], height = 14, accent = '#FF4757' }) {
  const bars = useMemo(() => {
    if (!Array.isArray(timeline) || timeline.length === 0) return [];
    return timeline.map((t) => {
      const p = Number(t.tampering_probability ?? t.probability ?? 0);
      let color = '#34E5A8';
      if (p >= 70) color = '#FF4757';
      else if (p >= 40) color = '#F5A623';
      return { p: Math.max(0, Math.min(100, p)), color };
    });
  }, [timeline]);

  if (bars.length === 0) return null;

  return (
    <div className="glass-surface rounded-2xl p-3 mt-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-slate-500 flex items-center gap-1.5">
          <Activity size={11} className="text-[#FF4757]" />
          Temporal Intensity Map
        </span>
        <span className="text-[9px] font-mono text-slate-600">
          {bars.length} samples · red = high · green = low
        </span>
      </div>
      <div
        className="relative w-full rounded-md overflow-hidden border border-white/[0.05] bg-black/40"
        style={{ height }}
      >
        <div className="absolute inset-0 flex">
          {bars.map((b, i) => (
            <div
              key={i}
              className="flex-1 h-full"
              style={{
                backgroundColor: b.color,
                opacity: 0.35 + (b.p / 100) * 0.65,
                boxShadow: b.p >= 70 ? `inset 0 0 8px ${accent}80` : 'none',
                transition: 'opacity 0.2s',
              }}
              title={`Sample ${i} · ${b.p.toFixed(1)}%`}
            />
          ))}
        </div>
        <div className="absolute inset-0 flex pointer-events-none">
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={i}
              className="flex-1 border-r"
              style={{ borderColor: 'rgba(255,255,255,0.04)' }}
            />
          ))}
        </div>
      </div>
      <div className="flex items-center gap-3 mt-2 text-[9px] font-mono">
        <span className="flex items-center gap-1 text-slate-500">
          <span className="w-2 h-2 rounded-sm bg-[#34E5A8]" /> Safe (&lt;40%)
        </span>
        <span className="flex items-center gap-1 text-slate-500">
          <span className="w-2 h-2 rounded-sm bg-[#F5A623]" /> Warn (40-70%)
        </span>
        <span className="flex items-center gap-1 text-slate-500">
          <span className="w-2 h-2 rounded-sm bg-[#FF4757]" /> Tampered (&gt;70%)
        </span>
      </div>
    </div>
  );
}
