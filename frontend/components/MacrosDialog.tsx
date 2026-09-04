'use client';

import { useState } from 'react';
import { Braces, Save } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { api } from '@/lib/api';

interface Props { open: boolean; macros: Record<string, string | (string | number)[]>; onClose: () => void }

function MacrosDialogSession({ open, macros, onClose }: Props) {
  const [text, setText] = useState(() => JSON.stringify(macros, null, 2));
  const [error, setError] = useState('');
  const save = async () => {
    setError('');
    try {
      const value = JSON.parse(text) as Record<string, string | (string | number)[]>;
      await api('/api/macros', { method: 'PUT', body: JSON.stringify({ macros: value }) });
      window.location.reload();
    } catch (reason) { setError((reason as Error).message); }
  };
  return (
    <Dialog open={open} onOpenChange={(value) => !value && onClose()}>
      <DialogContent className="macros-dialog" showCloseButton>
        <DialogHeader><DialogTitle><Braces /> Global LaTeX macros</DialogTitle><p className="dialog-subtitle">Names omit the leading backslash. Arrays use MathJax’s [replacement, argument-count] form.</p></DialogHeader>
        <textarea className="json-editor" spellCheck={false} value={text} onChange={(event) => setText(event.target.value)} />
        <pre className="macro-example">{`{\n  "RR": "\\\\mathbb{R}",\n  "Hom": ["\\\\operatorname{Hom}\\\\left(#1,#2\\\\right)", 2]\n}`}</pre>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions"><Button variant="ghost" onClick={onClose}>Cancel</Button><Button onClick={save}><Save /> Save and reload</Button></div>
      </DialogContent>
    </Dialog>
  );
}

export function MacrosDialog(props: Props) {
  return <MacrosDialogSession key={props.open ? JSON.stringify(props.macros) : 'closed'} {...props} />;
}
