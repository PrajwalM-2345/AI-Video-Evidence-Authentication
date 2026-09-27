// src/components/EvidenceTypeRouter.jsx
import React, { useMemo } from 'react';
import { Film, Waves, HelpCircle } from 'lucide-react';
import VideoTamperTimeline from './VideoTamperTimeline';
import AudioForensicConsole from './AudioForensicConsole';

const AUDIO_EXTENSIONS = ['mp3', 'wav', 'flac', 'm4a'];
const VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv'];

function extensionOf(name = '') {
  const parts = name.split('.');
  return parts.length > 1 ? parts.pop().toLowerCase() : '';
}

/**
 * Resolves which forensic console to render.
 * Priority: backend-declared media_type > file MIME type > filename extension.
 */
export function resolveMediaKind(file, analysisResult) {
  const backendKind = (analysisResult?.media_type || '').toLowerCase();
  if (backendKind === 'audio' || backendKind === 'video') return backendKind;

  const mime = file?.type || '';
  if (mime.startsWith('audio/')) return 'audio';
  if (mime.startsWith('video/')) return 'video';

  const ext = extensionOf(file?.name);
  if (AUDIO_EXTENSIONS.includes(ext)) return 'audio';
  if (VIDEO_EXTENSIONS.includes(ext)) return 'video';

  return 'unknown';
}

function RouterBadge({ kind }) {
  const config =
    kind === 'audio'
      ? { label: 'Audio Forensic Console', color: '#8B93FF', Icon: Waves }
      : kind === 'video'
      ? { label: 'Video Forensic Console', color: '#4FD1E8', Icon: Film }
      : { label: 'Unrecognized Media Type', color: '#F5A623', Icon: HelpCircle };
  const { label, color, Icon } = config;
  return (
    <div className="flex items-center gap-2 mb-3">
      <span
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-mono font-semibold tracking-wide"
        style={{ backgroundColor: `${color}12`, borderColor: `${color}40`, color }}
      >
        <Icon size={11} />
        {label}
      </span>
    </div>
  );
}

export default function EvidenceTypeRouter({ file, analysisResult, loading, audioUrl}) {
  const kind = useMemo(() => resolveMediaKind(file, analysisResult), [file, analysisResult]);

  if (!analysisResult) return null;

  return (
    <div className="tab-transition">
      <RouterBadge kind={kind} />

      {kind === 'audio' && <AudioForensicConsole analysisResult={analysisResult} file={file} loading={loading}  audioUrl={audioUrl} />}

      {kind === 'video' && (
        <VideoTamperTimeline
          timeline={analysisResult.timeline || analysisResult.audio_timeline}
          chartData={analysisResult.chart_data}
        />
      )}

      {kind === 'unknown' && (
        <div className="glass-surface rounded-[22px] p-6 text-center">
          <HelpCircle size={20} className="text-[#F5A623] mx-auto mb-2" />
          <p className="text-[11px] font-mono text-slate-500">
            Could not determine media type from the uploaded file or backend response. Supported formats: MP4, AVI, MOV, MKV, MP3, WAV, FLAC, M4A.
          </p>
        </div>
      )}
    </div>
  );
}
