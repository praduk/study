'use client';

import { useState } from 'react';
import { Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

export type DeleteTarget =
  | {
      type: 'entry';
      id: string;
      title: string;
      canonicalTag: string;
    }
  | {
      type: 'folder';
      id: string;
      name: string;
      namespace: string;
      parentId: string | null;
      descendantFolders: number;
      entries: number;
    };

interface Props {
  target: DeleteTarget | null;
  onClose: () => void;
  onDelete: (target: DeleteTarget) => Promise<void>;
}

function countLabel(count: number, singular: string) {
  return `${count} ${singular}${count === 1 ? '' : 's'}`;
}

function DeleteItemDialogSession({ target, onClose, onDelete }: Props) {
  const [confirmation, setConfirmation] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');
  const recursive = target?.type === 'folder'
    && (target.descendantFolders > 0 || target.entries > 0);
  const confirmed = !recursive || confirmation === target.name;

  const remove = async () => {
    if (!target || !confirmed) return;
    setDeleting(true);
    setError('');
    try {
      await onDelete(target);
      onClose();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Dialog open={Boolean(target)} onOpenChange={(value) => !value && !deleting && onClose()}>
      <DialogContent className="delete-item-dialog" showCloseButton={!deleting}>
        <DialogHeader>
          <DialogTitle><Trash2 /> Delete {target?.type === 'folder' ? 'folder' : 'entry'}</DialogTitle>
          <DialogDescription>
            {target?.type === 'folder'
              ? <>You are deleting <strong>{target.name}</strong> (<code>{target.namespace}</code>).</>
              : target
                ? <>You are deleting <strong>{target.title}</strong> (<code>{target.canonicalTag}</code>).</>
                : null}
          </DialogDescription>
        </DialogHeader>

        {target?.type === 'folder' && recursive ? <>
          <p className="delete-summary">
            This recursively removes this folder, {countLabel(target.descendantFolders, 'nested folder')},
            {' '}and {countLabel(target.entries, 'entry')}, including their authored content.
          </p>
          <label className="field-label" htmlFor="delete-folder-confirmation">
            Type <strong>{target.name}</strong> to confirm
            <Input
              id="delete-folder-confirmation"
              autoComplete="off"
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value)}
            />
          </label>
        </> : <p className="delete-summary">
          {target?.type === 'folder'
            ? 'This folder is empty and can be deleted safely.'
            : 'This removes the entry and its authored content from Study.'}
        </p>}

        <p className="safety-note">
          References to the deleted {target?.type === 'folder' ? 'subtree' : 'entry'} will become
          unresolved. This cannot be undone inside Study; content already committed to Git may be recoverable.
        </p>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions">
          <Button variant="outline" disabled={deleting} onClick={onClose}>Cancel</Button>
          <Button variant="destructive" disabled={!target || !confirmed || deleting} onClick={() => void remove()}>
            <Trash2 /> {deleting ? 'Deleting…' : recursive ? 'Delete recursively' : `Delete ${target?.type || 'item'}`}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export function DeleteItemDialog(props: Props) {
  const key = props.target ? `${props.target.type}:${props.target.id}` : 'closed';
  return <DeleteItemDialogSession key={key} {...props} />;
}
