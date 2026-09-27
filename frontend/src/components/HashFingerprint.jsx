// HashFingerprint.jsx — additive component, no existing code modified
import React, { useMemo } from 'react';
import { Fingerprint } from 'lucide-react';

function hashToBytes(hash) {
  if (!hash || typeof hash !== 'string') return [];
  const clean = hash.replace(/^0x/, '');
  const bytes = [];
  for (let i = 0; i < Math.min(clean.length, 64); i += 2) {
    const b = parseInt(clean.substr(i, 2), 16);
    if (!Number.isNaN(b)) bytes.push(b);
  }
  return bytes;
}

export default function HashFingerprint({ hash = '', size = 120, accent = '#34E5A8' }) {
  const bytes = useMemo(() => hashToBytes(hash), [hash]);

  const rings = useMemo(() => {
    if (bytes.length === 0) return [];
    const groups = [8, 12, 16, 20];
    let cursor = 0;
    return groups.map((count, gi) => {
      const rad = 14 + gi * 12;
      const arc = (Math.PI * 2) / count;
      const items = [];
      for (let i = 0; i < count; i++) {
        const b = bytes[(cursor + i) % bytes.length];
        const angle = i * arc;
        const x = size / 2 + Math.cos(angle) * rad;
        const y = size / 2 + Math.sin(angle) * rad;
        const intensity = b / 255;
        items.push({ x, y, intensity, angle, dist: rad, i });
      }
      cursor += count;
      return items;
    });
  }, [bytes, size]);

  if (!hash) return null;

  const shortHash = hash.replace(/^0x/, '').substring(0, 20);

  return (
    <div className="glass-surface rounded-[22px] p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono uppercase tracking-[0.2em] text-slate-500 flex items-center gap-1.5">
          <Fingerprint size={12} className="text-[#8B93FF]" /> Evidence Fingerprint
        </span>
        <span className="text-[9px] font-mono text-slate-600">SHA-256</span>
      </div>

      <div className="flex justify-center">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle cx={size / 2} cy={size / 2} r={4} fill={accent} opacity={0.8} />

          {rings.map((ring, ri) =>
            ring.map((p, pi) => (
              <circle
                key={`${ri}-${pi}`}
                cx={p.x}
                cy={p.y}
                r={1 + p.intensity * 2.2}
                fill={accent}
                opacity={0.25 + p.intensity * 0.75}
              />
            ))
          )}

          {rings.map((ring, ri) => (
            <circle
              key={`line-${ri}`}
              cx={size / 2}
              cy={size / 2}
              r={14 + ri * 12}
              fill="none"
              stroke={accent}
              strokeOpacity={0.08}
              strokeWidth={1}
              strokeDasharray="2 4"
            />
          ))}
        </svg>
      </div>

      <div className="text-center">
        <div className="text-[10px] font-mono text-slate-500 break-all px-2">
          {shortHash}
          {hash.length > 22 && '…'}
        </div>
      </div>
    </div>
  );
}
