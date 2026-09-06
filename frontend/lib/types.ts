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
  review: {
    due: number;
    completed_today: number;
    minutes_today: number;
    calibration: {
      model: string;
      target_grade: 'good-or-easy';
      target_probability: number;
      minimum_observations: number;
      minimum_delay_hours: number;
      processed_log_records: number;
      models: Record<string, {
        observations: number;
        successes: number;
        effective_observations: number;
        effective_exposure: number;
        posterior_log_scale_sd: number;
        ready: boolean;
      }>;
    };
  };
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

export interface ReviewCalendarSchedule {
  due_at: string;
  last_reviewed_at: string;
  last_grade: number;
  last_elapsed_ms: number;
  stability_days: number;
  difficulty: number;
  repetitions: number;
  lapses: number;
  last_confidence?: number | null;
  last_calibration?: number | null;
  scheduler?: {
    model: string;
    target_grade: 'good-or-easy';
    target_probability: number;
    calibrated: boolean;
    source: string;
    observations: number;
    distinct_cards?: number;
    effective_observations: number;
    interval_factor: number;
    interval_days: number | null;
    interval_minutes?: number | null;
    calibrated_interval_used?: boolean;
    reason?: string;
    bounded_direction: string | null;
    target_attainable?: boolean | null;
  };
}

export interface ReviewCalendarModelEstimate {
  model: string;
  target_grade: 'good-or-easy';
  source: string;
  posterior_source: string;
  ready: boolean;
  collecting: boolean;
  distinct_cards: number;
  boundary_limited: boolean;
  posterior_boundary_mass: { lower: number; upper: number };
  suggested_interval_factor: number;
  bounded_direction: string | null;
  target_attainable: boolean;
  prediction_domain: {
    minimum_delay_days: number;
    minimum_delay_hours: number;
    maximum_normalized_delay: number;
  };
  prediction_status_now: 'available' | 'unavailable' | 'short-delay-excluded' | 'beyond-model-range';
  prediction_status_at_due: 'available' | 'unavailable' | 'short-delay-excluded' | 'beyond-model-range';
  posterior_interval_scale?: {
    median: number;
    credible_interval_90: { lower: number; upper: number };
  } | null;
  predicted_good_or_easy_now?: number | null;
  predicted_good_or_easy_at_due?: number | null;
}

export interface ReviewCalendarEvent {
  card_id: string;
  entry_id: string;
  folder_id: string;
  title: string;
  canonical_tag: string;
  kind: EntryKind;
  mode: ReviewMode;
  mode_label: string;
  due_at: string;
  last_reviewed_at: string;
  active: boolean;
  review_enabled: boolean;
  orphaned: boolean;
  inactive_reason: string | null;
  schedule_at_last_grade: ReviewCalendarSchedule;
  model_estimate: ReviewCalendarModelEstimate;
}

export interface ReviewCalendarStatistics {
  attempts: number;
  elapsed_ms: number;
  minutes: number;
  grades: Record<'again' | 'hard' | 'good' | 'easy', number>;
  good_or_easy_self_grades: number;
  again_lapses: number;
  good_or_easy_self_grade_rate: number | null;
  daily_timezone: string;
}

export interface ReviewCalendarResponse {
  range: { start: string; end: string };
  events: ReviewCalendarEvent[];
  statistics: ReviewCalendarStatistics;
  calibration: {
    model: string;
    target_grade: 'good-or-easy';
    target_probability: number;
    observation_scope: string;
    history_discount: number;
    processed_log_records: number;
    readiness_requirements: {
      minimum_observations: number;
      minimum_distinct_cards: number;
      minimum_effective_observations: number;
      minimum_effective_exposure: number;
      maximum_posterior_log_scale_sd: number;
      maximum_boundary_mass: number;
      minimum_observation_delay_hours: number;
    };
    interpretation: string;
    forecast_evaluation: {
      count: number;
      brier_score: number | null;
      log_loss: number | null;
      mean_predicted_good_or_easy: number | null;
      observed_good_or_easy_self_grade_rate: number | null;
      reliability_bins: Array<{
        lower: number;
        upper: number;
        count: number;
        mean_predicted_good_or_easy: number | null;
        observed_good_or_easy_self_grade_rate: number | null;
      }>;
      interpretation: string;
    };
    models: Record<string, {
      observations: number;
      distinct_cards: number;
      good_or_easy_self_grades: number;
      good_or_easy_self_grade_rate: number | null;
      effective_observations: number;
      effective_good_or_easy_self_grades: number;
      effective_exposure: number;
      posterior_log_scale_sd: number;
      posterior_interval_scale: {
        median: number;
        credible_interval_90: { lower: number; upper: number };
      };
      posterior_boundary_mass: { lower: number; upper: number };
      boundary_limited: boolean;
      suggested_interval_factor: number;
      bounded_direction: string | null;
      target_attainable: boolean;
      last_observed_at: string | null;
      ready: boolean;
    }>;
  };
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
