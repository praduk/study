'use client';

import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { Sigma } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { waitForMathJax } from '@/lib/mathjax';
import type {
  AppState,
  BinaryFiles,
  DataURL,
  ExcalidrawImperativeAPI,
  LibraryItems,
} from '@excalidraw/excalidraw/types';
import type { FileId, OrderedExcalidrawElement } from '@excalidraw/excalidraw/element/types';

const LazyExcalidraw = lazy(async () => {
  window.EXCALIDRAW_ASSET_PATH = '/vendor/excalidraw/fonts/';
  const excalidraw = await import('@excalidraw/excalidraw');
  return { default: excalidraw.Excalidraw };
});

function utf8Base64(value: string): string {
  const bytes = new TextEncoder().encode(value);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

interface Props {
  open: boolean;
  entryId: string;
  dark: boolean;
  onClose: () => void;
  onInsert: (markdown: string) => void;
}

export function ExcalidrawDialog({ open, entryId, dark, onClose, onInsert }: Props) {
  const [name, setName] = useState('Excalidraw diagram');
  const [width, setWidth] = useState(76);
  const [invert, setInvert] = useState(true);
  const [latex, setLatex] = useState('\\varphi: A \\to B');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const sceneRef = useRef<{
    elements: readonly OrderedExcalidrawElement[];
    appState: AppState;
    files: BinaryFiles;
  } | null>(null);
  const apiRef = useRef<ExcalidrawImperativeAPI | null>(null);
  const libraryRef = useRef<LibraryItems>([]);

  useEffect(() => {
    if (!open) return;
    api<{ libraryItems: LibraryItems }>('/api/excalidraw/library')
      .then((library) => {
        libraryRef.current = library.libraryItems || [];
        return apiRef.current?.updateLibrary({ libraryItems: libraryRef.current, merge: false });
      })
      .catch(() => undefined);
  }, [open]);

  const insertLatex = async () => {
    setError('');
    try {
      await waitForMathJax();
      const wrapper = await window.MathJax?.tex2svgPromise?.(latex, { display: true });
      const svg = wrapper?.querySelector('svg');
      if (!svg || !apiRef.current) throw new Error('MathJax is not ready yet.');
      const serialized = new XMLSerializer().serializeToString(svg);
      const dataURL = `data:image/svg+xml;base64,${utf8Base64(serialized)}` as DataURL;
      const fileId = crypto.randomUUID().replaceAll('-', '').slice(0, 40) as FileId;
      apiRef.current.addFiles([{ id: fileId, dataURL, mimeType: 'image/svg+xml', created: Date.now() }]);
      const existing = apiRef.current.getSceneElements();
      const element = {
        id: crypto.randomUUID().replaceAll('-', '').slice(0, 20), type: 'image', x: 120, y: 120,
        width: 260, height: 90, angle: 0, strokeColor: 'transparent', backgroundColor: 'transparent',
        fillStyle: 'solid', strokeWidth: 1, strokeStyle: 'solid', roughness: 0, opacity: 100,
        groupIds: [], frameId: null, index: null, roundness: null, seed: Math.floor(Math.random() * 2 ** 30),
        version: 1, versionNonce: Math.floor(Math.random() * 2 ** 30), isDeleted: false,
        boundElements: null, updated: Date.now(), link: null, locked: false, status: 'saved', fileId,
        scale: [1, 1], crop: null, customData: { studyLatex: latex },
      };
      apiRef.current.updateScene({
        elements: [...existing, element as unknown as OrderedExcalidrawElement],
        captureUpdate: 'IMMEDIATELY',
      });
    } catch (reason) {
      setError((reason as Error).message);
    }
  };

  const save = async () => {
    setError('');
    const scene = sceneRef.current;
    if (!scene?.elements.length) { setError('Draw something before saving.'); return; }
    setSaving(true);
    try {
      const excalidraw = await import('@excalidraw/excalidraw');
      const preview = await excalidraw.exportToBlob({
        elements: scene.elements,
        appState: { ...scene.appState, exportWithDarkMode: false },
        files: scene.files,
        mimeType: 'image/png',
        quality: 0.95,
      });
      const form = new FormData();
      form.set('scene', JSON.stringify({ type: 'excalidraw', version: 2, source: 'Study', ...scene }));
      form.set('preview', preview, 'diagram.png');
      form.set('name', name);
      form.set('width', String(width));
      form.set('invert_lightness', String(invert));
      const result = await api<{ markdown: string }>(`/api/entries/${entryId}/diagrams/excalidraw`, { method: 'POST', body: form });
      onInsert(result.markdown);
      onClose();
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => !value && onClose()}>
      <DialogContent className="excalidraw-dialog" showCloseButton>
        <DialogHeader><DialogTitle>Excalidraw</DialogTitle></DialogHeader>
        <div className="drawing-toolbar">
          <Input value={name} aria-label="Drawing name" onChange={(event) => setName(event.target.value)} />
          <div className="latex-insert"><Input value={latex} aria-label="LaTeX to insert" onChange={(event) => setLatex(event.target.value)} /><Button variant="outline" onClick={insertLatex}><Sigma /> Insert LaTeX</Button></div>
          <label className="range-field">Width <input type="range" min="20" max="100" value={width} onChange={(event) => setWidth(Number(event.target.value))} /><span>{width}%</span></label>
          <label className="tiny-check"><input type="checkbox" checked={invert} onChange={(event) => setInvert(event.target.checked)} /> invert HSL lightness in dark mode</label>
        </div>
        <div className="excalidraw-canvas">
          <Suspense fallback={<div className="canvas-loading">Loading drawing tools…</div>}>
            <LazyExcalidraw
              theme={dark ? 'dark' : 'light'}
              excalidrawAPI={(drawingApi) => {
                apiRef.current = drawingApi;
                void drawingApi.updateLibrary({ libraryItems: libraryRef.current, merge: false });
              }}
              onChange={(elements, appState, files) => { sceneRef.current = { elements, appState, files }; }}
              onLibraryChange={(items: readonly unknown[]) => {
                libraryRef.current = items as LibraryItems;
                void api('/api/excalidraw/library', {
                  method: 'PUT', body: JSON.stringify({ type: 'excalidrawlib', version: 2, libraryItems: items }),
                }).catch(() => undefined);
              }}
              UIOptions={{ canvasActions: { loadScene: false, saveToActiveFile: false, export: false } }}
            />
          </Suspense>
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Insert drawing'}</Button></div>
      </DialogContent>
    </Dialog>
  );
}
