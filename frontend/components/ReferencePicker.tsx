'use client';

import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import type { EntryKind } from '@/lib/types';

interface ReferenceCandidate {
  entry_id: string;
  variant_id: string;
  kind: EntryKind;
  title: string;
  canonical_tag: string;
  folder_namespace: string;
  label: string;
  target_type: string;
  insert_text: string;
}

interface Props {
  open: boolean;
  folderId: string | null;
  onClose: () => void;
  onInsert: (value: string) => void;
}

function ReferencePickerSession({ open, folderId, onClose, onInsert }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ReferenceCandidate[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open || !folderId) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      const parameters = new URLSearchParams({
        folder_id: folderId,
        limit: '40',
      });
      const normalizedQuery = query.trim().replace(/^@/, '');
      if (normalizedQuery) parameters.set('q', normalizedQuery);
      setBusy(true);
      api<{ results: ReferenceCandidate[] }>(
        `/api/references/candidates?${parameters}`,
        { signal: controller.signal },
      )
        .then((result) => {
          setResults(result.results);
          setError('');
        })
        .catch((reason: Error) => {
          if (reason.name !== 'AbortError') setError(reason.message);
        })
        .finally(() => {
          if (!controller.signal.aborted) setBusy(false);
        });
    }, 120);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [folderId, open, query]);

  const choose = (candidate: ReferenceCandidate) => {
    onClose();
    window.requestAnimationFrame(() => onInsert(candidate.insert_text));
  };

  return (
    <Dialog open={open} onOpenChange={(value) => !value && onClose()}>
      <DialogContent className="reference-picker" showCloseButton>
        <DialogHeader>
          <DialogTitle>Insert a reference</DialogTitle>
          <p className="dialog-subtitle">
            Study searches the nearest folder first, then progressively broader
            subtrees, then the whole library. Ambiguous names are inserted
            canonically.
          </p>
        </DialogHeader>
        <Input
          maxLength={1000}
          aria-label="Find an entry or formulation to reference"
          placeholder="Search title or tag…"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setResults([]);
            setBusy(true);
          }}
        />
        <div className="reference-candidates" aria-live="polite">
          {!folderId ? (
            <p className="empty-copy">
              Choose a folder before inserting a reference.
            </p>
          ) : busy ? (
            <p className="empty-copy">Searching…</p>
          ) : results.length ? (
            results.map((candidate) => (
              <button
                key={`${candidate.entry_id}-${candidate.variant_id}`}
                type="button"
                onClick={() => choose(candidate)}
              >
                <span className={`type-chip type-${candidate.kind}`}>
                  {candidate.kind}
                </span>
                <span>
                  <strong>{candidate.title}</strong>
                  <small>
                    {candidate.folder_namespace} · {candidate.label} · {candidate.target_type}
                  </small>
                  <code>{candidate.insert_text}</code>
                </span>
              </button>
            ))
          ) : (
            <p className="empty-copy">No matching reference target.</p>
          )}
        </div>
        {error && (
          <div className="form-error" role="alert">
            {error}
          </div>
        )}
        <div className="dialog-actions">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export function ReferencePicker(props: Props) {
  return (
    <ReferencePickerSession
      key={`${props.open}:${props.folderId || ''}`}
      {...props}
    />
  );
}
