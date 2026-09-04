export type EntryKind = 'ax' | 'df' | 'rk' | 'th' | 'pb';
export type ReviewMode = 'statement' | 'proof-plan' | 'solve';

export interface Variant {
  id: string;
  label: string;
  subtag: string | null;
  file: string;
  main: boolean;
  content?: string;
  canonical_tag?: string;
  kind?: 'pf' | 'sl';
}

export interface Asset {
  id: string;
  kind: 'image' | 'excalidraw' | 'commutative';
  path?: string;
  source?: string;
  alt: string;
  width: number;
  invert_lightness?: boolean;
}

export interface EntrySummary {
  id: string;
  folder_id: string;
  kind: EntryKind;
  title: string;
  tag: string;
  header: string;
  order: number;
  canonical_tag: string;
  review_modes: ReviewMode[];
  problem_family?: string;
  confusable_with?: string[];
  formulations: Omit<Variant, 'content'>[];
  supplements: Omit<Variant, 'content'>[];
  assets: Asset[];
}

export interface EntryDetail extends EntrySummary {
  formulations: Variant[];
  supplements: Variant[];
}

export interface Folder {
  id: string;
  name: string;
  slug: string;
  namespace: string;
  parent_id: string | null;
  order: number;
  review_enabled: boolean;
}

export interface FolderNode extends Folder {
  entries: EntrySummary[];
  children: FolderNode[];
}

export interface GitStatus {
  available: boolean;
  branch?: string;
  remote?: string | null;
  dirty?: boolean;
  content_dirty?: boolean;
  changed?: { status: string; path: string }[];
  content_changed?: { status: string; path: string }[];
  ahead?: number | null;
  behind?: number | null;
  message?: string;
}

export interface Bootstrap {
  version: number;
  folders: Folder[];
  entries: EntrySummary[];
  tree: FolderNode[];
  macros: Record<string, string | (string | number)[]>;
  review: { due: number; completed_today: number; minutes_today: number };
  git: GitStatus;
  capabilities: Record<string, boolean>;
}

export interface ReviewCard {
  id: string;
  entry_id: string;
  folder_id: string;
  mode: ReviewMode;
  mode_label: string;
  title: string;
  kind: EntryKind;
  canonical_tag: string;
  header: string;
  prompt: string;
  prompt_body: string;
  due_at: string | null;
  new: boolean;
  repetitions: number;
}

export interface CommutativeNode {
  id: string;
  label: string;
  row: number;
  column: number;
}

export interface CommutativeArrow {
  source: string;
  target: string;
  label: string;
  dashed: boolean;
  double: boolean;
}

export interface CommutativeDiagram {
  version?: number;
  name: string;
  width: number;
  nodes: CommutativeNode[];
  arrows: CommutativeArrow[];
}
