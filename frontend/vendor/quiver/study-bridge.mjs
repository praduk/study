import { QuiverImportExport } from './quiver.mjs';

let importing = false;
let editable = true;
let changed = false;
let timer;
const send = (message) => parent.postMessage({ channel: 'study-quiver', ...message }, location.origin);
const encoded = (ui) => new URL(ui.quiver.export('base64', ui.settings, ui.options(), ui.definitions()).data).hash.slice(1).split('&').find(p => p.startsWith('q='))?.slice(2);
const diagnosticText = (message) => Array.isArray(message)
    ? message.map(diagnosticText).join('')
    : typeof message === 'string' ? message : message?.element?.textContent || 'Unsupported diagram syntax.';

function exportCode(ui) {
    const result = ui.quiver.export('tikz-cd', ui.settings, ui.options(), ui.definitions());
    return { code: result.data.replace(/^%[^\n]*\n/, ''),
        warnings: [...result.metadata.tikz_incompatibilities],
        dependencies: [...result.metadata.dependencies.keys()] };
}

window.addEventListener('message', (event) => {
    if (event.origin !== location.origin || event.source !== parent || event.data?.channel !== 'study-quiver') return;
    const ui = window.studyQuiver;
    if (!ui) return;
    const { type, source, macros, theme } = event.data;
    if (type === 'export') { send({ type: 'exported', id: event.data.id, changed, ...exportCode(ui) }); return; }
    if (type !== 'load' || typeof source !== 'string' || source.length > 65536) return;
    importing = true;
    changed = false;
    clearTimeout(timer);
    const backup = encoded(ui);
    try {
        ui.settings.set('quiver.renderer', 'katex');
        ui.settings.set('quiver.autosave', false);
        ui.settings.set('quiver.package_version', '1.4.2');
        ui.settings.set('export.centre_diagram', false);
        ui.settings.set('export.standalone', false);
        ui.switch_theme(theme === 'dark' ? 'dark' : 'light');
        if (typeof macros === 'string') ui.load_macros(macros.replace(/^\\providecommand\{\\[a-zA-Z]+\}\{\}\\renewcommand/gm, '\\newcommand'));
        ui.reset();
        const result = ui.quiver.import(ui, 'tikz-cd', source, ui.settings);
        ui.dismiss_pane();
        const diagnostics = result.diagnostics.map(d => diagnosticText(d.message));
        editable = diagnostics.length === 0;
        send({ type: 'loaded', source, diagnostics });
    } catch (error) {
        ui.reset();
        if (backup) QuiverImportExport.base64.import(ui, backup);
        editable = false;
        send({ type: 'loaded', source, diagnostics: [error.message] });
    } finally { importing = false; }
});

document.addEventListener('DOMContentLoaded', () => {
    const ui = window.studyQuiver;
    const original = ui.autosave_diagram.bind(ui);
    ui.autosave_diagram = () => {
        original();
        if (importing || !editable) return;
        changed = true;
        clearTimeout(timer);
        timer = setTimeout(() => send({ type: 'changed', ...exportCode(ui) }), 200);
    };
});
