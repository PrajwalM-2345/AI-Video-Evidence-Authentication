// src/components/ThreeGlobe.jsx
// ============================================================
// NEW FEATURE — Three.js Globe
// A real WebGL instrument (not CSS/SVG) built with Three.js r128,
// the version already available in this environment.
// r128 constraint notes respected:
//   - No THREE.OrbitControls (not present in r128 build here) —
//     implemented a tiny manual pointer-drag orbit instead.
//   - No THREE.CapsuleGeometry (r142+) — this globe only needs
//     SphereGeometry + Points, so it's unaffected either way.
// Purely additive: exported standalone, does not import from or
// modify App.jsx. Wire in wherever ThreeGlobe reads best, e.g.
// swapped in for (or placed beside) the existing <ThreatGlobe />.
// Props are intentionally shaped to match data already flowing
// through the dashboard (loading / verdictIsFake) so it reflects
// real pipeline state rather than fabricated telemetry.
// ============================================================
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeGlobe({ active = false, tone = '#34E5A8', height = 220 }) {
  const mountRef = useRef(null);
  const stateRef = useRef({});

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const width = mount.clientWidth || 320;
    const h = height;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / h, 0.1, 100);
    camera.position.set(0, 0, 5.6);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    mount.appendChild(renderer.domElement);

    // Wireframe core sphere — the "authentication lattice"
    const coreGeo = new THREE.SphereGeometry(1.65, 24, 18);
    const coreMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(tone),
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    scene.add(core);

    // Point cloud shell — scattered "evidence nodes" across the surface
    const nodeCount = 260;
    const positions = new Float32Array(nodeCount * 3);
    for (let i = 0; i < nodeCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / nodeCount);
      const theta = Math.sqrt(nodeCount * Math.PI) * phi;
      const r = 1.68;
      positions[i * 3] = r * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    const pointsGeo = new THREE.BufferGeometry();
    pointsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const pointsMat = new THREE.PointsMaterial({
      color: new THREE.Color(tone),
      size: 0.035,
      transparent: true,
      opacity: 0.85,
    });
    const points = new THREE.Points(pointsGeo, pointsMat);
    scene.add(points);

    // Inner glow sphere
    const glowGeo = new THREE.SphereGeometry(1.2, 20, 16);
    const glowMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(tone), transparent: true, opacity: 0.06 });
    scene.add(new THREE.Mesh(glowGeo, glowMat));

    // Manual pointer-drag orbit (no OrbitControls available in r128 here)
    let dragging = false;
    let lastX = 0, lastY = 0;
    let rotY = 0, rotX = 0.15;

    const onDown = (e) => { dragging = true; lastX = e.clientX; lastY = e.clientY; };
    const onUp = () => { dragging = false; };
    const onMove = (e) => {
      if (!dragging) return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      rotY += dx * 0.005;
      rotX = Math.max(-0.6, Math.min(0.6, rotX + dy * 0.005));
      lastX = e.clientX; lastY = e.clientY;
    };
    renderer.domElement.addEventListener('pointerdown', onDown);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('pointermove', onMove);

    let raf;
    const animate = () => {
      const autoSpeed = active ? 0.004 : 0.0012;
      if (!dragging) rotY += autoSpeed;
      core.rotation.y = rotY;
      core.rotation.x = rotX;
      points.rotation.y = rotY;
      points.rotation.x = rotX;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(animate);
    };
    animate();

    stateRef.current = { renderer, scene, camera, mount };

    const handleResize = () => {
      const w = mount.clientWidth || 320;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointermove', onMove);
      renderer.domElement.removeEventListener('pointerdown', onDown);
      coreGeo.dispose(); coreMat.dispose();
      pointsGeo.dispose(); pointsMat.dispose();
      glowGeo.dispose(); glowMat.dispose();
      renderer.dispose();
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tone, active, height]);

  return (
    <div className="glass-surface rounded-[28px] p-5 flex flex-col items-center">
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-1 self-start">
        Evidence Lattice — Live Node Field
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-2 self-start">Drag to orbit · auto-rotates during analysis</p>
      <div ref={mountRef} style={{ width: '100%', height }} className="rounded-2xl overflow-hidden cursor-grab active:cursor-grabbing" />
      <span className="text-[10px] text-slate-500 font-mono mt-2">{active ? 'Live analysis in progress' : 'Ambient — no active scan'}</span>
    </div>
  );
}
