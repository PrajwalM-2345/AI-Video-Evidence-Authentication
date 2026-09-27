// src/components/motion-shim.jsx
// Drop-in shim for framer-motion. Provides motion.*, AnimatePresence,
// and all the useXxx hooks App.jsx imports.

import React, { useEffect, useRef, useState, createContext, useContext } from 'react';

const toTransform = (vals = {}) => {
  const parts = [];
  if (vals.x !== undefined) parts.push(`translateX(${vals.x}px)`);
  if (vals.y !== undefined) parts.push(`translateY(${vals.y}px)`);
  if (vals.scale !== undefined) parts.push(`scale(${vals.scale})`);
  if (vals.rotate !== undefined) parts.push(`rotate(${vals.rotate}deg)`);
  return parts.length ? parts.join(' ') : undefined;
};

function makeMotionComponent(tag) {
  return function MotionComponent({
    children,
    layoutId,
    initial,
    animate,
    exit,
    transition,
    whileHover,
    whileTap,
    variants,
    layout,
    ...rest
  }) {
    const Tag = tag;
    return <Tag {...rest}>{children}</Tag>;
  };
}

export const motion = new Proxy({}, {
  get: (_, tag) => makeMotionComponent(tag),
});

const ExitContext = createContext(null);

export function AnimatePresence({ children }) {
  return <>{children}</>;
}

// ---------------- Hooks ----------------

export function useScroll(options = {}) {
  const [scrollY, setScrollY] = useState(0);
  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY || 0);
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  return { scrollY, scrollYProgress: { get: () => 0, set: () => {} } };
}

export function useVelocity() {
  return { get: () => 0, set: () => {} };
}

export function useDragControls() {
  return {
    start: () => {},
    stop: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
  };
}

export function useMotionValue(initial) {
  return { get: () => initial, set: () => {} };
}

export function useTransform(source, fn) {
  return { get: () => 0, set: () => {} };
}

export function useSpring(initial) {
  return { get: () => initial, set: () => {} };
}

export function useInView() {
  return true;
}

export function useAnimationFrame(cb) {
  if (typeof cb !== 'function') return;
  let id;
  let last = performance.now();
  const loop = (t) => {
    cb(t - last);
    last = t;
    id = requestAnimationFrame(loop);
  };
  id = requestAnimationFrame(loop);
  return () => cancelAnimationFrame(id);
}

export function useMotionTemplate() {
  return '';
}

export function useReducedMotion() {
  return false;
}

export function useWillChange() {
  return 'auto';
}

export default { motion, AnimatePresence };
