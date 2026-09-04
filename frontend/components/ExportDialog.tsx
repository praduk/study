'use client';

import { useState } from 'react';
import { Download } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { apiFile, downloadBlob } from '@/lib/api';
import type { EntryKind, Folder } from '@/lib/types';

const TYPES: { value: EntryKind; label: string }[] = [
  { value: 'ax', label: 'Axioms' }, { value: 'df', label: 'Definitions' }, { value: 'rk', label: 'Remarks' },
  { value: 'th', label: 'Theorems' }, { value: 'pb', label: 'Problems' },
];

export function ExportDialog({ open, folders, selectedFolderId, onClose }: { open: boolean; folders: Folder[]; selectedFolderId: string | null; onClose: () => void }) {
  const [folderId, setFolderId] = useState<string>(selectedFolderId || '');
  const [title, setTitle] = useState('Study notes');
  const [kinds, setKinds] = useState<EntryKind[]>(TYPES.map((item) => item.value));
  const [recursive, setRecursive] = useState(true);
  const [supplements, setSupplements] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    setBusy(true); setError('');
    try {
      const result = await apiFile('/api/export/pdf', {
        method: 'POST',
        body: JSON.stringify({ folder_id: folderId || null, recursive, kinds, include_supplements: supplements, title }),
      });
      downloadBlob(result.blob, result.filename);
      onClose();
    } catch (reason) { setError((reason as Error).message); }
    finally { setBusy(false); }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => !value && onClose()}>
      <DialogContent className="export-dialog" showCloseButton>
        <DialogHeader><DialogTitle>Export PDF</DialogTitle><p className="dialog-subtitle">Entries follow the same authored order as the library.</p></DialogHeader>
        <label className="field-label" htmlFor="export-title">Title<Input id="export-title" value={title} onChange={(event) => setTitle(event.target.value)} /></label>
        <label className="field-label">Folder<select value={folderId} onChange={(event) => setFolderId(event.target.value)}><option value="">Entire library</option>{folders.map((folder) => <option key={folder.id} value={folder.id}>{folder.namespace} — {folder.name}</option>)}</select></label>
        <fieldset className="export-types"><legend>Include</legend>{TYPES.map((item) => <label key={item.value}><input type="checkbox" checked={kinds.includes(item.value)} onChange={(event) => setKinds((current) => event.target.checked ? [...current, item.value] : current.filter((kind) => kind !== item.value))} /> {item.label}</label>)}</fieldset>
        <label className="tiny-check"><input type="checkbox" checked={recursive} onChange={(event) => setRecursive(event.target.checked)} /> include nested folders</label>
        <label className="tiny-check"><input type="checkbox" checked={supplements} onChange={(event) => setSupplements(event.target.checked)} /> include proofs and solutions</label>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button onClick={run} disabled={busy || !kinds.length}><Download /> {busy ? 'Rendering…' : 'Export PDF'}</Button></div>
      </DialogContent>
    </Dialog>
  );
}
