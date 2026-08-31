// src/components/VideoTamperTimeline.jsx
import React, { useMemo, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, ReferenceArea, Dot } from 'recharts';
import { ZoomIn, ZoomOut, RotateCcw, Film, TriangleAlert } from 'lucide-react';

function tierFor(probability) {
  if (probability >= 70) return { label: 'Tampered', color: '#FF4757' };
  if (probability >= 30) return { label: 'Suspicious', color: '#F5A623' };
  return { label: 'Authentic', color: '#34E5A8' };
}

function normalizeFrames(timeline) {
  if (!Array.isArray(timeline)) return [];
  return timeline
    .map((f, idx) => {
      const probability =
        typeof f.tamper_probability === 'number' ? f.tamper_probability :
        typeof f.confidence === 'number' ? f.confidence :
        typeof f.probability === 'number' ? f.probability * 100 :
        f.status === 'Tampered' ? 85 : 8;
      return {
        idx,
        frame: f.frame_number ?? f.frame_id ?? idx,
        timestamp: f.timestamp ?? '',
        probability: Math.max(0, Math.min(100, probability)),
        status: f.status || tierFor(probability).label,
      };
    })
    .sort((a, b) => a.idx - b.idx);
}

function TamperTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;
  const tier = tierFor(d.probability);
  return (
    <div className="bg-[#0A0E16]/95 backdrop-blur-xl border border-white/10 rounded-xl px-3 py-2 shadow-2xl shadow-black/60">
      <p className="text-[10px] font-mono text-slate-400 tabular-nums">Frame {d.frame} {d.timestamp && `· ${d.timestamp}`}</p>
      <p className="text-xs font-mono font-bold mt-1 tabular-nums" style={{ color: tier.color }}>
        {d.probability.toFixed(1)}% tamper probability
      </p>
      <p className="text-[9px] font-mono uppercase tracking-wide mt-0.5" style={{ color: tier.color }}>{tier.label}</p>
    </div>
  );
}

const ZOOM_STEPS = [1, 2, 4, 8];

export default function VideoTamperTimeline({ timeline, chartData }) {
  const frames = useMemo(() => {
    const fromTimeline = normalizeFrames(timeline);
    if (fromTimeline.length) return fromTimeline;
    if (Array.isArray(chartData) && chartData.length) {
      return chartData.map((c, idx) => ({
        idx,
        frame: c.frame ?? idx,
        timestamp: '',
        probability: Math.max(0, Math.min(100, (c.probability ?? 0) * (c.probability <= 1 ? 100 : 1))),
        status: tierFor(c.probability ?? 0).label,
      }));
    }
    return [];
  }, [timeline, chartData]);

  const [zoomIdx, setZoomIdx] = useState(0);
  const zoom = ZOOM_STEPS[zoomIdx];
  const [windowStart, setWindowStart] = useState(0);

  const visibleFrames = useMemo(() => {
    if (zoom === 1 || frames.length === 0) return frames;
    const windowSize = Math.max(4, Math.ceil(frames.length / zoom));
    const clampedStart = Math.min(windowStart, Math.max(0, frames.length - windowSize));
    return frames.slice(clampedStart, clampedStart + windowSize);
  }, [frames, zoom, windowStart]);

  const suspiciousFrames = useMemo(() => frames.filter((f) => f.probability >= 70), [frames]);

  const zoomIn = () => setZoomIdx((z) => Math.min(z + 1, ZOOM_STEPS.length - 1));
  const zoomOut = () => setZoomIdx((z) => Math.max(z - 1, 0));
  const resetZoom = () => { setZoomIdx(0); setWindowStart(0); };

  const panLeft = () => setWindowStart((s) => Math.max(0, s - Math.ceil(frames.length / zoom / 2)));
  const panRight = () => setWindowStart((s) => Math.min(Math.max(0, frames.length - 1), s + Math.ceil(frames.length / zoom / 2)));

  if (!frames.length) {
    return (
      <div className="glass-surface rounded-[24px] p-6 text-center">
        <Film size={18} className="text-slate-700 mx-auto mb-2" />
        <p className="text-[11px] font-mono text-slate-600 italic">No frame-level timeline data returned for this evidence file.</p>
      </div>
    );
  }

  return (
    <div className="glass-surface card-sheen rounded-[24px] p-5 space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight flex items-center gap-1.5">
          <Film size={14} className="text-[#4FD1E8]" /> Video Tampering Graph
        </h3>
        <div className="flex items-center gap-1">
          <button onClick={panLeft} disabled={zoom === 1} className="px-2 py-1.5 bg-black/30 hover:bg-black/50 disabled:opacity-30 disabled:cursor-not-allowed border border-white/10 rounded-lg text-[10px] font-mono text-slate-400 transition-colors">◂</button>
          <button onClick={zoomOut} disabled={zoom === 1} className="p-1.5 bg-black/30 hover:bg-black/50 disabled:opacity-30 disabled:cursor-not-allowed border border-white/10 rounded-lg text-slate-400 transition-colors" title="Zoom out">
            <ZoomOut size={12} />
          </button>
          <span className="text-[9px] font-mono text-slate-500 px-1 tabular-nums w-8 text-center">{zoom}×</span>
          <button onClick={zoomIn} disabled={zoom === ZOOM_STEPS[ZOOM_STEPS.length - 1]} className="p-1.5 bg-black/30 hover:bg-black/50 disabled:opacity-30 disabled:cursor-not-allowed border border-white/10 rounded-lg text-slate-400 transition-colors" title="Zoom in">
            <ZoomIn size={12} />
          </button>
          <button onClick={panRight} disabled={zoom === 1} className="px-2 py-1.5 bg-black/30 hover:bg-black/50 disabled:opacity-30 disabled:cursor-not-allowed border border-white/10 rounded-lg text-[10px] font-mono text-slate-400 transition-colors">▸</button>
          <button onClick={resetZoom} className="p-1.5 bg-black/30 hover:bg-black/50 border border-white/10 rounded-lg text-slate-400 transition-colors ml-1" title="Reset zoom">
            <RotateCcw size={12} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3 text-[9px] font-mono text-slate-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#34E5A8]" /> 0–30% Authentic</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#F5A623]" /> 30–70% Suspicious</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#FF4757]" /> 70–100% Tampered</span>
      </div>

      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={visibleFrames} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="tamperTimelineFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#FF4757" stopOpacity={0.35} />
                <stop offset="45%" stopColor="#F5A623" stopOpacity={0.22} />
                <stop offset="100%" stopColor="#34E5A8" stopOpacity={0.06} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1B2130" strokeDasharray="3 3" vertical={false} />
            <ReferenceArea y1={70} y2={100} fill="#FF4757" fillOpacity={0.04} strokeOpacity={0} />
            <ReferenceArea y1={30} y2={70} fill="#F5A623" fillOpacity={0.03} strokeOpacity={0} />
            <ReferenceLine y={70} stroke="#FF4757" strokeDasharray="2 4" strokeOpacity={0.4} />
            <ReferenceLine y={30} stroke="#F5A623" strokeDasharray="2 4" strokeOpacity={0.4} />
            <XAxis dataKey="frame" stroke="#4A5568" fontSize={9} tickLine={false} axisLine={{ stroke: '#1B2130' }} minTickGap={24} />
            <YAxis domain={[0, 100]} stroke="#4A5568" fontSize={9} tickLine={false} axisLine={false} width={28} />
            <Tooltip content={<TamperTooltip />} cursor={{ stroke: '#4FD1E8', strokeWidth: 1, strokeDasharray: '3 3' }} />
            <Area
              type="monotone"
              dataKey="probability"
              stroke="#4FD1E8"
              strokeWidth={2}
              fill="url(#tamperTimelineFill)"
              dot={(props) => {
                const { cx, cy, payload } = props;
                if (payload.probability < 70) return null;
                return <Dot key={`sus-${payload.idx}`} cx={cx} cy={cy} r={3} fill="#FF4757" stroke="#0A0E16" strokeWidth={1} />;
              }}
              activeDot={{ r: 4, fill: '#4FD1E8', stroke: '#0A0E16', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {suspiciousFrames.length > 0 && (
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#FF4757] bg-[#FF4757]/[0.06] border border-[#FF4757]/20 rounded-xl px-3 py-2">
          <TriangleAlert size={12} className="flex-shrink-0" />
          <span className="tabular-nums">{suspiciousFrames.length} frame{suspiciousFrames.length !== 1 ? 's' : ''} flagged above the 70% tamper threshold</span>
        </div>
      )}
    </div>
  );
}
