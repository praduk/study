'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, ArrowLeft, Brain, Check, ChevronRight, Eye, Pencil, RotateCcw } from 'lucide-react';

import { MathMarkdown } from '@/components/MathMarkdown';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { advanceReviewQueue, reviewAttemptSubmission } from '@/lib/review-session';
import type { ReviewAttemptSubmission } from '@/lib/review-session';
import type { ReviewCard, Variant } from '@/lib/types';

interface RevealResult {
  attempt_id: string;
  answer: { primary: Variant; alternatives: Variant[] };
  feedback_cues: string[];
}

interface Props {
  initialDue: number;
  isMobile: boolean;
  onExit: () => void;
  onChanged: () => void;
}

const GRADES = [
  { grade: 0, key: '1', label: 'Again', note: 'Major gap or no valid method', className: 'grade-again' },
  { grade: 1, key: '2', label: 'Hard', note: 'Partial, slow, or needed help', className: 'grade-hard' },
  { grade: 2, key: '3', label: 'Good', note: 'Correct and unaided', className: 'grade-good' },
  { grade: 3, key: '4', label: 'Easy', note: 'Fluent and precise', className: 'grade-easy' },
];

const REVIEW_BATCH_SIZE = 200;

export function ReviewView({ initialDue, isMobile, onExit, onChanged }: Props) {
  const [cards, setCards] = useState<ReviewCard[]>([]);
  const [index, setIndex] = useState(0);
  const [attempt, setAttempt] = useState('');
  const [attemptPreview, setAttemptPreview] = useState(false);
  const [submittedAttempt, setSubmittedAttempt] = useState<ReviewAttemptSubmission | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [revealed, setRevealed] = useState<RevealResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [queueError, setQueueError] = useState('');
  const [pendingAction, setPendingAction] = useState<'reveal' | 'grade' | null>(null);
  const [completed, setCompleted] = useState(0);
  const [startingDue] = useState(initialDue);
  const startedAt = useRef(0);
  const actionInFlight = useRef<'reveal' | 'grade' | null>(null);
  const queueLoadInFlight = useRef(false);

  const loadBatch = useCallback(async (afterSavedGrade = false) => {
    if (queueLoadInFlight.current) return;
    queueLoadInFlight.current = true;
    setLoading(true);
    setQueueError('');
    try {
      const result = await api<{ cards: ReviewCard[] }>(`/api/review/queue?limit=${REVIEW_BATCH_SIZE}`);
      if (!Array.isArray(result.cards)) throw new Error('The server returned an invalid review queue.');
      setCards(result.cards);
      setIndex(0);
      startedAt.current = Date.now();
    } catch (reason) {
      setCards([]);
      setIndex(0);
      const detail = (reason as Error).message;
      setQueueError(afterSavedGrade
        ? `Your grade was saved, but Study could not load the next review batch. ${detail}`
        : `Study could not load the review queue. ${detail}`);
    } finally {
      queueLoadInFlight.current = false;
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(() => loadBatch());
  }, [loadBatch]);

  const card = cards[index];
  const remainingInBatch = Math.max(0, cards.length - index);
  const progress = Math.min(100, (completed / Math.max(1, startingDue, completed + remainingInBatch)) * 100);

  const reveal = async () => {
    if (!card || actionInFlight.current) return;
    if (confidence === null) { setError('Rate your confidence before revealing the answer.'); return; }
    actionInFlight.current = 'reveal';
    setPendingAction('reveal');
    setError('');
    const submission = reviewAttemptSubmission(attempt, isMobile);
    try {
      const result = await api<RevealResult>(`/api/review/${encodeURIComponent(card.id)}/reveal`, {
        method: 'POST',
        body: JSON.stringify({ ...submission, confidence, elapsed_ms: startedAt.current ? Date.now() - startedAt.current : 0 }),
      });
      setSubmittedAttempt(submission);
      setRevealed(result);
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      actionInFlight.current = null;
      setPendingAction(null);
    }
  };

  const grade = async (value: number) => {
    if (!card || !revealed || actionInFlight.current) return;
    actionInFlight.current = 'grade';
    setPendingAction('grade');
    setError('');
    try {
      const result = await api<{ retry_in_session: boolean; retry_after_items: number | null }>(`/api/review/${encodeURIComponent(card.id)}/grade`, {
        method: 'POST', body: JSON.stringify({ grade: value, attempt_id: revealed.attempt_id }),
      });
      const advance = advanceReviewQueue(
        cards,
        index,
        result.retry_in_session
          ? { card: { ...card, new: false }, afterItems: result.retry_after_items ?? 3 }
          : null,
      );
      setCompleted((count) => count + 1);
      setCards(advance.cards);
      setIndex(advance.nextIndex);
      setAttempt('');
      setAttemptPreview(false);
      setSubmittedAttempt(null);
      setConfidence(null);
      setRevealed(null);
      startedAt.current = Date.now();
      onChanged();
      if (advance.batchExhausted) await loadBatch(true);
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      actionInFlight.current = null;
      setPendingAction(null);
    }
  };

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (!revealed || actionInFlight.current || !['1', '2', '3', '4'].includes(event.key)) return;
      event.preventDefault();
      void grade(Number(event.key) - 1);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  });

  if (loading) return <div className="review-screen"><div className="review-empty">Preparing today’s review…</div></div>;
  if (queueError) return (
    <div className="review-screen">
      <header className="review-top"><Button variant="ghost" onClick={onExit}><ArrowLeft /> Library</Button></header>
      <div className="review-empty" role="alert">
        <span className="complete-mark queue-error-mark"><AlertTriangle /></span>
        <h1>Review could not load</h1>
        <p>{queueError}</p>
        <Button onClick={() => void loadBatch(completed > 0)}>Try again</Button>
      </div>
    </div>
  );
  if (!card) return (
    <div className="review-screen">
      <header className="review-top"><Button variant="ghost" onClick={onExit}><ArrowLeft /> Library</Button></header>
      <div className="review-empty complete">
        <span className="complete-mark"><Check /></span>
        <h1>{completed ? 'Review complete' : 'Nothing is due'}</h1>
        <p>{completed ? `You completed ${completed} deliberate ${completed === 1 ? 'attempt' : 'attempts'}.` : 'Spacing only works when there is space. Come back when an item is due.'}</p>
        <Button onClick={onExit}>Return to library</Button>
      </div>
    </div>
  );

  return (
    <div className="review-screen">
      <header className="review-top">
        <Button variant="ghost" onClick={onExit}><ArrowLeft /> Library</Button>
        <div className="review-progress"><span style={{ width: `${progress}%` }} /></div>
        <div className="review-count">{completed} completed · {remainingInBatch} in current batch</div>
      </header>
      <main className="review-stage">
        <div className="review-context"><span className={`type-chip type-${card.kind}`}>{card.kind}</span><code>{card.canonical_tag}</code><span>{card.mode_label}</span>{card.new && <em>new</em>}</div>
        <h1>{card.title}</h1>
        {card.header && <MathMarkdown content={card.header} className="review-header-markdown" folderId={card.folder_id} interactive={revealed !== null} />}
        <section className="review-prompt">
          <div className="prompt-eyebrow"><Brain size={15} /> Retrieve before you reveal</div>
          <h2>{card.prompt}</h2>
          {card.prompt_body && <MathMarkdown content={card.prompt_body} folderId={card.folder_id} interactive={revealed !== null} />}
        </section>

        {!revealed ? (
          <section className="attempt-panel">
            <div className="attempt-heading">
              {isMobile ? <span>Think-only attempt</span> : <label htmlFor="review-attempt">Your attempt</label>}
              {!isMobile && <Button variant="ghost" size="sm" onClick={() => setAttemptPreview((value) => !value)} disabled={(!attempt.trim() && !attemptPreview) || pendingAction !== null}>
                {attemptPreview ? <Pencil /> : <Eye />} {attemptPreview ? 'Edit' : 'Preview'}
              </Button>}
            </div>
            {isMobile ? (
              <p className="think-only-guidance">Think through the complete answer before revealing it.</p>
            ) : attemptPreview ? (
              <div className="attempt-preview"><MathMarkdown content={attempt} folderId={card.folder_id} interactive={false} /></div>
            ) : (
              <textarea id="review-attempt" value={attempt} onChange={(event) => setAttempt(event.target.value)} placeholder="Write your statement, proof, or solution in Markdown—or leave this empty for think-only review…" disabled={pendingAction !== null} />
            )}
            <fieldset className="confidence-row">
              <legend>How confident are you in that answer?</legend>
              <div className="confidence-options">
                {[1, 2, 3].map((value) => <button key={value} type="button" aria-pressed={confidence === value} className={confidence === value ? 'selected' : ''} onClick={() => setConfidence(value)} disabled={pendingAction !== null}>{value === 1 ? 'Unsure' : value === 2 ? 'Somewhat' : 'Confident'}</button>)}
              </div>
            </fieldset>
            {error && <div className="form-error" role="alert">{error}</div>}
            <Button className="reveal-button" onClick={reveal} disabled={pendingAction !== null} aria-busy={pendingAction === 'reveal'}><Eye /> {pendingAction === 'reveal' ? 'Revealing…' : 'Reveal and compare'}</Button>
          </section>
        ) : (
          <section className="feedback-panel">
            <div className="comparison-grid">
              <div><div className="answer-label">Your attempt</div>{submittedAttempt?.overt ? <MathMarkdown content={submittedAttempt.attempt} folderId={card.folder_id} interactive={false} /> : <em>Think-only attempt</em>}</div>
              <div><div className="answer-label">Canonical answer</div><MathMarkdown content={revealed.answer.primary.content || ''} folderId={card.folder_id} /></div>
            </div>
            {revealed.answer.alternatives.map((item) => <details className="review-supplement" key={item.id}><summary>Alternative {card.mode === 'proof-plan' ? 'proof' : card.mode === 'solve' ? 'solution' : 'formulation'}: {item.label}</summary><MathMarkdown content={item.content || ''} folderId={card.folder_id} /></details>)}
            <div className="feedback-checklist">{revealed.feedback_cues.map((cue) => <p key={cue}><ChevronRight size={14} /> {cue}</p>)}</div>
            <div className="grade-prompt">Grade the retrieval, not familiarity after seeing the answer.</div>
            <div className="grade-grid">{GRADES.map((item) => <button key={item.grade} className={item.className} onClick={() => void grade(item.grade)} disabled={pendingAction !== null} aria-busy={pendingAction === 'grade'}><kbd>{item.key}</kbd><strong>{item.label}</strong><span>{item.note}</span></button>)}</div>
            {error && <div className="form-error" role="alert">{error}</div>}
            <p className="scheduler-disclosure"><RotateCcw size={13} /> “Again” returns later in this session; later spacing self-calibrates to grades from delayed reviews once enough evidence exists. It predicts your grading behavior, not objective mastery.</p>
          </section>
        )}
      </main>
    </div>
  );
}
