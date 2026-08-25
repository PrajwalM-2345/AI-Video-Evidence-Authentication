// src/components/UnifiedEvidenceConsole.jsx
import React, { useMemo } from 'react';
import { Film, Waves, Cpu, ShieldCheck, ShieldAlert, Fingerprint, Lock, CheckCircle2, Gauge } from 'lucide-react';
import { resolveMediaKind } from './EvidenceTypeRouter';

const VIDEO_MODELS = ['ViT', 'EfficientNet', 'Swin'];
const AUDIO_MODELS = ['AASIST'];

function EvidenceTypeSelector({ kind }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {[
        { id: 'video', label: 'Video', Icon: Film, color: '#4FD1E8' },
        { id: 'audio', label: 'Audio', Icon: Waves, color: '#8B93FF' },
      ].map(({ id, label, Icon, color }) => {
        const active = kind === id;
        return (
          <div
            key={id}
            className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl border font-mono text-[11px] font-semibold tracking-wide transition-all ${
              active ? '' : 'border-white/[0.06] bg-black/20 text-slate-600'
            }`}
            style={active ? { backgroundColor: `${color}14`, borderColor: `${color}45`, color } : undefined}
          >
            <Icon size={13} /> {label}
            {active && <CheckCircle2 size={11} className="ml-0.5" />}
          </div>
        );
      })}
    </div>
  );
}

function ModelChip({ name, active }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-[10px] font-mono font-semibold ${
        active ? 'bg-[#34E5A8]/10 border-[#34E5A8]/30 text-[#34E5A8]' : 'bg-black/20 border-white/[0.06] text-slate-600'
      }`}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: active ? '#34E5A8' : '#374151' }} />
      {name}
    </span>
  );
}

export default function UnifiedEvidenceConsole({ file, analysisResult }) {
  const kind = useMemo(() => resolveMediaKind(file, analysisResult), [file, analysisResult]);

  if (!analysisResult) return null;

  const verdict = analysisResult.verdict || 'Pending';
  const isTampered = verdict.toLowerCase().includes('tamper') || verdict.toLowerCase().includes('synthetic');
  const verdictColor = isTampered ? '#FF4757' : '#34E5A8';
  const VerdictIcon = isTampered ? ShieldAlert : ShieldCheck;

  const confidence = analysisResult.confidence ?? analysisResult.risk_score ?? null;
  const hash = analysisResult.hash_verification?.sha256_hash;
  const txStatus = analysisResult.blockchain_ledger?.data ? 'Confirmed' : hash ? 'Anchoring' : 'N/A';
  const activeModels = kind === 'audio' ? AUDIO_MODELS : kind === 'video' ? VIDEO_MODELS : [];

  return (
    <div className="glass-surface card-sheen rounded-[28px] p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-display font-bold text-slate-200 flex items-center gap-1.5">
          <Gauge size={15} className="text-[#34E5A8]" /> Unified Evidence Console
        </h2>
        <span className="text-[9px] font-mono text-slate-600 uppercase tracking-[0.15em]">Single-pane intelligence</span>
      </div>

      {/* Evidence Type */}
      <div>
        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-[0.15em] block mb-2">Evidence Type</span>
        <EvidenceTypeSelector kind={kind} />
      </div>

      <div className="shimmer-divider" />

      {/* AI Analysis */}
      <div>
        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-[0.15em] flex items-center gap-1.5 mb-2">
          <Cpu size={11} className="text-[#4FD1E8]" /> AI Analysis
        </span>
        <div className="flex flex-wrap gap-1.5">
          {(kind === 'audio' ? AUDIO_MODELS : VIDEO_MODELS).map((m) => (
            <ModelChip key={m} name={m} active={activeModels.includes(m)} />
          ))}
          {kind === 'unknown' && <span className="text-[10px] font-mono text-slate-600 italic">Model roster unavailable until media type resolves</span>}
        </div>
      </div>

      <div className="shimmer-divider" />

      {/* Risk Assessment */}
      <div>
        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-[0.15em] block mb-2">Risk Assessment</span>
        <div className="grid grid-cols-3 gap-2.5">
          <div className="bg-black/30 border rounded-xl p-3" style={{ borderColor: `${verdictColor}25` }}>
            <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Risk Score</span>
            <span className="text-lg font-display font-bold tabular-nums block mt-0.5" style={{ color: verdictColor }}>
              {typeof confidence === 'number' ? `${confidence}%` : '—'}
            </span>
          </div>
          <div className="bg-black/30 border rounded-xl p-3 flex flex-col justify-between" style={{ borderColor: `${verdictColor}25` }}>
            <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Verdict</span>
            <span className="text-[11px] font-display font-bold flex items-center gap-1 mt-1" style={{ color: verdictColor }}>
              <VerdictIcon size={12} /> {verdict}
            </span>
          </div>
          <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3">
            <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Confidence</span>
            <span className="text-lg font-display font-bold tabular-nums block mt-0.5 text-slate-200">
              {typeof confidence === 'number' ? `${confidence}%` : '—'}
            </span>
          </div>
        </div>
      </div>

      <div className="shimmer-divider" />

      {/* Blockchain Proof */}
      <div>
        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-[0.15em] flex items-center gap-1.5 mb-2">
          <Lock size={11} className="text-[#F5A623]" /> Blockchain Proof
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3 sm:col-span-2">
            <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide flex items-center gap-1"><Fingerprint size={10} /> SHA256 Hash</span>
            <code className="text-[10px] text-slate-300 font-mono break-all block mt-1">{hash || 'Not yet anchored'}</code>
          </div>
          <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3 flex flex-col justify-center">
            <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Tx Status</span>
            <span className={`text-[11px] font-mono font-bold mt-1 ${txStatus === 'Confirmed' ? 'text-[#34E5A8]' : 'text-slate-400'}`}>{txStatus}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
