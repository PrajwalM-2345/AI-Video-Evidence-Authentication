// ModalityGauges.jsx — additive component, no existing code modified
import React from 'react';
import { Film, Music, Image as ImageIcon } from 'lucide-react';

function Gauge({ label, value = 0, color = '#34E5A8', Icon }) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  const radius = 26;
  const circ = 2 * Math.PI * radius;
  const offset = circ * (1 - v / 100);

  return (
    <div className="flex flex-col items-center gap-1 flex-1">
      <div className="relative" style={{ width: 70, height: 70 }}>
        <svg width={70} height={70} viewBox="0 0 70 70">
          <circle
            cx={35}
            cy={35}
            r={radius}
            fill="none"
            stroke="#1B2130"
            strokeWidth={5}
          />
          <circle
            cx={35}
            cy={35}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={5}
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            transform="rotate(-90 35 35)"
            style={{ transition: 'stroke-dashoffset 0.5s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {Icon && <Icon size={10} style={{ color }} />}
          <span
            className="text-[13px] font-display font-bold tabular-nums"
            style={{ color }}
          >
            {Math.round(v)}%
          </span>
        </div>
      </div>
      <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wide">
        {label}
      </span>
    </div>
  );
}

export default function ModalityGauges({
  videoConfidence,
  audioConfidence,
  imageConfidence,
  verdictIsFake,
}) {
  const hasAny =
    videoConfidence !== undefined ||
    audioConfidence !== undefined ||
    imageConfidence !== undefined;

  if (!hasAny) return null;

  const baseColor = verdictIsFake ? '#FF4757' : '#34E5A8';

  return (
    <div className="glass-surface rounded-[22px] p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono uppercase tracking-[0.2em] text-slate-500">
          Modality Consensus
        </span>
        <span
          className="text-[9px] font-mono"
          style={{ color: baseColor }}
        >
          {verdictIsFake ? 'FLAGGED' : 'CLEAR'}
        </span>
      </div>
      <div className="flex items-center justify-around">
        <Gauge label="Video" value={videoConfidence} color={baseColor} Icon={Film} />
        <Gauge label="Audio" value={audioConfidence} color={baseColor} Icon={Music} />
        <Gauge label="Image" value={imageConfidence} color={baseColor} Icon={ImageIcon} />
      </div>
    </div>
  );
}
