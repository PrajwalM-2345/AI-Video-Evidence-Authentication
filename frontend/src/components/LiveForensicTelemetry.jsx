// src/components/LiveForensicTelemetry.jsx
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
