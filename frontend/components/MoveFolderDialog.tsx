'use client';

import { useMemo, useState, type ReactNode } from 'react';
import { CornerDownRight, Folder, FolderTree } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { Folder as StudyFolder, FolderNode } from '@/lib/types';

interface Props {
  open: boolean;
  folder: StudyFolder | null;
  folders: StudyFolder[];
  tree: FolderNode[];
  onClose: () => void;
  onMove: (destinationId: string | null, index: number) => Promise<boolean>;
}

function descendantIds(folderId: string, folders: StudyFolder[]) {
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

function MoveFolderDialogSession({ open, folder, folders, tree, onClose, onMove }: Props) {
  const [destinationId, setDestinationId] = useState<string | null | undefined>();
  const [moving, setMoving] = useState(false);
  const blocked = useMemo(
    () => folder ? descendantIds(folder.id, folders) : new Set<string>(),
    [folder, folders],
  );
  const destination = folders.find((item) => item.id === destinationId);
  const nextNamespace = folder
    ? destination ? `${destination.namespace}:${folder.slug}` : folder.slug
    : '';

  const siblingConflict = (parentId: string | null) => Boolean(folder && folders.some(
    (item) => item.id !== folder.id && item.parent_id === parentId && item.slug === folder.slug,
  ));

  const destinationRows = (nodes: FolderNode[], depth = 0): ReactNode => nodes.map((node) => {
    const invalidTreeTarget = blocked.has(node.id);
    const unchanged = folder?.parent_id === node.id;
    const conflict = siblingConflict(node.id);
    const disabled = invalidTreeTarget || unchanged || conflict;
    return <div key={node.id}>
      <button
        type="button"
        className={destinationId === node.id ? 'selected' : ''}
        style={{ paddingLeft: `${12 + depth * 18}px` }}
        disabled={disabled}
        title={invalidTreeTarget ? 'A folder cannot move inside itself or a descendant.' : conflict ? 'That namespace segment is already used here.' : unchanged ? 'This is already the parent folder.' : undefined}
        onClick={() => setDestinationId(node.id)}
      >
        <Folder />
        <span><strong>{node.name}</strong><code>{node.namespace}</code></span>
      </button>
      {destinationRows(node.children, depth + 1)}
    </div>;
  });

  const move = async () => {
    if (destinationId === undefined || !folder) return;
    setMoving(true);
    const index = destinationId === null
      ? tree.length
      : folders.filter((item) => item.parent_id === destinationId).length;
    const moved = await onMove(destinationId, index);
    setMoving(false);
    if (moved) onClose();
  };

  const rootDisabled = folder?.parent_id === null || siblingConflict(null);
  return (
    <Dialog open={open} onOpenChange={(value) => !value && onClose()}>
      <DialogContent className="move-folder-dialog" showCloseButton>
        <DialogHeader>
          <DialogTitle>Move {folder?.name || 'folder'}</DialogTitle>
          <p className="dialog-subtitle">Choose its new parent in the tree. The folder is appended within that parent.</p>
        </DialogHeader>
        <div className="folder-destination-tree" aria-label="Choose a destination folder">
          <button type="button" className={destinationId === null ? 'selected' : ''} disabled={rootDisabled} onClick={() => setDestinationId(null)}>
            <FolderTree /><span><strong>Top level</strong><code>Separate namespace root</code></span>
          </button>
          {destinationRows(tree)}
        </div>
        {destinationId !== undefined && folder && <div className="move-namespace-preview">
          <CornerDownRight /><span>New namespace</span><code>{nextNamespace}</code>
        </div>}
        <p className="safety-note">Moving changes canonical tags. Existing fully qualified references are not rewritten automatically.</p>
        <div className="dialog-actions">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={() => void move()} disabled={destinationId === undefined || moving}>{moving ? 'Moving…' : 'Move folder'}</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export function MoveFolderDialog(props: Props) {
  return <MoveFolderDialogSession key={`${props.open}:${props.folder?.id || ''}`} {...props} />;
}
