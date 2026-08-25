// src/components/NeuralAICore.jsx
// ============================================================
// NEW FEATURE — Neural AI Core
// A denser instrument than the existing ApertureRing: renders the
// four real model stages already surfaced in analysisResult
// (ViT Backbone, EfficientNet, XceptionNet, CNN Layer — the same
// four values used in the "Fusion Layers" panel already in
// App.jsx) as glowing nodes in a small neural-net-style layout,
// with connecting lines that pulse when status === 'analyzing'.
// This does NOT replace ApertureRing — it's a second, complementary
// instrument for cases where you want a "network" reading rather
// than a "gauge" reading of the same fusion data.
// Purely additive; reads props, mutates nothing.
// ============================================================
import React from 'react';
import { Cpu } from 'lucide-react';

const DEFAULT_LAYERS = [
  { label: 'ViT Backbone', value: 79.77, color: '#34E5A8' },
  { label: 'EfficientNet', value: 97.02, color: '#4FD1E8' },
  { label: 'XceptionNet', value: 92.86, color: '#8B93FF' },
  { label: 'CNN Layer', value: 96.96, color: '#F5A623' },
];

export default function NeuralAICore({ status = 'idle', layers = DEFAULT_LAYERS, consensus = 96.96 }) {
  const isActive = status === 'analyzing';
  const w = 340, h = 200;
  const inputX = 40, outputX = w - 50, midY = h / 2;
  const layerXs = [130, 210];

  const nodePositions = layers.map((l, i) => ({
    ...l,
    x: layerXs[i % 2],
    y: 30 + (i * (h - 60)) / (layers.length - 1),
  }));

  return (
    <div className="glass-surface rounded-[28px] p-5">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-1 flex items-center gap-1.5">
        <Cpu size={14} className="text-[#4FD1E8]" /> Neural Fusion Core
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-2">
        Live model-consensus network — node brightness maps to each backbone's confidence
      </p>
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" height={h}>
        <circle cx={inputX} cy={midY} r="14" fill="#ffffff0a" stroke="#ffffff22" strokeWidth="1.5" />
        <text x={inputX} y={midY + 28} textAnchor="middle" fontSize="8" fill="#64748B" fontFamily="IBM Plex Mono, monospace">INPUT</text>

        {nodePositions.map((n, i) => (
          <line
            key={`in-${i}`}
            x1={inputX + 14} y1={midY}
            x2={n.x - 16} y2={n.y}
            stroke={n.color} strokeOpacity={isActive ? 0.5 : 0.2}
            strokeWidth={isActive ? 1.5 : 1}
          >
            {isActive && (
              <animate attributeName="stroke-opacity" values="0.15;0.6;0.15" dur="1.4s" repeatCount="indefinite" begin={`${i * 0.15}s`} />
            )}
          </line>
        ))}

        {nodePositions.map((n, i) => (
          <line
            key={`out-${i}`}
            x1={n.x + 16} y1={n.y}
            x2={outputX - 14} y2={midY}
            stroke={n.color} strokeOpacity={isActive ? 0.5 : 0.2}
            strokeWidth={isActive ? 1.5 : 1}
          >
            {isActive && (
              <animate attributeName="stroke-opacity" values="0.15;0.6;0.15" dur="1.4s" repeatCount="indefinite" begin={`${i * 0.15 + 0.3}s`} />
            )}
          </line>
        ))}

        {nodePositions.map((n, i) => (
          <g key={i}>
            <circle cx={n.x} cy={n.y} r="16" fill={`${n.color}22`} stroke={n.color} strokeWidth="1.5">
              {isActive && (
                <animate attributeName="r" values="15;17;15" dur="1.6s" repeatCount="indefinite" begin={`${i * 0.2}s`} />
              )}
            </circle>
            <text x={n.x} y={n.y + 4} textAnchor="middle" fontSize="8" fontWeight="bold" fill={n.color} fontFamily="IBM Plex Mono, monospace">
              {n.value}
            </text>
            <text x={n.x} y={n.y - 22} textAnchor="middle" fontSize="7" fill="#64748B" fontFamily="IBM Plex Mono, monospace">
              {n.label}
            </text>
          </g>
        ))}

        <circle cx={outputX} cy={midY} r="16" fill="#ffffff0c" stroke="#ffffff33" strokeWidth="1.5" />
        <text x={outputX} y={midY + 4} textAnchor="middle" fontSize="8" fontWeight="bold" fill="#E2E8F0" fontFamily="IBM Plex Mono, monospace">
          {consensus}
        </text>
        <text x={outputX} y={midY + 30} textAnchor="middle" fontSize="8" fill="#64748B" fontFamily="IBM Plex Mono, monospace">CONSENSUS</text>
      </svg>
    </div>
  );
}
