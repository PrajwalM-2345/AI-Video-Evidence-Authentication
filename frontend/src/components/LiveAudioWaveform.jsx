// src/components/LiveAudioWaveform.jsx
import React, { useMemo, useState } from 'react';
import { AudioLines, Play, Pause } from 'lucide-react';

/**
 * Normalizes whatever shape waveform_points arrives in.
 * Accepts: array of numbers, or array of { amplitude, suspicious, timestamp }.
 */
function normalizePoints(waveformPoints) {
  if (!Array.isArray(waveformPoints)) return [];
  return waveformPoints.map((p, idx) => {
    if (typeof p === 'number') {
      return { idx, amplitude: Math.max(-1, Math.min(1, p)), suspicious: false, timestamp: null };
    }
    return {
      idx,
      amplitude: Math.max(-1, Math.min(1, p.amplitude ?? p.value ?? 0)),
      suspicious: Boolean(p.suspicious ?? p.is_suspicious ?? p.tampered),
      timestamp: p.timestamp ?? null,
    };
  });
}

export default function LiveAudioWaveform({ waveformPoints, durationSeconds, playing = false, onTogglePlay }) {
  const points = useMemo(() => normalizePoints(waveformPoints), [waveformPoints]);
  const [hoverIdx, setHoverIdx] = useState(null);

  if (!points.length) {
    return (
      <div className="glass-surface rounded-[22px] p-6 text-center">
        <AudioLines size={18} className="text-slate-700 mx-auto mb-2" />
        <p className="text-[11px] font-mono text-slate-600 italic">No waveform data returned for this audio evidence.</p>
      </div>
    );
  }

  const suspiciousCount = points.filter((p) => p.suspicious).length;
  const hovered = hoverIdx !== null ? points[hoverIdx] : null;

  return (
    <div className="glass-surface card-sheen rounded-[22px] p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight flex items-center gap-1.5">
          <AudioLines size={14} className="text-[#8B93FF]" /> Live Waveform
        </h3>
        <div className="flex items-center gap-2">
          {typeof durationSeconds === 'number' && (
            <span className="text-[10px] font-mono text-slate-500 tabular-nums">{durationSeconds.toFixed(1)}s</span>
          )}
          {onTogglePlay && (
            <button
              onClick={onTogglePlay}
              className="w-7 h-7 rounded-full bg-[#8B93FF]/10 hover:bg-[#8B93FF]/20 border border-[#8B93FF]/30 text-[#8B93FF] flex items-center justify-center transition-colors"
            >
              {playing ? <Pause size={11} /> : <Play size={11} className="ml-0.5" />}
            </button>
          )}
        </div>
      </div>

      <div
        className="relative h-24 flex items-center bg-black/30 rounded-xl border border-white/[0.05] px-2 overflow-hidden"
        onMouseLeave={() => setHoverIdx(null)}
      >
        <div className="ambient-glow opacity-30" />
        <div className="relative z-[1] w-full h-full flex items-center gap-[1.5px]">
          {points.map((p, i) => {
            const heightPct = Math.max(6, Math.abs(p.amplitude) * 100);
            const color = p.suspicious ? '#FF4757' : '#8B93FF';
            const isHovered = hoverIdx === i;
            return (
              <div
                key={i}
                onMouseEnter={() => setHoverIdx(i)}
                className="flex-1 min-w-[1px] rounded-full transition-all duration-150 cursor-pointer"
                style={{
                  height: `${heightPct}%`,
                  backgroundColor: color,
                  opacity: p.suspicious ? 0.85 : isHovered ? 0.9 : 0.5,
                  boxShadow: p.suspicious ? '0 0 6px -1px rgba(255,71,87,0.6)' : isHovered ? '0 0 6px -1px rgba(139,147,255,0.6)' : 'none',
                  transform: isHovered ? 'scaleY(1.08)' : 'scaleY(1)',
                }}
              />
            );
          })}
        </div>
        {playing && (
          <div className="absolute inset-y-0 w-px bg-[#4FD1E8] shadow-[0_0_8px_rgba(79,209,232,0.8)] pointer-events-none" style={{ left: '0%', animation: 'waveform-scan 4s linear infinite' }} />
        )}
      </div>

      <style>{`
        @keyframes waveform-scan {
          from { left: 0%; }
          to { left: 100%; }
        }
      `}</style>

      <div className="flex items-center justify-between text-[10px] font-mono">
        <span className="text-slate-500">
          {hovered
            ? <>Sample {hovered.idx} {hovered.timestamp !== null && `· ${hovered.timestamp}s`} · amp {hovered.amplitude.toFixed(2)}</>
            : `${points.length} samples analyzed`}
        </span>
        {suspiciousCount > 0 && (
          <span className="text-[#FF4757] font-semibold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF4757]" /> {suspiciousCount} suspicious region{suspiciousCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}
