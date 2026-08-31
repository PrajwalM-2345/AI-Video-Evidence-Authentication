// src/components/InvestigationCards.jsx
// ============================================================
// NEW FEATURE — Investigation Cards
// A card-grid rendering of the SAME feedback records the existing
// Investigation table already displays (item.feedback_id,
// video_hash, prediction, actual_result, reward) — this is an
// additional view, not a replacement of the table. Drop it in
// alongside the existing <table> in the Investigation tab, e.g.
// as a toggle or simply stacked beneath it.
//
// Usage:
//   <InvestigationCards items={visibleFeedbackHistory} />
// ============================================================
import React from 'react';
import { CheckCircle, AlertTriangle, Fingerprint } from 'lucide-react';

export default function InvestigationCards({ items = [] }) {
  if (!items || items.length === 0) {
    return (
      <div className="glass-surface rounded-[22px] p-10 text-center text-[11px] font-mono text-slate-600 italic">
        No calibration records to display as cards yet.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {items.map((item, idx) => {
        const isCorrect = item.reward > 0;
        return (
          <div
            key={idx}
            className={`glass-surface card-sheen rounded-2xl p-4 space-y-2.5 border-l-2 ${isCorrect ? 'border-l-[#34E5A8]' : 'border-l-[#FF4757]'}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-600 tabular-nums">#{item.feedback_id}</span>
              <span className={`flex items-center gap-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded-lg ${isCorrect ? 'bg-[#34E5A8]/10 text-[#34E5A8]' : 'bg-[#FF4757]/10 text-[#FF4757]'}`}>
                {isCorrect ? <CheckCircle size={11} /> : <AlertTriangle size={11} />}
                {isCorrect ? `+${item.reward}` : item.reward}
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
              <Fingerprint size={12} className="text-[#F5A623] flex-shrink-0" />
              <span className="truncate">{item.video_hash ? `${item.video_hash.substring(0, 18)}...` : 'N/A'}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono pt-1 border-t border-white/[0.05]">
              <div>
                <span className="text-slate-600 block uppercase tracking-wide">Prediction</span>
                <span className="text-[#4FD1E8] font-semibold">{item.prediction}</span>
              </div>
              <div>
                <span className="text-slate-600 block uppercase tracking-wide">Assessment</span>
                <span className="text-slate-400 font-semibold">{item.actual_result}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
