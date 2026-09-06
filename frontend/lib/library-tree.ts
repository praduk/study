import type {
  Bootstrap,
  BootstrapPayload,
  EntrySummary,
  Folder,
  FolderNode,
} from '@/lib/types';

function compareCodePoints(left: string, right: string) {
  const leftPoints = Array.from(left);
  const rightPoints = Array.from(right);
  const sharedLength = Math.min(leftPoints.length, rightPoints.length);
  for (let index = 0; index < sharedLength; index += 1) {
    const difference = leftPoints[index].codePointAt(0)! - rightPoints[index].codePointAt(0)!;
    if (difference) return difference;
  }
  return leftPoints.length - rightPoints.length;
}

function compareOrderThenLabel(
  left: { order: number },
  right: { order: number },
  leftLabel: string,
  rightLabel: string,
) {
  return left.order - right.order
    || compareCodePoints(leftLabel.toLowerCase(), rightLabel.toLowerCase());
}

export function buildLibraryTree(folders: Folder[], entries: EntrySummary[]): FolderNode[] {
  const nodes = new Map<string, FolderNode>(folders.map((folder) => [
    folder.id,
    { ...folder, entries: [], children: [] },
  ]));

  for (const entry of entries) nodes.get(entry.folder_id)?.entries.push(entry);
  for (const node of nodes.values()) {
    node.entries.sort((left, right) => compareOrderThenLabel(left, right, left.title, right.title));
  }

  const roots: FolderNode[] = [];
  for (const folder of folders) {
    const node = nodes.get(folder.id)!;
    const parent = folder.parent_id ? nodes.get(folder.parent_id) : undefined;
    if (parent) parent.children.push(node);
    else roots.push(node);
  }
  const sortFolders = (items: FolderNode[]) => {
    items.sort((left, right) => compareOrderThenLabel(left, right, left.name, right.name));
    items.forEach((item) => sortFolders(item.children));
  };
  sortFolders(roots);
  return roots;
}

export function hydrateBootstrap(payload: BootstrapPayload): Bootstrap {
  return {
    ...payload,
    tree: payload.tree ?? buildLibraryTree(payload.folders, payload.entries),
  };
}

function replaceTreeFolder(nodes: FolderNode[], folder: Folder): FolderNode[] {
  let changed = false;
  const next = nodes.map((node) => {
    if (node.id === folder.id) {
      changed = true;
      return { ...node, ...folder };
    }
    const children = replaceTreeFolder(node.children, folder);
    if (children === node.children) return node;
    changed = true;
    return { ...node, children };
  });
  return changed ? next : nodes;
}

export function updateBootstrapFolder(snapshot: Bootstrap, folder: Folder): Bootstrap {
  let found = false;
  const folders = snapshot.folders.map((item) => {
    if (item.id !== folder.id) return item;
    found = true;
    return { ...item, ...folder };
  });
  if (!found) return snapshot;
  return {
    ...snapshot,
    folders,
    tree: replaceTreeFolder(snapshot.tree, folder),
  };
}
