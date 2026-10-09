'use client';

import { useEffect, useRef, useState } from 'react';
import { TikzCdView } from '@/components/TikzCdView';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { getSharedMathMacros, renderEquationSvg } from '@/lib/mathjax';
import { DEFAULT_TIKZCD, macroPreamble, tikzCdMarkdown } from '@/lib/tikzcd';

interface Props {
  open: boolean;
  initialSource?: string;
  dark: boolean;
  onClose: () => void;
  onInsert: (markdown: string) => void;
}

function DiagramSession({ open, initialSource, dark, onClose, onInsert }: Props) {
  const [code, setCode] = useState(initialSource || DEFAULT_TIKZCD);
  const [dirty, setDirty] = useState(false);
  const [ready, setReady] = useState(false);
  const [diagnostics, setDiagnostics] = useState<string[]>([]);
  const [exportWarnings, setExportWarnings] = useState<string[]>([]);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const frame = useRef<HTMLIFrameElement>(null);
  const codeRef = useRef(code);
  const dirtyRef = useRef(false);
  const diagnosticsRef = useRef<string[]>([]);
  const exportRequest = useRef<{ id: string; resolve: (value: { code: string; warnings: string[]; changed: boolean }) => void } | null>(null);

  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (event.origin !== location.origin || event.source !== frame.current?.contentWindow
        || event.data?.channel !== 'study-quiver') return;
      if (event.data.type === 'exported' && event.data.id === exportRequest.current?.id) {
        exportRequest.current?.resolve({ code: event.data.code, warnings: event.data.warnings || [], changed: event.data.changed });
        exportRequest.current = null;
      }
      if (event.data.type === 'loaded' && event.data.source === codeRef.current) {
        setReady(true);
        const problems = Array.isArray(event.data.diagnostics) ? event.data.diagnostics.filter((d: unknown) => typeof d === 'string') : [];
        setDiagnostics(problems);
        diagnosticsRef.current = problems;
        dirtyRef.current = false; setDirty(false);
        setExportWarnings([]);
      }
      if (event.data.type === 'changed' && !dirtyRef.current && typeof event.data.code === 'string') {
        const warnings = event.data.warnings || [];
        setExportWarnings(warnings);
        if (warnings.length) return;
        codeRef.current = event.data.code; setCode(event.data.code);
        setPreview(null); setError('');
      }
    };
    window.addEventListener('message', receive);
    return () => window.removeEventListener('message', receive);
  }, []);

  const apply = () => {
    if (new TextEncoder().encode(codeRef.current).length > 65536) {
      setError('A diagram must be smaller than 64 KiB.');
      dirtyRef.current = true; setDirty(true); setReady(true); return;
    }
    setError(''); setReady(false); setPreview(null);
    frame.current?.contentWindow?.postMessage({ channel: 'study-quiver', type: 'load', source: codeRef.current,
      macros: macroPreamble(getSharedMathMacros()), theme: dark ? 'dark' : 'light' }, location.origin);
  };

  const insert = async () => {
    setSaving(true); setError('');
    try {
      let source = codeRef.current;
      if (ready && !dirtyRef.current && !diagnosticsRef.current.length) {
        const snapshot = await new Promise<{ code: string; warnings: string[]; changed: boolean }>((resolve, reject) => {
          const id = Array.from(crypto.getRandomValues(new Uint8Array(12)), n => n.toString(16).padStart(2, '0')).join('');
          const timer = setTimeout(() => { exportRequest.current = null; reject(new Error('The canvas did not respond. Try again.')); }, 5000);
          exportRequest.current = { id, resolve: (value) => { clearTimeout(timer); resolve(value); } };
          frame.current?.contentWindow?.postMessage({ channel: 'study-quiver', type: 'export', id }, location.origin);
        });
        if (snapshot.warnings.length) throw new Error(`These canvas features cannot be faithfully exported: ${snapshot.warnings.join(', ')}`);
        if (snapshot.changed) source = snapshot.code;
      }
      const { renderTikzCd } = await import('@/lib/tikz-renderer');
      await renderTikzCd(source);
      onInsert(tikzCdMarkdown(source)); onClose();
    } catch (reason) { setError((reason as Error).message); }
    finally { setSaving(false); }
  };

  return <Dialog open={open} onOpenChange={(value) => !value && !saving && onClose()}>
    <DialogContent className="tikzcd-dialog" showCloseButton={!saving}>
      <DialogHeader><DialogTitle>Commutative diagram · TikZ-CD</DialogTitle>
        <p className="dialog-subtitle">Double-click to place objects, drag between them to create arrows. Labels use Study’s MathJax macros.</p>
      </DialogHeader>
      <div className="tikzcd-editor-layout">
        <div className="quiver-frame-wrapper">
          <iframe ref={frame} title="Visual commutative diagram editor" src="/vendor/quiver/index.html"
            className={!ready || dirty || saving || diagnostics.length ? 'quiver-frame inactive' : 'quiver-frame'}
            onLoad={() => {
              const child = frame.current?.contentWindow;
              if (child) Object.defineProperty(child, 'studyRenderMath', { value: renderEquationSvg, configurable: true });
              apply();
            }} />
          {!ready && <div className="quiver-frame-notice">Loading diagram…</div>}
          {ready && dirty && <div className="quiver-frame-notice">Apply the edited code to continue working on the canvas.</div>}
          {!!diagnostics.length && <div className="quiver-frame-notice">Quiver could not fully import this code. Your source is preserved; use the code pane and rendered preview.</div>}
        </div>
        <div className="tikzcd-code-pane">
          <label className="field-label" htmlFor="tikzcd-code">TikZ-CD code</label>
          <textarea id="tikzcd-code" value={code} spellCheck={false} disabled={saving}
            onChange={(event) => { codeRef.current = event.target.value; setCode(event.target.value);
              dirtyRef.current = true; setDirty(true); setPreview(null); setExportWarnings([]); setError(''); }} />
          <div className="tikzcd-code-actions"><Button variant="outline" disabled={saving || !ready} onClick={apply}>Apply code to canvas</Button>
            <Button variant="outline" disabled={saving} onClick={() => setPreview(code)}>Render preview</Button></div>
          {diagnostics.length > 0 && <div className="safety-note">{diagnostics.join(' · ')}</div>}
          {exportWarnings.length > 0 && <div className="safety-note">These canvas features cannot be faithfully exported: {exportWarnings.join(', ')}. Your last valid code is preserved.</div>}
          <div className="tikzcd-code-preview">{preview ? <TikzCdView source={preview} /> : <p>Use Render preview to check the TikZ-CD result. Inserting stores the code directly in Markdown.</p>}</div>
        </div>
      </div>
      {error && <div className="form-error" role="alert">{error}</div>}
      <div className="dialog-actions"><Button variant="ghost" disabled={saving} onClick={onClose}>Cancel</Button>
        <Button disabled={saving} onClick={() => void insert()}>{saving ? 'Checking diagram…' : initialSource ? 'Replace diagram' : 'Insert TikZ-CD'}</Button></div>
    </DialogContent>
  </Dialog>;
}

export function CommutativeDiagramDialog(props: Props) {
  return <DiagramSession key={`${props.open}:${props.initialSource || 'new'}`} {...props} />;
}
