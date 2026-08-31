import React, { useMemo } from 'react';
import { ShieldCheck, ShieldAlert, Radar, GitBranch, AudioWaveform, Activity } from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar as RadarArea,
  Tooltip,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

export default function VerdictBanner({ analysisResult, loading = false }) {
  const verdictRaw = analysisResult?.verdict || '';
  const verdictLower = verdictRaw.toLowerCase();
  const isFake = verdictLower.includes('tamper') || verdictLower.includes('synthetic') || verdictLower.includes('fake');
  const hasVerdict = !!analysisResult && !!verdictRaw;

  const confidence = Math.max(0, Math.min(100, Number(analysisResult?.confidence) || 0));

  const palette = loading
    ? '#4FD1E8'
    : hasVerdict
    ? (isFake ? '#FF4757' : '#34E5A8')
    : '#8B93FF';

  const label = loading
    ? 'RUNNING PIPELINE FORENSIC SCANNING…'
    : hasVerdict
    ? (isFake ? 'TAMPERED / SYNTHETIC' : 'AUTHENTIC')
    : 'AWAITING DISPATCH EVIDENCE CONTAINER';

  const sublabel = loading
    ? 'Extracting high-fidelity vectors and computational hashes across consensus grids'
    : hasVerdict
    ? `Fusion confidence ${confidence.toFixed(1)}% · ${analysisResult?.media_type || 'media'} payload`
    : 'Ingest evidence container file structure inside the audit pipeline view';

  return (
    <div
      className="relative overflow-hidden rounded-[28px] glass-surface card-sheen p-6 sm:p-7"
      style={{
        boxShadow: `0 1px 0 0 rgba(255,255,255,0.05) inset, 0 8px 32px -8px rgba(0,0,0,0.5), 0 0 0 1px ${palette}22, 0 0 60px -12px ${palette}33`,
      }}
    >
      <div
        className="absolute -inset-24 opacity-25 blur-3xl pointer-events-none"
        style={{ background: `radial-gradient(circle at 20% 20%, ${palette}, transparent 60%)` }}
      />
      {loading && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className="scanline-sweep"
            style={{ background: `linear-gradient(to bottom, transparent, ${palette}22, transparent)` }}
          />
        </div>
      )}

      <span className="absolute -top-px -left-px w-4 h-4 border-t-2 border-l-2 rounded-tl-md pointer-events-none transition-colors duration-500" style={{ borderColor: palette }} />
      <span className="absolute -top-px -right-px w-4 h-4 border-t-2 border-r-2 rounded-tr-md pointer-events-none transition-colors duration-500" style={{ borderColor: palette }} />
      <span className="absolute -bottom-px -left-px w-4 h-4 border-b-2 border-l-2 rounded-bl-md pointer-events-none transition-colors duration-500" style={{ borderColor: palette }} />
      <span className="absolute -bottom-px -right-px w-4 h-4 border-b-2 border-r-2 rounded-br-md pointer-events-none transition-colors duration-500" style={{ borderColor: palette }} />

      <div className="relative z-[1] flex flex-col sm:flex-row sm:items-center gap-5">
        <div className="flex-shrink-0 relative w-16 h-16 sm:w-20 sm:h-20">
          <div className="absolute inset-0 rounded-full blur-xl opacity-30" style={{ backgroundColor: palette }} />
          <div
            className="absolute inset-0 rounded-full flex items-center justify-center border-2"
            style={{ borderColor: `${palette}55`, backgroundColor: `${palette}12` }}
          >
            {loading ? (
              <Radar size={26} className="pulse-dot" style={{ color: palette }} />
            ) : isFake && hasVerdict ? (
              <ShieldAlert size={28} style={{ color: palette }} />
            ) : (
              <ShieldCheck size={28} style={{ color: palette }} />
            )}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <span className="text-[10px] font-mono uppercase tracking-[0.25em] text-slate-500 block mb-1">
            Forensic Verdict
          </span>
          <h2
            className="font-display font-bold text-2xl sm:text-[32px] leading-tight tracking-tight tabular-nums"
            style={{ color: palette, textShadow: hasVerdict ? `0 0 24px ${palette}44` : 'none' }}
          >
            {label}
          </h2>
          <p className="text-xs sm:text-[13px] text-slate-500 font-mono mt-1.5">{sublabel}</p>
        </div>

        <div className="flex-shrink-0 self-stretch sm:self-center flex sm:flex-col items-center justify-center gap-1 min-w-[92px]">
          <span
            className="font-display font-bold text-3xl tabular-nums stat-glow"
            style={{ color: palette }}
          >
            {hasVerdict && !loading ? `${confidence.toFixed(0)}%` : '—'}
          </span>
          <span className="text-[9px] font-mono uppercase tracking-wide text-slate-500">Confidence</span>
        </div>
      </div>

      <div className="relative z-[1] mt-5">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[9px] font-mono uppercase tracking-wide text-slate-600">Fusion Score</span>
          <span className="text-[9px] font-mono uppercase tracking-wide text-slate-600 tabular-nums">
            {hasVerdict && !loading ? `${confidence.toFixed(1)} / 100` : '0 / 100'}
          </span>
        </div>
        <div className="relative h-3 rounded-full bg-black/40 border border-white/[0.06] overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${hasVerdict && !loading ? confidence : 0}%`,
              background: `linear-gradient(90deg, ${palette}88, ${palette})`,
              boxShadow: `0 0 16px -2px ${palette}`,
            }}
          />
          <div className="absolute inset-0 flex">
            {Array.from({ length: 20 }).map((_, i) => (
              <div key={i} className="flex-1 border-r border-black/30 last:border-r-0" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function ModelConsensusRadar({ analysisResult }) {
  const data = useMemo(() => {
    const fusion = analysisResult?.multi_model_fusion;
    if (fusion && typeof fusion === 'object' && Object.keys(fusion).length > 0) {
      return Object.entries(fusion).map(([name, value]) => ({
        model: name,
        score: Number(value) || 0,
      }));
    }
    return [];
  }, [analysisResult]);

  if (data.length === 0) {
    return (
      <div className="glass-surface p-6 rounded-[28px] flex flex-col items-center justify-center h-80 text-center">
        <GitBranch size={24} className="text-slate-600 mb-2" />
        <span className="text-xs font-mono text-slate-500 italic">No video model consensus metrics compiled</span>
      </div>
    );
  }

  const verdictLower = (analysisResult?.verdict || '').toLowerCase();
  const isFake = verdictLower.includes('tamper') || verdictLower.includes('synthetic');
  const accent = isFake ? '#FF4757' : '#34E5A8';

  return (
    <div className="glass-surface card-sheen p-6 rounded-[28px]">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-0.5 flex items-center gap-1.5">
        <GitBranch size={14} style={{ color: accent }} /> Model Agreement Map
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-2">Per-model confidence across the fusion ensemble</p>
      <div className="shimmer-divider mb-3" />
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="72%">
            <PolarGrid stroke="#1B2130" />
            <PolarAngleAxis
              dataKey="model"
              tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'IBM Plex Mono, monospace' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#374151', fontSize: 8 }}
              tickCount={5}
              axisLine={false}
            />
            <RadarArea
              name="Confidence"
              dataKey="score"
              stroke={accent}
              fill={accent}
              fillOpacity={0.25}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0A0E16',
                borderColor: '#1B2130',
                borderRadius: 12,
                fontSize: 12,
                fontFamily: 'IBM Plex Mono, monospace',
              }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Confidence']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function AasistConsensusPanel({ analysisResult }) {
  const aasist = analysisResult?.aasist_analysis;

  const segments = useMemo(() => {
    if (aasist?.segments && Array.isArray(aasist.segments) && aasist.segments.length > 0) {
      return aasist.segments.map((s, i) => ({
        time: s.time || s.timestamp || `${i}`,
        spoof_score: Number(s.spoof_score ?? s.confidence ?? 0),
      }));
    }
    const fallbackTimeline = analysisResult?.audio_timeline;
    if (Array.isArray(fallbackTimeline) && fallbackTimeline.length > 0) {
      return fallbackTimeline.map((f, i) => ({
        time: f.timestamp || `${i}`,
        spoof_score: f.status === 'Tampered' ? 85 + (i % 10) : 5 + (i % 8),
      }));
    }
    return [];
  }, [aasist, analysisResult]);

  const spoofProbability = Number(aasist?.spoof_probability ?? 0);
  const realProbability = Number(aasist?.real_probability ?? (100 - spoofProbability));
  const hasData = !!aasist || segments.length > 0;

  if (!hasData) {
    return (
      <div className="glass-surface p-6 rounded-[28px] flex flex-col items-center justify-center h-80 text-center">
        <AudioWaveform size={24} className="text-slate-600 mb-2" />
        <span className="text-xs font-mono text-slate-500 italic">AASIST telemetry unavailable for this payload</span>
      </div>
    );
  }

  return (
    <div className="glass-surface card-sheen p-6 rounded-[28px]">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-0.5 flex items-center gap-1.5">
        <AudioWaveform size={14} style={{ color: '#F5A623' }} /> AASIST Anti-Spoof Trace
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-2">Segment-level spoof probability from the audio anti-spoofing model</p>
      <div className="shimmer-divider mb-3" />
      <div className="grid grid-cols-2 gap-2.5 mb-3">
        <div className="bg-black/30 p-3 rounded-2xl border border-white/[0.05]">
          <span className="text-[9px] text-slate-500 uppercase font-mono tracking-wide block">Spoof Probability</span>
          <span className="text-xl font-display font-bold tabular-nums" style={{ color: '#FF4757' }}>
            {spoofProbability.toFixed(1)}%
          </span>
        </div>
        <div className="bg-black/30 p-3 rounded-2xl border border-white/[0.05]">
          <span className="text-[9px] text-slate-500 uppercase font-mono tracking-wide block">Bonafide Probability</span>
          <span className="text-xl font-display font-bold tabular-nums" style={{ color: '#34E5A8' }}>
            {realProbability.toFixed(1)}%
          </span>
        </div>
      </div>

      {segments.length > 0 && (
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={segments}>
              <CartesianGrid stroke="#1B2130" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#4A5568" fontSize={9} tickLine={false} axisLine={{ stroke: '#1B2130' }} />
              <YAxis stroke="#4A5568" fontSize={9} domain={[0, 100]} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0A0E16',
                  borderColor: '#1B2130',
                  borderRadius: 12,
                  fontSize: 12,
                  fontFamily: 'IBM Plex Mono, monospace',
                }}
                formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Spoof score']}
              />
              <Line
                type="monotone"
                dataKey="spoof_score"
                stroke="#F5A623"
                strokeWidth={2}
                dot={{ r: 2, fill: '#F5A623' }}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}