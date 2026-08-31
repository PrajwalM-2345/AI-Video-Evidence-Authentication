// src/components/ForensicReportPreview.jsx
import React from 'react';
import { FileText, Fingerprint, ShieldCheck, ShieldAlert, Gauge, Lock, Download, Hexagon } from 'lucide-react';

export default function ForensicReportPreview({ file, analysisResult, ledgerResult, onDownload, downloading }) {
  if (!analysisResult) return null;

  const verdict = analysisResult.verdict || 'Pending';
  const isTampered = verdict.toLowerCase().includes('tamper') || verdict.toLowerCase().includes('synthetic');
  const color = isTampered ? '#FF4757' : '#34E5A8';
  const VerdictIcon = isTampered ? ShieldAlert : ShieldCheck;

  const hash = analysisResult.hash_verification?.sha256_hash;
  const confidence = analysisResult.confidence ?? analysisResult.risk_score ?? null;
  const blockchainVerified = Boolean(ledgerResult?.blockchain_ledger?.data);

  return (
    <div className="glass-surface card-sheen rounded-[28px] p-6 space-y-5 relative overflow-hidden">
      <div className="ambient-glow opacity-30" />
      <div className="flex items-center justify-between relative z-[1]">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className="absolute inset-0 blur-md bg-[#34E5A8]/30 rounded-full" />
            <Hexagon className="h-6 w-6 text-[#34E5A8] relative" strokeWidth={1.5} />
          </div>
          <div>
            <h3 className="text-sm font-display font-bold text-white leading-none">Phoenix Forensic Report</h3>
            <span className="text-[9px] text-slate-500 font-mono block mt-1 tracking-wide">DOCUMENT PREVIEW</span>
          </div>
        </div>
        <FileText size={16} className="text-slate-600" />
      </div>

      <div className="shimmer-divider relative z-[1]" />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 relative z-[1]">
        <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3.5 sm:col-span-2">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide flex items-center gap-1"><FileText size={10} /> Evidence Filename</span>
          <span className="text-xs text-slate-200 font-mono font-semibold block mt-1 truncate">{file?.name || 'Unnamed evidence file'}</span>
        </div>

        <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3.5 sm:col-span-2">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide flex items-center gap-1"><Fingerprint size={10} /> SHA256</span>
          <code className="text-[10px] text-slate-300 font-mono break-all block mt-1">{hash || 'Not yet computed'}</code>
        </div>

        <div className="bg-black/30 border rounded-xl p-3.5" style={{ borderColor: `${color}30` }}>
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Verdict</span>
          <span className="text-sm font-display font-bold flex items-center gap-1.5 mt-1" style={{ color }}>
            <VerdictIcon size={14} /> {verdict}
          </span>
        </div>

        <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3.5">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide flex items-center gap-1"><Gauge size={10} /> Confidence</span>
          <span className="text-sm font-display font-bold text-slate-200 tabular-nums block mt-1">
            {typeof confidence === 'number' ? `${confidence}%` : '—'}
          </span>
        </div>

        <div className="bg-black/30 border border-white/[0.06] rounded-xl p-3.5 sm:col-span-2 flex items-center justify-between">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide flex items-center gap-1"><Lock size={10} /> Blockchain</span>
          <span className={`text-[11px] font-mono font-bold flex items-center gap-1.5 ${blockchainVerified ? 'text-[#34E5A8]' : 'text-slate-500'}`}>
            {blockchainVerified && <span className="w-1.5 h-1.5 rounded-full bg-[#34E5A8] pulse-dot" />}
            {blockchainVerified ? 'Verified' : 'Not yet anchored'}
          </span>
        </div>
      </div>

      {onDownload && (
        <button
          onClick={onDownload}
          disabled={downloading || !hash}
          className="btn-primary-elevated w-full text-[#06070A] font-display font-bold py-3 rounded-2xl flex items-center justify-center gap-2 text-sm disabled:opacity-60 relative z-[1]"
        >
          <Download size={15} />
          {downloading ? 'Compiling PDF…' : 'Download Full Forensic Report'}
        </button>
      )}
    </div>
  );
}
