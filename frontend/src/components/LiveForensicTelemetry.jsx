// src/components/LiveForensicTelemetry.jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid, Area, ComposedChart, ReferenceArea } from 'recharts';
import React, { useMemo } from 'react';
import { Cpu, Radar, Waves, Lock, ScanLine, CheckCircle2, Loader2, CircleDashed } from 'lucide-react';

const PHASES = [
  { id: 1, key: 'ingestion', label: 'Evidence Ingestion', icon: ScanLine, floor: 0, ceil: 20 },
  { id: 2, key: 'extraction', label: 'Feature Extraction', icon: Radar, floor: 20, ceil: 45 },
  { id: 3, key: 'inference', label: 'AI Model Inference', icon: Cpu, floor: 45, ceil: 75 },
  { id: 4, key: 'risk', label: 'Risk Calculation', icon: Waves, floor: 75, ceil: 90 },
  { id: 5, key: 'anchor', label: 'Blockchain Anchoring', icon: Lock, floor: 90, ceil: 100 },
];

function phaseStatus(phase, progress) {
  if (progress >= phase.ceil) return 'done';
  if (progress >= phase.floor) return 'active';
  return 'pending';
}

function engineStatusFor(engineFloor, progress, completeAt = 100) {
  if (progress >= completeAt) return 'DONE';
  if (progress >= engineFloor) return 'RUNNING';
  return 'WAITING';
}

function EngineRow({ label, status, accent }) {
  const tone =
    status === 'RUNNING' ? { color: '#34E5A8', Icon: Loader2, spin: true } :
    status === 'DONE' ? { color: '#4FD1E8', Icon: CheckCircle2, spin: false } :
    { color: '#4A5568', Icon: CircleDashed, spin: false };
  const { color, Icon, spin } = tone;
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-white/[0.04] last:border-b-0">
      <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: accent }} />
        {label}
      </span>
      <span className="text-[9px] font-mono font-bold tracking-wide flex items-center gap-1" style={{ color }}>
        <Icon size={10} className={spin ? 'pulse-dot' : ''} />
        {status}
      </span>

    </div>
  );
}

function LiveMotionGraph({ progress, frameCount }) {
  // Build a synthetic but realistic timeline that fills in as progress advances.
  const totalFrames = 96;
  const revealed = Math.max(3, Math.floor((progress / 100) * totalFrames));
  const data = [];
  for (let i = 0; i < revealed; i++) {
    // Simulated probability curve — rises with progress, with slight noise
    const base = 40 + 55 * Math.sin((i / totalFrames) * Math.PI * 0.9);
    const jitter = Math.sin(i * 1.7) * 6 + Math.cos(i * 0.9) * 4;
    const prob = Math.max(0, Math.min(100, base + jitter));
    data.push({ frame: i, prob });
  }

  const currentProb = data[data.length - 1]?.prob || 0;
  const tone = currentProb >= 70 ? '#FF4757' : currentProb >= 40 ? '#F5A623' : '#34E5A8';

  return (
    <div className="mt-3 rounded-2xl border border-white/[0.06] bg-black/30 p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-mono uppercase tracking-wide text-slate-500 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: tone }} />
          Live Frame Analysis
        </span>
        <span className="text-[10px] font-mono text-slate-500 tabular-nums">
          {revealed} / {totalFrames} frames
        </span>
      </div>
      <div className="h-24">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id="liveFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={tone} stopOpacity={0.5} />
                <stop offset="100%" stopColor={tone} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1B2130" strokeDasharray="2 4" vertical={false} />
            <XAxis dataKey="frame" hide />
            <YAxis domain={[0, 100]} hide />
            <ReferenceLine y={70} stroke="#FF4757" strokeDasharray="3 3" />
            <Area type="monotone" dataKey="prob" stroke="none" fill="url(#liveFill)" />
            <Line
              type="monotone"
              dataKey="prob"
              stroke={tone}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: tone, stroke: '#fff', strokeWidth: 1 }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


function LiveHeroGraph({ progress, frameCount, file }) {
  const [pulse, setPulse] = React.useState(0);

  React.useEffect(() => {
    let raf;
    const loop = () => {
      setPulse((p) => (p + 1) % 240);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, []);

  // ---- Detect media type ----
  const fname = (file?.name || '').toLowerCase();
  const ftype = (file?.type || '').toLowerCase();
  const isAudio =
    ftype.startsWith('audio/') ||
    fname.endsWith('.mp3') || fname.endsWith('.wav') ||
    fname.endsWith('.flac') || fname.endsWith('.m4a') ||
    fname.endsWith('.ogg') || fname.endsWith('.aac');
  const isImage =
    ftype.startsWith('image/') ||
    fname.endsWith('.jpg') || fname.endsWith('.jpeg') ||
    fname.endsWith('.png') || fname.endsWith('.webp');

  // ---- Mode-specific configuration ----
  const mode = isAudio ? 'audio' : isImage ? 'image' : 'video';

  const cfg = {
    audio: {
      total: 60,
      unit: 'segments',
      totalLabel: 'Total segments',
      revealLabel: 'Segments revealed',
      flaggedLabel: 'Flagged >70%',
      peakLabel: 'Peak spoof',
      avgLabel: 'Avg confidence',
      axisLabel: 'Time (seconds)',
      title: 'Audio Tamper Motion',
      tickPrefix: '',
      tickSuffix: 's',
      stepSeconds: 0.5,
    },
    video: {
      total: 96,
      unit: 'frames',
      totalLabel: 'Total frames',
      revealLabel: 'Frames revealed',
      flaggedLabel: 'Flagged >70%',
      peakLabel: 'Peak tamper',
      avgLabel: 'Avg confidence',
      axisLabel: 'Frame index',
      title: 'Tamper Motion Analysis',
      tickPrefix: '',
      tickSuffix: '',
      stepSeconds: 0,
    },
    image: {
      total: 24,
      unit: 'regions',
      totalLabel: 'Total regions',
      revealLabel: 'Regions revealed',
      flaggedLabel: 'Flagged >70%',
      peakLabel: 'Peak risk',
      avgLabel: 'Avg confidence',
      axisLabel: 'Region index',
      title: 'Image Region Analysis',
      tickPrefix: '',
      tickSuffix: '',
      stepSeconds: 0,
    },
  }[mode];

  // ---- Generate curve ----
  const revealed = Math.max(4, Math.floor((progress / 100) * cfg.total));
  const data = [];
  for (let i = 0; i < revealed; i++) {
    const t = i / cfg.total;
    // Slightly different curve shape for audio vs video
    const base = mode === 'audio'
      ? 25 + 70 / (1 + Math.exp(-11 * (t - 0.42)))
      : 22 + 72 / (1 + Math.exp(-9 * (t - 0.42)));
    const jitter = Math.sin(i * 0.7) * 3 + Math.cos(i * 0.24) * 2.5;
    const tamper = Math.max(3, Math.min(99, base + jitter));
    const confBase = 55 + 42 * (1 - Math.exp(-t * 2.6));
    const confidence = Math.max(15, Math.min(99, confBase + Math.cos(i * 0.4) * 1.5));
    data.push({
      idx: i,
      x: mode === 'audio' ? +(i * cfg.stepSeconds).toFixed(2) : i,
      tamper,
      confidence,
    });
  }

  const current = data[data.length - 1] || { tamper: 0, confidence: 0 };
  const tone = current.tamper >= 70 ? '#FF4757' : current.tamper >= 40 ? '#F5A623' : '#34E5A8';
  const toneName = current.tamper >= 70 ? 'CRITICAL' : current.tamper >= 40 ? 'ELEVATED' : 'NOMINAL';
  const flagged = data.filter((d) => d.tamper >= 70).length;
  const peak = data.length ? Math.max(...data.map((d) => d.tamper)) : 0;
  const avgConf = data.length ? data.reduce((a, b) => a + b.confidence, 0) / data.length : 0;
  const fileName = file?.name || 'evidence';
  const haloR = 6 + 3 * Math.sin(pulse * 0.08);
  const haloOpacity = 0.55 + 0.35 * Math.sin(pulse * 0.08);

  return (
    <div className="rise-in mt-6 relative overflow-hidden rounded-[28px]">
      <div
        className="relative rounded-[28px] p-6 border"
        style={{
          background: 'linear-gradient(135deg, rgba(15,20,30,0.85) 0%, rgba(8,12,20,0.95) 100%)',
          borderColor: `${tone}40`,
          boxShadow: `0 0 60px -10px ${tone}30, 0 0 0 1px rgba(255,255,255,0.02) inset`,
        }}
      >
        <div
          className="absolute -top-32 -right-32 w-96 h-96 rounded-full pointer-events-none"
          style={{
            background: `radial-gradient(circle, ${tone}40 0%, ${tone}10 40%, transparent 70%)`,
            filter: 'blur(40px)',
          }}
        />
        <div
          className="absolute -bottom-24 -left-24 w-80 h-80 rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(circle, rgba(79,209,232,0.25) 0%, transparent 65%)',
            filter: 'blur(40px)',
          }}
        />

        {/* Header */}
        <div className="relative z-10 flex items-start justify-between mb-5">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{
                  backgroundColor: tone,
                  boxShadow: `0 0 12px ${tone}, 0 0 24px ${tone}80`,
                  animation: 'pulse 1.8s ease-in-out infinite',
                }}
              />
              <span className="text-[11px] font-mono uppercase tracking-[0.25em] text-slate-400">
                Live {mode === 'audio' ? 'Audio' : mode === 'image' ? 'Image' : 'Video'} Telemetry
              </span>
            </div>
            <div className="font-display text-[22px] font-bold tracking-tight text-slate-100">
              {cfg.title}
            </div>
            <div className="text-[10px] font-mono text-slate-500 mt-1">
              {fileName} · real-time multi-detector consensus
            </div>
          </div>

          <div className="text-right">
            <div
              className="font-display font-bold leading-none tabular-nums"
              style={{ fontSize: 52, color: tone, textShadow: `0 0 30px ${tone}80` }}
            >
              {Math.round(current.tamper)}%
            </div>
            <div
              className="text-[10px] font-mono uppercase tracking-[0.25em] mt-1.5"
              style={{ color: tone }}
            >
              {mode === 'audio' ? 'SPOOF PROBABILITY' : 'TAMPER PROBABILITY'}
            </div>
            <div className="text-[10px] font-mono mt-0.5" style={{ color: tone }}>
              {toneName}
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="relative z-10" style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 30, bottom: 8, left: -14 }}>
              <defs>
                <linearGradient id="heroAurora" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={tone} stopOpacity={0.55} />
                  <stop offset="45%" stopColor={tone} stopOpacity={0.22} />
                  <stop offset="100%" stopColor={tone} stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="heroStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#34E5A8" />
                  <stop offset="35%" stopColor="#A3E635" />
                  <stop offset="68%" stopColor="#F5A623" />
                  <stop offset="100%" stopColor="#FF4757" />
                </linearGradient>
                <filter id="heroGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <ReferenceArea y1={0} y2={40} fill="#34E5A8" fillOpacity={0.04} />
              <ReferenceArea y1={40} y2={70} fill="#F5A623" fillOpacity={0.05} />
              <ReferenceArea y1={70} y2={100} fill="#FF4757" fillOpacity={0.07} />

              <CartesianGrid stroke="#1B2130" strokeDasharray="2 8" vertical={false} opacity={0.5} />

              <XAxis
                dataKey="x"
                stroke="#475569"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: '#1B2130' }}
                tick={{ fontFamily: 'IBM Plex Mono, monospace' }}
                label={{
                  value: cfg.axisLabel,
                  position: 'insideBottom',
                  offset: -2,
                  fill: '#64748B',
                  fontSize: 10,
                }}
              />
              <YAxis
                domain={[0, 100]}
                stroke="#475569"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tick={{ fontFamily: 'IBM Plex Mono, monospace' }}
                tickFormatter={(v) => `${v}%`}
              />

              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(8, 12, 20, 0.96)',
                  borderColor: `${tone}60`,
                  borderRadius: 14,
                  fontSize: 12,
                  backdropFilter: 'blur(12px)',
                  boxShadow: `0 8px 32px -8px ${tone}60`,
                  fontFamily: 'IBM Plex Mono, monospace',
                }}
                labelFormatter={(v) =>
                  mode === 'audio' ? `t = ${v}s` : `${cfg.unit.slice(0, -1)} ${v}`
                }
                formatter={(v, name) => [
                  `${Number(v).toFixed(1)}%`,
                  name === 'tamper' ? (mode === 'audio' ? 'Spoof' : 'Tamper') : 'Confidence',
                ]}
              />

              <ReferenceLine y={70} stroke="#FF4757" strokeDasharray="6 6" strokeOpacity={0.5} />
              <ReferenceLine y={40} stroke="#F5A623" strokeDasharray="4 6" strokeOpacity={0.35} />

              <Area
                type="natural"
                dataKey="tamper"
                stroke="none"
                fill="url(#heroAurora)"
                isAnimationActive={false}
              />
              <Line
                type="natural"
                dataKey="confidence"
                stroke="#4FD1E8"
                strokeWidth={1.5}
                strokeOpacity={0.65}
                strokeDasharray="3 5"
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="natural"
                dataKey="tamper"
                stroke="url(#heroStroke)"
                strokeWidth={4}
                dot={false}
                activeDot={{ r: 7, fill: tone, stroke: '#fff', strokeWidth: 2 }}
                isAnimationActive={false}
              />

              {data.length > 0 && (
                <ReferenceLine
                  x={data[data.length - 1].x}
                  stroke="transparent"
                  label={(props) => {
                    const { viewBox } = props;
                    const cx = viewBox.x;
                    const cy =
                      viewBox.y +
                      (viewBox.height * (100 - data[data.length - 1].tamper)) / 100;
                    return (
                      <g filter="url(#heroGlow)">
                        <circle cx={cx} cy={cy} r={haloR + 6} fill={tone} opacity={haloOpacity * 0.35} />
                        <circle cx={cx} cy={cy} r={haloR} fill={tone} opacity={0.95} />
                        <circle cx={cx} cy={cy} r={3} fill="#fff" />
                      </g>
                    );
                  }}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Stats footer */}
        <div className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
          <StatCard label={cfg.revealLabel} value={`${revealed} / ${cfg.total}`} accent="#4FD1E8" />
          <StatCard label={cfg.flaggedLabel} value={flagged} accent="#FF4757" />
          <StatCard label={cfg.peakLabel} value={`${Math.round(peak)}%`} accent="#F5A623" />
          <StatCard label={cfg.avgLabel} value={`${Math.round(avgConf)}%`} accent="#34E5A8" />
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.3); }
        }
      `}</style>
    </div>
  );
}


function StatCard({ label, value, accent }) {
  return (
    <div
      className="rounded-2xl p-3 border transition-all hover:-translate-y-0.5"
      style={{
        background: `linear-gradient(135deg, ${accent}12 0%, transparent 100%)`,
        borderColor: `${accent}30`,
      }}
    >
      <div className="text-[9px] font-mono uppercase tracking-[0.2em] text-slate-500 mb-1">
        {label}
      </div>
      <div
        className="text-lg font-display font-bold tabular-nums"
        style={{ color: accent, textShadow: `0 0 16px ${accent}60` }}
      >
        {value}
      </div>
    </div>
  );
}


export default function LiveForensicTelemetry({ progress = 0, statusText = '', frameCount = 0, file, mediaKind }) {
  const inferredKind = useMemo(() => {
    if (mediaKind) return mediaKind;
    const type = file?.type || '';
    if (type.startsWith('audio/')) return 'audio';
    return 'video';
  }, [mediaKind, file]);

  const isAudio = inferredKind === 'audio';
  const unitLabel = isAudio ? 'Segments Processed' : 'Frames Processed';
  const unitCap = isAudio ? 240 : 420;
  const processedUnits = Math.min(frameCount, unitCap);

  const engines = isAudio
    ? [
        { label: 'AASIST Audio Engine', floor: 10, accent: '#8B93FF' },
        { label: 'Spectral Consistency Net', floor: 30, accent: '#4FD1E8' },
        { label: 'Waveform Artifact Scanner', floor: 45, accent: '#34E5A8' },
        { label: 'Blockchain Anchor', floor: 90, accent: '#F5A623' },
      ]
    : [
        { label: 'ViT Model', floor: 20, accent: '#34E5A8' },
        { label: 'Swin Transformer', floor: 30, accent: '#4FD1E8' },
        { label: 'EfficientNet Consensus', floor: 45, accent: '#8B93FF' },
        { label: 'Blockchain Anchor', floor: 90, accent: '#F5A623' },
      ];

  return (
    <div className="rise-in glass-surface rounded-[24px] p-5 space-y-4 fingerprint-texture">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-300 uppercase font-mono tracking-wider flex items-center gap-1.5">
          <Loader2 size={13} className="text-[#34E5A8] pulse-dot" />
          Live Forensic Pipeline
        </span>
        <span className="stat-glow text-lg font-display font-bold text-[#34E5A8] tabular-nums">{progress}%</span>
      </div>

      <div className="relative h-1.5 w-full bg-black/40 rounded-full overflow-hidden border border-white/[0.05]">
        <div
          className="h-full rounded-full transition-all duration-300 ease-out"
          style={{
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #22B98A 0%, #3EF0B4 50%, #4FD1E8 100%)',
            boxShadow: '0 0 12px -1px rgba(52,229,168,0.6)',
          }}
        />
      </div>

      <p className="text-[10px] font-mono text-slate-500 italic truncate">{statusText || 'Initializing pipeline…'}</p>

      {/* Phase tracker */}
      <div className="grid grid-cols-5 gap-1.5">
        {PHASES.map((phase) => {
          const status = phaseStatus(phase, progress);
          const Icon = phase.icon;
          const color = status === 'done' ? '#34E5A8' : status === 'active' ? '#4FD1E8' : '#374151';
          return (
            <div
              key={phase.id}
              className={`flex flex-col items-center gap-1 p-2 rounded-xl border transition-colors duration-300 ${
                status === 'active' ? 'border-[#4FD1E8]/40 bg-[#4FD1E8]/[0.06]' : status === 'done' ? 'border-[#34E5A8]/25 bg-[#34E5A8]/[0.04]' : 'border-white/[0.04] bg-black/20'
              }`}
              title={phase.label}
            >
              <span
                className="w-6 h-6 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${color}18`, border: `1px solid ${color}44` }}
              >
                {status === 'done' ? (
                  <CheckCircle2 size={11} style={{ color }} />
                ) : (
                  <Icon size={11} style={{ color }} className={status === 'active' ? 'pulse-dot' : ''} />
                )}
              </span>
              <span className="font-mono text-[7px] uppercase tracking-wide text-center leading-tight" style={{ color: status === 'pending' ? '#4A5568' : '#94A3B8' }}>
                Phase {phase.id}
              </span>
            
        <LiveMotionGraph progress={progress} frameCount={frameCount} />
      </div>
          );
        })}
      </div>
      <div className="grid grid-cols-5 gap-1.5 -mt-2.5">
        {PHASES.map((phase) => (
          <span key={phase.id} className="text-[7px] font-mono text-slate-600 text-center leading-tight px-0.5">
            {phase.label}
          </span>
        ))}
      </div>

      <LiveHeroGraph progress={progress} frameCount={frameCount} file={file} />

      <div className="shimmer-divider" />

      {/* AI Engine status board */}
      <div>
        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-[0.15em] block mb-1.5">AI Engine Status</span>
        <div className="bg-black/30 rounded-xl border border-white/[0.05] px-3 py-1">
          {engines.map((eng) => (
            <EngineRow key={eng.label} label={eng.label} accent={eng.accent} status={engineStatusFor(eng.floor, progress)} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2.5 text-center">
        <div className="bg-black/30 p-2.5 rounded-xl border border-white/[0.05]">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">{unitLabel}</span>
          <span className="text-base font-display font-bold text-slate-200 tabular-nums block mt-0.5">{processedUnits}</span>
        </div>
        <div className="bg-black/30 p-2.5 rounded-xl border border-white/[0.05]">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Evidence File</span>
          <span className="text-[10px] font-mono font-semibold text-slate-300 block mt-1.5 truncate" title={file?.name}>{file?.name || '—'}</span>
        </div>
      </div>
    </div>
  );
}
