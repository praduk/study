'use client';

/* oxlint-disable jsx-a11y/prefer-tag-over-role */
// An accessible inline SVG is correctly exposed with image semantics.

import { useEffect, useId, useMemo, useRef, useState, useSyncExternalStore } from 'react';

import { api } from '@/lib/api';
import { typesetWithMathJax } from '@/lib/mathjax';
import type { CommutativeArrow, CommutativeDiagram, CommutativeNode } from '@/lib/types';

const CELL_X = 180;
const CELL_Y = 112;
const PAD_X = 70;
const PAD_Y = 50;

function subscribeTheme(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  return () => observer.disconnect();
}

function getThemeSnapshot() {
  return document.documentElement.classList.contains('dark');
}

function Arrow({ arrow, nodes, markerId }: { arrow: CommutativeArrow; nodes: Map<string, CommutativeNode>; markerId: string }) {
  const source = nodes.get(arrow.source);
  const target = nodes.get(arrow.target);
  if (!source || !target) return null;
  const x1 = PAD_X + source.column * CELL_X;
  const y1 = PAD_Y + source.row * CELL_Y;
  const x2 = PAD_X + target.column * CELL_X;
  const y2 = PAD_Y + target.row * CELL_Y;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.sqrt(dx * dx + dy * dy) || 1;
  const trim = 28;
  const startX = x1 + (dx / length) * trim;
  const startY = y1 + (dy / length) * trim;
  const endX = x2 - (dx / length) * trim;
  const endY = y2 - (dy / length) * trim;
  const doubleOffsetX = (-dy / length) * 5;
  const doubleOffsetY = (dx / length) * 5;
  return (
    <g>
      <line
        x1={startX}
        y1={startY}
        x2={endX}
        y2={endY}
        className="diagram-arrow"
        strokeDasharray={arrow.dashed ? '7 6' : undefined}
        markerEnd={`url(#${markerId})`}
      />
      {arrow.double && <line x1={endX + doubleOffsetX} y1={endY + doubleOffsetY} x2={startX + doubleOffsetX} y2={startY + doubleOffsetY} className="diagram-arrow" strokeDasharray={arrow.dashed ? '7 6' : undefined} markerEnd={`url(#${markerId})`} />}
      {arrow.label && (
        <foreignObject x={(x1 + x2) / 2 - 60} y={(y1 + y2) / 2 - 28} width="120" height="40">
          <div className="diagram-arrow-label">{arrow.label}</div>
        </foreignObject>
      )}
    </g>
  );
}

export function DiagramGraphic({ diagram, width = 76 }: { diagram: CommutativeDiagram; width?: number }) {
  const container = useRef<HTMLElement>(null);
  const dark = useSyncExternalStore(subscribeTheme, getThemeSnapshot, () => false);
  const markerId = `arrowhead-${useId().replaceAll(':', '')}`;
  const nodeMap = useMemo(() => new Map(diagram.nodes.map((node) => [node.id, node])), [diagram.nodes]);
  const maxColumn = Math.max(...diagram.nodes.map((node) => node.column), 0);
  const maxRow = Math.max(...diagram.nodes.map((node) => node.row), 0);
  const viewWidth = PAD_X * 2 + maxColumn * CELL_X;
  const viewHeight = PAD_Y * 2 + maxRow * CELL_Y;
  useEffect(() => {
    const element = container.current;
    if (!element) return;
    void typesetWithMathJax(element).catch(() => undefined);
  }, [dark, diagram]);
  return (
    <figure ref={container} className="commutative-view" style={{ width: `${width}%` }}>
      <svg key={dark ? 'dark' : 'light'} viewBox={`0 0 ${viewWidth} ${viewHeight}`} role="img" aria-label={diagram.name}>
        <defs>
          <marker id={markerId} markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L0,6 L7,3 z" className="diagram-arrow-head" />
          </marker>
        </defs>
        {diagram.arrows.map((arrow, index) => <Arrow key={`${arrow.source}-${arrow.target}-${index}`} arrow={arrow} nodes={nodeMap} markerId={markerId} />)}
        {diagram.nodes.map((node) => (
          <foreignObject key={node.id} x={PAD_X + node.column * CELL_X - 65} y={PAD_Y + node.row * CELL_Y - 25} width="130" height="50">
            <div className="diagram-node">{node.label}</div>
          </foreignObject>
        ))}
      </svg>
      <figcaption>{diagram.name}</figcaption>
    </figure>
  );
}

export function CommutativeDiagramView({ id, width }: { id: string; width: number }) {
  const [diagram, setDiagram] = useState<CommutativeDiagram | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    api<CommutativeDiagram>(`/api/commutative/${id}.commutative.json`)
      .then(setDiagram)
      .catch((reason: Error) => setError(reason.message));
  }, [id]);
  if (error) return <div className="diagram-error">Diagram unavailable: {error}</div>;
  if (!diagram) return <div className="diagram-loading">Loading diagram…</div>;
  return <DiagramGraphic diagram={diagram} width={width} />;
}
