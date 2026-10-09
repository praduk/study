'use client';

import { useEffect, useRef, useState } from 'react';
import {
  createImageElement, expressionLibrary, GraphPanel, LibraryPanel, shapeToExcalidrawElements,
  type ExcalimathMetadata, type GraphConfig, type LibraryShape,
} from '@excalimath/core';
import { CaptureUpdateAction } from '@excalidraw/excalidraw';
import type { BinaryFileData, ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types';
import type { OrderedExcalidrawElement } from '@excalidraw/excalidraw/element/types';
import { Button } from '@/components/ui/button';
import { renderEquationSvg } from '@/lib/mathjax';

type Tab = 'equation' | 'graph' | 'library';
type Preview = Awaited<ReturnType<typeof renderEquationSvg>>;

/** ExcaliMath panels and metadata, with Study's MathJax equation renderer. */
export default function ExcaliMathTools({ drawingApi, dark }: {
  drawingApi: ExcalidrawImperativeAPI;
  dark: boolean;
}) {
  const [tab, setTab] = useState<Tab | null>(null);
  const [latex, setLatex] = useState('\\varphi: A \\to B');
  const [graph, setGraph] = useState<GraphConfig | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [rendered, setRendered] = useState<(Preview & { latex: string }) | null>(null);
  const preview = rendered?.latex === latex ? rendered : null;
  const [error, setError] = useState('');
  const selectedRef = useRef<string | null>(null);

  useEffect(() => drawingApi.onChange((elements, state) => {
    const ids = Object.keys(state.selectedElementIds).filter((id) => state.selectedElementIds[id]);
    const id = ids.length === 1 ? ids[0] : null;
    if (id === selectedRef.current) return;
    selectedRef.current = id;
    setEditingId(null);
    setGraph(null);
    const selected = elements.find((element) => element.id === id);
    const data = selected?.customData;
    const source = data?.excalimath_latex ?? data?.studyLatex;
    if (typeof source === 'string') {
      setLatex(source);
      setEditingId(id);
      setTab('equation');
    } else if (data?.excalimath_type === 'graph' && typeof data.excalimath_graph_config === 'string') {
      try {
        setGraph(JSON.parse(data.excalimath_graph_config));
        setEditingId(id);
        setTab('graph');
      } catch { setError('This graph has invalid saved settings.'); }
    }
  }), [drawingApi]);

  useEffect(() => {
    if (tab !== 'equation') return;
    let cancelled = false;
    const timer = setTimeout(() => {
      setError('');
      if (!latex.trim()) return;
      void renderEquationSvg(latex).then((value) => {
        if (!cancelled) setRendered({ ...value, latex });
      }).catch((reason: Error) => { if (!cancelled) setError(reason.message); });
    }, 180);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [latex, tab]);

  const insertImage = (image: Preview, metadata: ExcalimathMetadata) => {
    const state = drawingApi.getAppState();
    const existing = drawingApi.getSceneElements();
    const previous = existing.find((element) => element.id === editingId);
    const { element, fileEntry } = createImageElement({
      ...image, metadata,
      x: previous?.x ?? -state.scrollX + state.width / (2 * state.zoom.value) - image.width / 2,
      y: previous?.y ?? -state.scrollY + state.height / (2 * state.zoom.value) - image.height / 2,
    });
    // Retain position, styling, groups and identity when updating an equation/graph.
    const updated = { ...previous, ...element,
      ...(previous ? { id: previous.id, angle: previous.angle, groupIds: previous.groupIds,
        frameId: previous.frameId, index: previous.index, opacity: previous.opacity,
        locked: previous.locked, link: previous.link, version: previous.version + 1,
        customData: { ...previous.customData, ...metadata } } : {}),
      crop: null,
    } as unknown as OrderedExcalidrawElement;
    selectedRef.current = updated.id;
    drawingApi.updateScene({
      elements: previous ? existing.map((item) => item.id === previous.id ? updated : item) : [...existing, updated],
      appState: { selectedElementIds: { [updated.id]: true } },
      captureUpdate: CaptureUpdateAction.IMMEDIATELY,
    });
    // Register after the element exists so Excalidraw immediately loads its image cache.
    drawingApi.addFiles([fileEntry as BinaryFileData]);
    setEditingId(updated.id);
  };

  const insertShape = (shape: LibraryShape) => {
    const state = drawingApi.getAppState();
    const prepared = shapeToExcalidrawElements({ ...shape, elements: shape.elements.map((element) => ({
      ...element, roughness: 0, roundness: null,
      ...(element.type === 'text' ? { fontFamily: 2 } : {}),
    })) },
      -state.scrollX + state.width / (2 * state.zoom.value) - 50,
      -state.scrollY + state.height / (2 * state.zoom.value) - 50);
    const elements = prepared.elements as unknown as OrderedExcalidrawElement[];
    drawingApi.updateScene({
      elements: [...drawingApi.getSceneElements(), ...elements],
      appState: { selectedElementIds: Object.fromEntries(elements.map((element) => [element.id, true])) },
      captureUpdate: CaptureUpdateAction.IMMEDIATELY,
    });
    drawingApi.addFiles(prepared.files as BinaryFileData[]);
  };

  return <>
    <Button size="sm" variant="outline" aria-expanded={tab !== null}
      onClick={() => setTab(tab ? null : 'equation')}>∑ ExcaliMath</Button>
    {tab && <aside className="study-excalimath-panel" aria-label="ExcaliMath tools">
      <div className="study-excalimath-tabs">
        {(['equation', 'graph', 'library'] as const).map((value) => <Button key={value}
          size="sm" variant={tab === value ? 'secondary' : 'ghost'}
          onClick={() => {
            if (value !== tab) { setEditingId(null); setGraph(null); }
            setTab(value); setError('');
          }}>
          {{ equation: 'Equation', graph: 'Graph', library: 'Shapes' }[value]}
        </Button>)}
        <Button size="sm" variant="ghost" aria-label="Close ExcaliMath" onClick={() => setTab(null)}>×</Button>
      </div>
      {tab === 'equation' && <div className="study-equation-panel">
        <label className="field-label">LaTeX equation<textarea value={latex}
          onChange={(event) => setLatex(event.target.value)} spellCheck={false} /></label>
        <p>Uses Study’s shared MathJax macros. Select an equation on the canvas to edit it.</p>
        <label className="field-label">Expression library<select value="" onChange={(event) => setLatex(event.target.value)}>
          <option value="" disabled>Choose an expression…</option>
          {expressionLibrary.map((item) => <option key={`${item.category}:${item.label}`} value={item.latex}>{item.category} · {item.label}</option>)}
        </select></label>
        <div className="study-equation-preview" aria-label="Equation preview">
          {/* Local SVG data URLs need no image optimization or network request. */}
          {/* oxlint-disable-next-line next/no-img-element */}
          {preview ? <img src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(preview.svg)}`} alt={latex} /> : 'Type an equation to preview it.'}
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}
        <Button disabled={!preview} onClick={() => preview && insertImage(preview, {
          excalimath_type: 'equation', excalimath_source: 'study-mathjax', excalimath_latex: latex,
        })}>{editingId ? 'Update equation' : 'Insert equation'}</Button>
        {editingId && <Button variant="ghost" onClick={() => {
          setEditingId(null);
          drawingApi.updateScene({ appState: { selectedElementIds: {} } });
        }}>New equation</Button>}
      </div>}
      {tab === 'graph' && <GraphPanel visible isDark={dark} editingConfig={graph} onClose={() => setTab(null)}
        onInsert={(config, svg, width, height) => {
          insertImage({ svg, width, height }, {
            excalimath_type: 'graph', excalimath_source: 'graph-panel', excalimath_graph_config: JSON.stringify(config),
          });
          setGraph(config);
        }} />}
      {tab === 'library' && <LibraryPanel visible isDark={dark} onClose={() => setTab(null)} onInsert={insertShape} />}
    </aside>}
  </>;
}
