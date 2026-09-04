interface EditorVimActions {
  close: () => void;
  save: () => void;
}

let activeEditor: EditorVimActions | null = null;

const closeActiveEditor = () => activeEditor?.close();
const saveActiveEditor = () => activeEditor?.save();

export const editorVimCommands = [
  { name: 'quit', prefix: 'q', run: closeActiveEditor },
  { name: 'write', prefix: 'w', run: saveActiveEditor },
] as const;

export function activateEditorVimActions(actions: EditorVimActions) {
  activeEditor = actions;
  return () => {
    if (activeEditor === actions) activeEditor = null;
  };
}
