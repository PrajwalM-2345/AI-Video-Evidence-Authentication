// src/components/motion-shim.jsx
// ============================================================
// NEW FEATURE — Framer Motion (shim)
// IMPORTANT CONSTRAINT: this environment's available React
// library list (recharts, lodash, d3, mathjs, three, etc.) does
// NOT include framer-motion, and it cannot be installed here.
// Rather than silently fail at build time, this file provides a
// drop-in replacement with the same day-to-day API surface:
//   import { motion, AnimatePresence } from './motion-shim';
//   <motion.div initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} transition={{duration:0.4}} />
// under the hood it uses the native Web Animations API (already
// available in the browser, zero extra dependency) to interpolate
// the same kind of props real framer-motion accepts (opacity, x,
// y, scale, rotate). This is additive only — App.jsx is untouched;
// use this import path anywhere motion.* / AnimatePresence is
// wanted going forward.
// ============================================================
import React, { useEffect, useRef, useState, createContext, useContext } from 'react';

const toTransform = (vals = {}) => {
  const parts = [];
  if (vals.x !== undefined) parts.push(`translateX(${vals.x}px)`);
  if (vals.y !== undefined) parts.push(`translateY(${vals.y}px)`);
  if (vals.scale !== undefined) parts.push(`scale(${vals.scale})`);
  if (vals.rotate !== undefined) parts.push(`rotate(${vals.rotate}deg)`);
  return parts.length ? parts.join(' ') : undefined;
};

function useMotionAnimate(ref, initial, animate, transition, exiting, onExitComplete) {
  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const dur = (transition?.duration ?? 0.35) * 1000;
    const easing = transition?.ease === 'linear' ? 'linear' : 'cubic-bezier(0.22,1,0.36,1)';
    const delay = (transition?.delay ?? 0) * 1000;

    const from = { opacity: initial?.opacity ?? 1, transform: toTransform(initial) || 'none' };
    const to = { opacity: animate?.opacity ?? 1, transform: toTransform(animate) || 'none' };

    const anim = el.animate([from, to], { duration: dur, delay, easing, fill: 'both' });

    if (exiting) {
      anim.onfinish = () => onExitComplete && onExitComplete();
    }

    return () => anim.cancel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(animate), exiting]);
}

function makeMotionComponent(tag) {
  return function MotionTag({ initial, animate, exit, transition, whileHover, whileTap, className, style, children, onClick, ...rest }) {
    const ref = useRef(null);
    const [exiting, setExiting] = useState(false);
    const exitCtx = useContext(ExitContext);

    useMotionAnimate(ref, initial, exiting ? exit : animate, transition, exiting, exitCtx?.onDone);

    const hoverHandlers = whileHover
      ? {
          onMouseEnter: (e) => {
            if (ref.current) Object.assign(ref.current.style, { transform: toTransform(whileHover), transition: 'transform 0.2s ease' });
          },
          onMouseLeave: (e) => {
            if (ref.current) Object.assign(ref.current.style, { transform: toTransform(animate) || 'none' });
          },
        }
      : {};

    const tapHandlers = whileTap
      ? {
          onMouseDown: () => { if (ref.current) ref.current.style.transform = toTransform(whileTap); },
          onMouseUp: () => { if (ref.current) ref.current.style.transform = toTransform(animate) || 'none'; },
        }
      : {};

    useEffect(() => {
      if (exitCtx) setExiting(true);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [exitCtx?.leaving]);

    const Tag = tag;
    return (
      <Tag ref={ref} className={className} style={{ ...style, opacity: initial?.opacity ?? 1 }} onClick={onClick} {...hoverHandlers} {...tapHandlers} {...rest}>
        {children}
      </Tag>
    );
  };
}

export const motion = new Proxy({}, { get: (_, tag) => makeMotionComponent(tag) });

const ExitContext = createContext(null);

export function AnimatePresence({ children }) {
  // Minimal viable version: renders children directly. Exit animations
  // fire via the ExitContext when a child unmounts naturally in React's
  // lifecycle is non-trivial without the real library's fiber hooks, so
  // this shim focuses on covering enter/hover/tap — the majority of
  // everyday usage — and gracefully no-ops extra exit choreography.
  return <>{children}</>;
}

export default { motion, AnimatePresence };
