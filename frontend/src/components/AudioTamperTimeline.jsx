// src/components/AudioTamperTimeline.jsx
import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, ReferenceArea } from 'recharts';
import { Radio, TriangleAlert } from 'lucide-react';

function tierFor(probability) {
  if (probability >= 70) return { label: 'Tampered', color: '#FF4757' };
  if (probability >= 30) return { label: 'Suspicious', color: '#F5A623' };
  return { label: 'Normal', color: '#34E5A8' };
}

function normalizeSegments(audioTimeline) {
  if (!Array.isArray(audioTimeline)) return [];
  return audioTimeline.map((seg, idx) => {
    const probability =
      typeof seg.tamper_probability === 'number' ? seg.tamper_probability :
      typeof seg.confidence === 'number' ? seg.confidence :
      typeof seg.probability === 'number' ? seg.probability * (seg.probability <= 1 ? 100 : 1) :
      0;
    const timeSec =
      typeof seg.timestamp_seconds === 'number' ? seg.timestamp_seconds :
      typeof seg.timestamp === 'number' ? seg.timestamp :
      typeof seg.timestamp === 'string' ? parseFloat(seg.timestamp) : idx;
    return {
      idx,
      timeSec: Number.isFinite(timeSec) ? timeSec : idx,
      probability: Math.max(0, Math.min(100, probability)),
      status: seg.status || tierFor(probability).label,
    };
  }).sort((a, b) => a.timeSec - b.timeSec);
}

function SegmentTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;
  const tier = tierFor(d.probability);
  return (
    <div className="bg-[#0A0E16]/95 backdrop-blur-xl border border-white/10 rounded-xl px-3 py-2 shadow-2xl shadow-black/60">
      <p className="text-[10px] font-mono text-slate-400 tabular-nums">{d.timeSec.toFixed(1)} sec</p>
      <p className="text-xs font-mono font-bold mt-1 tabular-nums" style={{ color: tier.color }}>
        Tampering probability: {d.probability.toFixed(0)}%
      </p>
      <p className="text-[9px] font-mono uppercase tracking-wide mt-0.5" style={{ color: tier.color }}>{tier.label}</p>
    </div>
  );
}

export default function AudioTamperTimeline({ audioTimeline }) {
  const segments = useMemo(() => normalizeSegments(audioTimeline), [audioTimeline]);
  const flagged = useMemo(() => segments.filter((s) => s.probability >= 70), [segments]);

  if (!segments.length) {
    return (
      <div className="glass-surface rounded-[22px] p-6 text-center">
        <Radio size={18} className="text-slate-700 mx-auto mb-2" />
        <p className="text-[11px] font-mono text-slate-600 italic">No AASIST segment timeline returned for this audio evidence.</p>
      </div>
    );
  }

  return (
    <div className="glass-surface card-sheen rounded-[22px] p-5 space-y-3">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight flex items-center gap-1.5">
        <Radio size={14} className="text-[#F5A623]" /> AASIST Analysis Timeline
      </h3>

      <div className="flex items-center gap-3 text-[9px] font-mono text-slate-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#34E5A8]" /> Normal</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#F5A623]" /> Suspicious</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#FF4757]" /> Tampered</span>
      </div>

      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={segments} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
            <CartesianGrid stroke="#1B2130" strokeDasharray="3 3" vertical={false} />
            <ReferenceArea y1={70} y2={100} fill="#FF4757" fillOpacity={0.04} strokeOpacity={0} />
            <ReferenceArea y1={30} y2={70} fill="#F5A623" fillOpacity={0.03} strokeOpacity={0} />
            <ReferenceLine y={70} stroke="#FF4757" strokeDasharray="2 4" strokeOpacity={0.4} />
            <ReferenceLine y={30} stroke="#F5A623" strokeDasharray="2 4" strokeOpacity={0.4} />
            <XAxis dataKey="timeSec" stroke="#4A5568" fontSize={9} tickLine={false} axisLine={{ stroke: '#1B2130' }} tickFormatter={(v) => `${v.toFixed(1)}s`} minTickGap={30} />
            <YAxis domain={[0, 100]} stroke="#4A5568" fontSize={9} tickLine={false} axisLine={false} width={28} />
            <Tooltip content={<SegmentTooltip />} cursor={{ stroke: '#F5A623', strokeWidth: 1, strokeDasharray: '3 3' }} />
            <Line
              type="monotone"
              dataKey="probability"
              stroke="#F5A623"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload, index } = props;
                const tier = tierFor(payload.probability);
                return <circle key={`aseg-${index}`} cx={cx} cy={cy} r={3} fill={tier.color} stroke="#0A0E16" strokeWidth={1} />;
              }}
              activeDot={{ r: 5, fill: '#F5A623', stroke: '#0A0E16', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {segments.slice(0, 3).map((s) => {
          const tier = tierFor(s.probability);
          return (
            <div key={s.idx} className="bg-black/30 p-2 rounded-lg border border-white/[0.05] text-center">
              <span className="text-[9px] text-slate-500 font-mono block tabular-nums">{s.timeSec.toFixed(1)} sec</span>
              <span className="text-[11px] font-mono font-bold block tabular-nums" style={{ color: tier.color }}>{s.probability.toFixed(0)}%</span>
            </div>
          );
        })}
      </div>

      {flagged.length > 0 && (
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#FF4757] bg-[#FF4757]/[0.06] border border-[#FF4757]/20 rounded-xl px-3 py-2">
          <TriangleAlert size={12} className="flex-shrink-0" />
          <span className="tabular-nums">{flagged.length} segment{flagged.length !== 1 ? 's' : ''} above the 70% tamper threshold</span>
        </div>
      )}
    </div>
  );
}
