'use client';

import { useMemo, useState } from 'react';
import { ArrowRight, Plus, Trash2 } from 'lucide-react';

import { DiagramGraphic } from '@/components/CommutativeDiagramView';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import type { CommutativeArrow, CommutativeDiagram, CommutativeNode } from '@/lib/types';

interface Props {
  open: boolean;
  entryId: string;
  onClose: () => void;
  onInsert: (markdown: string) => void;
}

export function CommutativeDiagramDialog({ open, entryId, onClose, onInsert }: Props) {
  const [name, setName] = useState('Commutative diagram');
  const [width, setWidth] = useState(76);
  const [labels, setLabels] = useState<Record<string, string>>({ n00: '$A$', n01: '$B$', n10: '$C$', n11: '$D$' });
  const [arrows, setArrows] = useState<CommutativeArrow[]>([
    { source: 'n00', target: 'n01', label: '$f$', dashed: false, double: false },
    { source: 'n00', target: 'n10', label: '$g$', dashed: false, double: false },
    { source: 'n01', target: 'n11', label: '$h$', dashed: false, double: false },
    { source: 'n10', target: 'n11', label: '$k$', dashed: false, double: false },
  ]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const nodes = useMemo<CommutativeNode[]>(() => Object.entries(labels)
    .filter(([, label]) => label.trim())
    .map(([id, label]) => ({ id, label, row: Number(id[1]), column: Number(id[2]) })), [labels]);
  const validIds = new Set(nodes.map((node) => node.id));
  const validArrows = arrows.flatMap((arrow, sourceIndex) => validIds.has(arrow.source) && validIds.has(arrow.target) ? [{ arrow, sourceIndex }] : []);
  const diagram: CommutativeDiagram = { name, width, nodes, arrows: validArrows.map(({ arrow }) => arrow) };

  const addArrow = () => {
    if (nodes.length < 2) return;
    setArrows((current) => [...current, { source: nodes[0].id, target: nodes[1].id, label: '', dashed: false, double: false }]);
  };

  const save = async () => {
    setError('');
    if (!nodes.length) { setError('Add at least one object.'); return; }
    setSaving(true);
    try {
      const result = await api<{ markdown: string }>(`/api/entries/${entryId}/diagrams/commutative`, {
        method: 'POST',
        body: JSON.stringify(diagram),
      });
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
      <DialogContent className="diagram-dialog" showCloseButton>
        <DialogHeader>
          <DialogTitle>Commutative diagram</DialogTitle>
          <p className="dialog-subtitle">Place objects on a grid, connect them, and use $…$ inside labels.</p>
        </DialogHeader>
        <div className="diagram-editor-layout">
          <div className="diagram-controls">
            <label className="field-label" htmlFor="diagram-name">Name<Input id="diagram-name" value={name} onChange={(event) => setName(event.target.value)} /></label>
            <div className="object-grid" aria-label="Diagram object grid">
              {Array.from({ length: 9 }, (_, index) => {
                const row = Math.floor(index / 3);
                const column = index % 3;
                const id = `n${row}${column}`;
                return <Input key={id} aria-label={`Object row ${row + 1}, column ${column + 1}`} placeholder="Object" value={labels[id] || ''} onChange={(event) => setLabels((current) => ({ ...current, [id]: event.target.value }))} />;
              })}
            </div>
            <div className="arrow-list">
              <div className="section-label"><span>Arrows</span><Button size="xs" variant="ghost" onClick={addArrow}><Plus /> Add</Button></div>
              {validArrows.map(({ arrow, sourceIndex }) => (
                <div className="arrow-row" key={sourceIndex}>
                  <select value={arrow.source} onChange={(event) => setArrows((current) => current.map((item, itemIndex) => itemIndex === sourceIndex ? { ...item, source: event.target.value } : item))}>
                    {nodes.map((node) => <option value={node.id} key={node.id}>{node.label}</option>)}
                  </select>
                  <ArrowRight size={14} />
                  <select value={arrow.target} onChange={(event) => setArrows((current) => current.map((item, itemIndex) => itemIndex === sourceIndex ? { ...item, target: event.target.value } : item))}>
                    {nodes.map((node) => <option value={node.id} key={node.id}>{node.label}</option>)}
                  </select>
                  <Input aria-label="Arrow label" placeholder="$f$" value={arrow.label} onChange={(event) => setArrows((current) => current.map((item, itemIndex) => itemIndex === sourceIndex ? { ...item, label: event.target.value } : item))} />
                  <label className="tiny-check"><input type="checkbox" checked={arrow.dashed} onChange={(event) => setArrows((current) => current.map((item, itemIndex) => itemIndex === sourceIndex ? { ...item, dashed: event.target.checked } : item))} /> dashed</label>
                  <label className="tiny-check"><input type="checkbox" checked={arrow.double} onChange={(event) => setArrows((current) => current.map((item, itemIndex) => itemIndex === sourceIndex ? { ...item, double: event.target.checked } : item))} /> double</label>
                  <Button size="icon-xs" variant="ghost" aria-label="Remove arrow" onClick={() => setArrows((current) => current.filter((_, itemIndex) => itemIndex !== sourceIndex))}><Trash2 /></Button>
                </div>
              ))}
            </div>
            <label className="range-field">Width <input type="range" min="30" max="100" value={width} onChange={(event) => setWidth(Number(event.target.value))} /><span>{width}%</span></label>
          </div>
          <div className="diagram-preview"><DiagramGraphic diagram={diagram} width={Math.min(100, Math.max(30, width))} /></div>
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Insert diagram'}</Button></div>
      </DialogContent>
    </Dialog>
  );
}
