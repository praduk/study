const byId = (id) => document.getElementById(id);
const app = byId('app');
const main = byId('main');
const dialog = byId('dialog');
const dialogContent = byId('dialog-content');

const state = {
  csrf: null,
  authRequired: false,
  data: null,
  entry: null,
  selectedEntryId: null,
  selectedFolderId: null,
  selectedVariantId: null,
  expanded: new Set(),
  view: 'library',
  month: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  calendarIncludeInactive: false,
  review: null,
};

const kindNames = { ax: 'Axiom', df: 'Definition', rk: 'Remark', th: 'Theorem', pb: 'Problem' };
const gradeNames = ['Again', 'Hard', 'Good', 'Easy'];

function node(tag, className = '', text = '') {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== '') element.textContent = text;
  return element;
}

function button(label, action, className = '') {
  const element = node('button', className, label);
  element.type = 'button';
  element.addEventListener('click', action);
  return element;
}

function clear(element) {
  element.replaceChildren();
  return element;
}

function iso(value) {
  if (!value) return 'Not yet';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toLocaleString();
}

function percent(value, digits = 0) {
  return typeof value === 'number' && Number.isFinite(value)
    ? `${(value * 100).toFixed(digits)}%`
    : '—';
}

function prediction(value, status) {
  if (typeof value === 'number' && Number.isFinite(value)) return percent(value, 1);
  if (status === 'short-delay-excluded') return '— (under six-hour evidence minimum)';
  if (status === 'beyond-model-range') return '— (beyond normalized-delay cap)';
  return '—';
}

function showToast(message, isError = false) {
  const toast = byId('toast');
  toast.textContent = message;
  toast.classList.toggle('error', isError);
  toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => { toast.hidden = true; }, 4200);
}

async function api(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method) && state.csrf) {
    headers.set('x-study-csrf', state.csrf);
  }
  const response = await fetch(path, { ...options, method, headers });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      detail = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail || payload);
    } catch { /* retain the status */ }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  const type = response.headers.get('content-type') || '';
  return type.includes('application/json') ? response.json() : response;
}

async function renderMarkdown(source, folderId = '') {
  if (!source) return '';
  const result = await api('/api/render/markdown', {
    method: 'POST',
    body: JSON.stringify({ source, folder_id: folderId || null }),
  });
  return result.html;
}

async function typeset(element = main) {
  if (!window.MathJax?.typesetPromise) return;
  try {
    await window.MathJax.typesetPromise([element]);
  } catch (reason) {
    console.warn('MathJax could not typeset this view.', reason);
  }
}

function installMathJax(macros) {
  if (byId('mathjax-runtime')) return;
  window.MathJax = {
    loader: {
      paths: {
        mathjax: '/vendor/mathjax',
        'mathjax-newcm': '/vendor/mathjax-newcm-font',
      },
      load: ['ui/safe'],
    },
    tex: {
      inlineMath: [['\\(', '\\)'], ['$', '$']],
      displayMath: [['\\[', '\\]'], ['$$', '$$']],
      processEscapes: true,
      macros: macros || {},
    },
    chtml: { displayOverflow: 'linebreak' },
    options: { enableMenu: false },
    startup: { typeset: false },
  };
  const script = document.createElement('script');
  script.id = 'mathjax-runtime';
  script.src = '/vendor/mathjax/tex-chtml.js';
  script.async = true;
  script.addEventListener('load', () => void typeset());
  script.addEventListener('error', () => showToast('Math remains readable as source; the optional local typesetter is unavailable.', true));
  document.head.appendChild(script);
}

function folderPath(folderId) {
  const folders = state.data?.folders || [];
  const byFolder = new Map(folders.map((folder) => [folder.id, folder]));
  const path = [];
  let current = byFolder.get(folderId);
  while (current) {
    path.unshift(current.id);
    current = current.parent_id ? byFolder.get(current.parent_id) : null;
  }
  return path;
}

function entryUrl(entry, variant = null) {
  let tag = entry.canonical_tag;
  if (variant?.canonical_tag) tag = variant.canonical_tag;
  return `/library/${tag.split(':').map(encodeURIComponent).join('/')}`;
}

function syncLocation(replace = false) {
  if (!state.entry) return;
  const variants = [...state.entry.formulations, ...state.entry.supplements];
  const active = variants.find((item) => item.id === state.selectedVariantId) || null;
  const path = entryUrl(state.entry, active);
  if (window.location.pathname !== path) history[replace ? 'replaceState' : 'pushState'](null, '', path);
}

function selectFromLocation() {
  if (!state.data || !window.location.pathname.startsWith('/library/')) return null;
  const tag = window.location.pathname.slice('/library/'.length).split('/').map(decodeURIComponent).join(':');
  let best = null;
  for (const entry of state.data.entries) {
    if (tag === entry.canonical_tag || tag.startsWith(`${entry.canonical_tag}:`)) {
      if (!best || entry.canonical_tag.length > best.canonical_tag.length) best = entry;
    }
  }
  return best;
}

async function loadBootstrap({ preserveSelection = true } = {}) {
  const data = await api('/api/bootstrap');
  state.data = data;
  byId('due-count').textContent = String(data.review?.due || 0);
  byId('library-count').textContent = `${data.entries.length} items · ${data.folders.length} folders`;
  installMathJax(data.macros);
  const locationEntry = selectFromLocation();
  const current = preserveSelection && data.entries.find((item) => item.id === state.selectedEntryId);
  const target = locationEntry || current || data.entries[0] || null;
  if (target) {
    state.selectedEntryId = target.id;
    state.selectedFolderId = target.folder_id;
    folderPath(target.folder_id).forEach((id) => state.expanded.add(id));
  }
  renderTree();
  return data;
}

function renderTree() {
  const root = clear(byId('tree'));
  if (!state.data?.tree.length) {
    root.append(node('p', 'callout', 'Create a folder to begin.'));
    return;
  }

  function renderFolder(folder, depth = 0) {
    const container = node('div');
    const row = node('div', 'tree-row');
    row.style.paddingLeft = `${6 + depth * 5}px`;
    const toggle = button(state.expanded.has(folder.id) ? '▾' : '▸', () => {
      if (state.expanded.has(folder.id)) state.expanded.delete(folder.id);
      else state.expanded.add(folder.id);
      renderTree();
    });
    toggle.className = 'chevron';
    toggle.setAttribute('aria-label', `${state.expanded.has(folder.id) ? 'Collapse' : 'Expand'} ${folder.name}`);
    const check = document.createElement('input');
    check.type = 'checkbox';
    check.checked = Boolean(folder.review_enabled);
    check.title = `Include ${folder.name} in review`;
    check.addEventListener('change', async () => {
      try {
        await api(`/api/folders/${encodeURIComponent(folder.id)}`, {
          method: 'PATCH', body: JSON.stringify({ review_enabled: check.checked }),
        });
        await loadBootstrap();
      } catch (reason) { check.checked = !check.checked; showToast(reason.message, true); }
    });
    const name = button(folder.name, () => {
      state.selectedFolderId = folder.id;
      state.expanded.add(folder.id);
      renderTree();
    });
    name.className = 'tree-name';
    const count = node('span', 'count', String(folder.entries.length));
    row.append(toggle, check, name, count);
    container.append(row);
    if (state.expanded.has(folder.id)) {
      const group = node('div', 'tree-group');
      for (const entry of folder.entries) {
        const entryButton = button('', () => void openEntry(entry.id));
        entryButton.className = `tree-row entry ${state.selectedEntryId === entry.id ? 'active' : ''}`;
        entryButton.append(node('span', 'kind', entry.kind), node('span', 'tree-name', entry.title));
        group.append(entryButton);
      }
      for (const child of folder.children) group.append(renderFolder(child, depth + 1));
      container.append(group);
    }
    return container;
  }

  state.data.tree.forEach((folder) => root.append(renderFolder(folder)));
}

async function openEntry(entryId, { replace = false, variantId = null } = {}) {
  try {
    const entry = await api(`/api/entries/${encodeURIComponent(entryId)}`);
    state.view = 'library';
    state.entry = entry;
    state.selectedEntryId = entry.id;
    state.selectedFolderId = entry.folder_id;
    state.selectedVariantId = variantId || entry.formulations.find((item) => item.main)?.id || entry.formulations[0]?.id || null;
    folderPath(entry.folder_id).forEach((id) => state.expanded.add(id));
    renderTree();
    await renderEntry();
    syncLocation(replace);
    app.classList.remove('mobile-library');
  } catch (reason) {
    showToast(reason.message, true);
  }
}

async function renderEntry() {
  const entry = state.entry;
  if (!entry) return renderEmpty();
  clear(main);
  const article = node('article', 'document');
  const folder = state.data.folders.find((item) => item.id === entry.folder_id);
  article.append(node('div', 'breadcrumbs', `${folder?.namespace?.split(':').join(' / ') || ''} / ${kindNames[entry.kind]}`));
  const heading = node('div', 'document-heading');
  const title = node('div');
  title.append(node('div', 'canonical', entry.canonical_tag), node('h1', '', entry.title));
  const actions = node('div', 'row-actions desktop-author');
  actions.append(button('Edit', () => openEditor(entry)));
  heading.append(title, actions);
  article.append(heading);

  if (entry.header) {
    const header = node('div', 'content-header markdown-body');
    header.innerHTML = await renderMarkdown(entry.header, entry.folder_id);
    article.append(header);
  }

  const active = entry.formulations.find((item) => item.id === state.selectedVariantId) || entry.formulations[0];
  if (entry.formulations.length > 1) {
    const tabs = node('div', 'variant-tabs');
    for (const variant of entry.formulations) {
      tabs.append(button(`${variant.label}${variant.main ? ' · main' : ''}`, async () => {
        state.selectedVariantId = variant.id;
        await renderEntry();
        syncLocation(true);
      }, variant.id === active.id ? 'active' : ''));
    }
    article.append(tabs);
  }
  const body = node('div', 'markdown-body');
  body.innerHTML = await renderMarkdown(active?.content || '', entry.folder_id);
  article.append(body);

  if (entry.supplements.length) {
    const section = node('section', 'supplements');
    section.append(node('h2', '', entry.kind === 'pb' ? 'Solutions' : 'Proofs'));
    for (const supplement of entry.supplements) {
      const details = document.createElement('details');
      const summary = node('summary', '', `${supplement.label}${supplement.main ? ' · main' : ''}`);
      const content = node('div', 'markdown-body');
      content.innerHTML = await renderMarkdown(supplement.content || '', entry.folder_id);
      details.append(summary, content);
      section.append(details);
    }
    article.append(section);
  }
  main.append(article);
  await typeset(article);
}

function renderEmpty() {
  clear(main);
  const empty = node('section', 'empty-state');
  empty.append(node('h1', '', 'Your study library'), node('p', '', 'Choose an item from the library. Authored content is stored as ordinary Markdown and small JSON sidecars.'));
  main.append(empty);
}

function field(labelText, control, full = false) {
  const label = node('label', `field${full ? ' full' : ''}`);
  label.append(node('span', '', labelText), control);
  return label;
}

function showDialog(title, content, actions = []) {
  clear(dialogContent);
  dialogContent.append(node('h2', '', title), content);
  if (actions.length) {
    const footer = node('div', 'dialog-actions');
    actions.forEach((action) => footer.append(action));
    dialogContent.append(footer);
  }
  dialog.showModal();
}

function openEditor(existing = null) {
  const folderId = existing?.folder_id || state.selectedFolderId || state.data?.folders[0]?.id;
  if (!folderId) return showToast('Create a folder before creating an item.', true);
  const active = existing
    ? existing.formulations.find((item) => item.id === state.selectedVariantId) || existing.formulations[0]
    : null;
  const grid = node('div', 'form-grid');
  const title = document.createElement('input'); title.value = existing?.title || '';
  const tag = document.createElement('input'); tag.value = existing?.tag || '';
  const kind = document.createElement('select');
  Object.entries(kindNames).forEach(([value, label]) => {
    const option = node('option', '', label); option.value = value; option.selected = value === (existing?.kind || 'df'); kind.append(option);
  });
  const header = document.createElement('textarea'); header.value = existing?.header || ''; header.style.minHeight = '75px';
  const content = document.createElement('textarea'); content.value = active?.content || '';
  grid.append(field('Title', title), field('Tag', tag), field('Type', kind), field('Header', header), field(active ? active.label : 'Main formulation', content, true));
  const note = node('p', 'callout field full', 'This no-build editor covers ordinary Markdown. Alternative variants and graphical editing remain available when the optional rich frontend is installed.');
  grid.append(note);
  const save = button('Save', async () => {
    save.disabled = true;
    try {
      let saved;
      if (existing) {
        saved = await api(`/api/entries/${encodeURIComponent(existing.id)}`, {
          method: 'PATCH',
          body: JSON.stringify({ title: title.value, tag: tag.value, kind: kind.value, header: header.value }),
        });
        saved = await api(`/api/entries/${encodeURIComponent(existing.id)}/content/${encodeURIComponent(active.id)}`, {
          method: 'PUT', body: JSON.stringify({ content: content.value }),
        });
      } else {
        saved = await api('/api/entries', {
          method: 'POST',
          body: JSON.stringify({ folder_id: folderId, kind: kind.value, title: title.value, tag: tag.value, header: header.value, content: content.value }),
        });
      }
      dialog.close();
      await loadBootstrap({ preserveSelection: false });
      await openEntry(saved.id, { variantId: saved.formulations[0]?.id || null });
      showToast('Saved.');
    } catch (reason) {
      showToast(reason.message, true);
    } finally { save.disabled = false; }
  }, 'primary');
  showDialog(existing ? `Edit ${existing.title}` : 'New study item', grid, [button('Cancel', () => dialog.close()), save]);
  title.focus();
}

async function createFolder() {
  const name = window.prompt('Folder name');
  if (!name) return;
  const suggested = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const slug = window.prompt('Namespace segment', suggested);
  if (!slug) return;
  try {
    const created = await api('/api/folders', {
      method: 'POST', body: JSON.stringify({ name, slug, parent_id: state.selectedFolderId || null }),
    });
    state.selectedFolderId = created.id;
    state.expanded.add(created.id);
    await loadBootstrap();
    showToast('Folder created.');
  } catch (reason) { showToast(reason.message, true); }
}

function monthRange(month) {
  const start = new Date(month.getFullYear(), month.getMonth(), 1);
  const end = new Date(month.getFullYear(), month.getMonth() + 1, 1);
  return { start: start.toISOString(), end: end.toISOString() };
}

function localDateKey(value) {
  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function calendarEventButton(event) {
  return button(
    `${new Date(event.due_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })} · ${event.title || event.card_id}`,
    () => showCalendarEvent(event),
    `calendar-event${event.active ? '' : ' inactive'}`,
  );
}

function showCalendarEvent(event) {
  const schedule = event.schedule_at_last_grade || event.schedule || {};
  const estimate = event.model_estimate || {};
  const scheduler = schedule.scheduler || null;
  const fixedAgain = scheduler?.reason === 'again';
  const interval = estimate.posterior_interval_scale || null;
  const scheduledInterval = fixedAgain
    ? `${scheduler.interval_minutes ?? 10} minutes · fixed Again retry`
    : scheduler?.interval_days != null
      ? `${scheduler.interval_days} days · ${Number(scheduler.interval_factor).toFixed(2)}× factor`
      : 'Fallback schedule';
  const scheduleSource = fixedAgain
    ? 'Fixed Again rule; Bayesian interval not used'
    : scheduler?.calibrated_interval_used
      ? `${scheduler.source} Bayesian calibration · ${scheduler.observations} qualified observations`
      : `Conservative fallback${scheduler ? ` · ${scheduler.observations} qualified observations` : ''}`;
  const scheduleBound = scheduler?.bounded_direction === 'shorter'
    ? ' · lower safety bound reached'
    : scheduler?.bounded_direction === 'longer'
      ? ' · upper safety bound reached'
      : '';
  const body = node('div');
  const description = node('p', 'canonical', event.canonical_tag || event.card_id);
  const list = node('dl', 'detail-list');
  const rows = [
    ['Task', event.mode_label || event.mode],
    ['Review status', event.active ? 'Active' : event.inactive_reason === 'review-disabled' ? 'Review disabled' : 'Unavailable'],
    ['Due', iso(event.due_at)],
    ['Last reviewed', iso(schedule.last_reviewed_at)],
    ['Last self-grade', Number.isInteger(schedule.last_grade) ? gradeNames[schedule.last_grade] : '—'],
    ['Stability heuristic', schedule.stability_days == null ? '—' : `${schedule.stability_days} days`],
    ['Difficulty heuristic', schedule.difficulty ?? '—'],
    ['Interval-advancing grades / Again lapses', `${schedule.repetitions ?? 0} / ${schedule.lapses ?? 0}`],
    ['Scheduled interval', scheduledInterval],
    ['Schedule source', scheduleSource + scheduleBound],
    ['Model status', estimate.boundary_limited ? 'Collecting; posterior meets a model boundary' : estimate.ready ? 'Ready' : 'Collecting evidence'],
    ['Posterior interval-scale median', interval ? Number(interval.median).toFixed(2) : '—'],
    ['Posterior interval-scale 90% credible interval', interval ? `${Number(interval.credible_interval_90.lower).toFixed(2)}–${Number(interval.credible_interval_90.upper).toFixed(2)}` : '—'],
    ['Predicted Good-or-Easy now', prediction(estimate.predicted_good_or_easy_now, estimate.prediction_status_now)],
    ['Predicted Good-or-Easy at due', prediction(estimate.predicted_good_or_easy_at_due, estimate.prediction_status_at_due)],
  ];
  for (const [term, value] of rows) list.append(node('dt', '', term), node('dd', '', String(value)));
  body.append(description, list, node('p', 'callout', 'These model-conditional probabilities predict your future self-grade. They are not probabilities of correctness, mastery, or durable remembering.'));
  showDialog(event.title || 'Review schedule', body, [button('Close', () => dialog.close())]);
}

function statCard(value, label) {
  const card = node('div', 'stat-card');
  card.append(node('strong', '', String(value ?? '—')), node('span', '', label));
  return card;
}

async function renderCalendar({ updateHistory = true } = {}) {
  state.view = 'calendar';
  if (updateHistory && window.location.pathname !== '/calendar') history.pushState(null, '', '/calendar');
  clear(main);
  const view = node('section', 'calendar-view');
  view.append(node('div', 'eyebrow', 'Review schedule'), node('h1', '', 'Calendar and model statistics'));
  const disclosure = node('p', 'callout', 'Each event is the next due time for one reviewed card. Future dates cannot be forecast beyond the next review because your next self-grade changes the schedule.');
  view.append(disclosure);
  const inactiveLabel = node('label', 'calendar-inactive');
  const inactiveToggle = document.createElement('input');
  inactiveToggle.type = 'checkbox';
  inactiveToggle.checked = state.calendarIncludeInactive;
  inactiveToggle.addEventListener('change', () => {
    state.calendarIncludeInactive = inactiveToggle.checked;
    void renderCalendar({ updateHistory: false });
  });
  inactiveLabel.append(inactiveToggle, ' Show disabled and unavailable scheduled items');
  view.append(inactiveLabel);
  const loading = node('p', '', 'Loading calendar…');
  view.append(loading);
  main.append(view);
  try {
    const range = monthRange(state.month);
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const inactive = state.calendarIncludeInactive ? '&include_inactive=true' : '';
    const payload = await api(`/api/review/calendar?start=${encodeURIComponent(range.start)}&end=${encodeURIComponent(range.end)}&timezone=${encodeURIComponent(timezone)}${inactive}`);
    loading.remove();
    const stats = payload.statistics || {};
    const statGrid = node('div', 'stat-grid');
    statGrid.append(
      statCard(stats.attempts ?? stats.total_attempts ?? 0, 'attempts this month'),
      statCard(stats.minutes ?? stats.minutes_reviewed ?? 0, 'minutes reviewed'),
      statCard(percent(stats.good_or_easy_self_grade_rate), 'Good-or-Easy self-grades'),
      statCard(stats.again_lapses ?? 0, 'Again self-grades'),
    );
    view.append(statGrid);

    const toolbar = node('div', 'calendar-toolbar');
    const previous = button('←', () => { state.month = new Date(state.month.getFullYear(), state.month.getMonth() - 1, 1); void renderCalendar(); });
    const next = button('→', () => { state.month = new Date(state.month.getFullYear(), state.month.getMonth() + 1, 1); void renderCalendar(); });
    toolbar.append(previous, node('h2', '', state.month.toLocaleDateString([], { month: 'long', year: 'numeric' })), next);
    view.append(toolbar);

    const events = payload.events || [];
    const eventsByDate = new Map();
    for (const event of events) {
      const key = localDateKey(event.due_at);
      if (!eventsByDate.has(key)) eventsByDate.set(key, []);
      eventsByDate.get(key).push(event);
    }
    const grid = node('div', 'calendar-grid');
    ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach((day) => grid.append(node('div', 'calendar-weekday', day)));
    const first = new Date(state.month.getFullYear(), state.month.getMonth(), 1);
    const cursor = new Date(first); cursor.setDate(1 - first.getDay());
    const today = localDateKey(new Date());
    for (let index = 0; index < 42; index += 1) {
      const date = new Date(cursor); date.setDate(cursor.getDate() + index);
      const key = localDateKey(date);
      const day = node('div', `calendar-day${date.getMonth() !== state.month.getMonth() ? ' outside' : ''}${key === today ? ' today' : ''}`);
      day.append(node('span', 'day-number', String(date.getDate())));
      for (const event of eventsByDate.get(key) || []) day.append(calendarEventButton(event));
      grid.append(day);
    }
    view.append(grid);

    const agenda = node('div', 'agenda');
    if (!events.length) agenda.append(node('p', 'callout', 'No reviewed cards are due in this month.'));
    for (const [key, dayEvents] of [...eventsByDate.entries()].sort()) {
      const section = node('section', 'agenda-day');
      section.append(node('h3', '', new Date(`${key}T12:00:00`).toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })));
      dayEvents.forEach((event) => section.append(calendarEventButton(event)));
      agenda.append(section);
    }
    view.append(agenda);

    const calibration = payload.calibration || state.data?.review?.calibration;
    if (calibration?.models) {
      view.append(node('h2', '', 'Bayesian scheduling diagnostics'));
      const table = node('table', 'model-table');
      const head = node('thead'); const headRow = node('tr');
      ['Model', 'Evidence', 'Good / Easy', 'Exposure', 'Suggested factor', 'Uncertainty', 'Status'].forEach((label) => headRow.append(node('th', '', label)));
      head.append(headRow); table.append(head);
      const body = node('tbody');
      const labels = ['Model', 'Evidence', 'Good / Easy', 'Exposure', 'Suggested factor', 'Uncertainty', 'Status'];
      for (const [name, model] of Object.entries(calibration.models)) {
        const row = node('tr');
        const values = [
          name === 'proof-plan' ? 'theorem proof' : name === 'solve' ? 'problem solution' : name,
          `${model.observations ?? 0} / ${model.distinct_cards ?? 0} cards`,
          model.observations ? `${model.good_or_easy_self_grades ?? 0} / ${model.observations}` : '—',
          String(model.effective_exposure ?? 0),
          model.suggested_interval_factor == null ? '—' : `${Number(model.suggested_interval_factor).toFixed(2)}×${model.bounded_direction ? ` (${model.bounded_direction} bound)` : ''}`,
          String(model.posterior_log_scale_sd ?? '—'),
          model.boundary_limited ? 'boundary-limited' : model.ready ? 'ready' : 'collecting',
        ];
        row.append(...values.map((value, index) => {
          const cell = node('td', '', value);
          cell.dataset.label = labels[index];
          return cell;
        }));
        body.append(row);
      }
      table.append(body);
      const tableScroll = node('div', 'model-table-scroll');
      tableScroll.append(table);
      view.append(tableScroll);
      const forecast = calibration.forecast_evaluation;
      if (forecast) {
        view.append(node('p', 'callout', forecast.count
          ? `${forecast.count} qualified pre-outcome self-grade forecasts · Brier score ${Number(forecast.brier_score).toFixed(3)} · log loss ${Number(forecast.log_loss).toFixed(3)}. Lower scores are better; these do not measure answer correctness.`
          : 'No qualified pre-outcome forecasts are available yet for Brier score or log-loss evaluation.'));
      }
      view.append(node('p', 'disclosure', `The model targets a ${percent(calibration.target_probability)} chance of a Good-or-Easy self-grade. It uses completed delayed reviews and a conditional-independence approximation; selection and repeated-card correlation can make uncertainty look too small. It does not assess mathematical correctness.`));
    }
  } catch (reason) {
    loading.textContent = reason.message;
    loading.className = 'error';
  }
}

async function startReview({ updateHistory = true } = {}) {
  state.view = 'review';
  if (updateHistory && window.location.pathname !== '/review') history.pushState(null, '', '/review');
  clear(main);
  main.append(node('section', 'review-view', 'Loading review…'));
  try {
    const payload = await api('/api/review/queue?limit=200');
    const cards = payload.cards || [];
    state.review = { cards, mayHaveMore: cards.length === 200, completed: 0, confidence: null, attemptId: null, startedAt: performance.now() };
    await renderReviewCard();
  } catch (reason) { showToast(reason.message, true); renderEmpty(); }
}

async function renderReviewCard() {
  clear(main);
  const session = state.review;
  let card = session?.cards[0];
  if (!card && session?.mayHaveMore) {
    main.append(node('section', 'review-view', 'Loading the next review batch…'));
    try {
      const payload = await api('/api/review/queue?limit=200');
      session.cards = payload.cards || [];
      session.mayHaveMore = session.cards.length === 200;
      card = session.cards[0];
      if (card) return renderReviewCard();
    } catch (reason) {
      showToast(reason.message, true);
      session.mayHaveMore = true;
      clear(main);
      const failed = node('section', 'review-view');
      failed.append(
        node('h1', '', 'The next review batch could not load'),
        node('p', 'callout error', reason.message),
        button('Try again', () => void renderReviewCard(), 'primary'),
      );
      main.append(failed);
      return;
    }
    clear(main);
  }
  const view = node('section', 'review-view');
  if (!card) {
    view.append(node('div', 'eyebrow', 'Session complete'), node('h1', '', session?.completed ? `${session.completed} reviews completed` : 'Nothing is due'), node('p', 'callout', 'Spacing needs actual time between attempts. Return when another card is due.'));
    view.append(button('Return to library', () => void returnToLibrary(), 'primary'));
    main.append(view);
    await loadBootstrap();
    return;
  }
  session.confidence = null;
  session.attemptId = null;
  session.startedAt = performance.now();
  view.append(node('div', 'review-context', `${card.kind.toUpperCase()} · ${card.canonical_tag} · ${card.mode_label}${card.new ? ' · new' : ''}`), node('h1', '', card.title));
  if (card.header) {
    const header = node('div', 'content-header markdown-body'); header.innerHTML = await renderMarkdown(card.header, card.folder_id); view.append(header);
  }
  const prompt = node('section', 'review-card');
  prompt.append(node('div', 'eyebrow', 'Retrieve before revealing'), node('h2', '', card.prompt));
  if (card.prompt_body) { const body = node('div', 'markdown-body'); body.innerHTML = await renderMarkdown(card.prompt_body, card.folder_id); prompt.append(body); }
  view.append(prompt);
  const attemptCard = node('section', 'attempt-card');
  const attempt = document.createElement('textarea'); attempt.placeholder = 'Write your statement, proof, or solution—or leave this empty for a think-only attempt…';
  if (window.matchMedia('(max-width: 800px)').matches) {
    attemptCard.append(node('p', 'callout', 'Retrieve the answer mentally. Phone review records a think-only attempt.'));
  } else {
    attemptCard.append(attempt);
  }
  attemptCard.append(node('p', 'disclosure', 'Rate confidence after making the attempt and before revealing the stored answer.'));
  const confidence = node('div', 'confidence');
  ['Unsure', 'Somewhat', 'Confident'].forEach((label, index) => confidence.append(button(label, (event) => {
    session.confidence = index + 1;
    confidence.querySelectorAll('button').forEach((item) => item.classList.toggle('selected', item === event.currentTarget));
  })));
  attemptCard.append(confidence);
  attemptCard.append(button('Reveal and compare', async () => {
    if (!session.confidence) return showToast('Choose a confidence rating first.', true);
    try {
      const result = await api(`/api/review/${encodeURIComponent(card.id)}/reveal`, {
        method: 'POST',
        body: JSON.stringify({ attempt: attempt.value, confidence: session.confidence, elapsed_ms: Math.round(performance.now() - session.startedAt), overt: Boolean(attempt.value.trim()), hints_used: 0 }),
      });
      session.attemptId = result.attempt_id;
      await showReviewAnswer(view, attemptCard, attempt.value, result, card);
    } catch (reason) { showToast(reason.message, true); }
  }, 'primary'));
  view.append(attemptCard);
  main.append(view);
  await typeset(view);
}

async function showReviewAnswer(view, attemptCard, attempt, result, card) {
  attemptCard.remove();
  const answerCard = node('section', 'answer-card');
  const compare = node('div', 'answer-compare');
  const yours = node('div'); yours.append(node('div', 'eyebrow', 'Your attempt'));
  const yoursBody = node('div', 'markdown-body'); yoursBody.innerHTML = attempt.trim() ? await renderMarkdown(attempt, card.folder_id) : '<em>Think-only attempt</em>'; yours.append(yoursBody);
  const canonical = node('div'); canonical.append(node('div', 'eyebrow', 'Canonical answer'));
  const answerBody = node('div', 'markdown-body'); answerBody.innerHTML = await renderMarkdown(result.answer.primary.content || '', card.folder_id); canonical.append(answerBody);
  compare.append(yours, canonical); answerCard.append(compare);
  const cueList = node('div', 'callout'); (result.feedback_cues || []).forEach((cue) => cueList.append(node('p', '', cue))); answerCard.append(cueList);
  answerCard.append(node('p', '', 'Grade the retrieval, not familiarity after seeing the answer.'));
  const grades = node('div', 'grade-grid');
  const notes = ['Major gap or no valid method', 'Partial, slow, or needed help', 'Correct and unaided', 'Fluent and precise'];
  gradeNames.forEach((name, grade) => {
    const gradeButton = button('', () => void finishGrade(card, grade));
    gradeButton.append(node('strong', '', `${grade + 1} · ${name}`), node('small', '', notes[grade])); grades.append(gradeButton);
  });
  answerCard.append(grades, node('p', 'disclosure', 'Study predicts future Good-or-Easy self-grades, not correctness or mastery.'));
  view.append(answerCard);
  await typeset(answerCard);
}

async function finishGrade(card, grade) {
  try {
    const result = await api(`/api/review/${encodeURIComponent(card.id)}/grade`, {
      method: 'POST', body: JSON.stringify({ attempt_id: state.review.attemptId, grade }),
    });
    const completed = state.review.cards.shift();
    state.review.completed += 1;
    if (result.retry_in_session) {
      const index = Math.min(result.retry_after_items ?? 3, state.review.cards.length);
      state.review.cards.splice(index, 0, completed);
    }
    await renderReviewCard();
  } catch (reason) { showToast(reason.message, true); }
}

async function returnToLibrary() {
  state.view = 'library';
  await loadBootstrap();
  if (state.selectedEntryId) await openEntry(state.selectedEntryId, { replace: true });
  else renderEmpty();
}

async function showGit() {
  try {
    const status = await api('/api/git/status');
    const body = node('div');
    const list = node('dl', 'detail-list');
    const rows = [
      ['Branch', status.branch || '—'],
      ['Authored changes', status.content_dirty ? 'Yes' : 'No'],
      ['Other changes', status.other_dirty ? 'Yes' : 'No'],
      ['Ahead / behind', `${status.ahead ?? '—'} / ${status.behind ?? '—'}`],
    ];
    rows.forEach(([term, value]) => list.append(node('dt', '', term), node('dd', '', value)));
    body.append(list, node('p', 'callout', 'Study’s built-in Git actions remain conservative: authored data only for commit, and clean fast-forward-only pulls. Resolve merges and rebases with Git, then run Study’s validation command.'));
    showDialog('Git status', body, [button('Close', () => dialog.close())]);
  } catch (reason) { showToast(reason.message, true); }
}

async function search() {
  const input = byId('search');
  const results = byId('search-results');
  const query = input.value.trim();
  window.clearTimeout(search.timer);
  if (!query) { results.hidden = true; clear(results); return; }
  search.timer = window.setTimeout(async () => {
    try {
      const payload = await api(`/api/search?q=${encodeURIComponent(query)}&limit=30`);
      clear(results);
      for (const result of payload.results || []) {
        const item = button('', () => {
          input.value = ''; results.hidden = true;
          void openEntry(result.entry_id || result.id, { variantId: result.variant_id || null });
        }, 'search-result');
        item.append(node('span', 'kind', result.kind), node('strong', '', result.title), node('small', '', result.canonical_tag));
        results.append(item);
      }
      if (!results.children.length) results.append(node('p', 'callout', 'No matches.'));
      results.hidden = false;
    } catch (reason) { showToast(reason.message, true); }
  }, 140);
}

function showLogin() {
  byId('loading').hidden = true;
  const form = node('div', 'empty-state');
  form.append(node('h1', '', 'Study'), node('p', '', 'This library is password protected.'));
  const password = document.createElement('input'); password.type = 'password'; password.placeholder = 'Password'; password.style.padding = '10px';
  form.append(password, button('Open library', async () => {
    try {
      const result = await api('/api/login', { method: 'POST', body: JSON.stringify({ password: password.value }) });
      state.csrf = result.csrf;
      form.remove();
      await start();
    } catch (reason) { showToast(reason.message, true); }
  }, 'primary'));
  document.body.append(form);
  password.focus();
}

async function start() {
  try {
    const session = await api('/api/session');
    state.csrf = session.csrf;
    state.authRequired = session.auth_required;
    if (!session.authenticated) return showLogin();
    byId('logout-button').hidden = !state.authRequired;
    await loadBootstrap({ preserveSelection: false });
    byId('loading').hidden = true;
    app.hidden = false;
    const route = window.location.pathname;
    if (route === '/calendar') await renderCalendar({ updateHistory: false });
    else if (route === '/review') await startReview({ updateHistory: false });
    else if (state.selectedEntryId) await openEntry(state.selectedEntryId, { replace: true });
    else renderEmpty();
  } catch (reason) {
    byId('loading').textContent = `Study could not open: ${reason.message}`;
    byId('loading').classList.add('error');
  }
}

byId('library-toggle').addEventListener('click', () => {
  if (window.matchMedia('(max-width: 800px)').matches) app.classList.toggle('mobile-library');
  else app.classList.toggle('sidebar-closed');
});
byId('brand').addEventListener('click', () => void returnToLibrary());
byId('calendar-button').addEventListener('click', () => void renderCalendar());
byId('review-button').addEventListener('click', () => void startReview());
byId('theme-button').addEventListener('click', () => {
  const dark = !document.documentElement.classList.contains('dark');
  document.documentElement.classList.toggle('dark', dark);
  localStorage.setItem('study-theme', dark ? 'dark' : 'light');
  void typeset();
});
byId('new-folder-button').addEventListener('click', () => void createFolder());
byId('new-entry-button').addEventListener('click', () => openEditor());
byId('git-button').addEventListener('click', () => void showGit());
byId('logout-button').addEventListener('click', async () => {
  try {
    await api('/api/logout', { method: 'POST' });
    window.location.reload();
  } catch (reason) { showToast(reason.message, true); }
});
byId('search').addEventListener('input', () => void search());
byId('search').addEventListener('keydown', (event) => { if (event.key === 'Escape') { event.currentTarget.value = ''; void search(); } });
document.addEventListener('click', (event) => { if (!event.target.closest('.search-wrap')) byId('search-results').hidden = true; });
window.addEventListener('popstate', () => {
  if (window.location.pathname === '/calendar') void renderCalendar({ updateHistory: false });
  else if (window.location.pathname === '/review') void startReview({ updateHistory: false });
  else {
    const target = selectFromLocation();
    if (target) void openEntry(target.id, { replace: true });
    else void returnToLibrary();
  }
});

document.documentElement.classList.toggle('dark', localStorage.getItem('study-theme') === 'dark');
void start();
