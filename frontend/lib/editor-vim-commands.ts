interface EditorVimActions {
  close: () => void;
  save: () => void;
  saveAndClose: () => void;
}

let activeEditor: EditorVimActions | null = null;

const closeActiveEditor = () => activeEditor?.close();
const saveActiveEditor = () => activeEditor?.save();
const saveAndCloseActiveEditor = () => activeEditor?.saveAndClose();

export const editorVimCommands = [
  { name: 'quit', prefix: 'q', run: closeActiveEditor },
  { name: 'write', prefix: 'w', run: saveActiveEditor },
  { name: 'wq', prefix: 'wq', run: saveAndCloseActiveEditor },
] as const;

export function activateEditorVimActions(actions: EditorVimActions) {
  activeEditor = actions;
  return () => {
    if (activeEditor === actions) activeEditor = null;
  };
}
