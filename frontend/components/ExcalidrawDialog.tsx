'use client';

import { lazy, Suspense, useEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import type {
  AppState,
  BinaryFiles,
  ExcalidrawImperativeAPI,
  LibraryItems,
} from '@excalidraw/excalidraw/types';
import type { OrderedExcalidrawElement } from '@excalidraw/excalidraw/element/types';

const LazyExcalidraw = lazy(async () => {
  window.EXCALIDRAW_ASSET_PATH = '/vendor/excalidraw/';
  const styles = new Promise<void>((resolve, reject) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/vendor/excalidraw/index.css';
    link.onload = () => resolve();
    link.onerror = () => reject(new Error('The drawing stylesheet could not be loaded.'));
    document.head.appendChild(link);
  });
  const [excalidraw] = await Promise.all([import('@excalidraw/excalidraw'), styles]);
  return { default: excalidraw.Excalidraw };
});

const LazyExcaliMathTools = lazy(() => import('@/components/ExcaliMathTools'));

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
  const [drawingApi, setDrawingApi] = useState<ExcalidrawImperativeAPI | null>(null);
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
      onInsert(`\n\n${result.markdown}\n\n`);
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
          <label className="range-field">Width <input type="range" min="20" max="100" value={width} onChange={(event) => setWidth(Number(event.target.value))} /><span>{width}%</span></label>
          <label className="tiny-check"><input type="checkbox" checked={invert} onChange={(event) => setInvert(event.target.checked)} /> invert HSL lightness in dark mode</label>
        </div>
        <div className="excalidraw-canvas">
          <Suspense fallback={<div className="canvas-loading">Loading drawing tools…</div>}>
            <LazyExcalidraw
              theme={dark ? 'dark' : 'light'}
              initialData={{ appState: { currentItemRoughness: 0, currentItemRoundness: 'sharp', currentItemFontFamily: 2, currentItemFillStyle: 'solid' } }}
              renderTopRightUI={() => drawingApi && <Suspense fallback={<span>Loading math tools…</span>}>
                <LazyExcaliMathTools drawingApi={drawingApi} dark={dark} />
              </Suspense>}
              excalidrawAPI={(drawingApi) => {
                apiRef.current = drawingApi;
                setDrawingApi(drawingApi);
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
