'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import CodeMirror, { ReactCodeMirrorRef } from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { EditorView } from '@codemirror/view';
import { Vim, vim } from '@replit/codemirror-vim';
import { AtSign, FileImage, GitCompareArrows, ImagePlus, Plus, Save, Shapes } from 'lucide-react';

import { CommutativeDiagramDialog } from '@/components/CommutativeDiagramDialog';
import { ExcalidrawDialog } from '@/components/ExcalidrawDialog';
import { MathMarkdown } from '@/components/MathMarkdown';
import { ReferencePicker } from '@/components/ReferencePicker';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import type { EntryDetail, EntryKind } from '@/lib/types';

const KINDS: { value: EntryKind; label: string }[] = [
  { value: 'ax', label: 'Axiom' }, { value: 'df', label: 'Definition' }, { value: 'rk', label: 'Remark' },
  { value: 'th', label: 'Theorem' }, { value: 'pb', label: 'Problem' },
];

let activeEditorClose: (() => void) | null = null;
Vim.defineEx('quit', 'q', () => activeEditorClose?.());

interface Props {
  open: boolean;
  entry: EntryDetail | null;
  folderId: string | null;
  initialKind?: EntryKind;
  insertIndex?: number | null;
  dark: boolean;
  onClose: () => void;
  onSaved: (entry: EntryDetail) => void;
}

function EditorDialogSession({ open, entry, folderId, initialKind = 'df', insertIndex = null, dark, onClose, onSaved }: Props) {
  const [working, setWorking] = useState<EntryDetail | null>(entry);
  const [title, setTitle] = useState(entry?.title || '');
  const [tag, setTag] = useState(entry?.tag || '');
  const [kind, setKind] = useState<EntryKind>(entry?.kind || initialKind);
  const [header, setHeader] = useState(entry?.header || '');
  const [activeId, setActiveId] = useState(entry ? (entry.formulations.find((item) => item.main)?.id || entry.formulations[0]?.id) : 'new');
  const [drafts, setDrafts] = useState<Record<string, string>>(() => {
    if (!entry) return { new: '' };
    return Object.fromEntries([...entry.formulations, ...entry.supplements].map((item) => [item.id, item.content || '']));
  });
  const [preview, setPreview] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [imageWidth, setImageWidth] = useState(76);
  const [invertImage, setInvertImage] = useState(true);
  const [drawingOpen, setDrawingOpen] = useState(false);
  const [diagramOpen, setDiagramOpen] = useState(false);
  const [referenceOpen, setReferenceOpen] = useState(false);
  const editorRef = useRef<ReactCodeMirrorRef>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const editorExtensions = useMemo(
    () => [vim({ status: true }), markdown(), EditorView.lineWrapping],
    [],
  );

  const variants = useMemo(() => working ? [...working.formulations, ...working.supplements] : [], [working]);
  const active = variants.find((variant) => variant.id === activeId);
  const currentContent = drafts[activeId] || '';
  const hasMainProof = kind === 'th' && working?.supplements.some((item) => item.kind === 'pf' && item.main);
  const hasMainSolution = kind === 'pb' && working?.supplements.some((item) => item.kind === 'sl' && item.main);
  const reviewPolicy = kind === 'th'
    ? hasMainProof ? 'Statement · Proof of theorem' : 'Statement · proof review starts after a main proof is added'
    : kind === 'pb'
      ? hasMainSolution ? 'Solve' : 'Solve review starts after a main solution is added'
      : 'Statement';

  useEffect(() => {
    if (!open) return;
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.shiftKey && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        event.stopPropagation();
        if (working?.folder_id || folderId) setReferenceOpen(true);
      }
    };
    window.addEventListener('keydown', handler, { capture: true });
    return () => window.removeEventListener('keydown', handler, { capture: true });
  }, [folderId, open, working?.folder_id]);

  useEffect(() => {
    if (!open) return;
    const close = () => onClose();
    activeEditorClose = close;
    return () => {
      if (activeEditorClose === close) activeEditorClose = null;
    };
  }, [onClose, open]);

  const insertAtCursor = (text: string) => {
    const view = editorRef.current?.view;
    if (!view) {
      setDrafts((current) => ({ ...current, [activeId]: `${current[activeId] || ''}\n${text}\n` }));
      return;
    }
    const position = view.state.selection.main.head;
    view.dispatch({ changes: { from: position, insert: text }, selection: { anchor: position + text.length } });
    view.focus();
  };

  const uploadImage = async (file: File) => {
    if (!working) { setError('Save the entry before adding images.'); return; }
    setError('');
    const form = new FormData();
    form.set('image', file, file.name || 'pasted-image.png');
    form.set('alt', file.name.replace(/\.[^.]+$/, '') || 'Pasted image');
    form.set('width', String(imageWidth));
    form.set('invert_lightness', String(invertImage));
    try {
      const result = await api<{ markdown: string }>(`/api/entries/${working.id}/images`, { method: 'POST', body: form });
      insertAtCursor(result.markdown);
    } catch (reason) {
      setError((reason as Error).message);
    }
  };

  const handlePaste = (event: React.ClipboardEvent<HTMLDivElement>) => {
    const image = Array.from(event.clipboardData.files).find((file) => file.type.startsWith('image/'));
    if (!image) return;
    event.preventDefault();
    void uploadImage(image);
  };

  const save = async () => {
    setError('');
    if (!folderId && !working) { setError('Choose a folder first.'); return; }
    if (!title.trim() || !tag.trim()) { setError('Title and tag are required.'); return; }
    setSaving(true);
    try {
      if (!working) {
        const created = await api<EntryDetail>('/api/entries', {
          method: 'POST',
          body: JSON.stringify({ folder_id: folderId, index: insertIndex, kind, title, tag, header, content: drafts.new || '' }),
        });
        onSaved(created);
        onClose();
        return;
      }
      await api<EntryDetail>(`/api/entries/${working.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ title, tag, kind, header }),
      });
      await Promise.all(variants.map((variant) => api<EntryDetail>(`/api/entries/${working.id}/content/${variant.id}`, {
        method: 'PUT', body: JSON.stringify({ content: drafts[variant.id] || '' }),
      })));
      const refreshed = await api<EntryDetail>(`/api/entries/${working.id}`);
      setWorking(refreshed);
      onSaved(refreshed);
      onClose();
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const addFormulation = async () => {
    if (!working) return;
    const label = window.prompt('Alternative formulation label (for example, Category-theoretic)');
    if (!label) return;
    const subtag = window.prompt('Unique subtag (for example, category)');
    if (!subtag) return;
    try {
      const updated = await api<EntryDetail>(`/api/entries/${working.id}/formulations`, {
        method: 'POST', body: JSON.stringify({ label, subtag, content: '', main: false }),
      });
      const added = updated.formulations.at(-1)!;
      setWorking(updated);
      setDrafts((current) => ({ ...current, [added.id]: '' }));
      setActiveId(added.id);
    } catch (reason) { setError((reason as Error).message); }
  };

  const addSupplement = async () => {
    if (!working || !['th', 'pb'].includes(working.kind)) return;
    const supplementKind = working.kind === 'th' ? 'pf' : 'sl';
    const label = window.prompt(`${supplementKind === 'pf' ? 'Proof' : 'Solution'} label`, 'Main');
    if (!label) return;
    const hasOne = working.supplements.some((item) => item.kind === supplementKind);
    const subtag = hasOne ? window.prompt('Alternative subtag') : null;
    if (hasOne && !subtag) return;
    try {
      const updated = await api<EntryDetail>(`/api/entries/${working.id}/supplements`, {
        method: 'POST', body: JSON.stringify({ kind: supplementKind, label, subtag, content: '', main: !hasOne }),
      });
      const added = updated.supplements.at(-1)!;
      setWorking(updated);
      setDrafts((current) => ({ ...current, [added.id]: '' }));
      setActiveId(added.id);
    } catch (reason) { setError((reason as Error).message); }
  };

  const makeMain = async () => {
    if (!working || !active) return;
    try {
      const updated = await api<EntryDetail>(`/api/entries/${working.id}/variants/${active.id}`, {
        method: 'PATCH', body: JSON.stringify({ main: true }),
      });
      setWorking(updated);
    } catch (reason) { setError((reason as Error).message); }
  };

  return (
    <Dialog open={open} onOpenChange={(value, details) => {
      if (!value && details.reason === 'escape-key') return;
      if (!value) onClose();
    }}>
      <DialogContent className="editor-dialog" showCloseButton>
        <DialogHeader className="editor-dialog-header">
          <DialogTitle>{working ? `Edit ${working.title}` : 'New study entry'}</DialogTitle>
          <p className="dialog-subtitle">Markdown + MathJax · Vim keybindings are active in the editor.</p>
        </DialogHeader>
        <div className="metadata-grid editor-metadata">
          <label className="field-label title-field" htmlFor="entry-title">Title<Input id="entry-title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Fundamental theorem of algebra" /></label>
          <label className="field-label">Type<select value={kind} onChange={(event) => setKind(event.target.value as EntryKind)}>{KINDS.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
          <label className="field-label" htmlFor="entry-tag">Tag<Input id="entry-tag" value={tag} onChange={(event) => setTag(event.target.value.toLowerCase())} placeholder="fundamental-theorem" /></label>
          <label className="field-label header-field">Custom Markdown header<textarea value={header} onChange={(event) => setHeader(event.target.value)} placeholder="Prerequisites, source, or a short orientation note…" /></label>
        </div>
        <div className="editor-variant-slot">{working && (
          <div className="variant-bar">
            <div className="variant-tabs editor-variant-tabs">
              {variants.map((variant) => (
                <button key={variant.id} className={variant.id === activeId ? 'selected' : ''} onClick={() => setActiveId(variant.id)}>
                  {variant.kind ? `${variant.kind}: ` : ''}{variant.label}{variant.main ? ' · main' : ''}
                </button>
              ))}
            </div>
            <div className="variant-actions">
              {['ax', 'df', 'th'].includes(working.kind) && <Button size="xs" variant="ghost" onClick={addFormulation}><Plus /> Formulation</Button>}
              {['th', 'pb'].includes(working.kind) && <Button size="xs" variant="ghost" onClick={addSupplement}><Plus /> {working.kind === 'th' ? 'Proof' : 'Solution'}</Button>}
              {active && !active.main && <Button size="xs" variant="ghost" onClick={makeMain}>Make main</Button>}
            </div>
          </div>
        )}</div>
        <div className={`editor-workspace ${preview ? 'with-preview' : ''}`} onPasteCapture={handlePaste}>
          <div className="editor-column">
            <div className="editor-toolbar">
              <span className="vim-status">VIM</span>
              <Button size="xs" variant="ghost" onClick={() => fileInput.current?.click()} disabled={!working}><ImagePlus /> Image</Button>
              <Button size="xs" variant="ghost" onClick={() => setDrawingOpen(true)} disabled={!working}><Shapes /> Excalidraw</Button>
              <Button size="xs" variant="ghost" onClick={() => setDiagramOpen(true)} disabled={!working}><GitCompareArrows /> Commutative</Button>
              <Button size="xs" variant="ghost" aria-keyshortcuts="Control+Shift+K Meta+Shift+K" title="Insert reference (⌘/Ctrl+Shift+K)" onClick={() => setReferenceOpen(true)} disabled={!working?.folder_id && !folderId}><AtSign /> Reference</Button>
              <Button size="xs" variant={preview ? 'secondary' : 'ghost'} onClick={() => setPreview((value) => !value)}><FileImage /> Preview</Button>
              <span className="toolbar-spacer" />
              <label className="range-field compact">Image width <input type="range" min="20" max="100" value={imageWidth} onChange={(event) => setImageWidth(Number(event.target.value))} /><span>{imageWidth}%</span></label>
              <label className="tiny-check"><input type="checkbox" checked={invertImage} onChange={(event) => setInvertImage(event.target.checked)} /> dark invert</label>
              <input ref={fileInput} className="visually-hidden" type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => event.target.files?.[0] && void uploadImage(event.target.files[0])} />
            </div>
            <CodeMirror
              ref={editorRef}
              className="study-markdown-editor"
              value={currentContent}
              height="100%"
              theme={dark ? 'dark' : 'light'}
              extensions={editorExtensions}
              onChange={(value) => setDrafts((current) => ({ ...current, [activeId]: value }))}
              basicSetup={{ lineNumbers: true, foldGutter: true, autocompletion: true }}
              aria-label="Markdown editor with Vim keybindings"
            />
          </div>
          {preview && <div className="editor-preview">
            {header && <MathMarkdown content={header} className="content-header editor-header-preview" folderId={working?.folder_id || folderId || ''} />}
            <MathMarkdown content={currentContent} folderId={working?.folder_id || folderId || ''} />
          </div>}
        </div>
        <div className="review-policy"><strong>Review</strong><span>{reviewPolicy}</span></div>
        <div className="editor-error-slot">{error && <div className="form-error" role="alert">{error}</div>}</div>
        <div className="dialog-actions editor-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button onClick={save} disabled={saving}><Save /> {saving ? 'Saving…' : 'Save'}</Button></div>
        {working && <ExcalidrawDialog open={drawingOpen} entryId={working.id} dark={dark} onClose={() => setDrawingOpen(false)} onInsert={insertAtCursor} />}
        {working && <CommutativeDiagramDialog open={diagramOpen} entryId={working.id} onClose={() => setDiagramOpen(false)} onInsert={insertAtCursor} />}
        <ReferencePicker open={referenceOpen} folderId={working?.folder_id || folderId} onClose={() => setReferenceOpen(false)} onInsert={insertAtCursor} />
      </DialogContent>
    </Dialog>
  );
}

export function EditorDialog(props: Props) {
  return <EditorDialogSession key={`${props.open ? 'open' : 'closed'}:${props.entry?.id || 'new'}:${props.initialKind || 'df'}:${props.insertIndex ?? 'end'}`} {...props} />;
}
