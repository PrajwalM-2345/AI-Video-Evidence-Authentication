// AnchorChainMini.jsx — additive component, no existing code modified
import React from 'react';
import { Lock, Link2 } from 'lucide-react';

export default function AnchorChainMini({ anchors = [], currentHash = '' }) {
  const list = Array.isArray(anchors) ? anchors : [];

  if (list.length === 0) return null;

  const visible = list.slice(0, 12);
  const current = (currentHash || '').replace(/^0x/, '').substring(0, 10);

  return (
    <div className="glass-surface rounded-[22px] p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono uppercase tracking-[0.2em] text-slate-500 flex items-center gap-1.5">
          <Lock size={12} className="text-[#34E5A8]" /> Anchor Chain
        </span>
        <span className="text-[9px] font-mono text-slate-600">
          {list.length} anchor{list.length !== 1 ? 's' : ''} on chain
        </span>
      </div>

      <div className="flex items-center gap-1 overflow-x-auto pb-1">
        {visible.map((a, i) => {
          const isCurrent = current && (a.hash || '').toLowerCase().includes(current);
          return (
            <React.Fragment key={i}>
              <div
                className="flex flex-col items-center gap-1 flex-shrink-0"
                title={a.hash || ''}
              >
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center border"
                  style={{
                    backgroundColor: isCurrent ? '#34E5A8' : 'rgba(52,229,168,0.12)',
                    borderColor: isCurrent ? '#34E5A8' : 'rgba(52,229,168,0.35)',
                    boxShadow: isCurrent ? '0 0 12px rgba(52,229,168,0.7)' : 'none',
                  }}
                >
                  <Lock size={9} style={{ color: isCurrent ? '#06070A' : '#34E5A8' }} />
                </div>
                <span className="text-[7px] font-mono text-slate-600 tabular-nums">
                  {a.block || a.blockNumber || i}
                </span>
              </div>

              {i < visible.length - 1 && (
                <div className="flex-1 min-w-[8px] h-px bg-gradient-to-r from-[#34E5A8]/50 to-[#34E5A8]/10 relative">
                  <Link2
                    size={8}
                    className="text-[#34E5A8]/60 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
        {list.length > 12 && (
          <span className="text-[9px] font-mono text-slate-600 ml-2">
            +{list.length - 12} more
          </span>
        )}
      </div>

      <div className="text-[9px] font-mono text-slate-600">
        Each anchor is immutable on-chain. Hash → Block → Confirm.
      </div>
    </div>
  );
}
