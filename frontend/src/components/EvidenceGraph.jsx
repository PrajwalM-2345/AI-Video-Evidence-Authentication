// src/components/EvidenceGraph.jsx
// ============================================================
// NEW FEATURE — Evidence Graph
// A force-simulated node graph (D3-force, already available in
// this environment as part of the d3 bundle) showing how a Case,
// its uploaded Video, the resulting Hash, and the Ledger Anchor
// relate to each other. Every node/edge shown is derived from
// REAL fields already present on analysisResult / ledgerResult /
// targetCaseId in App.jsx — nothing here invents relationships
// that don't exist in the data model.
//
// Usage (additive — call from wherever you want it rendered,
// passing the same state App.jsx already holds):
//   <EvidenceGraph
//     caseId={targetCaseId}
//     fileName={file?.name}
//     hash={analysisResult?.hash_verification?.sha256_hash}
//     verdict={analysisResult?.verdict}
//     ledgerConfidence={ledgerResult?.blockchain_ledger?.data?.confidence_score_percentage}
//   />
// ============================================================
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Briefcase, Film, Fingerprint, Lock, HelpCircle } from 'lucide-react';

export default function EvidenceGraph({ caseId, fileName, hash, verdict, ledgerConfidence, height = 260 }) {
  const svgRef = useRef(null);
  const [dims, setDims] = useState({ w: 480, h: height });
  const wrapRef = useRef(null);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDims((d) => ({ ...d, w: entry.contentRect.width || d.w }));
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const nodes = [];
  const links = [];

  nodes.push({ id: 'case', label: caseId || 'No case selected', kind: 'case' });
  if (fileName) {
    nodes.push({ id: 'video', label: fileName, kind: 'video' });
    links.push({ source: 'case', target: 'video' });
  }
  if (hash) {
    nodes.push({ id: 'hash', label: `${hash.substring(0, 10)}...`, kind: 'hash' });
    links.push({ source: 'video', target: 'hash' });
  }
  if (ledgerConfidence !== undefined && ledgerConfidence !== null) {
    nodes.push({ id: 'ledger', label: `Anchor · ${ledgerConfidence}%`, kind: 'ledger' });
    links.push({ source: 'hash', target: 'ledger' });
  }

  const isEmpty = nodes.length <= 1;

  useEffect(() => {
    if (isEmpty || !svgRef.current) return;
    const { w, h } = dims;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simNodes = nodes.map((n) => ({ ...n }));
    const simLinks = links.map((l) => ({ ...l }));

    const color = {
      case: '#8B93FF',
      video: '#4FD1E8',
      hash: '#F5A623',
      ledger: '#34E5A8',
    };

    const sim = d3
      .forceSimulation(simNodes)
      .force('link', d3.forceLink(simLinks).id((d) => d.id).distance(90))
      .force('charge', d3.forceManyBody().strength(-220))
      .force('center', d3.forceCenter(w / 2, h / 2))
      .force('collide', d3.forceCollide(46));

    const link = svg
      .append('g')
      .selectAll('line')
      .data(simLinks)
      .join('line')
      .attr('stroke', '#ffffff22')
      .attr('stroke-width', 1.5);

    const node = svg
      .append('g')
      .selectAll('g')
      .data(simNodes)
      .join('g')
      .call(
        d3
          .drag()
          .on('start', (event, d) => {
            if (!event.active) sim.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
          })
          .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
          .on('end', (event, d) => {
            if (!event.active) sim.alphaTarget(0);
            d.fx = null; d.fy = null;
          })
      );

    node
      .append('circle')
      .attr('r', 22)
      .attr('fill', (d) => `${color[d.kind]}22`)
      .attr('stroke', (d) => color[d.kind])
      .attr('stroke-width', 1.5);

    node
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 42)
      .attr('font-size', 9)
      .attr('font-family', 'IBM Plex Mono, monospace')
      .attr('fill', '#94A3B8')
      .text((d) => (d.label.length > 18 ? d.label.substring(0, 18) + '…' : d.label));

    sim.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);
      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    return () => sim.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dims.w, dims.h, caseId, fileName, hash, ledgerConfidence, isEmpty]);

  const iconFor = (kind) => ({ case: Briefcase, video: Film, hash: Fingerprint, ledger: Lock }[kind] || HelpCircle);

  return (
    <div className="glass-surface rounded-[28px] p-5" ref={wrapRef}>
      <h3 className="text-[13px] font-semibold text-slate-200 font-display tracking-tight mb-1">
        Evidence Relationship Graph
      </h3>
      <p className="text-[10px] text-slate-600 font-mono mb-3">
        Case → Video → Hash → Ledger Anchor, built from live case/audit state
      </p>
      {isEmpty ? (
        <div className="text-center text-[11px] font-mono text-slate-600 py-10 italic">
          No linked evidence yet. Select a case and run an audit to populate this graph.
        </div>
      ) : (
        <svg ref={svgRef} width="100%" height={dims.h} viewBox={`0 0 ${dims.w} ${dims.h}`} />
      )}
      <div className="flex flex-wrap gap-3 mt-2 pt-2 border-t border-white/[0.05]">
        {[
          { kind: 'case', label: 'Case' },
          { kind: 'video', label: 'Video' },
          { kind: 'hash', label: 'Hash' },
          { kind: 'ledger', label: 'Ledger' },
        ].map(({ kind, label }) => {
          const Icon = iconFor(kind);
          const c = { case: '#8B93FF', video: '#4FD1E8', hash: '#F5A623', ledger: '#34E5A8' }[kind];
          return (
            <span key={kind} className="flex items-center gap-1 text-[9px] font-mono text-slate-500">
              <Icon size={10} style={{ color: c }} /> {label}
            </span>
          );
        })}
      </div>
    </div>
  );
}
