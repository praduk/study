'use client';

import { useEffect, useState } from 'react';
import { GitCommit, GitPullRequest, RefreshCw } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import type { GitStatus } from '@/lib/types';

interface Props {
  open: boolean;
  onClose: () => void;
  onPulled: () => Promise<void>;
}

function GitSyncDialogSession({ open, onClose, onPulled }: Props) {
  const [status, setStatus] = useState<GitStatus | null>(null);
  const [message, setMessage] = useState('Update study notes');
  const [busy, setBusy] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    api<GitStatus>('/api/git/status', { signal: controller.signal }).then(setStatus).catch((reason: Error) => {
      if (!controller.signal.aborted) setError(reason.message);
    });
    return () => controller.abort();
  }, [open]);

  if (!open) return null;

  const refresh = async () => {
    setBusy('refresh'); setError('');
    try {
      setStatus(await api<GitStatus>('/api/git/status'));
    } catch (reason) { setError((reason as Error).message); }
    finally { setBusy(''); }
  };

  const commit = async () => {
    setBusy('commit'); setError(''); setNotice('');
    try {
      const result = await api<{ revision: string; status: GitStatus }>('/api/git/commit', { method: 'POST', body: JSON.stringify({ message }) });
      setStatus(result.status); setNotice(`Committed content as ${result.revision}.`);
    } catch (reason) { setError((reason as Error).message); }
    finally { setBusy(''); }
  };

  const pull = async () => {
    if (!window.confirm('Pull fast-forward-only from the configured upstream? This will never force, merge, or discard local work.')) return;
    setBusy('pull'); setError(''); setNotice('');
    try {
      const result = await api<{ summary: string; status: GitStatus }>('/api/git/pull', { method: 'POST' });
      setStatus(result.status);
      await onPulled();
      setNotice(result.summary || 'Already up to date.');
    } catch (reason) { setError((reason as Error).message); }
    finally { setBusy(''); }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => !value && onClose()}>
      <DialogContent className="git-dialog" showCloseButton>
        <DialogHeader><DialogTitle>Repository</DialogTitle><p className="dialog-subtitle">Commit authored data locally or pull a safe fast-forward from the associated repository.</p></DialogHeader>
        {!status && !error && <output>Reading repository status…</output>}
        {status && !status.available && <div className="form-error">{status.message || 'Git is unavailable.'}</div>}
        {status?.available && <>
          <div className="repo-summary"><div><span>Branch</span><strong>{status.branch}</strong></div><div><span>Ahead</span><strong>{status.ahead ?? '—'}</strong></div><div><span>Behind</span><strong>{status.behind ?? '—'}</strong></div></div>
          <section className="git-section">
            <h3>Authored content</h3>
            {status.content_changed?.length ? <div className="change-list">{status.content_changed.map((item) => <div key={`${item.status}-${item.path}`}><code>{item.status}</code><span>{item.path}</span></div>)}</div> : <p className="empty-copy">No uncommitted content changes.</p>}
            <label className="field-label" htmlFor="commit-message">Commit message<Input id="commit-message" value={message} onChange={(event) => setMessage(event.target.value)} /></label>
            <Button onClick={commit} disabled={!status.content_dirty || !message.trim() || Boolean(busy)}><GitCommit /> {busy === 'commit' ? 'Committing…' : 'Commit content'}</Button>
          </section>
          {!!status.changed?.filter((item) => !item.path.startsWith('data/')).length && <p className="safety-note">Other repository changes are shown by Git status but are deliberately not included by “Commit content.”</p>}
          <section className="git-section pull-section"><div><h3>Pull from upstream</h3><p>Allowed only when the entire worktree is clean. Uses fast-forward-only mode, so it cannot create a merge commit.</p></div><Button variant="outline" onClick={pull} disabled={Boolean(status.dirty) || !status.remote || Boolean(busy)}><GitPullRequest /> {busy === 'pull' ? 'Pulling…' : 'Pull'}</Button></section>
        </>}
        {notice && <div className="success-note">{notice}</div>}
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions"><Button variant="ghost" disabled={Boolean(busy) || (!status && !error)} onClick={() => void refresh()}><RefreshCw /> Refresh</Button><Button variant="outline" onClick={onClose}>Done</Button></div>
      </DialogContent>
    </Dialog>
  );
}

export function GitSyncDialog(props: Props) {
  return <GitSyncDialogSession key={props.open ? 'open' : 'closed'} {...props} />;
}
