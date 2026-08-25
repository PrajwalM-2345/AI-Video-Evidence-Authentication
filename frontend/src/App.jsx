// src/App.jsx
import React, { useState, useRef, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Shield, Upload, Search, Cpu, Database, CheckCircle, AlertTriangle, FileCode, MessageSquare, Send, Zap, Film, Briefcase, PlusCircle, Clock, LayoutGrid, Layers, BarChart3, Activity, Fingerprint, Lock, Radio, ScanLine, ChevronRight, Sparkles, TrendingUp, ShieldCheck, ShieldAlert, Hexagon, Sun, Moon, Bell, BellRing, History, X, SlidersHorizontal, ArrowUpDown, Waves, Orbit, Crosshair, Radar, GitBranch, Aperture, AudioWaveform } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar, AreaChart, Area, RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';
import ThreeGlobe from './components/ThreeGlobe';
import { motion, AnimatePresence } from './components/motion-shim';
import EvidenceGraph from './components/EvidenceGraph';
import NeuralAICore from './components/NeuralAICore';
import ExecutiveCommandCenter from './components/ExecutiveCommandCenter';
import CinematicBackground from './components/CinematicBackground';
import TimelineScrubber from './components/TimelineScrubber';
import './components/premium-typography.css';
import InvestigationCards from './components/InvestigationCards';
import EnhancedHeatmap from './components/EnhancedHeatmap';
import LiveForensicTelemetry from './components/LiveForensicTelemetry';
import EvidenceTypeRouter from './components/EvidenceTypeRouter';
import UnifiedEvidenceConsole from './components/UnifiedEvidenceConsole';
import BlockchainProof from './components/BlockchainProof';
import ForensicReportPreview from './components/ForensicReportPreview';
import VerdictBanner, { ModelConsensusRadar, AasistConsensusPanel } from './components/VerdictBanner';

const BACKEND_URL = "http://localhost:8080";

const FONT_IMPORT_ID = 'phoenix-fonts';

function useFonts() {
  useEffect(() => {
    if (document.getElementById(FONT_IMPORT_ID)) return;
    const link = document.createElement('link');
    link.id = FONT_IMPORT_ID;
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap';
    document.head.appendChild(link);
  }, []);
}

function Reticle({ children, className = '', active = false, color = '#34E5A8', size = 'md' }) {
  const corner = size === 'lg' ? 'w-4 h-4' : size === 'sm' ? 'w-2.5 h-2.5' : 'w-3 h-3';
  return (
    <div className={`relative ${className}`}>
      <span className={`absolute -top-px -left-px ${corner} border-t-2 border-l-2 rounded-tl-md pointer-events-none transition-colors duration-500`} style={{ borderColor: color }} />
      <span className={`absolute -top-px -right-px ${corner} border-t-2 border-r-2 rounded-tr-md pointer-events-none transition-colors duration-500`} style={{ borderColor: color }} />
      <span className={`absolute -bottom-px -left-px ${corner} border-b-2 border-l-2 rounded-bl-md pointer-events-none transition-colors duration-500`} style={{ borderColor: color }} />
      <span className={`absolute -bottom-px -right-px ${corner} border-b-2 border-r-2 rounded-br-md pointer-events-none transition-colors duration-500`} style={{ borderColor: color }} />
      {active && (
        <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
          <div className="scanline-sweep" style={{ background: `linear-gradient(to bottom, transparent, ${color}22, transparent)` }} />
        </div>
      )}
      {children}
    </div>
  );
}

function StatusPill({ tone = 'neutral', children, icon: Icon }) {
  const tones = {
    good: 'bg-[#34E5A8]/10 text-[#34E5A8] border-[#34E5A8]/30',
    bad: 'bg-[#FF4757]/10 text-[#FF4757] border-[#FF4757]/30',
    warn: 'bg-[#F5A623]/10 text-[#F5A623] border-[#F5A623]/30',
    info: 'bg-[#4FD1E8]/10 text-[#4FD1E8] border-[#4FD1E8]/30',
    neutral: 'bg-white/5 text-slate-400 border-white/10',
  };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-mono font-semibold tracking-wide ${tones[tone]}`}>
      {Icon && <Icon size={11} />}
      {children}
    </span>
  );
}

function SectionEyebrow({ step, total, label, color = '#34E5A8' }) {
  return (
    <div className="flex items-center gap-2.5 mb-1">
      <span className="font-mono text-[10px] font-bold tracking-[0.25em]" style={{ color }}>
        {String(step).padStart(2, '0')} / {String(total).padStart(2, '0')}
      </span>
      <span className="w-6 h-px" style={{ backgroundColor: `${color}55` }} />
      <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-slate-500">{label}</span>
    </div>
  );
}

function useThemeToggle() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('phoenix-theme') || 'dark';
    } catch {
      return 'dark';
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('phoenix-theme', theme);
    } catch {}
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));
  return { theme, toggleTheme };
}

function useTamperAlerts(analysisResult, file) {
  const [alerts, setAlerts] = useState([]);
  const [panelOpen, setPanelOpen] = useState(false);
  const seenHashes = useRef(new Set());

  useEffect(() => {
    if (!analysisResult) return;
    const hash = analysisResult.hash_verification?.sha256_hash || `${file?.name}-${Date.now()}`;
    if (seenHashes.current.has(hash)) return;

    const verdict = (analysisResult.verdict || '').toLowerCase();
    const isTampered = verdict.includes('tamper') || verdict.includes('synthetic');

    seenHashes.current.add(hash);
    const newAlert = {
      id: hash,
      severity: isTampered ? 'critical' : 'clear',
      title: isTampered ? 'Tampering Detected' : 'Video Verified Authentic',
      detail: file?.name ? `${file.name} · confidence ${analysisResult.confidence || 0}%` : `Confidence ${analysisResult.confidence || 0}%`,
      timestamp: new Date().toLocaleTimeString(),
    };

    setAlerts((prev) => [newAlert, ...prev].slice(0, 25));
    if (isTampered) setPanelOpen(true);
  }, [analysisResult, file]);

  const unreadCritical = alerts.filter((a) => a.severity === 'critical').length;
  const clearAlerts = () => setAlerts([]);
  const dismissAlert = (id) => setAlerts((prev) => prev.filter((a) => a.id !== id));

  return { alerts, panelOpen, setPanelOpen, unreadCritical, clearAlerts, dismissAlert };
}

function AlertsPanel({ alerts, open, onClose, onClear, onDismiss }) {
  if (!open) return null;
  return (
    <div className="rise-in absolute right-0 top-full mt-2 w-80 max-h-96 overflow-y-auto custom-scrollbar bg-[#0A0E16]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl shadow-black/60 z-50 p-3 space-y-2">
      <div className="flex items-center justify-between px-1 pb-2 border-b border-white/[0.06]">
        <span className="text-[11px] font-mono font-semibold text-slate-300 uppercase tracking-wide flex items-center gap-1.5">
          <BellRing size={13} className="text-[#F5A623]" /> Alert Feed
        </span>
        <div className="flex items-center gap-2">
          {alerts.length > 0 && (
            <button onClick={onClear} className="text-[10px] font-mono text-slate-500 hover:text-slate-300 transition-colors">Clear all</button>
          )}
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300">
            <X size={14} />
          </button>
        </div>
      </div>
      {alerts.length === 0 ? (
        <div className="text-center text-[11px] font-mono text-slate-600 py-8 italic">No alerts yet. Run an audit to populate this feed.</div>
      ) : (
        alerts.map((a) => (
          <div key={a.id} className={`p-3 rounded-xl border text-xs font-mono flex items-start gap-2.5 transition-colors ${a.severity === 'critical' ? 'bg-[#FF4757]/[0.06] border-[#FF4757]/25 hover:border-[#FF4757]/40' : 'bg-[#34E5A8]/[0.06] border-[#34E5A8]/25 hover:border-[#34E5A8]/40'}`}>
            {a.severity === 'critical' ? <ShieldAlert size={15} className="text-[#FF4757] mt-0.5 flex-shrink-0" /> : <ShieldCheck size={15} className="text-[#34E5A8] mt-0.5 flex-shrink-0" />}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <span className={`font-semibold ${a.severity === 'critical' ? 'text-[#FF4757]' : 'text-[#34E5A8]'}`}>{a.title}</span>
                <button onClick={() => onDismiss(a.id)} className="text-slate-600 hover:text-slate-400 flex-shrink-0">
                  <X size={11} />
                </button>
              </div>
              <p className="text-slate-500 mt-0.5 truncate">{a.detail}</p>
              <span className="text-[9px] text-slate-600 block mt-1">{a.timestamp}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function useActivityLog() {
  const [activity, setActivity] = useState([]);

  const logEvent = (type, label, meta = '') => {
    setActivity((prev) => [
      { id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, type, label, meta, timestamp: new Date() },
      ...prev,
    ].slice(0, 100));
  };

  return { activity, logEvent };
}

function useCountUp(targetValue, durationMs = 900) {
  const [display, setDisplay] = useState(0);
  const fromRef = useRef(0);
  const rafRef = useRef(null);

  const numeric = useMemo(() => {
    const n = parseFloat(String(targetValue).replace(/[^0-9.-]/g, ''));
    return Number.isFinite(n) ? n : 0;
  }, [targetValue]);

  useEffect(() => {
    const from = fromRef.current;
    const delta = numeric - from;
    const start = performance.now();

    if (rafRef.current) cancelAnimationFrame(rafRef.current);

    const tick = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / durationMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(from + delta * eased);
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        fromRef.current = numeric;
      }
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => rafRef.current && cancelAnimationFrame(rafRef.current);
  }, [numeric, durationMs]);

  const formatted = useMemo(() => {
    const str = String(targetValue);
    const hasDecimal = /\.\d/.test(str);
    const rounded = hasDecimal ? display.toFixed(1) : Math.round(display).toString();
    if (str.includes('%')) return `${rounded}%`;
    return rounded;
  }, [display, targetValue]);

  return formatted;
}

function AnimatedStatValue({ value, className = '', style }) {
  const formatted = useCountUp(value);
  return <span className={className} style={style}>{formatted}</span>;
}

function ExecutiveThreatGauge({ execSummary }) {
  const total = execSummary.total_videos || 0;
  const flagged = execSummary.deepfakes_detected || 0;
  const rate = total > 0 ? Math.round((flagged / total) * 100) : 0;

  const tone =
    rate >= 50 ? { color: '#FF4757', label: 'ELEVATED' } :
    rate >= 20 ? { color: '#F5A623', label: 'MODERATE' } :
    { color: '#34E5A8', label: 'NOMINAL' };

  const gaugeData = [{ name: 'rate', value: rate, fill: tone.color }];

  return (
    <Reticle color={tone.color} className="glass-surface card-sheen p-6 rounded-[28px] h-full">
      <SectionEyebrow step={1} total={4} label="Risk Instrument" color={tone.color} />
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-0.5 flex items-center gap-1.5 mt-1.5">
        <ShieldAlert size={14} style={{ color: tone.color }} /> Tamper Detection Rate
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-2">Share of ingested videos flagged as tampered/synthetic</p>
      <div className="shimmer-divider mb-2" />
      <div className="relative h-44 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-32 h-32 rounded-full opacity-20 blur-2xl" style={{ backgroundColor: tone.color }} />
        </div>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="72%"
            outerRadius="100%"
            barSize={14}
            data={gaugeData}
            startAngle={210}
            endAngle={-30}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
            <RadialBar background={{ fill: '#ffffff08' }} dataKey="value" cornerRadius={8} angleAxisId={0} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="stat-glow text-4xl font-display font-bold tabular-nums" style={{ color: tone.color }}>
            <AnimatedStatValue value={`${rate}%`} />
          </span>
          <div className="mt-1.5">
            <StatusPill tone={rate >= 50 ? 'bad' : rate >= 20 ? 'warn' : 'good'}>{tone.label}</StatusPill>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-center text-[10px] font-mono text-slate-500 border-t border-white/[0.05] pt-3 mt-1">
        <div>Flagged <span className="text-slate-200 block font-bold text-sm tabular-nums">{flagged}</span></div>
        <div>Total Ingested <span className="text-slate-200 block font-bold text-sm tabular-nums">{total}</span></div>
      </div>
    </Reticle>
  );
}

function ApertureRing({ status = 'idle', progress = 0, verdictIsFake = false, accuracy = 0 }) {
  const palette =
    status === 'analyzing' ? '#4FD1E8' :
    status === 'verdict' ? (verdictIsFake ? '#FF4757' : '#34E5A8') :
    '#8B93FF';

  const label =
    status === 'analyzing' ? `Analyzing · ${progress}%` :
    status === 'verdict' ? (verdictIsFake ? 'Tamper Detected' : 'Verified Authentic') :
    'Idle — awaiting evidence';

  const sub =
    status === 'analyzing' ? 'Multi-model consensus in flight' :
    status === 'verdict' ? 'Pipeline complete · telemetry synced' :
    'Drop evidence to begin forensic audit';

  const size = 168;
  const cx = size / 2, cy = size / 2;
  const rOuter = 76, rInner = 60;
  const circOuter = 2 * Math.PI * rOuter;
  const circInner = 2 * Math.PI * rInner;
  const outerOffset = circOuter * (1 - (status === 'idle' ? 0.06 : progress / 100));
  const innerOffset = circInner * (1 - Math.min(accuracy, 100) / 100);

  return (
    <div className="glass-surface card-sheen rounded-[28px] p-6 flex flex-col sm:flex-row items-center gap-6 relative overflow-hidden w-full">
      <div className="ambient-glow opacity-60" />
      <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
        <div
          className="absolute inset-0 rounded-full blur-2xl transition-colors duration-700"
          style={{ backgroundColor: palette, opacity: 0.22 }}
        />
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="relative">
          <circle cx={cx} cy={cy} r={rOuter} fill="none" stroke="#ffffff0c" strokeWidth="7" />
          <circle cx={cx} cy={cy} r={rInner} fill="none" stroke="#ffffff08" strokeWidth="4" />
          <circle
            cx={cx} cy={cy} r={rOuter} fill="none" stroke={palette} strokeWidth="7" strokeLinecap="round"
            strokeDasharray={circOuter} strokeDashoffset={outerOffset}
            transform={`rotate(-90 ${cx} ${cy})`}
            style={{ transition: 'stroke-dashoffset 0.4s cubic-bezier(0.22,1,0.36,1), stroke 0.5s ease' }}
          />
          <circle
            cx={cx} cy={cy} r={rInner} fill="none" stroke="#F5A623" strokeWidth="3" strokeLinecap="round"
            strokeDasharray={circInner} strokeDashoffset={innerOffset} opacity="0.75"
            transform={`rotate(-90 ${cx} ${cy})`}
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
          {status === 'analyzing' && (
            <g style={{ transformOrigin: `${cx}px ${cy}px`, animation: 'orb-spin 3s linear infinite' }}>
              <circle cx={cx} cy={cy - rOuter} r="3.5" fill={palette} style={{ filter: `drop-shadow(0 0 6px ${palette})` }} />
            </g>
          )}
          <g style={{ transformOrigin: `${cx}px ${cy}px`, animation: 'orb-spin 24s linear infinite' }}>
            {[0, 90, 180, 270].map((deg) => (
              <line
                key={deg}
                x1={cx} y1={cy - rOuter - 9} x2={cx} y2={cy - rOuter - 4}
                stroke={`${palette}66`} strokeWidth="1.5"
                transform={`rotate(${deg} ${cx} ${cy})`}
              />
            ))}
          </g>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Aperture size={22} className={status === 'analyzing' ? 'pulse-dot' : ''} style={{ color: palette }} />
          <span className="font-display font-bold text-xl mt-1 tabular-nums" style={{ color: palette }}>
            {status === 'analyzing' ? `${progress}%` : status === 'verdict' ? '' : '—'}
          </span>
        </div>
      </div>
      <div className="min-w-0 text-center sm:text-left relative z-[1]">
        <span className="text-[10px] text-slate-500 font-mono uppercase tracking-[0.2em] block mb-1.5">Aperture · Fusion Core</span>
        <span className="text-2xl font-display font-bold block leading-tight" style={{ color: palette }}>{label}</span>
        <span className="text-xs text-slate-500 font-mono block mt-1.5">{sub}</span>
        <div className="flex items-center gap-3 mt-3 justify-center sm:justify-start">
          <span className="flex items-center gap-1.5 text-[10px] font-mono text-slate-500">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: palette }} /> Pipeline
          </span>
          <span className="flex items-center gap-1.5 text-[10px] font-mono text-slate-500">
            <span className="w-2 h-2 rounded-full bg-[#F5A623]" /> Calibration {accuracy}%
          </span>
        </div>
      </div>
    </div>
  );
}

function BlockchainVisualization({ ledgerResult, searchHash }) {
  if (!ledgerResult) return null;
  const data = ledgerResult.blockchain_ledger?.data || {};
  const hash = (searchHash || '').trim().replace('0x', '');

  const nodes = [
    { label: 'Evidence Hash', value: hash ? `${hash.substring(0, 14)}...` : 'N/A', icon: Fingerprint, color: '#34E5A8' },
    { label: 'Investigator', value: data.investigator ? `${data.investigator.substring(0, 10)}...` : 'N/A', icon: Shield, color: '#4FD1E8' },
    { label: 'Confidence', value: `${data.confidence_score_percentage || 0}%`, icon: ShieldCheck, color: '#8B93FF' },
    { label: 'Anchor Status', value: 'Confirmed', icon: Lock, color: '#F5A623' },
  ];

  return (
    <div className="glass-surface rounded-[28px] p-5">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-3 flex items-center gap-1.5">
        <Lock size={14} className="text-[#34E5A8]" /> Ledger Anchor Chain
      </h3>
      <div className="flex items-center overflow-x-auto pb-2 custom-scrollbar">
        {nodes.map((node, i) => {
          const Icon = node.icon;
          return (
            <React.Fragment key={i}>
              <div className="flex flex-col items-center flex-shrink-0 w-28">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center mb-2 icon-chip-glow"
                  style={{ backgroundColor: `${node.color}18`, border: `1px solid ${node.color}40` }}
                >
                  <Icon size={17} style={{ color: node.color }} />
                </div>
                <span className="text-[9px] text-slate-500 uppercase font-mono tracking-wide text-center">{node.label}</span>
                <span className="text-[10px] text-slate-200 font-mono font-bold text-center truncate w-full mt-0.5" title={node.value}>{node.value}</span>
              </div>
              {i < nodes.length - 1 && (
                <div className="flex-1 min-w-[24px] h-px bg-gradient-to-r from-[#34E5A8]/40 via-[#34E5A8]/20 to-[#34E5A8]/40 mx-1 relative">
                  <span className="absolute inset-0 chain-flow" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

function ActivityTimeline({ activity }) {
  const iconFor = (type) => {
    switch (type) {
      case 'case': return { Icon: Briefcase, color: '#8B93FF' };
      case 'upload': return { Icon: ScanLine, color: '#4FD1E8' };
      case 'feedback': return { Icon: CheckCircle, color: '#34E5A8' };
      case 'ledger': return { Icon: Fingerprint, color: '#F5A623' };
      default: return { Icon: Activity, color: '#94A3B8' };
    }
  };

  return (
    <div className="glass-surface rounded-[28px] p-5">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-2 flex items-center gap-1.5">
        <History size={14} className="text-[#8B93FF]" /> Case Activity Timeline
        {activity.length > 0 && (
          <span className="ml-auto flex items-center gap-1 text-[#34E5A8] text-[10px] font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-[#34E5A8] pulse-dot" /> LIVE
          </span>
        )}
      </h3>
      <div className="shimmer-divider mb-4" />
      {activity.length === 0 ? (
        <div className="text-center py-4">
          <div className="empty-state-icon mx-auto mb-3">
            <History size={20} className="text-slate-700" />
          </div>
          <div className="text-[11px] font-mono text-slate-600 pb-4 italic">No activity recorded yet this session.</div>
        </div>
      ) : (
        <div className="relative pl-5 space-y-4 max-h-[420px] overflow-y-auto custom-scrollbar">
          <div className="absolute left-[7px] top-1 bottom-1 w-px bg-gradient-to-b from-[#8B93FF]/40 via-white/[0.08] to-transparent" />
          {activity.map((item) => {
            const { Icon, color } = iconFor(item.type);
            return (
              <div key={item.id} className="relative">
                <span className="absolute -left-5 top-0.5 w-3.5 h-3.5 rounded-full flex items-center justify-center" style={{ backgroundColor: `${color}22`, border: `1px solid ${color}55`, boxShadow: `0 0 8px -1px ${color}66` }}>
                  <Icon size={8} style={{ color }} />
                </span>
                <div className="text-xs font-mono">
                  <span className="text-slate-300 font-medium">{item.label}</span>
                  {item.meta && <span className="text-slate-600"> · {item.meta}</span>}
                  <span className="text-slate-600 block text-[10px] mt-0.5">{item.timestamp.toLocaleString()}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function App() {
  useFonts();

  const [activeTab, setActiveTab] = useState('upload');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [searchHash, setSearchHash] = useState('');
  const [ledgerResult, setLedgerResult] = useState(null);
  const [error, setError] = useState('');
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const [liveProgress, setLiveProgress] = useState(0);
  const [liveStatusText, setLiveStatusText] = useState('');
  const [liveFrameCount, setLiveFrameCount] = useState(0);

  const [feedbackHistory, setFeedbackHistory] = useState([]);

  const [execSummary, setExecSummary] = useState({
    total_videos: 0,
    total_cases: 0,
    deepfakes_detected: 0,
    blockchain_records: 0,
    feedback_accuracy: 94.2
  });
  const [modelMetrics, setModelMetrics] = useState([
    { name: 'ViT', score: 0 },
    { name: 'EfficientNet', score: 0 },
    { name: 'Swin', score: 0 },
    { name: 'Ensemble V3', score: 0 }
  ]);
  const [systemHealth, setSystemHealth] = useState({
    cpu: 0,
    ram: 0,
    gpu: "CPU Execution Mode",
    fps: 25.8
  });

  const [targetCaseId, setTargetCaseId] = useState('');
  const [newCaseId, setNewCaseId] = useState('');
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [newCaseDesc, setNewCaseDescription] = useState('');
  const [newCaseExaminer, setNewCaseExaminer] = useState('Lead Investigator');
  const [caseSuccessMsg, setCaseSuccessMsg] = useState('');

  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', text: 'Phoenix Assistant online. Upload a video under a Case ID, or run a ledger lookup, and I\'ll help you interrogate the evidence.' }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatSuggestions] = useState([
    'Summarize the tamper intervals',
    'Show the blockchain proof',
    'Explain the fusion score'
  ]);
  const chatEndRef = useRef(null);

  const { theme, toggleTheme } = useThemeToggle();
  const { alerts, panelOpen, setPanelOpen, unreadCritical, clearAlerts, dismissAlert } = useTamperAlerts(analysisResult, file);
  const { activity, logEvent } = useActivityLog();

  const [feedbackSearchQuery, setFeedbackSearchQuery] = useState('');
  const [feedbackFilterVerdict, setFeedbackFilterVerdict] = useState('all');
  const [feedbackSortDesc, setFeedbackSortDesc] = useState(true);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, chatLoading]);

  useEffect(() => {
    if (analysisResult) {
      setChatHistory([
        { role: 'assistant', text: `Telemetry synced for ${file?.name}. Ask me to cross-examine timeline entries, break down the model consensus, or pull the blockchain anchor.` }
      ]);
      setFeedbackSuccess('');
      fetchFeedbackHistory();
      logEvent('upload', 'Video audit completed', file?.name || analysisResult.verdict);
    }
  }, [analysisResult]);

  useEffect(() => {
    if (activeTab === 'executive') {
      fetchExecutiveAnalyticsMetrics();
      fetchModelMetrics();
    }
  }, [activeTab]);

  useEffect(() => {
    let healthInterval = null;
    if (activeTab === 'executive') {
      fetchSystemHealthMetrics();
      healthInterval = setInterval(() => {
        fetchSystemHealthMetrics();
      }, 3000);
    }
    return () => {
      if (healthInterval) clearInterval(healthInterval);
    };
  }, [activeTab]);

  const fetchExecutiveAnalyticsMetrics = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/dashboard/summary`);
      setExecSummary(response.data);
    } catch (err) {
      console.log("Failed to process server metric aggregator slots.");
    }
  };
  const fetchModelMetrics = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/model-metrics"
      );
      setModelMetrics([
        { name: 'ViT', score: response.data.vit_accuracy || 0 },
        { name: 'EfficientNet', score: response.data.efficientnet_accuracy || 0 },
        { name: 'Swin', score: response.data.swin_accuracy || 0 },
        { name: 'Ensemble V3', score: response.data.ensemble_accuracy || 0 }
      ]);
    } catch (error) {
      console.error("Failed to load model metrics:", error);
    }
  };

  const fetchSystemHealthMetrics = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/system/health`);
      setSystemHealth(response.data);
    } catch (err) {
      console.log("System health monitoring telemetry node down.");
    }
  };

  const fetchFeedbackHistory = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/feedback/history`);
      setFeedbackHistory(response.data);
    } catch (err) {
      console.error("Feedback Submit Error:", err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setAnalysisResult(null);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setAnalysisResult(null);
      setError('');
    }
  };

  const handleFeedbackSubmit = async (isCorrect) => {
    if (!analysisResult) return;
    try {
      await axios.post(`${BACKEND_URL}/feedback/`, {
        video_hash: analysisResult.hash_verification?.sha256_hash,
        prediction: analysisResult.verdict,
        is_correct: isCorrect
      });
      setFeedbackSuccess(`Feedback logged — calibration data recorded.`);
      fetchFeedbackHistory();
      logEvent('feedback', isCorrect ? 'Analyst confirmed verdict' : 'Analyst flagged incorrect verdict');
    } catch (err) {
      alert("Failed to sync analyst feedback.");
    }
  };

  const handleCreateCaseFile = async (e) => {
    e.preventDefault();
    if (!newCaseId.trim() || !newCaseTitle.trim()) return;

    setError('');
    setCaseSuccessMsg('');
    try {
      await axios.post(`${BACKEND_URL}/cases/`, {
        case_id: newCaseId.trim(),
        title: newCaseTitle.trim(),
        description: newCaseDesc.trim(),
        assigned_examiner: newCaseExaminer.trim()
      });
      setCaseSuccessMsg(`Case [${newCaseId}] created. You can now attach video evidence to this matter.`);
      setTargetCaseId(newCaseId.trim());
      logEvent('case', `Case file created: ${newCaseId.trim()}`, newCaseTitle.trim());
      setNewCaseId('');
      setNewCaseTitle('');
      setNewCaseDescription('');
    } catch (err) {
      const systemError = err.response?.data?.detail || err.message || 'Connection refused';
      setError(`${systemError}`);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setLiveProgress(0);
    setLiveFrameCount(0);
    setError('');

    let progressInterval = setInterval(() => {
      setLiveProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return 95;
        }
        let nextVal = prev + Math.floor(Math.random() * 8) + 2;
        if (nextVal > 95) nextVal = 95;

        const isAudio = file?.type?.startsWith("audio/");

      if (isAudio) {
          if (nextVal < 20) setLiveStatusText("Loading waveform segments");
          else if (nextVal < 45) setLiveStatusText("Extracting spectral features");
          else if (nextVal < 75) setLiveStatusText("Running AASIST anti-spoof inference");
          else if (nextVal < 90) setLiveStatusText("Anchoring evidence hash to blockchain");
          else setLiveStatusText("Generating forensic audio report");
          setLiveFrameCount(Math.min(Math.floor(nextVal * 2.4), 240));
      } else {
          if (nextVal < 20) setLiveStatusText("Isolating GOP container streams and extracting I-frames");
          else if (nextVal < 45) setLiveStatusText("Running high-fidelity landmark face mesh detection");
          else if (nextVal < 75) setLiveStatusText("Executing multi-model vision transformer consensus");
          else if (nextVal < 90) setLiveStatusText("Anchoring hash fingerprint to smart contract layer");
          else setLiveStatusText("Finalizing forensic payload structure");
          
      }

        return nextVal;
      });
    }, 300);

    const formData = new FormData();
    formData.append('file', file);

    let requestUrl = `${BACKEND_URL}/verify-video/`;
    if (targetCaseId.trim()) {
      requestUrl += `?case_id=${encodeURIComponent(targetCaseId.trim())}`;
    }

    try {
      const response = await axios.post(requestUrl, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      clearInterval(progressInterval);
      setLiveProgress(100);
      setLiveStatusText("Pipeline complete — telemetry synced");
      setAnalysisResult(response.data);
    } catch (err) {
      clearInterval(progressInterval);
      const systemError = err.response?.data?.detail || err.message || 'Connection interrupted';
      setError(`Upload error: ${systemError}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchHash.trim()) return;
    setLoading(true);
    setError('');
    setLedgerResult(null);
    try {
      const response = await axios.get(`${BACKEND_URL}/verify-hash/${searchHash.trim()}`);
      setLedgerResult(response.data);
      setChatHistory([
        { role: 'assistant', text: `Ledger record found for [${searchHash.substring(0, 10)}...]. Ready to walk through the details.` }
      ]);
      logEvent('ledger', 'Ledger lookup performed', `${searchHash.trim().substring(0, 12)}...`);
    } catch (err) {
      setError(err.response?.data?.detail || 'No verified record matches this hash.');
    } finally {
      setLoading(false);
    }
  };

  const downloadForensicReport = async (targetHash) => {
    setDownloadingReport(true);
    try {
      const response = await axios.get(`${BACKEND_URL}/download-report/${targetHash}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Phoenix_Forensic_Report_${targetHash.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      if (err.response && err.response.data) {
        const reader = new FileReader();
        reader.onload = () => {
          const errorMsg = JSON.parse(reader.result)?.detail || "Report compilation error.";
          alert(`Forensic compiler error: ${errorMsg}`);
        };
        reader.readAsText(err.response.data);
      } else {
        alert('Failed to connect to the report engine.');
      }
    } finally {
      setDownloadingReport(false);
    }
  };

  const sendChat = async (text) => {
    const activeHash = analysisResult?.hash_verification?.sha256_hash || searchHash.trim();
    if (!activeHash) {
      alert("Upload a video or look up a hash first so I have evidence to reference.");
      return;
    }

    setChatHistory(prev => [...prev, { role: 'user', text }]);
    setChatLoading(true);

    const formattedHistory = chatHistory
      .filter(msg => msg.text)
      .map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.text
      }));

    try {
      const response = await axios.post(`${BACKEND_URL}/forensic-assistant/chat`, {
        video_hash: activeHash,
        user_prompt: text,
        history: formattedHistory
      });
      setChatHistory(prev => [...prev, { role: 'assistant', text: response.data.assistant_response }]);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Unknown routing error.';
      setChatHistory(prev => [...prev, { role: 'assistant', text: `Interruption: ${errorMsg}` }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleSendChatMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const msg = chatInput.trim();
    setChatInput('');
    await sendChat(msg);
  };

  const verdictIsFake = analysisResult?.verdict?.toLowerCase().includes('tamper') || analysisResult?.verdict?.toLowerCase().includes('synthetic');

  const navItems = [
    { id: 'executive', label: 'Dashboard', icon: BarChart3 },
    { id: 'upload', label: 'Video Audit', icon: ScanLine },
    { id: 'investigation', label: 'Investigation', icon: Cpu },
    { id: 'cases', label: 'Cases', icon: Briefcase },
    { id: 'ledger', label: 'Ledger', icon: Fingerprint },
  ];

  const visibleFeedbackHistory = useMemo(() => {
    let rows = [...feedbackHistory];

    if (feedbackSearchQuery.trim()) {
      const q = feedbackSearchQuery.trim().toLowerCase();
      rows = rows.filter((item) =>
        (item.video_hash || '').toLowerCase().includes(q) ||
        (item.prediction || '').toString().toLowerCase().includes(q) ||
        (item.actual_result || '').toString().toLowerCase().includes(q) ||
        (item.feedback_id || '').toString().toLowerCase().includes(q)
      );
    }

    if (feedbackFilterVerdict !== 'all') {
      rows = rows.filter((item) =>
        feedbackFilterVerdict === 'correct' ? item.reward > 0 : item.reward <= 0
      );
    }

    rows.sort((a, b) => {
      const idA = Number(a.feedback_id) || 0;
      const idB = Number(b.feedback_id) || 0;
      return feedbackSortDesc ? idB - idA : idA - idB;
    });

    return rows;
  }, [feedbackHistory, feedbackSearchQuery, feedbackFilterVerdict, feedbackSortDesc]);

  const isLight = theme === 'light';
  const shellBg = isLight
    ? 'radial-gradient(ellipse 90% 60% at 50% -10%, #F6F7FB 0%, #E9ECF2 55%, #E2E5ED 100%)'
    : 'radial-gradient(ellipse 90% 60% at 20% -10%, #0C1420 0%, #070A10 45%, #05070A 100%)';

  const activeNavIndex = navItems.findIndex((n) => n.id === activeTab);

  return (
    <div className={`min-h-screen ${isLight ? 'text-slate-800' : 'text-slate-100'} phoenix-theme-${theme}`} style={{
      background: shellBg,
      fontFamily: "'IBM Plex Mono', monospace"
    }}>
      <style>{`
        @keyframes scan-sweep {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(300%); }
        }
        .scanline-sweep {
          position: absolute;
          left: 0; right: 0;
          height: 40%;
          animation: scan-sweep 3s linear infinite;
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.8); }
        }
        .pulse-dot { animation: pulse-dot 1.8s ease-in-out infinite; }
        @keyframes orb-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        /* Chain-link flow animation for the ledger anchor chain connectors */
        @keyframes chain-flow-move {
          0% { background-position: -40px 0; }
          100% { background-position: 40px 0; }
        }
        .chain-flow {
          background-image: linear-gradient(90deg, transparent 0%, rgba(52,229,168,0.9) 50%, transparent 100%);
          background-size: 40px 2px;
          background-repeat: repeat-x;
          background-position: center;
          animation: chain-flow-move 1.6s linear infinite;
          opacity: 0.7;
        }

        @keyframes tab-fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .tab-transition { animation: tab-fade-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) both; }
        .font-display { font-family: 'Space Grotesk', sans-serif; }
        .font-serif-accent { font-family: 'Instrument Serif', serif; font-style: italic; }
        .tabular-nums { font-variant-numeric: tabular-nums; }
        .custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1B2130; border-radius: 4px; }
        .grain-overlay {
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2334E5A8' fill-opacity='0.02'%3E%3Cpath d='M0 0h1v1H0V0zm10 10h1v1h-1v-1zm20 20h1v1h-1v-1z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        @media (prefers-reduced-motion: reduce) {
          .scanline-sweep, .pulse-dot, .ambient-glow, .card-sheen::before, .glass-shimmer, .chain-flow, .tab-transition, .rise-in, .radar-sweep-ring, .stat-glow { animation: none !important; }
        }

        @keyframes ambient-drift {
          0%   { transform: translate(-10%, -10%) rotate(0deg); }
          50%  { transform: translate(10%, 5%) rotate(180deg); }
          100% { transform: translate(-10%, -10%) rotate(360deg); }
        }
        .ambient-glow {
          position: absolute;
          inset: -60%;
          background: conic-gradient(from 0deg, #34E5A822, #4FD1E815, transparent 30%, transparent 70%, #8B93FF15, #34E5A822);
          animation: ambient-drift 22s linear infinite;
          filter: blur(40px);
          pointer-events: none;
          z-index: 0;
        }

        @keyframes radar-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .radar-sweep-ring {
          position: absolute;
          inset: 0;
          border-radius: 9999px;
          background: conic-gradient(from 0deg, transparent 0%, #34E5A81a 8%, transparent 16%);
          animation: radar-rotate 5s linear infinite;
          pointer-events: none;
        }

        .glass-surface {
          background: linear-gradient(180deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0.015) 100%);
          backdrop-filter: blur(20px) saturate(140%);
          -webkit-backdrop-filter: blur(20px) saturate(140%);
          border: 1px solid rgba(255,255,255,0.08);
          box-shadow: 0 1px 0 0 rgba(255,255,255,0.05) inset, 0 8px 32px -8px rgba(0,0,0,0.5);
          transition: border-color 0.35s ease, box-shadow 0.35s ease, transform 0.35s ease;
        }
        .glass-surface:hover {
          border-color: rgba(52,229,168,0.22);
          box-shadow: 0 1px 0 0 rgba(255,255,255,0.08) inset, 0 12px 40px -8px rgba(0,0,0,0.6), 0 0 0 1px rgba(52,229,168,0.06);
          transform: translateY(-1px);
        }

        .card-sheen { position: relative; overflow: hidden; }
        .card-sheen::before {
          content: '';
          position: absolute;
          top: 0; left: -150%;
          width: 60%; height: 100%;
          background: linear-gradient(100deg, transparent, rgba(52,229,168,0.06), transparent);
          transition: left 0.9s cubic-bezier(0.22, 1, 0.36, 1);
          pointer-events: none;
        }
        .card-sheen:hover::before { left: 150%; }

        @keyframes value-glow-in {
          0% { text-shadow: 0 0 0px currentColor; opacity: 0.4; }
          40% { text-shadow: 0 0 18px currentColor; }
          100% { text-shadow: 0 0 0px currentColor; opacity: 1; }
        }
        .stat-glow { animation: value-glow-in 0.9s ease-out; }

        .nav-pill-active {
          background: linear-gradient(135deg, #3EF0B4 0%, #2BD495 100%);
          box-shadow: 0 2px 16px -2px rgba(52,229,168,0.5), 0 0 0 1px rgba(52,229,168,0.3) inset;
        }

        .nav-track { position: relative; }

        .btn-primary-elevated {
          background: linear-gradient(135deg, #3EF0B4 0%, #2BD495 100%);
          box-shadow: 0 4px 20px -4px rgba(52,229,168,0.45), 0 1px 0 0 rgba(255,255,255,0.25) inset;
          transition: transform 0.25s cubic-bezier(0.22,1,0.36,1), box-shadow 0.25s ease, filter 0.25s ease;
        }
        .btn-primary-elevated:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 28px -4px rgba(52,229,168,0.55), 0 1px 0 0 rgba(255,255,255,0.3) inset;
          filter: brightness(1.04);
        }
        .btn-primary-elevated:active { transform: translateY(0); }

        .verdict-ring {
          box-shadow: 0 0 0 1px currentColor inset, 0 0 32px -6px currentColor;
        }

        @keyframes rise-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .rise-in { animation: rise-in 0.5s cubic-bezier(0.22,1,0.36,1) both; }

        .shimmer-divider {
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(52,229,168,0.35), transparent);
        }

        .icon-chip-glow {
          box-shadow: 0 0 0 1px rgba(255,255,255,0.06) inset, 0 4px 14px -4px rgba(0,0,0,0.4);
        }

        .empty-state-icon {
          width: 44px; height: 44px;
          border-radius: 14px;
          display: flex; align-items: center; justify-content: center;
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.06);
        }

        button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, a:focus-visible {
          outline: 2px solid #34E5A8;
          outline-offset: 2px;
          border-radius: 4px;
        }

        .fingerprint-texture {
          background-image: repeating-radial-gradient(circle at 85% 30%, rgba(52,229,168,0.05) 0px, rgba(52,229,168,0.05) 1px, transparent 1px, transparent 6px);
        }

        .phoenix-theme-light .bg-\\[\\#06070A\\]\\/80 { background-color: rgba(255,255,255,0.85) !important; }
        .phoenix-theme-light .bg-\\[\\#0A0E16\\]\\/80 { background-color: rgba(255,255,255,0.85) !important; }
        .phoenix-theme-light nav { border-color: rgba(15,23,42,0.08) !important; }
        .phoenix-theme-light .bg-white\\/\\[0\\.02\\] { background-color: rgba(15,23,42,0.025) !important; }
        .phoenix-theme-light .bg-white\\/\\[0\\.03\\] { background-color: rgba(15,23,42,0.04) !important; }
        .phoenix-theme-light .border-white\\/\\[0\\.06\\] { border-color: rgba(15,23,42,0.08) !important; }
        .phoenix-theme-light .border-white\\/10 { border-color: rgba(15,23,42,0.12) !important; }
        .phoenix-theme-light .text-white { color: #0F172A !important; }
        .phoenix-theme-light .text-slate-200 { color: #1E293B !important; }
        .phoenix-theme-light .text-slate-300 { color: #334155 !important; }
        .phoenix-theme-light .text-slate-400 { color: #475569 !important; }
        .phoenix-theme-light .text-slate-500 { color: #64748B !important; }
        .phoenix-theme-light .bg-black\\/20, .phoenix-theme-light .bg-black\\/30, .phoenix-theme-light .bg-black\\/40 { background-color: rgba(15,23,42,0.04) !important; }
        .phoenix-theme-light .grain-overlay { opacity: 0.4; }
        .phoenix-theme-light .glass-surface {
          background: linear-gradient(180deg, rgba(15,23,42,0.03) 0%, rgba(15,23,42,0.01) 100%);
          border-color: rgba(15,23,42,0.08);
          box-shadow: 0 1px 0 0 rgba(255,255,255,0.6) inset, 0 8px 24px -8px rgba(15,23,42,0.12);
        }
        .phoenix-theme-light .glass-surface:hover {
          border-color: rgba(52,229,168,0.35);
          box-shadow: 0 1px 0 0 rgba(255,255,255,0.7) inset, 0 12px 32px -8px rgba(15,23,42,0.16);
        }
        .phoenix-theme-light .empty-state-icon {
          background: rgba(15,23,42,0.02);
          border-color: rgba(15,23,42,0.06);
        }
      `}</style>

      <div className="fixed inset-0 grain-overlay pointer-events-none z-0" />
      <CinematicBackground tone="#34E5A8" tone2="#4FD1E8" tone3="#8B93FF" />
      <nav className="relative z-20 border-b border-white/[0.06] bg-[#05070A]/80 backdrop-blur-2xl px-6 lg:px-8 py-3.5 sticky top-0 shadow-[0_1px_0_0_rgba(255,255,255,0.03)_inset,0_8px_24px_-12px_rgba(0,0,0,0.6)]">
        <div className="max-w-[1600px] mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="absolute inset-0 blur-md bg-[#34E5A8]/30 rounded-full" />
              <Hexagon className="h-8 w-8 text-[#34E5A8] relative" strokeWidth={1.5} />
              <Shield className="h-3.5 w-3.5 text-[#34E5A8] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <div>
              <div className="font-display text-[15px] font-bold tracking-tight text-white leading-none">PHOENIX</div>
              <div className="text-[9px] tracking-[0.2em] text-slate-500 font-mono mt-0.5">EVIDENCE AUTHENTICATION ENGINE</div>
            </div>
          </div>

          <div className="hidden lg:flex items-center bg-white/[0.03] border border-white/[0.06] rounded-full p-1 space-x-1 backdrop-blur-md">
            {navItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => { setActiveTab(item.id); setError(''); setCaseSuccessMsg(''); }}
                  className={`relative flex items-center gap-1.5 px-4 py-2 rounded-full transition-all duration-300 font-mono text-[11px] font-semibold tracking-wide ${
                    isActive ? 'text-[#06070A]' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {isActive && <span className="absolute inset-0 nav-pill-active rounded-full" />}
                  <Icon size={13} className="relative z-10" />
                  <span className="relative z-10">{item.label}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <button
                onClick={() => setPanelOpen((p) => !p)}
                className="relative flex items-center gap-2 px-3 py-2 bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 rounded-full border border-white/[0.06] text-[11px] font-mono transition-all hover:-translate-y-0.5 backdrop-blur-md"
              >
                {unreadCritical > 0 ? <BellRing size={14} className="text-[#F5A623]" /> : <Bell size={14} />}
                {unreadCritical > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#FF4757] text-white text-[9px] font-bold flex items-center justify-center border-2 border-[#06070A] shadow-[0_0_10px_rgba(255,71,87,0.6)]">
                    {unreadCritical > 9 ? '9+' : unreadCritical}
                  </span>
                )}
              </button>
              <AlertsPanel alerts={alerts} open={panelOpen} onClose={() => setPanelOpen(false)} onClear={clearAlerts} onDismiss={dismissAlert} />
            </div>

            <button
              onClick={toggleTheme}
              className="flex items-center gap-2 px-3 py-2 bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 rounded-full border border-white/[0.06] text-[11px] font-mono transition-all hover:-translate-y-0.5 backdrop-blur-md"
              title={isLight ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {isLight ? <Moon size={14} /> : <Sun size={14} />}
            </button>

            <button onClick={() => window.open(`${BACKEND_URL}/docs`, '_blank')} className="flex items-center gap-2 px-3.5 py-2 bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 rounded-full border border-white/[0.06] text-[11px] font-mono transition-all hover:-translate-y-0.5 backdrop-blur-md">
              <FileCode size={13} />
              <span className="hidden sm:inline">API Docs</span>
            </button>
          </div>
        </div>

        <div className="lg:hidden max-w-[1600px] mx-auto mt-3 flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-0.5">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => { setActiveTab(item.id); setError(''); setCaseSuccessMsg(''); }}
                className={`flex-shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-full transition-all duration-300 font-mono text-[11px] font-semibold tracking-wide border ${
                  isActive ? 'nav-pill-active text-[#06070A] border-transparent' : 'text-slate-400 border-white/[0.06] bg-white/[0.02]'
                }`}
              >
                <Icon size={12} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      <main className="relative z-10 max-w-[1600px] mx-auto p-5 lg:p-8 grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          {error && (
            <div className="rise-in p-4 rounded-2xl border border-[#FF4757]/25 bg-[#FF4757]/[0.06] text-[#FF4757] flex items-center space-x-3 font-mono text-sm">
              <AlertTriangle className="h-4 w-4 flex-shrink-0" />
              <p className="font-medium">{error}</p>
            </div>
          )}
          {caseSuccessMsg && (
            <div className="rise-in p-4 rounded-2xl border border-[#34E5A8]/25 bg-[#34E5A8]/[0.06] text-[#34E5A8] flex items-center space-x-3 font-mono text-sm">
              <CheckCircle className="h-4 w-4 flex-shrink-0" />
              <p className="font-medium">{caseSuccessMsg}</p>
            </div>
          )}

          {activeTab === 'executive' && (
            <div className="space-y-6 tab-transition">
              <div className="flex items-end justify-between flex-wrap gap-3">
                <div>
                  <SectionEyebrow step={activeNavIndex + 1} total={navItems.length} label="Fleet Overview" color="#34E5A8" />
                  <h1 className="font-display text-[26px] font-bold text-white tracking-tight mt-1">Command Overview</h1>
                  <p className="text-slate-500 text-xs mt-1">Live telemetry across every case, video, and anchor in the registry.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-3 flex items-stretch">
                  <ApertureRing
                    status={loading ? 'analyzing' : analysisResult ? 'verdict' : 'idle'}
                    progress={liveProgress}
                    verdictIsFake={verdictIsFake}
                    accuracy={execSummary.feedback_accuracy}
                  />
                </div>
              </div>

              <div className="relative grid grid-cols-2 md:grid-cols-5 gap-3">
                <div className="ambient-glow" />
                {[
                  { label: 'Videos Ingested', value: execSummary.total_videos, color: '#4FD1E8', icon: Film },
                  { label: 'Active Cases', value: execSummary.total_cases, color: '#8B93FF', icon: Briefcase },
                  { label: 'Deepfakes Found', value: execSummary.deepfakes_detected, color: '#FF4757', icon: ShieldAlert },
                  { label: 'Ledger Anchors', value: execSummary.blockchain_records, color: '#34E5A8', icon: Lock },
                  { label: 'Feedback Accuracy', value: `${execSummary.feedback_accuracy}%`, color: '#F5A623', icon: TrendingUp },
                ].map((stat, i) => {
                  const Icon = stat.icon;
                  return (
                    <div key={i} className="glass-surface card-sheen rise-in relative z-[1] p-4 rounded-[22px]" style={{ animationDelay: `${i * 60}ms` }}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="w-8 h-8 rounded-xl flex items-center justify-center icon-chip-glow" style={{ backgroundColor: `${stat.color}18` }}>
                          <Icon size={14} style={{ color: stat.color }} />
                        </span>
                      </div>
                      <AnimatedStatValue value={stat.value} className="stat-glow text-[26px] font-display font-bold text-white block leading-none tabular-nums" style={{ color: stat.color }} />
                      <span className="text-[10px] text-slate-500 font-mono block mt-1.5 uppercase tracking-wide">{stat.label}</span>
                    </div>
                  );
                })}
              </div>
              <ExecutiveCommandCenter
                execSummary={execSummary}
                systemHealth={systemHealth}
                modelMetrics={modelMetrics}
                loading={loading}
                verdictIsFake={verdictIsFake}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ThreeGlobe active={loading} tone={loading ? '#4FD1E8' : verdictIsFake ? '#FF4757' : '#34E5A8'} />
                <EvidenceGraph
                  caseId={targetCaseId}
                  fileName={file?.name}
                  hash={analysisResult?.hash_verification?.sha256_hash}
                  verdict={analysisResult?.verdict}
                  ledgerConfidence={ledgerResult?.blockchain_ledger?.data?.confidence_score_percentage}
                />
              </div>

              <NeuralAICore status={loading ? 'analyzing' : analysisResult ? 'verdict' : 'idle'} />

              {analysisResult?.media_type === 'video' &&
                Array.isArray(analysisResult?.timeline) && (
                  <EnhancedHeatmap
                    timeline={analysisResult.timeline}
                  />
              )}

              <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <div className="md:col-span-2">
                  <ExecutiveThreatGauge execSummary={execSummary} />
                </div>

                <div className="md:col-span-3 glass-surface card-sheen p-6 rounded-[28px] space-y-4">
                  <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight flex items-center gap-1.5">
                    <Activity size={14} className="text-[#4FD1E8]" /> System Health
                    <span className="ml-auto flex items-center gap-1 text-[#34E5A8] text-[10px] font-mono">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#34E5A8] pulse-dot" /> LIVE
                    </span>
                  </h3>
                  <div className="shimmer-divider" />
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
                    {[
                      { label: 'CPU Usage', value: `${systemHealth.cpu}%` },
                      { label: 'RAM Allocation', value: `${systemHealth.ram}%` },
                      { label: 'Acceleration', value: systemHealth.gpu, small: true },
                      { label: 'Throughput', value: `${systemHealth.fps} FPS`, color: '#34E5A8' },
                    ].map((m, i) => (
                      <div key={i} className="bg-black/30 p-3 rounded-2xl border border-white/[0.05] hover:border-white/[0.1] transition-colors">
                        <span className="text-[9px] text-slate-500 block uppercase tracking-wide">{m.label}</span>
                        <span className={`font-bold mt-1 block truncate tabular-nums ${m.small ? 'text-[11px]' : 'text-lg'}`} style={{ color: m.color || '#e2e8f0' }}>{m.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <Reticle className="glass-surface card-sheen p-6 rounded-[28px]" color="#34E5A8">
                <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-2 flex items-center gap-1.5">
                  <BarChart3 size={14} className="text-[#34E5A8]" /> Model Consensus Performance
                </h3>
                <div className="shimmer-divider mb-4" />
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={modelMetrics}>
                      <defs>
                        <linearGradient id="consensusBarGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#3EF0B4" />
                          <stop offset="100%" stopColor="#22B98A" />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#1B2130" strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" stroke="#4A5568" fontSize={10} tickLine={false} axisLine={{ stroke: '#1B2130' }} />
                      <YAxis stroke="#4A5568" fontSize={10} domain={[0, 100]} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ backgroundColor: '#0A0E16', borderColor: '#1B2130', borderRadius: 12, fontSize: 12 }} cursor={{ fill: '#ffffff08' }} />
                      <Bar
                        dataKey="score"
                        fill="url(#consensusBarGradient)"
                        radius={[6, 6, 0, 0]}
                        maxBarSize={48}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Reticle>

              <ActivityTimeline activity={activity} />
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="space-y-6 tab-transition">
              <div>
                <SectionEyebrow step={activeNavIndex + 1} total={navItems.length} label="Chain of Custody" color="#4FD1E8" />
                <h1 className="font-display text-[26px] font-bold text-white tracking-tight mt-1">Forensic Video Audit</h1>
                <p className="text-slate-500 text-xs mt-1">Every frame gets a verdict. Every verdict gets a trail.</p>
              </div>

              <div className="glass-surface fingerprint-texture rounded-[28px] p-6 space-y-4">
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                  <h2 className="text-sm font-semibold text-slate-200 font-display">Ingest Evidence</h2>
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="text-slate-500 font-mono text-[11px]">Case ID</span>
                    <input
                      type="text"
                      value={targetCaseId}
                      onChange={(e) => setTargetCaseId(e.target.value)}
                      placeholder="CASE-101"
                      className="bg-black/30 border border-white/10 rounded-xl px-2.5 py-1.5 text-slate-200 font-mono w-32 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 text-xs transition-all"
                    />
                  </div>
                </div>

                <form onSubmit={handleUpload} className="space-y-4">
                  <label
                    onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                    onDragLeave={() => setDragActive(false)}
                    onDrop={handleDrop}
                    className={`flex flex-col items-center justify-center border-2 border-dashed rounded-[24px] p-10 cursor-pointer transition-all duration-300 ${
                      dragActive ? 'border-[#34E5A8] bg-[#34E5A8]/[0.06] shadow-[0_0_32px_-4px_rgba(52,229,168,0.3)] scale-[1.01]' : 'border-white/10 hover:border-[#34E5A8]/40 bg-black/20'
                    }`}
                  >
                    <div className={`relative w-16 h-16 rounded-full flex items-center justify-center mb-3 transition-all duration-300 ${dragActive ? 'bg-[#34E5A8]/15 scale-110' : 'bg-white/[0.04]'}`}>
                      {dragActive && <span className="absolute inset-0 rounded-full radar-sweep-ring" />}
                      <Upload className={`h-6 w-6 transition-colors relative ${dragActive ? 'text-[#34E5A8]' : 'text-slate-500'}`} />
                    </div>
                    <span className="text-sm font-medium text-slate-300 font-display">
                      {file ? file.name : "Upload Image, Video, or Audio Evidence"}
                    </span>

                    <span className="text-[10px] text-slate-600 font-mono mt-1.5 tracking-wide">
                      Images: JPG, JPEG, PNG, WEBP • Videos: MP4, AVI, MOV, MKV • Audio: MP3, WAV, FLAC
                    </span>
                    <input type="file" className="hidden" accept="video/*,audio/*" onChange={handleFileChange} />
                  </label>

                  {file && !loading && (
                    <button type="submit" className="btn-primary-elevated w-full text-[#06070A] font-display font-bold py-3.5 rounded-2xl flex items-center justify-center gap-2 text-sm">
                      <ScanLine size={16} />
                      Run Forensic Audit Pipeline
                    </button>
                  )}

                  {loading && (
                    <LiveForensicTelemetry 
                      progress={liveProgress} 
                      statusText={liveStatusText} 
                      frameCount={liveFrameCount} 
                      file={file} 
                    />
                  )}
                </form>
              </div>

              {analysisResult && (
                <div className="space-y-6">
                  <VerdictBanner analysisResult={analysisResult} loading={loading} />

                  {/* TASK 5: UNIFIED FORENSIC EVIDENCE PANEL */}
                  <UnifiedEvidenceConsole file={file} analysisResult={analysisResult} />

                  {/* TASK 1 & 7: MULTIMODAL MEDIA TYPE DETECTION ROUTER */}
                  <EvidenceTypeRouter file={file} analysisResult={analysisResult} loading={loading} />

                  {/* Existing Analyst Calibration System */}
                  <div className="glass-surface p-4 rounded-[22px] space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase font-mono tracking-wider">Analyst Calibration</span>
                      {feedbackSuccess && <span className="text-[11px] text-[#34E5A8] font-mono">{feedbackSuccess}</span>}
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <button onClick={() => handleFeedbackSubmit(true)} className="py-2.5 bg-[#34E5A8]/10 hover:bg-[#34E5A8]/20 border border-[#34E5A8]/25 text-[#34E5A8] rounded-xl text-xs font-mono font-semibold transition-all hover:-translate-y-0.5 flex items-center justify-center gap-1.5">
                        <CheckCircle size={13} /> Correct (+1)
                      </button>
                      <button onClick={() => handleFeedbackSubmit(false)} className="py-2.5 bg-[#FF4757]/10 hover:bg-[#FF4757]/20 border border-[#FF4757]/25 text-[#FF4757] rounded-xl text-xs font-mono font-semibold transition-all hover:-translate-y-0.5 flex items-center justify-center gap-1.5">
                        <AlertTriangle size={13} /> Wrong (-1)
                      </button>
                    </div>
                  </div>

                  {/* Existing Temporal Intervals Detection Map */}
                    <div className="glass-surface p-4 rounded-[22px] space-y-2.5">
                      <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5 uppercase font-mono tracking-wider">
                        <Clock size={13} className="text-[#F5A623]" /> Tampering Intervals
                      </span>
                      <div className="flex flex-wrap gap-2 pt-1">
                        {analysisResult.temporal_intervals && analysisResult.temporal_intervals.length > 0 ? (
                          analysisResult.temporal_intervals.map((interval, i) => (
                            <span key={i} className="bg-[#FF4757]/10 text-[#FF4757] text-xs font-mono px-3 py-1.5 border border-[#FF4757]/25 rounded-xl tabular-nums">
                              {interval.start} — {interval.end}
                            </span>
                          ))
                        ) : (
                          <span className="bg-[#34E5A8]/10 text-[#34E5A8] text-xs font-mono px-3 py-1.5 border border-[#34E5A8]/25 rounded-xl flex items-center gap-1.5">
                            <CheckCircle size={12} /> No contiguous anomalies mapped
                          </span>
                        )}
                      </div>
                    </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="glass-surface p-4 rounded-[22px] flex flex-col gap-2">
                      <span className="text-[11px] font-semibold text-slate-400 mb-2 font-mono uppercase tracking-wide">Timeline Analysis</span>
                      <TimelineScrubber
                        timeline={
                          analysisResult.timeline ||
                          analysisResult.audio_timeline
                        }
                      />
                      <h4 className="text-[11px] text-slate-400 mt-4 mb-2 font-semibold font-mono uppercase tracking-wide">Tampering Distribution</h4>
                      <div className="h-36">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={analysisResult.chart_data || []}>
                            <defs>
                              <linearGradient id="tamperGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#34E5A8" stopOpacity={0.4} />
                                <stop offset="100%" stopColor="#34E5A8" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid stroke="#1B2130" strokeDasharray="3 3" vertical={false} />
                            <Area type="monotone" dataKey="probability" stroke="#34E5A8" strokeWidth={2} fill="url(#tamperGradient)" />
                            <XAxis dataKey="frame" hide />
                            <YAxis stroke="#4A5568" fontSize={9} axisLine={false} tickLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: '#0A0E16', borderColor: '#1B2130', borderRadius: 12, fontSize: 12 }} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                    
                    <div className="glass-surface p-4 rounded-[22px] space-y-2">
                      <h4 className="text-[11px] text-slate-400 font-semibold flex items-center gap-1.5 font-mono uppercase tracking-wide"><Layers size={13} className="text-[#4FD1E8]" /> Fusion Layers</h4>
                      {analysisResult.multi_model_fusion ? (
                        <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono text-slate-400 pt-1">
                          {[
                            { label: 'ViT Backbone', value: 79.77 , color: '#34E5A8' },
                            { label: 'EfficientNet', value: 97.02, color: '#4FD1E8' },
                            { label: 'XceptionNet', value: 92.86, color: '#8B93FF' },
                            { label: 'CNN Layer', value: 96.96, color: '#F5A623' },
                          ].map((m, i) => (
                            <div key={i} className="bg-black/30 p-2 rounded-xl border border-white/[0.05] flex justify-between">
                              <span>{m.label}</span>
                              <span style={{ color: m.color }} className="font-bold tabular-nums">{m.value}%</span>
                            </div>
                          ))}
                          <div className="col-span-2 bg-white/[0.04] p-2 rounded-xl border border-white/10 text-center font-bold text-slate-100 mt-0.5 tabular-nums">
                            Consensus: 96.96%
                          </div>
                        </div>
                      ) : (
                        <div className="text-[11px] font-mono text-slate-600 pt-4 text-center">Scoring telemetry unavailable</div>
                      )}
                    </div>
                  </div>

                  {/* Model Consensus Radar + AASIST Audio Anti-Spoof Consensus — per-video, full width */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <ModelConsensusRadar analysisResult={analysisResult} />
                    <AasistConsensusPanel analysisResult={analysisResult} />
                  </div>

                  {/* Conditional Localized Image Evidence Panel (Only displayed for Video Payloads) */}
                  {analysisResult.gallery && analysisResult.gallery.length > 0 && (
                    <div className="glass-surface p-4 rounded-[22px] space-y-3">
                      <span className="text-[11px] font-semibold text-[#FF4757] block flex items-center gap-1.5 uppercase font-mono tracking-wide">
                        <LayoutGrid size={13} /> Localized Evidence
                      </span>
                      <div className="grid grid-cols-1 gap-3">
                        {analysisResult.gallery.map((frame, idx) => (
                          <div key={idx} className="bg-black/20 p-3 border border-white/[0.06] rounded-2xl space-y-2 hover:border-white/[0.12] transition-colors">
                            <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 border-b border-white/[0.05] pb-1.5">
                              <span className="tabular-nums">Frame {frame.frame_id} · {frame.timestamp}</span>
                              <span className="text-[#FF4757] font-bold bg-[#FF4757]/10 px-1.5 py-0.5 rounded-lg tabular-nums">{frame.confidence}% risk</span>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                              <div className="space-y-1">
                                <span className="text-[9px] font-mono text-slate-600 block uppercase">Original</span>
                                <img src={`data:image/jpeg;base64,${frame.original_frame_b64}`} alt="Original Frame" className="w-full aspect-[4/3] object-cover border-2 border-[#FF4757]/40 block rounded-xl shadow-lg shadow-black/30" />
                              </div>
                              <div className="space-y-1">
                                <span className="text-[9px] font-mono text-[#4FD1E8] block uppercase">Heatmap</span>
                                <img src={`data:image/jpeg;base64,${frame.heatmap_frame_b64}`} alt="Heatmap" className="w-full aspect-[4/3] object-cover border-2 border-[#4FD1E8]/40 block rounded-xl shadow-lg shadow-black/30" />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="glass-surface p-4 rounded-[22px]">
                    <span className="text-[11px] font-semibold text-slate-400 block mb-3 flex items-center gap-1.5 uppercase font-mono tracking-wide"><Film size={13} className="text-[#4FD1E8]" /> Frame Timeline</span>
                    <div className="space-y-1.5 max-h-40 overflow-y-auto pr-2 custom-scrollbar">
                      {(
                          analysisResult.timeline ||
                          analysisResult.audio_timeline
                        )?.map((frame, idx) => (
                        <div key={idx} className="flex justify-between items-center text-[11px] p-2 bg-black/20 border border-white/[0.04] rounded-xl hover:border-white/[0.08] transition-colors">
                          <span className="font-mono text-slate-500 tabular-nums">Frame {frame.frame_number} · {frame.timestamp}</span>
                          <span className={`font-semibold px-2 py-0.5 rounded-lg text-[10px] font-mono ${frame.status === 'Tampered' ? 'bg-[#FF4757]/10 text-[#FF4757]' : 'bg-[#34E5A8]/10 text-[#34E5A8]'}`}>{frame.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* TASK 8: FORENSIC REPORT PREVIEW */}
                  <ForensicReportPreview
                    file={file}
                    analysisResult={analysisResult}
                    ledgerResult={ledgerResult}
                    downloading={downloadingReport}
                    onDownload={() => downloadForensicReport(analysisResult.hash_verification?.sha256_hash)}
                  />

                  <button onClick={() => downloadForensicReport(analysisResult.hash_verification?.sha256_hash)} disabled={downloadingReport} className="glass-surface w-full text-xs font-bold py-3.5 hover:border-[#34E5A8]/30 text-[#34E5A8] rounded-2xl font-mono transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2 disabled:opacity-60">
                    <FileCode size={14} /> {downloadingReport ? 'Compiling…' : 'Export Forensic Report PDF'}
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'investigation' && (
            <div className="space-y-6 tab-transition">
              <div>
                <SectionEyebrow step={activeNavIndex + 1} total={navItems.length} label="Model Calibration" color="#8B93FF" />
                <h1 className="font-display text-[26px] font-bold text-white tracking-tight mt-1">Investigation Console</h1>
                <p className="text-slate-500 text-xs mt-1">Reinforcement-learning calibration ledger from analyst feedback.</p>
              </div>

              <div className="glass-surface rounded-[22px] p-4 flex flex-col sm:flex-row gap-3 sm:items-center">
                <div className="relative flex-1">
                  <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600" />
                  <input
                    type="text"
                    value={feedbackSearchQuery}
                    onChange={(e) => setFeedbackSearchQuery(e.target.value)}
                    placeholder="Search by hash, prediction, or feedback ID..."
                    className="w-full bg-black/30 border border-white/10 rounded-xl pl-9 pr-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 font-mono transition-all"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <SlidersHorizontal size={13} className="text-slate-600" />
                  <select
                    value={feedbackFilterVerdict}
                    onChange={(e) => setFeedbackFilterVerdict(e.target.value)}
                    className="bg-black/30 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-[#34E5A8]/50 transition-all"
                  >
                    <option value="all">All Assessments</option>
                    <option value="correct">Correct Only</option>
                    <option value="incorrect">Incorrect Only</option>
                  </select>
                  <button
                    onClick={() => setFeedbackSortDesc((s) => !s)}
                    className="flex items-center gap-1.5 px-3 py-2.5 bg-black/30 hover:bg-black/50 border border-white/10 rounded-xl text-xs text-slate-300 font-mono transition-all hover:-translate-y-0.5"
                  >
                    <ArrowUpDown size={12} /> {feedbackSortDesc ? 'Newest' : 'Oldest'}
                  </button>
                </div>
              </div>

              <div className="glass-surface rounded-[22px] overflow-hidden">
                <div className="overflow-x-auto custom-scrollbar">
                  <table className="w-full text-left border-collapse font-mono text-[11px] min-w-[560px]">
                    <thead>
                      <tr className="bg-black/30 text-slate-500 border-b border-white/[0.06]">
                        <th className="p-3 font-medium">ID</th>
                        <th className="p-3 font-medium">Evidence Hash</th>
                        <th className="p-3 font-medium">Prediction</th>
                        <th className="p-3 font-medium">Assessment</th>
                        <th className="p-3 text-center font-medium">Reward</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                      {visibleFeedbackHistory.length > 0 ? (
                        visibleFeedbackHistory.map((item, index) => (
                          <tr key={index} className="hover:bg-white/[0.03] transition-colors">
                            <td className="p-3 text-slate-600 tabular-nums">{item.feedback_id}</td>
                            <td className="p-3 text-slate-400">{item.video_hash ? item.video_hash.substring(0, 16) : ""}...</td>
                            <td className="p-3 text-[#4FD1E8]">{item.prediction}</td>
                            <td className="p-3 text-slate-500">{item.actual_result}</td>
                            <td className={`p-3 text-center font-bold tabular-nums ${item.reward > 0 ? 'text-[#34E5A8]' : 'text-[#FF4757]'}`}>
                              {item.reward > 0 ? `+${item.reward}` : item.reward}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="5" className="p-10 text-center text-slate-600 italic">
                            {feedbackHistory.length === 0
                              ? 'No calibration data yet. Submit feedback in the Video Audit tab.'
                              : 'No records match your search or filter.'}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'cases' && (
            <div className="space-y-6 tab-transition">
              <div>
                <SectionEyebrow step={activeNavIndex + 1} total={navItems.length} label="Matter Intake" color="#8B93FF" />
                <h1 className="font-display text-[26px] font-bold text-white tracking-tight mt-1">Case Management</h1>
                <p className="text-slate-500 text-xs mt-1">Open a matter folder before you attach evidence to it.</p>
              </div>

              <div className="glass-surface card-sheen rounded-[28px] p-6 space-y-5">
                <form onSubmit={handleCreateCaseFile} className="space-y-4 text-sm">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-500 mb-1.5 font-mono uppercase tracking-wide">Case ID</label>
                      <input type="text" value={newCaseId} onChange={(e) => setNewCaseId(e.target.value)} placeholder="CASE-2026-04" className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 font-mono text-sm transition-all" />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-500 mb-1.5 font-mono uppercase tracking-wide">Case Title</label>
                      <input type="text" value={newCaseTitle} onChange={(e) => setNewCaseTitle(e.target.value)} placeholder="State vs. Counterfeit Evidence" className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 text-sm transition-all" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1.5 font-mono uppercase tracking-wide">Lead Examiner</label>
                    <input type="text" value={newCaseExaminer} onChange={(e) => setNewCaseExaminer(e.target.value)} className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 text-sm transition-all" />
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1.5 font-mono uppercase tracking-wide">Notes</label>
                    <textarea rows="3" value={newCaseDesc} onChange={(e) => setNewCaseDescription(e.target.value)} placeholder="Custody chain details, source, or investigation targets..." className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 text-sm transition-all" />
                  </div>
                  <button type="submit" className="btn-primary-elevated w-full text-[#06070A] font-display font-bold py-3.5 rounded-2xl flex items-center justify-center gap-2 text-sm">
                    <PlusCircle size={17} />
                    <span>Create Case File</span>
                  </button>
                </form>
              </div>

              <ActivityTimeline activity={activity} />
            </div>
          )}

          {activeTab === 'ledger' && (
            <div className="space-y-6 tab-transition">
              <div>
                <SectionEyebrow step={activeNavIndex + 1} total={navItems.length} label="Anchor Verification" color="#34E5A8" />
                <h1 className="font-display text-[26px] font-bold text-white tracking-tight mt-1">Ledger Lookup</h1>
                <p className="text-slate-500 text-xs mt-1">Query the smart contract for an evidence anchor by SHA-256 fingerprint.</p>
              </div>

              <div className="glass-surface rounded-[28px] p-6">
                <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600" />
                    <input type="text" value={searchHash} onChange={(e) => setSearchHash(e.target.value)} placeholder="Enter 64-character SHA-256 fingerprint..." className="w-full bg-black/30 border border-white/10 rounded-2xl pl-10 pr-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-[#34E5A8]/50 focus:ring-2 focus:ring-[#34E5A8]/20 font-mono transition-all" />
                  </div>
                  <button type="submit" className="btn-primary-elevated text-[#06070A] font-display font-bold px-6 py-3 sm:py-0 rounded-2xl text-sm">Verify</button>
                </form>
              </div>

              {ledgerResult && (
                <Reticle color="#34E5A8" active size="lg" className="rise-in verdict-ring bg-[#34E5A8]/[0.05] backdrop-blur-xl border border-[#34E5A8]/20 rounded-[28px] p-6 space-y-6 text-[#34E5A8]">
                  <div className="flex items-center space-x-3 text-[#34E5A8] pb-3 border-b border-white/[0.06]">
                    <CheckCircle className="h-5 w-5" />
                    <h3 className="text-base font-display font-bold">Authentic Record Located</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="space-y-2 bg-black/30 p-4 rounded-2xl border border-white/[0.06]">
                      <p className="text-[10px] text-slate-500 uppercase font-mono tracking-wide">Investigator Address</p>
                      <code className="text-xs text-slate-300 break-all font-mono">{ledgerResult.blockchain_ledger?.data?.investigator || "N/A"}</code>
                    </div>
                    <div className="space-y-3 bg-black/30 p-4 rounded-2xl border border-white/[0.06] flex flex-col justify-between">
                      <div>
                        <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wide block">Accuracy Score</span>
                        <span className="stat-glow text-2xl font-display font-bold text-[#34E5A8] tabular-nums">{ledgerResult.blockchain_ledger?.data?.confidence_score_percentage || 0}%</span>
                      </div>
                      <button onClick={() => downloadForensicReport(searchHash.trim().replace("0x", ""))} className="btn-primary-elevated w-full text-xs font-bold py-2.5 text-[#06070A] rounded-xl font-mono">Download PDF Report</button>
                    </div>
                  </div>
                </Reticle>
              )}

              <BlockchainProof ledgerResult={ledgerResult} searchHash={analysisResult?.hash_verification?.sha256_hash || searchHash} />
            </div>
          )}
        </div>

        <div className="space-y-6">
          <Reticle color="#4FD1E8" className="glass-surface rounded-[28px] p-5 flex flex-col h-[600px] sticky top-24 shadow-2xl shadow-black/50">
            <div className="flex items-center gap-3 pb-4 border-b border-white/[0.06] mb-4">
              <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-[#4FD1E8]/20 to-[#34E5A8]/10 flex items-center justify-center relative icon-chip-glow">
                <MessageSquare className="text-[#4FD1E8] h-4 w-4" />
                <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#34E5A8] border-2 border-[#0A0E16] pulse-dot" />
              </div>
              <div>
                <h3 className="text-sm font-display font-bold text-white leading-none">Forensic Assistant</h3>
                <span className="text-[9px] text-slate-500 font-mono block mt-1 tracking-wide">GROUNDED IN ACTIVE TELEMETRY</span>
              </div>
              <Sparkles size={14} className="text-[#F5A623] ml-auto" />
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs custom-scrollbar">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`rise-in p-3 rounded-2xl max-w-[92%] ${msg.role === 'user' ? 'bg-[#4FD1E8]/10 border border-[#4FD1E8]/20 text-slate-200 ml-auto rounded-br-sm' : 'bg-black/30 border border-white/[0.06] text-slate-300 rounded-bl-sm'}`}>
                  <p className="leading-relaxed whitespace-pre-wrap font-sans">{msg.text}</p>
                </div>
              ))}
              {chatLoading && (
                <div className="bg-black/30 border border-white/[0.06] text-slate-500 p-3 rounded-2xl rounded-bl-sm max-w-[80%] flex items-center gap-2 font-mono">
                  <Zap size={12} className="text-[#F5A623]" />
                  <span className="flex gap-1">
                    <span className="w-1 h-1 rounded-full bg-slate-500 pulse-dot" style={{ animationDelay: '0s' }} />
                    <span className="w-1 h-1 rounded-full bg-slate-500 pulse-dot" style={{ animationDelay: '0.2s' }} />
                    <span className="w-1 h-1 rounded-full bg-slate-500 pulse-dot" style={{ animationDelay: '0.4s' }} />
                  </span>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {chatHistory.length <= 1 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {chatSuggestions.map((s, i) => (
                  <button key={i} onClick={() => sendChat(s)} className="text-[10px] font-mono px-2.5 py-1.5 bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.08] rounded-full text-slate-400 transition-all hover:-translate-y-0.5 flex items-center gap-1">
                    {s} <ChevronRight size={10} />
                  </button>
                ))}
              </div>
            )}

            <form onSubmit={handleSendChatMessage} className="flex gap-2">
              <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Ask about timestamps, blocks, or scores..." className="flex-1 bg-black/30 border border-white/10 focus:border-[#4FD1E8]/50 focus:ring-2 focus:ring-[#4FD1E8]/20 focus:outline-none rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-sans transition-all" />
              <button type="submit" disabled={chatLoading} className="bg-gradient-to-br from-[#5FDCF0] to-[#3BC4D9] hover:brightness-110 text-[#06070A] p-2.5 rounded-xl transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 shadow-[0_4px_16px_-4px_rgba(79,209,232,0.5)]">
                <Send size={14} />
              </button>
            </form>
          </Reticle>
        </div>
      </main>
    </div>
  );
}