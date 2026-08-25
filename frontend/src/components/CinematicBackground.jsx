// src/components/CinematicBackground.jsx
// ============================================================
// NEW FEATURE — Cinematic Background
// A fixed, full-viewport ambient background layer: slow-drifting
// aurora-style gradient blobs + a very sparse particle field.
// Pure CSS/SVG (no external deps beyond what's already imported),
// z-indexed at -1 so it sits BEHIND the existing app content and
// never intercepts pointer events (pointer-events: none).
// Purely additive: mount it once near the root, above or below
// the existing `<div className="fixed inset-0 grain-overlay ...">`
// layer already in App.jsx — it does not replace or alter that
// element, it's a second, independent fixed layer.
// Respects prefers-reduced-motion by disabling the drift animation.
// ============================================================
import React from 'react';

export default function CinematicBackground({ tone = '#34E5A8', tone2 = '#4FD1E8', tone3 = '#8B93FF' }) {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: -1,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      <style>{`
        @keyframes cinematic-drift-1 {
          0%, 100% { transform: translate(-8%, -6%) scale(1); }
          50% { transform: translate(10%, 8%) scale(1.15); }
        }
        @keyframes cinematic-drift-2 {
          0%, 100% { transform: translate(12%, 10%) scale(1); }
          50% { transform: translate(-10%, -6%) scale(1.1); }
        }
        @keyframes cinematic-drift-3 {
          0%, 100% { transform: translate(-4%, 14%) scale(1); }
          50% { transform: translate(6%, -10%) scale(1.05); }
        }
        .cinematic-blob {
          position: absolute;
          border-radius: 9999px;
          filter: blur(90px);
          will-change: transform;
        }
        @media (prefers-reduced-motion: reduce) {
          .cinematic-blob { animation: none !important; }
        }
      `}</style>
      <div
        className="cinematic-blob"
        style={{
          width: '55vw', height: '55vw', top: '-10%', left: '-10%',
          background: `radial-gradient(circle, ${tone}14, transparent 70%)`,
          animation: 'cinematic-drift-1 26s ease-in-out infinite',
        }}
      />
      <div
        className="cinematic-blob"
        style={{
          width: '48vw', height: '48vw', bottom: '-15%', right: '-10%',
          background: `radial-gradient(circle, ${tone2}10, transparent 70%)`,
          animation: 'cinematic-drift-2 32s ease-in-out infinite',
        }}
      />
      <div
        className="cinematic-blob"
        style={{
          width: '38vw', height: '38vw', top: '35%', left: '55%',
          background: `radial-gradient(circle, ${tone3}0d, transparent 70%)`,
          animation: 'cinematic-drift-3 38s ease-in-out infinite',
        }}
      />
    </div>
  );
}
