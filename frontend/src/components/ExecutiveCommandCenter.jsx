// src/components/ExecutiveCommandCenter.jsx
// ============================================================
// NEW FEATURE — Executive Command Center
// A composed, denser view of the same real execSummary /
// systemHealth / modelMetrics data App.jsx already fetches and
// holds in state — arranged as a single "mission control" strip
// meant to sit above or alongside the existing Command Overview
// section. This component does not fetch anything itself: it is
// purely a presentational composition over props you already have
// in App.jsx, so wiring it in means passing existing state down,
// never duplicating fetch logic.
//
// Usage:
//   <ExecutiveCommandCenter
//     execSummary={execSummary}
//     systemHealth={systemHealth}
//     modelMetrics={modelMetrics}
//     loading={loading}
//     verdictIsFake={verdictIsFake}
//   />
// ============================================================
import React from 'react';
import { Activity, ShieldAlert, ShieldCheck, Cpu, Gauge, Radio } from 'lucide-react';

function MiniReadout({ label, value, tone = '#34E5A8', icon: Icon }) {
  return (
    <div className="bg-black/30 rounded-2xl border border-white/[0.06] p-3 flex items-center gap-3 hover:border-white/[0.12] transition-colors">
      <span className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${tone}18` }}>
        <Icon size={14} style={{ color: tone }} />
      </span>
      <div className="min-w-0">
        <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block truncate">{label}</span>
        <span className="text-sm font-display font-bold tabular-nums block" style={{ color: tone }}>{value}</span>
      </div>
    </div>
  );
}

export default function ExecutiveCommandCenter({ execSummary = {}, systemHealth = {}, modelMetrics = [], loading = false, verdictIsFake = false }) {
  const status = loading ? { label: 'ANALYZING', color: '#4FD1E8' } : verdictIsFake ? { label: 'THREAT ACTIVE', color: '#FF4757' } : { label: 'NOMINAL', color: '#34E5A8' };
  const topModel = [...modelMetrics].sort((a, b) => (b.score || 0) - (a.score || 0))[0];

  return (
    <div className="glass-surface rounded-[28px] p-6 relative overflow-hidden">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div>
          <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight flex items-center gap-1.5">
            <Radio size={14} style={{ color: status.color }} /> Executive Command Center
          </h3>
          <p className="text-[10px] text-slate-600 font-mono mt-0.5">Unified readout — pipeline, hardware, and model layers in one strip</p>
        </div>
        <span
          className="px-3 py-1 rounded-full text-[10px] font-mono font-bold tracking-wide border"
          style={{ color: status.color, borderColor: `${status.color}44`, backgroundColor: `${status.color}12` }}
        >
          {status.label}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        <MiniReadout label="Videos Ingested" value={execSummary.total_videos ?? 0} tone="#4FD1E8" icon={Activity} />
        <MiniReadout label="Deepfakes Found" value={execSummary.deepfakes_detected ?? 0} tone="#FF4757" icon={ShieldAlert} />
        <MiniReadout label="Feedback Accuracy" value={`${execSummary.feedback_accuracy ?? 0}%`} tone="#34E5A8" icon={ShieldCheck} />
        <MiniReadout label="Top Model" value={topModel ? `${topModel.name} ${Math.round(topModel.score || 0)}%` : '—'} tone="#8B93FF" icon={Cpu} />
      </div>

      <div className="grid grid-cols-3 gap-2.5 mt-2.5">
        <MiniReadout label="CPU" value={`${systemHealth.cpu ?? 0}%`} tone="#F5A623" icon={Gauge} />
        <MiniReadout label="RAM" value={`${systemHealth.ram ?? 0}%`} tone="#F5A623" icon={Gauge} />
        <MiniReadout label="Throughput" value={`${systemHealth.fps ?? 0} FPS`} tone="#34E5A8" icon={Activity} />
      </div>
    </div>
  );
}
