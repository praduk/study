'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { ArrowLeft, CalendarDays, ChevronLeft, ChevronRight, Clock3, Info, RefreshCw } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import type { ReviewCalendarEvent, ReviewCalendarResponse, ReviewCalendarSchedule } from '@/lib/types';

interface Props {
  onExit: () => void;
}

const GRADE_LABELS = ['Again', 'Hard', 'Good', 'Easy'];

function browserTimeZone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch {
    return 'UTC';
  }
}

function dayKey(value: Date | string, timeZone: string) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone, year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(new Date(value));
  const part = (kind: string) => parts.find((item) => item.type === kind)?.value || '';
  return `${part('year')}-${part('month')}-${part('day')}`;
}

function formatDate(value: Date | string, timeZone: string, options: Intl.DateTimeFormatOptions) {
  return new Intl.DateTimeFormat(undefined, { timeZone, ...options }).format(new Date(value));
}

function monthName(month: Date, timeZone: string) {
  return formatDate(month, timeZone, { month: 'long', year: 'numeric' });
}

function percentage(value: number | null | undefined) {
  return value === null || value === undefined ? '—' : `${Math.round(value * 100)}%`;
}

function predictionText(
  value: number | null | undefined,
  status: ReviewCalendarEvent['model_estimate']['prediction_status_now'],
) {
  if (value !== null && value !== undefined) return percentage(value);
  if (status === 'short-delay-excluded') return 'Not estimated (under six hours)';
  if (status === 'beyond-model-range') return 'Not estimated (beyond model range)';
  return 'Not available';
}

function shiftMonth(month: Date, delta: number) {
  return new Date(month.getFullYear(), month.getMonth() + delta, 1);
}

function dueTime(event: ReviewCalendarEvent, timeZone: string) {
  return formatDate(event.due_at, timeZone, { hour: 'numeric', minute: '2-digit' });
}

function eventLabel(event: ReviewCalendarEvent) {
  return event.title || (event.orphaned ? 'Unavailable review item' : 'Untitled review item');
}

function scheduledInterval(scheduler: ReviewCalendarSchedule['scheduler']) {
  if (!scheduler) return 'Legacy fallback schedule';
  if (scheduler.interval_minutes !== null && scheduler.interval_minutes !== undefined) {
    const unit = scheduler.interval_minutes === 1 ? 'minute' : 'minutes';
    return `${scheduler.interval_minutes} ${unit} · fixed Again retry`;
  }
  if (scheduler.interval_days !== null) {
    const unit = scheduler.interval_days === 1 ? 'day' : 'days';
    return `${scheduler.interval_days} ${unit} · ${scheduler.interval_factor.toFixed(2)}× factor`;
  }
  return 'Fixed schedule';
}

function schedulingSource(scheduler: ReviewCalendarSchedule['scheduler']) {
  if (!scheduler) return 'Legacy fallback';
  const isAgainRetry = scheduler.reason === 'again'
    || (scheduler.interval_minutes !== null && scheduler.interval_minutes !== undefined);
  if (isAgainRetry) {
    return `Fixed Again retry · Bayesian interval adjustment not used · ${scheduler.observations} qualified observations`;
  }
  const calibratedIntervalUsed = scheduler.calibrated_interval_used ?? scheduler.calibrated;
  const source = calibratedIntervalUsed
    ? `${scheduler.source} Bayesian calibration · ${scheduler.observations} qualified observations`
    : `Fallback heuristic · ${scheduler.observations} qualified observations`;
  if (scheduler.bounded_direction === 'shorter') return `${source} · lower safety bound reached`;
  if (scheduler.bounded_direction === 'longer') return `${source} · upper safety bound reached`;
  return source;
}

function EventDetail({ event, timeZone }: { event: ReviewCalendarEvent; timeZone: string }) {
  const schedule = event.schedule_at_last_grade;
  const scheduler = schedule.scheduler;
  const model = event.model_estimate;
  const interval = model.posterior_interval_scale;
  return <section className="calendar-detail" aria-label="Review item details">
    <div className="calendar-detail-heading">
      <div>
        <span className="calendar-eyebrow">{event.mode_label}</span>
        <h2>{eventLabel(event)}</h2>
        {event.canonical_tag && <code>{event.canonical_tag}</code>}
      </div>
      {!event.active && <span className="calendar-status">{event.inactive_reason === 'review-disabled' ? 'Review disabled' : 'Unavailable'}</span>}
    </div>
    <dl className="calendar-schedule">
      <div><dt>Due</dt><dd>{formatDate(event.due_at, timeZone, { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</dd></div>
      <div><dt>Last grade</dt><dd>{GRADE_LABELS[schedule.last_grade] || 'Unknown'}</dd></div>
      <div><dt>Last reviewed</dt><dd>{formatDate(event.last_reviewed_at, timeZone, { month: 'short', day: 'numeric', year: 'numeric' })}</dd></div>
      <div><dt>Interval-advancing grades</dt><dd>{schedule.repetitions}</dd></div>
      <div><dt>Again grades (lapses)</dt><dd>{schedule.lapses}</dd></div>
      <div><dt>Stability heuristic</dt><dd>{schedule.stability_days.toFixed(1)} days</dd></div>
      <div><dt>Difficulty heuristic</dt><dd>{schedule.difficulty.toFixed(2)}</dd></div>
      <div><dt>Scheduled interval</dt><dd>{scheduledInterval(scheduler)}</dd></div>
      <div><dt>Scheduling source</dt><dd>{schedulingSource(scheduler)}</dd></div>
    </dl>
    <section className="calendar-model" aria-label="Bayesian self-grade estimate">
      <div className="calendar-model-heading"><Info size={15} /><strong>Bayesian self-grade estimate</strong></div>
      <p>Predicted probability of a <strong>Good-or-Easy self-grade</strong>: <strong>{predictionText(model.predicted_good_or_easy_now, model.prediction_status_now)} now</strong> and <strong>{predictionText(model.predicted_good_or_easy_at_due, model.prediction_status_at_due)} at its due time</strong>.</p>
      {interval && <p className="calendar-muted">Posterior interval-scale median {interval.median.toFixed(2)} (90% credible interval {interval.credible_interval_90.lower.toFixed(2)}–{interval.credible_interval_90.upper.toFixed(2)}).</p>}
      <p className="calendar-muted">{model.boundary_limited ? 'The posterior reaches a model boundary, so it is not ready to control spacing.' : model.collecting ? 'Collecting delayed-review evidence; this posterior is diagnostic and spacing uses the fallback heuristic.' : `Using ${model.source} calibration${model.target_attainable ? '' : ` at the ${model.bounded_direction} safety bound`}.`} This model-conditional estimate is not a correctness, memory, or mastery probability.</p>
    </section>
  </section>;
}

export function ReviewCalendar({ onExit }: Props) {
  const [timeZone] = useState(browserTimeZone);
  const [month, setMonth] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const [includeInactive, setIncludeInactive] = useState(false);
  const [report, setReport] = useState<ReviewCalendarResponse | null>(null);
  const [selected, setSelected] = useState<ReviewCalendarEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError('');
    const end = shiftMonth(month, 1);
    try {
      const query = new URLSearchParams({
        start: month.toISOString(), end: end.toISOString(), timezone: timeZone,
      });
      if (includeInactive) query.set('include_inactive', 'true');
      const next = await api<ReviewCalendarResponse>(`/api/review/calendar?${query}`, { signal });
      if (!Array.isArray(next.events)) throw new Error('The server returned an invalid review calendar.');
      setReport(next);
      setSelected((current) => current ? next.events.find((event) => event.card_id === current.card_id) || null : null);
    } catch (reason) {
      if ((reason as Error).name !== 'AbortError') {
        setReport(null);
        setSelected(null);
        setError((reason as Error).message);
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [includeInactive, month, timeZone]);

  useEffect(() => {
    const controller = new AbortController();
    void Promise.resolve().then(() => load(controller.signal));
    return () => controller.abort();
  }, [load]);

  const eventsByDay = useMemo(() => {
    const result = new Map<string, ReviewCalendarEvent[]>();
    for (const event of report?.events || []) {
      const key = dayKey(event.due_at, timeZone);
      result.set(key, [...(result.get(key) || []), event]);
    }
    return result;
  }, [report, timeZone]);
  const days = useMemo(() => {
    const firstWeekday = month.getDay();
    const first = new Date(month.getFullYear(), month.getMonth(), 1 - firstWeekday);
    return Array.from({ length: 42 }, (_, index) => new Date(first.getFullYear(), first.getMonth(), first.getDate() + index));
  }, [month]);
  const stats = report?.statistics;
  const calibrationReport = report?.calibration;
  const calibration = calibrationReport?.models?.pooled;
  const posterior = calibration?.posterior_interval_scale;
  const forecast = calibrationReport?.forecast_evaluation;

  return <div className="calendar-screen">
    <header className="calendar-top">
      <Button variant="ghost" onClick={onExit}><ArrowLeft /> Library</Button>
      <div><span className="calendar-eyebrow"><CalendarDays size={14} /> Review calendar</span><h1>{monthName(month, timeZone)}</h1></div>
      <div className="calendar-controls">
        <Button variant="ghost" size="icon-sm" aria-label="Previous month" onClick={() => setMonth((value) => shiftMonth(value, -1))}><ChevronLeft /></Button>
        <Button variant="ghost" size="icon-sm" aria-label="Next month" onClick={() => setMonth((value) => shiftMonth(value, 1))}><ChevronRight /></Button>
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={loading}><RefreshCw className={loading ? 'spin' : ''} /> Refresh</Button>
      </div>
    </header>
    <main className="calendar-stage">
      <div className="calendar-summary">
        <div><span>Attempts</span><strong>{stats?.attempts ?? '—'}</strong></div>
        <div><span>Good-or-Easy self-grades</span><strong>{percentage(stats?.good_or_easy_self_grade_rate)}</strong></div>
        <div><span>Review time</span><strong>{stats ? `${stats.minutes.toFixed(1)} min` : '—'}</strong></div>
        <div><span>Again grades</span><strong>{stats?.again_lapses ?? '—'}</strong></div>
      </div>
      <p className="calendar-disclosure"><Info size={14} /> Statistics use validated review history in {stats?.daily_timezone || timeZone}. A Good-or-Easy rate is a self-grade rate, not an accuracy or retention measurement.</p>
      <label className="calendar-inactive"><input type="checkbox" checked={includeInactive} onChange={(event) => setIncludeInactive(event.target.checked)} /> Show disabled and unavailable scheduled items</label>
      {error ? <section className="calendar-error" role="alert"><p>Calendar could not load: {error}</p><Button onClick={() => void load()}>Try again</Button></section> : <div className="calendar-layout">
        <section className="calendar-board" aria-busy={loading}>
          <div className="calendar-weekdays">{['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => <span key={day}>{day}</span>)}</div>
          <div className="calendar-grid">
            {days.map((day) => {
              const key = dayKey(day, timeZone);
              const dayEvents = eventsByDay.get(key) || [];
              const currentMonth = day.getMonth() === month.getMonth();
              return <div className={`calendar-day ${currentMonth ? '' : 'outside'}`} key={key}>
                <time dateTime={key}>{day.getDate()}</time>
                <div className="calendar-day-events">{dayEvents.map((event) => <button type="button" key={event.card_id} className={`calendar-event ${selected?.card_id === event.card_id ? 'selected' : ''} ${event.active ? '' : 'inactive'}`} onClick={() => setSelected(event)} title={`${eventLabel(event)} · ${dueTime(event, timeZone)}`}><Clock3 size={11} /><span>{eventLabel(event)}</span></button>)}</div>
              </div>;
            })}
          </div>
        </section>
        <aside className="calendar-agenda">
          <h2>{selected ? 'Review configuration' : 'Scheduled reviews'}</h2>
          {selected ? <EventDetail event={selected} timeZone={timeZone} /> : <>
            <p className="calendar-muted">Select an item to inspect its current scheduling configuration and Bayesian self-grade estimate.</p>
            <div className="calendar-agenda-list">{(report?.events || []).map((event) => <button type="button" key={event.card_id} onClick={() => setSelected(event)}><time>{formatDate(event.due_at, timeZone, { month: 'short', day: 'numeric' })}</time><span><strong>{eventLabel(event)}</strong><small>{event.mode_label} · {dueTime(event, timeZone)}</small></span></button>)}</div>
          </>}
        </aside>
      </div>}
      <section className="calendar-calibration">
        <h2>Bayesian calibration</h2>
        <p>Study models completed delayed Good-or-Easy self-grades to adjust spacing. Its credible intervals are conditional on the chosen curve, bounded prior, and an independence approximation; selective review and repeated-card correlation can make them too narrow. It does not infer whether an answer was correct or whether material is mastered.</p>
        <dl>
          <div><dt>Qualified observations</dt><dd>{calibration?.observations ?? 0}</dd></div>
          <div><dt>Distinct reviewed cards</dt><dd>{calibration?.distinct_cards ?? 0}</dd></div>
          <div><dt>Good-or-Easy self-grades</dt><dd>{calibration?.good_or_easy_self_grades ?? 0}</dd></div>
          <div><dt>Effective observations</dt><dd>{calibration?.effective_observations.toFixed(1) ?? '—'}</dd></div>
          <div><dt>Posterior interval scale</dt><dd>{posterior ? `${posterior.median.toFixed(2)} (${posterior.credible_interval_90.lower.toFixed(2)}–${posterior.credible_interval_90.upper.toFixed(2)} 90% CrI)` : '—'}</dd></div>
          <div><dt>Suggested interval factor</dt><dd>{calibration ? `${calibration.suggested_interval_factor.toFixed(2)}×${calibration.bounded_direction ? ` · ${calibration.bounded_direction} bound` : ''}` : '—'}</dd></div>
          <div><dt>Posterior boundary check</dt><dd>{calibration?.boundary_limited ? 'Limited by model boundary' : 'Clear'}</dd></div>
          <div><dt>Ready for individualized calibration</dt><dd>{calibration?.ready ? 'Yes' : 'Collecting evidence'}</dd></div>
          <div><dt>Evaluated forecasts</dt><dd>{forecast?.count ?? 0}</dd></div>
          <div><dt>Self-grade Brier score</dt><dd>{forecast?.brier_score == null ? '—' : forecast.brier_score.toFixed(3)}</dd></div>
          <div><dt>Self-grade log loss</dt><dd>{forecast?.log_loss == null ? '—' : forecast.log_loss.toFixed(3)}</dd></div>
        </dl>
        {calibrationReport && <p className="calendar-calibration-note">Readiness requires at least {calibrationReport.readiness_requirements.minimum_observations} delayed observations across {calibrationReport.readiness_requirements.minimum_distinct_cards} cards, {calibrationReport.readiness_requirements.minimum_effective_exposure.toFixed(0)} units of normalized-delay exposure, sufficiently narrow uncertainty, and no material posterior mass at a model boundary. Brier score and log loss evaluate pre-outcome self-grade forecasts; lower is better. They do not score mathematical correctness.</p>}
      </section>
    </main>
  </div>;
}
