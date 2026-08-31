// src/components/AudioForensicConsole.jsx
import React, { useState } from 'react';
import { Waves, ShieldCheck, ShieldAlert, Clock, Radio } from 'lucide-react';
import LiveAudioWaveform from './LiveAudioWaveform';
import AudioTamperTimeline from './AudioTamperTimeline';

function VerdictBadge({ verdict, riskScore }) {
  const isTampered = (verdict || '').toLowerCase().includes('tamper') || (verdict || '').toLowerCase().includes('synthetic');
  const color = isTampered ? '#FF4757' : '#34E5A8';
  const Icon = isTampered ? ShieldAlert : ShieldCheck;
  return (
    <div className="flex items-center gap-2.5 bg-black/30 border rounded-2xl px-4 py-3" style={{ borderColor: `${color}30` }}>
      <span className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${color}18` }}>
        <Icon size={16} style={{ color }} />
      </span>
      <div className="min-w-0">
        <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Verdict</span>
        <span className="text-sm font-display font-bold block truncate" style={{ color }}>{verdict || 'Pending'}</span>
      </div>
      {typeof riskScore === 'number' && (
        <div className="ml-auto text-right flex-shrink-0">
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wide block">Risk Score</span>
          <span className="text-lg font-display font-bold tabular-nums" style={{ color }}>{riskScore}%</span>
        </div>
      )}
    </div>
  );
}

export default function AudioForensicConsole({ analysisResult, file, loading }) {
  const [playing, setPlaying] = useState(false);

  if (loading) {
    return (
      <div className="glass-surface rounded-[24px] p-6 text-center">
        <Waves size={18} className="text-[#8B93FF] mx-auto mb-2 pulse-dot" />
        <p className="text-[11px] font-mono text-slate-500 italic">Audio pipeline running — results will populate once telemetry completes.</p>
      </div>
    );
  }

  if (!analysisResult) return null;

  const {
    sample_rate,
    duration_seconds,
    audio_timeline,
    waveform_points,
    risk_score,
    verdict,
  } = analysisResult;

  const hasAnyAudioField = sample_rate || duration_seconds || audio_timeline || waveform_points || typeof risk_score === 'number';

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-sm font-display font-bold text-slate-200 flex items-center gap-1.5">
          <Waves size={15} className="text-[#8B93FF]" /> Audio Authentication Core
        </h2>
        <div className="flex items-center gap-3 text-[10px] font-mono text-slate-500">
          {typeof sample_rate === 'number' && (
            <span className="flex items-center gap-1 tabular-nums"><Radio size={10} /> {sample_rate.toLocaleString()} Hz</span>
          )}
          {typeof duration_seconds === 'number' && (
            <span className="flex items-center gap-1 tabular-nums"><Clock size={10} /> {duration_seconds.toFixed(1)}s</span>
          )}
        </div>
      </div>

      {!hasAnyAudioField && (
        <div className="glass-surface rounded-[22px] p-5 text-center">
          <p className="text-[11px] font-mono text-slate-600 italic">
            Backend response did not include audio-specific telemetry (sample_rate, waveform_points, audio_timeline, risk_score). Showing what's available below.
          </p>
        </div>
      )}

      <VerdictBadge verdict={verdict || analysisResult.verdict} riskScore={typeof risk_score === 'number' ? risk_score : undefined} />

      <LiveAudioWaveform
        waveformPoints={waveform_points}
        durationSeconds={duration_seconds}
        playing={playing}
        onTogglePlay={() => setPlaying((p) => !p)}
      />

      <AudioTamperTimeline audioTimeline={audio_timeline} />
    </div>
  );
}
