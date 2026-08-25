// src/components/BlockchainProof.jsx
import React from 'react';
import { Fingerprint, FileSignature, Boxes, Link2, Award, Lock, ShieldCheck, ArrowDown } from 'lucide-react';

function statusFor(ledgerResult) {
  const data = ledgerResult?.blockchain_ledger?.data;
  if (data) return { label: 'Confirmed', color: '#34E5A8' };
  if (ledgerResult) return { label: 'Anchoring', color: '#F5A623' };
  return { label: 'Awaiting Evidence', color: '#4A5568' };
}

function ChainNode({ Icon, label, value, color, isLast, confirmed }) {
  return (
    <div className="relative">
      <div className="flex items-start gap-3">
        <div className="flex flex-col items-center flex-shrink-0">
          <span
            className="w-10 h-10 rounded-2xl flex items-center justify-center icon-chip-glow relative"
            style={{ backgroundColor: `${color}18`, border: `1px solid ${color}40` }}
          >
            <Icon size={16} style={{ color }} />
            {confirmed && (
              <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-[#0A0E16] flex items-center justify-center border border-[#34E5A8]/50">
                <ShieldCheck size={9} className="text-[#34E5A8]" />
              </span>
            )}
          </span>
          {!isLast && (
            <div className="w-px flex-1 min-h-[28px] mt-1.5 relative overflow-hidden" style={{ backgroundColor: `${color}30` }}>
              {confirmed && <span className="absolute inset-0 chain-flow-vertical" />}
            </div>
          )}
        </div>
        <div className="pb-7 min-w-0 flex-1">
          <span className="text-[9px] text-slate-500 uppercase font-mono tracking-wide block">{label}</span>
          <code className="text-xs text-slate-200 font-mono font-semibold break-all block mt-0.5">{value}</code>
        </div>
      </div>
    </div>
  );
}

export default function BlockchainProof({ ledgerResult, searchHash }) {
  const data = ledgerResult?.blockchain_ledger?.data || {};
  const hash = (searchHash || '').trim().replace('0x', '');
  const status = statusFor(ledgerResult);
  const confirmed = status.label === 'Confirmed';

  const nodes = [
    { Icon: Fingerprint, label: 'Evidence Hash', value: hash ? `${hash.substring(0, 24)}…` : 'Not yet computed', color: '#34E5A8' },
    { Icon: FileSignature, label: 'Smart Contract Transaction', value: data.transaction_hash || data.tx_hash || (confirmed ? 'tx anchored' : 'Pending submission'), color: '#4FD1E8' },
    { Icon: Boxes, label: 'Block Number', value: data.block_number ?? data.block ?? (confirmed ? 'Assigned' : '—'), color: '#8B93FF' },
    { Icon: Link2, label: 'Ledger Confirmation', value: confirmed ? 'Confirmed on-chain' : 'Awaiting confirmation', color: '#F5A623' },
    { Icon: Award, label: 'Certificate ID', value: data.certificate_id || (hash ? `CERT-${hash.substring(0, 10).toUpperCase()}` : '—'), color: '#34E5A8' },
  ];

  return (
    <div className="glass-surface card-sheen rounded-[28px] p-6 space-y-4 relative overflow-hidden">
      {confirmed && <div className="ambient-glow opacity-40" />}
      <div className="flex items-center justify-between relative z-[1]">
        <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight flex items-center gap-1.5">
          <Lock size={14} className="text-[#34E5A8]" /> Blockchain Proof Chain
        </h3>
        <span
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-mono font-semibold tracking-wide"
          style={{ backgroundColor: `${status.color}12`, borderColor: `${status.color}40`, color: status.color }}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${confirmed ? 'pulse-dot' : ''}`} style={{ backgroundColor: status.color }} />
          {status.label}
        </span>
      </div>

      {!ledgerResult ? (
        <div className="text-center py-6 relative z-[1]">
          <div className="empty-state-icon mx-auto mb-3">
            <Lock size={18} className="text-slate-700" />
          </div>
          <p className="text-[11px] font-mono text-slate-600 italic">Run a ledger lookup or complete a video audit to populate the proof chain.</p>
        </div>
      ) : (
        <>
          <div className="relative z-[1] pl-1">
            {nodes.map((n, i) => (
              <ChainNode key={n.label} {...n} isLast={i === nodes.length - 1} confirmed={confirmed} />
            ))}
          </div>

          {confirmed && (
            <div className="flex items-center gap-2 text-[10px] font-mono text-[#34E5A8] bg-[#34E5A8]/[0.06] border border-[#34E5A8]/20 rounded-xl px-3 py-2.5 relative z-[1]">
              <ShieldCheck size={13} className="flex-shrink-0" />
              <span>This evidence record is cryptographically anchored and immutable — any alteration to the source file invalidates the hash match.</span>
            </div>
          )}
        </>
      )}

      <style>{`
        @keyframes chain-flow-vertical-move {
          0% { background-position: 0 -30px; }
          100% { background-position: 0 30px; }
        }
        .chain-flow-vertical {
          background-image: linear-gradient(180deg, transparent 0%, rgba(52,229,168,0.9) 50%, transparent 100%);
          background-size: 2px 30px;
          background-repeat: repeat-y;
          animation: chain-flow-vertical-move 1.4s linear infinite;
        }
      `}</style>
    </div>
  );
}
