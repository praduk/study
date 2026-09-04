'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore, type CSSProperties } from 'react';
import {
  BookOpen, Braces, Check, ChevronDown, ChevronRight, Download, FilePlus2, FolderInput,
  FolderPen, FolderPlus, FolderTree, GitBranch, Library, LoaderCircle, LogIn, LogOut, Menu,
  Moon, PanelLeftClose, PanelLeftOpen, Search, Plus, Sigma, Sun, Trash2,
} from 'lucide-react';

import { DeleteItemDialog, type DeleteTarget } from '@/components/DeleteItemDialog';
import { EditorDialog } from '@/components/EditorDialog';
import { ExportDialog } from '@/components/ExportDialog';
import { GitSyncDialog } from '@/components/GitSyncDialog';
import { MacrosDialog } from '@/components/MacrosDialog';
import { MathMarkdown } from '@/components/MathMarkdown';
import { MoveFolderDialog } from '@/components/MoveFolderDialog';
import { ReviewView } from '@/components/ReviewView';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useIsMobile } from '@/hooks/use-mobile';
import { api, setCsrfToken } from '@/lib/api';
import { configureMathJax } from '@/lib/mathjax';
import { readingVariantSelection } from '@/lib/reference-navigation';
import type { Bootstrap, EntryDetail, EntryKind, Folder, FolderNode, GitStatus } from '@/lib/types';

const KIND_LABEL: Record<EntryKind, string> = { ax: 'Axiom', df: 'Definition', rk: 'Remark', th: 'Theorem', pb: 'Problem' };
const ENTRY_KINDS = Object.entries(KIND_LABEL) as [EntryKind, string][];
interface DragPayload { type: 'folder' | 'entry'; id: string }
interface SearchResult { id: string; title: string; kind: EntryKind; canonical_tag: string; folder_id?: string }
interface DeleteResponse { deletion: { next_entry_id?: string | null; next_folder_id?: string | null } }

function subscribeTheme(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  return () => observer.disconnect();
}

function getThemeSnapshot() {
  return document.documentElement.classList.contains('dark');
}

function parseDrag(event: React.DragEvent): DragPayload | null {
  try { return JSON.parse(event.dataTransfer.getData('application/x-study-item')) as DragPayload; }
  catch { return null; }
}

function beginDrag(event: React.DragEvent, payload: DragPayload, label: string) {
  event.stopPropagation();
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('application/x-study-item', JSON.stringify(payload));
  const preview = document.createElement('div');
  preview.className = 'tree-drag-preview';
  preview.textContent = label;
  document.body.appendChild(preview);
  event.dataTransfer.setDragImage(preview, 12, 12);
  window.setTimeout(() => preview.remove(), 0);
}

function folderSubtreeIds(folderId: string, folders: Folder[]) {
  const result = new Set<string>([folderId]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const folder of folders) {
      if (folder.parent_id && result.has(folder.parent_id) && !result.has(folder.id)) {
        result.add(folder.id);
        changed = true;
      }
    }
  }
  return result;
}

function InsertionPoint({ parentFolderId, folderName, entryIndex, folderIndex, empty, onInsertEntry, onInsertFolder, onMove }: {
  parentFolderId: string | null;
  folderName: string;
  entryIndex?: number;
  folderIndex?: number;
  empty?: boolean;
  onInsertEntry: (folderId: string, index: number, kind: EntryKind) => void;
  onInsertFolder: (parentId: string | null, index: number) => void;
  onMove: (payload: DragPayload, destination: string | null, index: number) => void;
}) {
  const [open, setOpen] = useState(false);
  const allowsEntries = parentFolderId !== null && entryIndex !== undefined;
  const allowsFolders = folderIndex !== undefined;
  const position = entryIndex ?? folderIndex ?? 0;
  return <div
    className={`entry-insert-slot ${allowsEntries ? 'entry-slot' : ''} ${allowsFolders ? 'folder-slot' : ''} ${empty ? 'empty' : ''}`}
    onDragOver={(event) => { event.preventDefault(); event.stopPropagation(); event.currentTarget.classList.add('drop-target'); }}
    onDragLeave={(event) => event.currentTarget.classList.remove('drop-target')}
    onDrop={(event) => {
      event.preventDefault();
      event.stopPropagation();
      event.currentTarget.classList.remove('drop-target');
      const payload = parseDrag(event);
      if (payload?.type === 'entry' && allowsEntries) onMove(payload, parentFolderId, entryIndex);
      if (payload?.type === 'folder' && allowsFolders) onMove(payload, parentFolderId, folderIndex);
    }}
  >
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        className="entry-insert-trigger"
        aria-label={`${empty ? 'Add the first item' : 'Insert here'} in ${folderName} at position ${position + 1}`}
        title="Insert here"
      >
        <Plus aria-hidden="true" />
      </PopoverTrigger>
      <PopoverContent align="start" side="right" className="entry-insert-menu">
        <PopoverHeader>
          <PopoverTitle>{empty ? 'Add first item' : 'Insert here'}</PopoverTitle>
          <PopoverDescription>Choose what to add at this exact position.</PopoverDescription>
        </PopoverHeader>
        <div className="entry-kind-options">
          {allowsEntries && ENTRY_KINDS.map(([kind, label]) => <button key={kind} type="button" onClick={() => { setOpen(false); onInsertEntry(parentFolderId, entryIndex, kind); }}>
            <span className={`type-chip type-${kind}`}>{kind}</span><span>{label}</span>
          </button>)}
          {allowsFolders && <button type="button" onClick={() => { setOpen(false); onInsertFolder(parentFolderId, folderIndex); }}>
            <span className="folder-option-icon"><FolderPlus /></span><span>Folder</span>
          </button>}
        </div>
      </PopoverContent>
    </Popover>
  </div>;
}

function TreeNode({ node, selectedEntry, selectedFolder, expanded, readOnly, onToggle, onSelectEntry, onSelectFolder, onReviewToggle, onMove, onInsertEntry, onInsertFolder }: {
  node: FolderNode; selectedEntry: string | null; selectedFolder: string | null; expanded: Set<string>;
  readOnly: boolean;
  onToggle: (id: string) => void; onSelectEntry: (id: string, folderId: string) => void;
  onSelectFolder: (id: string) => void; onReviewToggle: (id: string, enabled: boolean) => void;
  onMove: (payload: DragPayload, destination: string | null, index: number) => void;
  onInsertEntry: (folderId: string, index: number, kind: EntryKind) => void;
  onInsertFolder: (parentId: string | null, index: number) => void;
}) {
  const open = expanded.has(node.id);
  const count = node.entries.length + node.children.reduce((sum, child) => sum + child.entries.length, 0);
  return <div className="tree-node">
    <div className={`tree-row folder-row ${selectedFolder === node.id ? 'selected-folder' : ''}`} draggable={!readOnly}
      onDragStart={readOnly ? undefined : (event) => beginDrag(event, { type: 'folder', id: node.id }, node.name)}
      onDragOver={readOnly ? undefined : (event) => { event.preventDefault(); event.stopPropagation(); event.currentTarget.classList.add('drop-target'); }}
      onDragLeave={(event) => event.currentTarget.classList.remove('drop-target')}
      onDrop={readOnly ? undefined : (event) => { event.preventDefault(); event.stopPropagation(); event.currentTarget.classList.remove('drop-target'); const payload = parseDrag(event); if (payload && payload.id !== node.id) onMove(payload, node.id, payload.type === 'entry' ? node.entries.length : node.children.length); }}>
      <button className="tree-chevron" aria-label={open ? 'Collapse folder' : 'Expand folder'} onClick={() => onToggle(node.id)}>{open ? <ChevronDown /> : <ChevronRight />}</button>
      <Checkbox checked={node.review_enabled} disabled={readOnly} aria-label={`Include ${node.name} in review`} onCheckedChange={(checked) => !readOnly && onReviewToggle(node.id, Boolean(checked))} />
      <button className="folder-name" onClick={() => { onSelectFolder(node.id); if (!open) onToggle(node.id); }}>{node.name}</button>
      <span className="count">{count}</span>
    </div>
    {open && <div className="tree-children"><div className="entry-list">
      {!readOnly && <InsertionPoint parentFolderId={node.id} folderName={node.name} entryIndex={0} folderIndex={!node.entries.length ? 0 : undefined} empty={!node.entries.length && !node.children.length} onInsertEntry={onInsertEntry} onInsertFolder={onInsertFolder} onMove={onMove} />}
      {node.entries.map((entry, index) => <div className="entry-row-group" key={entry.id}><button
        className={`entry-row ${selectedEntry === entry.id ? 'active' : ''}`} draggable={!readOnly}
        onDragStart={readOnly ? undefined : (event) => beginDrag(event, { type: 'entry', id: entry.id }, entry.title)}
        onDragOver={readOnly ? undefined : (event) => { event.preventDefault(); event.stopPropagation(); }}
        onDrop={readOnly ? undefined : (event) => { event.preventDefault(); event.stopPropagation(); const payload = parseDrag(event); if (payload?.type === 'entry') onMove(payload, node.id, index); }}
        onClick={() => onSelectEntry(entry.id, node.id)}><span className={`type-chip type-${entry.kind}`}>{entry.kind}</span><span>{entry.title}</span></button>
        {!readOnly && <InsertionPoint parentFolderId={node.id} folderName={node.name} entryIndex={index + 1} folderIndex={index === node.entries.length - 1 ? 0 : undefined} onInsertEntry={onInsertEntry} onInsertFolder={onInsertFolder} onMove={onMove} />}
      </div>)}</div>
      {node.children.map((child, index) => <div className="folder-row-group" key={child.id}><TreeNode node={child} selectedEntry={selectedEntry} selectedFolder={selectedFolder} expanded={expanded} readOnly={readOnly} onToggle={onToggle} onSelectEntry={onSelectEntry} onSelectFolder={onSelectFolder} onReviewToggle={onReviewToggle} onMove={onMove} onInsertEntry={onInsertEntry} onInsertFolder={onInsertFolder} />
        {!readOnly && <InsertionPoint parentFolderId={node.id} folderName={node.name} folderIndex={index + 1} onInsertEntry={onInsertEntry} onInsertFolder={onInsertFolder} onMove={onMove} />}
      </div>)}
    </div>}
  </div>;
}

function LibraryTree(props: Omit<React.ComponentProps<typeof TreeNode>, 'node'> & { tree: FolderNode[] }) {
  return <nav aria-label="Content library" className="tree">
    {!props.readOnly && <InsertionPoint parentFolderId={null} folderName="the library" folderIndex={0} empty={!props.tree.length} onInsertEntry={props.onInsertEntry} onInsertFolder={props.onInsertFolder} onMove={props.onMove} />}
    {props.tree.map((node, index) => <div className="folder-row-group" key={node.id}><TreeNode {...props} node={node} />
      {!props.readOnly && <InsertionPoint parentFolderId={null} folderName="the library" folderIndex={index + 1} onInsertEntry={props.onInsertEntry} onInsertFolder={props.onInsertFolder} onMove={props.onMove} />}
    </div>)}
  </nav>;
}

function LibraryResizeHandle({ value, onChange }: { value: number; onChange: (value: number) => void }) {
  const clamp = (next: number) => Math.min(520, Math.max(220, next));
  const startResize = (event: React.PointerEvent<HTMLButtonElement>) => {
    event.preventDefault();
    const origin = event.clientX;
    const initial = value;
    document.body.classList.add('panel-resizing');
    const move = (pointerEvent: PointerEvent) => onChange(clamp(initial + pointerEvent.clientX - origin));
    const finish = () => {
      document.body.classList.remove('panel-resizing');
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', finish);
      window.removeEventListener('pointercancel', finish);
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', finish);
    window.addEventListener('pointercancel', finish);
  };
  return <button type="button" className="library-resizer" aria-label={`Resize library panel; current width ${value} pixels`} title="Drag or use arrow keys to resize the library panel"
    onPointerDown={startResize}
    onKeyDown={(event) => {
      if (event.key === 'ArrowLeft') { event.preventDefault(); onChange(clamp(value - 20)); }
      if (event.key === 'ArrowRight') { event.preventDefault(); onChange(clamp(value + 20)); }
      if (event.key === 'Home') { event.preventDefault(); onChange(220); }
      if (event.key === 'End') { event.preventDefault(); onChange(520); }
    }} />;
}

function LoginScreen({ onLogin }: { onLogin: (csrf: string) => void }) {
  const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async (event: React.SubmitEvent<HTMLFormElement>) => { event.preventDefault(); setBusy(true); setError(''); try { const result = await api<{ authenticated: boolean; csrf: string }>('/api/login', { method: 'POST', body: JSON.stringify({ password }) }); onLogin(result.csrf); } catch (reason) { setError((reason as Error).message); } finally { setBusy(false); } };
  return <main className="login-screen"><form className="login-card" onSubmit={submit}><span className="brand-mark large"><Sigma /></span><h1>Study</h1><p>Your mathematical library is password protected.</p><label className="field-label" htmlFor="study-password">Password<Input id="study-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>{error && <div className="form-error">{error}</div>}<Button type="submit" disabled={busy || !password}><LogIn /> {busy ? 'Opening…' : 'Open library'}</Button></form></main>;
}

function ReadingPane({ entry, folders, canEdit, selectedVariantId, onSelectVariant, onEdit, onDelete, onReview, onOpenEntry }: { entry: EntryDetail | null; folders: Folder[]; canEdit: boolean; selectedVariantId: string | null; onSelectVariant: (variantId: string) => void; onEdit: () => void; onDelete: () => void; onReview: () => void; onOpenEntry: (entryId: string, variantId?: string) => void }) {
  if (!entry) return <article className="reading-pane empty-library"><div><span className="brand-mark large"><Library /></span><h1>Your study library</h1><p>Select an entry, or create one in a folder. Content is stored as ordinary Markdown under <code>data/</code>.</p></div></article>;
  const target = readingVariantSelection(entry, selectedVariantId);
  const folder = folders.find((item) => item.id === entry.folder_id); const active = entry.formulations.find((item) => item.id === target.formulationId) || entry.formulations[0];
  return <article className="reading-pane"><div className="breadcrumbs">{folder?.namespace.split(':').join(' / ')} <span>/</span> {KIND_LABEL[entry.kind]}</div>
    <div className="document-heading"><div><span className="canonical-tag">{active?.canonical_tag || entry.canonical_tag}</span><h1>{entry.title}</h1></div><div className="document-actions desktop-write"><Button variant="outline" disabled={!canEdit} onClick={onEdit}>Edit</Button><Button variant="destructive" disabled={!canEdit} onClick={onDelete}><Trash2 /> Delete</Button></div></div>
    {entry.header && <MathMarkdown content={entry.header} className="content-header" folderId={entry.folder_id} onOpenEntry={onOpenEntry} />}
    {entry.formulations.length > 1 && <div className="variant-tabs">{entry.formulations.map((item) => <button key={item.id} className={active?.id === item.id ? 'selected' : ''} onClick={() => onSelectVariant(item.id)}>{item.label}{item.main ? ' · main' : ''}</button>)}</div>}
    <MathMarkdown content={active?.content || ''} folderId={entry.folder_id} onOpenEntry={onOpenEntry} />
    {!!entry.supplements.length && <section className="supplement-list"><h2>{entry.kind === 'th' ? 'Proofs' : 'Solutions'}</h2>{entry.supplements.map((item) => <details key={item.id} open={target.supplementId ? target.supplementId === item.id : item.main}><summary><span>{item.label}</span><code>{item.canonical_tag}</code></summary><MathMarkdown content={item.content || ''} folderId={entry.folder_id} onOpenEntry={onOpenEntry} /></details>)}</section>}
    <section className="recall-cue"><div className="recall-icon"><Check /></div><div><strong>Reading is not review</strong><span>Test recall or solve before revealing the stored answer.</span></div><Button variant="ghost" onClick={onReview}>Practice</Button></section>
  </article>;
}

export default function Home() {
  const isMobile = useIsMobile();
  const [session, setSession] = useState({ loading: true, authenticated: false, authRequired: false });
  const [data, setData] = useState<Bootstrap | null>(null); const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null); const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null); const [selectedVariantId, setSelectedVariantId] = useState<string | null>(null); const [entry, setEntry] = useState<EntryDetail | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set()); const dark = useSyncExternalStore(subscribeTheme, getThemeSnapshot, () => false); const [mode, setMode] = useState<'library' | 'review'>('library'); const [editorOpen, setEditorOpen] = useState(false); const [createEntry, setCreateEntry] = useState(false); const [createKind, setCreateKind] = useState<EntryKind>('df'); const [createIndex, setCreateIndex] = useState<number | null>(null);
  const [gitOpen, setGitOpen] = useState(false); const [exportOpen, setExportOpen] = useState(false); const [macrosOpen, setMacrosOpen] = useState(false); const [moveFolderOpen, setMoveFolderOpen] = useState(false); const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null); const [mobileLibrary, setMobileLibrary] = useState(false); const [libraryOpen, setLibraryOpen] = useState(true); const [libraryWidth, setLibraryWidth] = useState(270); const [query, setQuery] = useState(''); const [searchResults, setSearchResults] = useState<SearchResult[]>([]); const [searching, setSearching] = useState(false); const [notice, setNotice] = useState(''); const [error, setError] = useState(''); const searchRef = useRef<HTMLInputElement>(null);
  const [librarySynchronized, setLibrarySynchronized] = useState(true); const [pullReloadError, setPullReloadError] = useState('');

  const load = useCallback(async () => { try { const next = await api<Bootstrap>('/api/bootstrap'); setData(next); configureMathJax(next.macros); setExpanded((current) => { const valid = new Set(next.folders.map((folder) => folder.id)); return new Set([...current].filter((id) => valid.has(id))); }); setSelectedEntryId((current) => current && next.entries.some((item) => item.id === current) ? current : next.entries[0]?.id || null); setSelectedFolderId((current) => current && next.folders.some((item) => item.id === current) ? current : next.entries[0]?.folder_id || next.folders[0]?.id || null); } catch (reason) { setError((reason as Error).message); } }, []);
  useEffect(() => { api<{ authenticated: boolean; auth_required: boolean; csrf: string | null }>('/api/session').then((result) => { setCsrfToken(result.csrf); setSession({ loading: false, authenticated: result.authenticated, authRequired: result.auth_required }); if (result.authenticated) return load(); }).catch((reason: Error) => { setSession({ loading: false, authenticated: false, authRequired: true }); setError(reason.message); }); }, [load]);
  useEffect(() => {
    if (!selectedEntryId || !session.authenticated || !librarySynchronized) return;
    const controller = new AbortController();
    api<EntryDetail>(`/api/entries/${selectedEntryId}`, { signal: controller.signal })
      .then(setEntry)
      .catch((reason: Error) => { if (reason.name !== 'AbortError') setError(reason.message); });
    return () => controller.abort();
  }, [librarySynchronized, selectedEntryId, session.authenticated]);
  useEffect(() => { const stored = localStorage.getItem('study-theme'); const value = stored ? stored === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches; document.documentElement.classList.toggle('dark', value); }, []);
  useEffect(() => { const handler = (event: KeyboardEvent) => { if ((event.metaKey || event.ctrlKey) && !event.shiftKey && event.key.toLowerCase() === 'k') { event.preventDefault(); searchRef.current?.focus(); } }; window.addEventListener('keydown', handler); return () => window.removeEventListener('keydown', handler); }, []);
  useEffect(() => {
    const needle = query.trim();
    if (!needle) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setSearching(true);
      api<{ results: SearchResult[] }>(`/api/search?q=${encodeURIComponent(needle)}&limit=40`, { signal: controller.signal })
        .then((result) => setSearchResults(result.results))
        .catch((reason: Error) => { if (reason.name !== 'AbortError') setError(reason.message); })
        .finally(() => { if (!controller.signal.aborted) setSearching(false); });
    }, 140);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [query]);
  useEffect(() => { const context = document.modelContext; if (!context?.registerTool || !data) return; const lifecycle = new AbortController(); const report = (reason: unknown) => setError(reason instanceof Error ? reason.message : String(reason)); const registrations = [
    context.registerTool({ name: 'read_study_library_summary', title: 'Read Study library summary', description: 'Return folder, entry, and due-review counts without changing the library.', inputSchema: { type: 'object', properties: {}, additionalProperties: false }, annotations: { readOnlyHint: true, untrustedContentHint: false }, execute: () => api('/api/webmcp/library-summary') }, { signal: lifecycle.signal }),
    context.registerTool({ name: 'start_study_review', title: 'Start review', description: 'Open the visible due-review flow in authored library order.', inputSchema: { type: 'object', properties: {}, additionalProperties: false }, annotations: { readOnlyHint: false, untrustedContentHint: false }, execute: () => { setMode('review'); return { status: 'opened', due: data.review.due }; } }, { signal: lifecycle.signal }),
    ...(!isMobile && librarySynchronized ? [context.registerTool({ name: 'create_study_entry', title: 'Create study entry', description: 'Create one Markdown mathematics entry in a named folder using the same action as the editor.', inputSchema: { type: 'object', properties: { folder_id: { type: 'string' }, kind: { type: 'string', enum: ['ax', 'df', 'rk', 'th', 'pb'] }, title: { type: 'string' }, tag: { type: 'string' }, content: { type: 'string' } }, required: ['folder_id', 'kind', 'title', 'tag', 'content'], additionalProperties: false }, annotations: { readOnlyHint: false, untrustedContentHint: false }, execute: async (input) => { const value = input as { folder_id: string; kind: EntryKind; title: string; tag: string; content: string }; const created = await api<EntryDetail>('/api/entries', { method: 'POST', body: JSON.stringify({ ...value, header: '' }) }); await load(); setSelectedEntryId(created.id); return { id: created.id, canonical_tag: created.canonical_tag }; } }, { signal: lifecycle.signal })] : []),
  ]; registrations.forEach((registration) => void Promise.resolve(registration).catch(report)); return () => lifecycle.abort(); }, [data, isMobile, librarySynchronized, load]);

  const toggleTheme = () => { const next = !dark; document.documentElement.classList.toggle('dark', next); localStorage.setItem('study-theme', next ? 'dark' : 'light'); };
  const chooseEntry = useCallback((id: string, folderId: string, variantId: string | null = null) => { setEntry((current) => current?.id === id ? current : null); setSelectedEntryId(id); setSelectedFolderId(folderId); setSelectedVariantId(variantId); setMobileLibrary(false); }, []);
  const openEntryReference = useCallback((entryId: string, variantId?: string) => {
    const target = data?.entries.find((item) => item.id === entryId);
    if (target) chooseEntry(target.id, target.folder_id, variantId ?? null);
  }, [chooseEntry, data?.entries]);
  const chooseSearchResult = (result: SearchResult) => {
    const folderId = result.folder_id || data?.entries.find((item) => item.id === result.id)?.folder_id;
    setEntry((current) => current?.id === result.id ? current : null);
    setSelectedEntryId(result.id);
    setSelectedVariantId(null);
    if (folderId) setSelectedFolderId(folderId);
    setQuery(''); setSearchResults([]); setSearching(false);
  };
  const reloadAfterPull = useCallback(async (status: GitStatus) => {
    setLibrarySynchronized(false);
    setPullReloadError('');
    setEditorOpen(false);
    setCreateEntry(false);
    setCreateIndex(null);
    setEntry(null);
    try {
      const next = await api<Bootstrap>('/api/bootstrap');
      const nextEntryId = selectedEntryId && next.entries.some((item) => item.id === selectedEntryId)
        ? selectedEntryId
        : next.entries[0]?.id || null;
      const nextEntry = nextEntryId
        ? await api<EntryDetail>(`/api/entries/${nextEntryId}`)
        : null;
      const nextFolderId = nextEntry?.folder_id
        || (selectedFolderId && next.folders.some((item) => item.id === selectedFolderId) ? selectedFolderId : null)
        || next.folders[0]?.id
        || null;
      configureMathJax(next.macros);
      setData({ ...next, git: status });
      setExpanded((current) => {
        const valid = new Set(next.folders.map((folder) => folder.id));
        return new Set([...current].filter((id) => valid.has(id)));
      });
      setSelectedEntryId(nextEntryId);
      setSelectedFolderId(nextFolderId);
      setSelectedVariantId(null);
      setEntry(nextEntry);
      setLibrarySynchronized(true);
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : String(reason);
      const message = `Pull completed, but Study could not reload the updated library (${detail}). Editing is disabled to protect pulled content.`;
      setPullReloadError(message);
      throw new Error(message);
    }
  }, [selectedEntryId, selectedFolderId]);
  const updateFolderReview = async (id: string, enabled: boolean) => { if (isMobile || !librarySynchronized) return; try { await api(`/api/folders/${id}`, { method: 'PATCH', body: JSON.stringify({ review_enabled: enabled }) }); await load(); } catch (reason) { setError((reason as Error).message); } };
  const refreshSelectedEntry = async (syncFolder: boolean) => { if (!selectedEntryId) return; const refreshed = await api<EntryDetail>(`/api/entries/${selectedEntryId}`); setEntry(refreshed); if (syncFolder) setSelectedFolderId(refreshed.folder_id); };
  const moveItem = async (payload: DragPayload, destination: string | null, index: number) => { if (isMobile || !librarySynchronized) return false; try { await api(`/api/items/${payload.type}/${payload.id}/move`, { method: 'POST', body: JSON.stringify({ destination_folder_id: destination, index }) }); await load(); if (selectedEntryId && (payload.type === 'folder' || payload.id === selectedEntryId)) await refreshSelectedEntry(payload.type === 'entry'); setNotice(payload.type === 'folder' ? 'Folder moved. Its canonical namespace has changed.' : 'Entry moved. Its canonical namespace has changed.'); return true; } catch (reason) { setError((reason as Error).message); return false; } };
  const addFolder = async (parentId: string | null, index: number | null = null) => { if (isMobile || !librarySynchronized) return; const name = window.prompt(parentId ? 'Subfolder name' : 'Top-level folder name'); if (!name) return; const slug = window.prompt('Namespace segment', name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')); if (!slug) return; try { const created = await api<Folder>('/api/folders', { method: 'POST', body: JSON.stringify({ name, slug, parent_id: parentId, index }) }); setSelectedFolderId(created.id); setExpanded((current) => new Set(current).add(parentId || created.id)); await load(); } catch (reason) { setError((reason as Error).message); } };
  const renameFolder = async () => { if (isMobile || !librarySynchronized || !data || !selectedFolderId) return; const folder = data.folders.find((item) => item.id === selectedFolderId); if (!folder) return; const name = window.prompt('Folder name', folder.name); if (!name) return; const slug = window.prompt('Namespace segment', folder.slug); if (!slug) return; try { await api(`/api/folders/${folder.id}`, { method: 'PATCH', body: JSON.stringify({ name, slug }) }); await load(); await refreshSelectedEntry(false); } catch (reason) { setError((reason as Error).message); } };
  const beginDeleteFolder = () => {
    if (isMobile || !librarySynchronized || !data || !selectedFolderId) return;
    const folder = data.folders.find((item) => item.id === selectedFolderId);
    if (!folder) return;
    const subtree = folderSubtreeIds(folder.id, data.folders);
    setDeleteTarget({
      type: 'folder',
      id: folder.id,
      name: folder.name,
      namespace: folder.namespace,
      parentId: folder.parent_id,
      descendantFolders: subtree.size - 1,
      entries: data.entries.filter((item) => subtree.has(item.folder_id)).length,
    });
  };
  const deleteItem = async (target: DeleteTarget) => {
    const recursive = target.type === 'folder' && (target.descendantFolders > 0 || target.entries > 0);
    const deletedFolders = target.type === 'folder' && data
      ? folderSubtreeIds(target.id, data.folders)
      : null;
    const response = await api<DeleteResponse>(target.type === 'entry'
      ? `/api/entries/${target.id}`
      : `/api/folders/${target.id}${recursive ? '?recursive=true' : ''}`, { method: 'DELETE' });
    const selectedEntryDeleted = target.type === 'entry' && selectedEntryId === target.id;
    const selectedEntrySummary = data?.entries.find((item) => item.id === selectedEntryId);
    const selectedEntryFolder = selectedEntrySummary?.folder_id;
    if (selectedEntryDeleted || (selectedEntryFolder && deletedFolders?.has(selectedEntryFolder))) {
      setEntry(null);
      const nextEntryId = target.type === 'entry' ? response.deletion.next_entry_id || null : null;
      const nextEntryFolder = data?.entries.find((item) => item.id === nextEntryId)?.folder_id || null;
      setSelectedEntryId(nextEntryId);
      setSelectedFolderId(nextEntryFolder);
      setSelectedVariantId(null);
    }
    if (target.type === 'folder') {
      setSelectedFolderId(selectedEntryFolder && !deletedFolders?.has(selectedEntryFolder)
        ? selectedEntryFolder
        : null);
      setExpanded((current) => {
        const next = new Set(current);
        deletedFolders?.forEach((id) => next.delete(id));
        return next;
      });
    }
    setSearchResults([]);
    await load();
    setNotice(`${target.type === 'folder' ? 'Folder' : 'Entry'} deleted.`);
  };
  const beginCreateEntry = (folderId: string, index: number | null, kind: EntryKind = 'df') => { if (isMobile || !librarySynchronized) return; setSelectedFolderId(folderId); setCreateKind(kind); setCreateIndex(index); setCreateEntry(true); setEditorOpen(true); };
  const handleSaved = async (saved: EntryDetail) => { setSelectedEntryId(saved.id); setSelectedFolderId(saved.folder_id); setCreateEntry(false); setCreateIndex(null); await load(); setEntry(saved); setNotice('Saved.'); };
  const logout = async () => { await api('/api/logout', { method: 'POST' }); setCsrfToken(null); setSession({ loading: false, authenticated: false, authRequired: true }); setData(null); };

  if (session.loading) return <div className="app-loading"><LoaderCircle className="spin" /><span>Opening Study…</span></div>;
  if (!session.authenticated && session.authRequired) return <LoginScreen onLogin={(csrf) => { setCsrfToken(csrf); setSession({ loading: false, authenticated: true, authRequired: true }); void load(); }} />;
  if (mode === 'review' && data) return <ReviewView initialDue={data.review.due} onExit={() => { setMode('library'); void load(); }} onChanged={() => void load()} />;

  const resizeLibrary = (width: number) => setLibraryWidth(width);
  const selectedFolder = data?.folders.find((folder) => folder.id === selectedFolderId) || null;
  const treeProps = { tree: data?.tree || [], selectedEntry: selectedEntryId, selectedFolder: selectedFolderId, expanded, readOnly: isMobile || !librarySynchronized, onToggle: (id: string) => setExpanded((current) => { const next = new Set(current); if (next.has(id)) next.delete(id); else next.add(id); return next; }), onSelectEntry: chooseEntry, onSelectFolder: setSelectedFolderId, onReviewToggle: updateFolderReview, onMove: moveItem, onInsertEntry: beginCreateEntry, onInsertFolder: addFolder };
  return <main className={`app-frame ${libraryOpen ? '' : 'library-closed'}`} style={{ '--library-width': `${libraryWidth}px` } as CSSProperties}><header className="topbar"><div className="brand-cluster"><Button className="library-toggle" variant="ghost" size="icon-sm" aria-label={libraryOpen ? 'Hide library panel' : 'Show library panel'} onClick={() => setLibraryOpen((value) => !value)}>{libraryOpen ? <PanelLeftClose /> : <PanelLeftOpen />}</Button><button className="brand" aria-label="Open Study library" onClick={() => isMobile ? setMobileLibrary(true) : setLibraryOpen(true)}><span className="brand-mark"><Sigma /></span><span>Study</span></button></div>
    <div className="searchbox"><Search /><input ref={searchRef} type="search" maxLength={1000} aria-label="Search your library" aria-controls="study-search-results" placeholder="Search definitions, theorems, problems…" value={query} onChange={(event) => { const value = event.target.value; setQuery(value); setSearchResults([]); setSearching(Boolean(value.trim())); }} onKeyDown={(event) => { if (event.key === 'Enter' && searchResults[0]) { event.preventDefault(); chooseSearchResult(searchResults[0]); } else if (event.key === 'Escape') { setQuery(''); setSearchResults([]); setSearching(false); } }} /><kbd>⌘ K</kbd>{query.trim() && <section id="study-search-results" className="search-results" aria-label="Search results"><div className="search-status" aria-live="polite">{searching ? 'Searching…' : `${searchResults.length} result${searchResults.length === 1 ? '' : 's'}`}</div>{!searching && searchResults.map((result) => <button key={result.id} type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => chooseSearchResult(result)}><span className={`type-chip type-${result.kind}`}>{result.kind}</span><span><strong>{result.title}</strong><code>{result.canonical_tag}</code></span></button>)}</section>}</div>
    <div className="top-actions"><Button variant="ghost" size="icon" aria-label="Edit global LaTeX macros" disabled={!librarySynchronized} onClick={() => setMacrosOpen(true)}><Braces /></Button><Button variant="ghost" size="icon" aria-label="Export PDF" onClick={() => setExportOpen(true)}><Download /></Button><Button variant="ghost" size="icon" aria-label="Toggle dark mode" onClick={toggleTheme}>{dark ? <Sun /> : <Moon />}</Button><Button variant="outline" onClick={() => setGitOpen(true)}><GitBranch /> {data?.git.content_dirty ? 'Changes' : data?.git.branch || 'Git'}</Button><Button className="review-button" onClick={() => setMode('review')}><BookOpen /> Review <span>{data?.review.due || 0}</span></Button>{session.authRequired && <Button variant="ghost" size="icon" aria-label="Log out" onClick={() => void logout()}><LogOut /></Button>}</div></header>
    <aside className={`library-sidebar ${mobileLibrary ? 'mobile-open' : ''}`}><div className="sidebar-heading"><span>Library</span><Button className="mobile-close" variant="ghost" size="icon-sm" aria-label="Close library" onClick={() => setMobileLibrary(false)}><Menu /></Button></div>{data && <LibraryTree {...treeProps} />}<div className="sidebar-create desktop-write"><Button size="sm" variant="ghost" disabled={!librarySynchronized} onClick={() => void addFolder(null)}><FolderPlus /> Top-level</Button><Button size="sm" variant="ghost" disabled={!librarySynchronized || !selectedFolderId} onClick={() => void addFolder(selectedFolderId)}><FolderInput /> Subfolder</Button><Button size="sm" variant="ghost" disabled={!librarySynchronized || !selectedFolderId} onClick={() => selectedFolderId && beginCreateEntry(selectedFolderId, null)}><FilePlus2 /> Entry</Button><Button size="sm" variant="ghost" disabled={!librarySynchronized || !selectedFolderId} onClick={() => setMoveFolderOpen(true)}><FolderTree /> Move</Button><Button size="sm" variant="ghost" disabled={!librarySynchronized || !selectedFolderId} onClick={renameFolder}><FolderPen /> Rename</Button><Button size="sm" variant="destructive" disabled={!librarySynchronized || !selectedFolderId} onClick={beginDeleteFolder}><Trash2 /> Delete</Button></div></aside>
    {libraryOpen && <LibraryResizeHandle value={libraryWidth} onChange={resizeLibrary} />}
    <ReadingPane entry={entry} folders={data?.folders || []} canEdit={librarySynchronized} selectedVariantId={selectedVariantId} onSelectVariant={setSelectedVariantId} onEdit={() => { setCreateEntry(false); setCreateIndex(null); setEditorOpen(true); }} onDelete={() => entry && setDeleteTarget({ type: 'entry', id: entry.id, title: entry.title, canonicalTag: entry.canonical_tag })} onReview={() => setMode('review')} onOpenEntry={openEntryReference} />
    {notice && <button className="toast-notice" onClick={() => setNotice('')}>{notice}</button>}{pullReloadError ? <button className="toast-error" onClick={() => window.location.reload()}>{pullReloadError} Reload Study.</button> : error && <button className="toast-error" onClick={() => setError('')}>{error}</button>}
    <EditorDialog open={editorOpen} entry={createEntry ? null : entry} folderId={selectedFolderId} initialKind={createKind} insertIndex={createIndex} dark={dark} onClose={() => { setEditorOpen(false); setCreateEntry(false); setCreateIndex(null); }} onSaved={handleSaved} />
    <DeleteItemDialog target={deleteTarget} onClose={() => setDeleteTarget(null)} onDelete={deleteItem} />
    {data && <MoveFolderDialog open={moveFolderOpen} folder={selectedFolder} folders={data.folders} tree={data.tree} onClose={() => setMoveFolderOpen(false)} onMove={async (destinationId, index) => {
      if (!selectedFolderId) return false;
      const moved = await moveItem({ type: 'folder', id: selectedFolderId }, destinationId, index);
      if (moved) setExpanded((current) => { const next = new Set(current); next.add(selectedFolderId); if (destinationId) next.add(destinationId); return next; });
      return moved;
    }} />}
    {data && <GitSyncDialog open={gitOpen} initial={data.git} onClose={() => setGitOpen(false)} onChanged={(status: GitStatus) => setData((current) => current ? { ...current, git: status } : current)} onPulled={reloadAfterPull} />}{data && <ExportDialog open={exportOpen} folders={data.folders} selectedFolderId={selectedFolderId} onClose={() => setExportOpen(false)} />}{data && <MacrosDialog open={macrosOpen} macros={data.macros} onClose={() => setMacrosOpen(false)} />}
  </main>;
}
