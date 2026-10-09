import {
  copyFileSync,
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { svgPictureMarkers } from '../vendor/tikzjax/study-picture-markers.mjs';

const frontend = dirname(dirname(fileURLToPath(import.meta.url)));
const publicVendor = join(frontend, 'public', 'vendor');
const excalidrawFonts = join(
  frontend,
  'node_modules',
  '@excalidraw',
  'excalidraw',
  'dist',
  'prod',
  'fonts',
);
const excalidrawPublic = join(publicVendor, 'excalidraw');

rmSync(publicVendor, { recursive: true, force: true });
mkdirSync(publicVendor, { recursive: true });

// MathJax can load optional TeX components dynamically. Copying the pinned
// package keeps those requests same-origin and preserves the original
// frontend's complete offline typesetting surface.
cpSync(
  join(frontend, 'node_modules', 'mathjax'),
  join(publicVendor, 'mathjax'),
  { recursive: true },
);
cpSync(
  join(frontend, 'node_modules', '@mathjax', 'mathjax-newcm-font', 'svg', 'dynamic'),
  join(publicVendor, 'mathjax-newcm-font', 'svg', 'dynamic'),
  { recursive: true },
);
copyFileSync(
  join(frontend, 'node_modules', 'mathjax', 'LICENSE'),
  join(publicVendor, 'mathjax-newcm-font', 'LICENSE'),
);

for (const name of ['bbm', 'bboldx', 'dsfont', 'mhchem']) {
  const packageName = `mathjax-${name}-font-extension`;
  const target = join(publicVendor, 'mathjax-fonts', packageName);
  mkdirSync(target, { recursive: true });
  copyFileSync(join(frontend, 'node_modules', '@mathjax', packageName, 'svg.js'), join(target, 'svg.js'));
}
copyFileSync(join(frontend, '..', 'study_app', 'mathjax_extensions.json'),
  join(publicVendor, 'mathjax', 'study-extensions.json'));

// Pin the upstream sources and build the tiny Study bridge without a CDN or service worker.
const quiver = join(publicVendor, 'quiver');
cpSync(join(frontend, 'vendor', 'quiver'), quiver, { recursive: true });
const uiPath = join(quiver, 'ui.mjs');
let ui = readFileSync(uiPath, 'utf8');
function replaceRequired(source, before, after) {
  if (!source.includes(before)) throw new Error(`The pinned diagram runtime changed: ${before}`);
  return source.replaceAll(before, after);
}
ui = replaceRequired(ui, 'ui.initialise();', 'ui.settings.set("quiver.renderer", "katex"); ui.initialise(); window.studyQuiver = ui;');
ui = replaceRequired(ui, '[["katex", "LaTeX"], ["typst", "Typst"]]', '[["katex", "LaTeX"]]');
ui = replaceRequired(ui, '["katex", "typst"].includes(renderer)', '["katex"].includes(renderer)');
const typstStart = ui.indexOf('// Load the Typst library as an ES6 module');
const typstEnd = ui.indexOf('// We want until the (minimal) DOM content');
if (typstStart < 0 || typstEnd <= typstStart) throw new Error('The pinned Quiver renderer changed.');
ui = ui.slice(0, typstStart) + 'const load_typst = () => Promise.reject(new Error("Study uses local MathJax labels."));\n\n' + ui.slice(typstEnd);
ui = replaceRequired(ui, 'import("/KaTeX/katex.mjs")', 'import("./mathjax-renderer.mjs")');
ui = replaceRequired(ui, 'KaTeX.then((katex) => {', 'KaTeX.then(async (katex) => {');
ui = replaceRequired(ui, 'katex.render(', 'await katex.render(');
// A new import can remove a label while its MathJax promise is still pending.
ui = replaceRequired(ui,
  'const update_label_transformation = (mode = CONSTANTS.DEFAULT_RENDERER) => {',
  'const update_label_transformation = (mode = CONSTANTS.DEFAULT_RENDERER) => { if (!ui.quiver.contains_cell(cell) || !label.element.isConnected) return;');
ui = replaceRequired(ui, 'href: "KaTeX/katex.css"', 'href: "study.css"');
ui = ui.replaceAll('getItem("settings")', 'getItem("study-quiver-settings")')
  .replaceAll('setItem("settings",', 'setItem("study-quiver-settings",');
writeFileSync(uiPath, ui);

// TikZJax compiles in a Web Worker. Expose its worker API rather than scanning the
// whole document, so React owns each diagram and compilation errors remain visible.
const tikz = join(publicVendor, 'tikzjax');
cpSync(join(frontend, 'node_modules', '@planktimerr', 'tikzjax', 'dist'), tikz, { recursive: true });
cpSync(join(frontend, 'vendor', 'tikzjax'), tikz, { recursive: true });
let runtime = readFileSync(join(tikz, 'tikzjax.js'), 'utf8');
runtime = replaceRequired(runtime, 'M()(A.A,B);', '');
// Carry the build fingerprint through to the worker. A changed runtime must
// not reuse a cached worker from an earlier deployment under the same URL.
runtime = replaceRequired(runtime, 'new o(`${e}/run-tex.js`)', 'new o(`${e}/run-tex.js${N.search}`)');
runtime = replaceRequired(runtime,
  '"complete"==document.readyState?K():window.addEventListener("load",K)',
  'window.StudyTikzJax={render:async(source,options)=>{const worker=await V;return worker.texify(source,options)},stop:async()=>{await n.terminate(await V);window.TikzJax=false}}');
writeFileSync(join(tikz, 'tikzjax.js'), runtime);
let worker = readFileSync(join(tikz, 'run-tex.js'), 'utf8');
// Upstream computes the final depth before emitting picture tags. A nested
// empty matrix cell can open and close in one special, creating an extra SVG
// opening with no closing tag. Process the markers in their actual order.
const svgDepthStart = worker.indexOf('this.svgDepth+=(A.match(');
const svgDepthEnd = worker.indexOf('A=(A=A.replace(/{\\?x}/g', svgDepthStart);
if (svgDepthStart < 0 || svgDepthEnd <= svgDepthStart) throw new Error('The pinned SVG converter changed.');
worker = replaceRequired(worker, worker.slice(svgDepthStart, svgDepthEnd),
  `A=(${svgPictureMarkers.toString()})(A,this),`);
worker = replaceRequired(worker, 'const Xn=async A=>{',
  'const Xn=async A=>{if(!/^(?:tex\\.wasm\\.gz|core\\.dump\\.gz|tex_files\\/[A-Za-z0-9_.+-]+\\.gz)$/.test(A))throw new Error("Invalid TeX resource path");');
// TeX may probe a missing optional package. Never fall back to fetching a URL
// named by authored TeX: all supported packages live in the pinned local tree.
worker = replaceRequired(worker,
  'try{const t=await fetch(A);if(!t.ok)throw new Error(`Unable to load ${A}.`);{const e=await t.text();An[A]=e}}catch{}', '');
worker = replaceRequired(worker, 'const g=dn("input.dvi").buffer;',
  'const log=new TextDecoder().decode(dn("input.log"));if(/(^|\\n)!/.test(log))throw new Error(log.match(/(?:^|\\n)![^\\n]*/)[0].trim());const g=dn("input.dvi").buffer;');
writeFileSync(join(tikz, 'run-tex.js'), worker);
const tikzVersion = createHash('sha256').update(runtime).update(worker).digest('hex').slice(0, 16);
writeFileSync(join(frontend, 'lib', 'tikz-runtime.json'), JSON.stringify({ version: tikzVersion }) + '\n');
writeFileSync(join(tikz, 'tex_files', 'quiver.sty.gz'),
  gzipSync(readFileSync(join(quiver, 'quiver.sty'))));

// Excalidraw's JavaScript is bundled by Vite, but its stylesheet and fonts are
// same-origin runtime assets. Both CSS and the Excalidraw loader use this one
// font tree, so the release snapshot does not carry a duplicate copy.
cpSync(excalidrawFonts, join(excalidrawPublic, 'fonts'), { recursive: true });
copyFileSync(
  join(frontend, 'licenses', 'excalidraw-LICENSE'),
  join(excalidrawPublic, 'LICENSE'),
);
const excalidrawCss = readFileSync(
  join(frontend, 'node_modules', '@excalidraw', 'excalidraw', 'dist', 'prod', 'index.css'),
  'utf8',
).replaceAll('url("./fonts/', 'url("/vendor/excalidraw/fonts/');
writeFileSync(join(excalidrawPublic, 'index.css'), excalidrawCss, 'utf8');
const lock = JSON.parse(readFileSync(join(frontend, 'package-lock.json'), 'utf8'));
const notices = new Map();
const licenseTexts = new Map();
notices.set('quiver@2f289ecbae9b7e5a473e04b924750c538ed5c4cf', 'MIT');
licenseTexts.set('quiver@2f289ecbae9b7e5a473e04b924750c538ed5c4cf', [
  { filename: 'LICENSE', text: readFileSync(join(quiver, 'LICENSE'), 'utf8') },
]);
licenseTexts.set('@planktimerr/tikzjax@1.0.8', [
  { filename: 'LICENSE', text: readFileSync(join(tikz, 'LICENSE'), 'utf8') },
]);
for (const [location, metadata] of Object.entries(lock.packages || {})) {
  if (!location.includes('node_modules/') || !metadata.version) continue;
  const name = location.split('node_modules/').at(-1);
  const key = `${name}@${metadata.version}`;
  notices.set(key, metadata.license || 'License declared by upstream package metadata');
  if (licenseTexts.has(key)) continue;
  const packageDirectory = join(frontend, location);
  if (!existsSync(packageDirectory)) continue;
  const files = readdirSync(packageDirectory, { withFileTypes: true })
    .filter(
      (item) =>
        item.isFile() && /^(?:licen[cs]e|copying|notice)(?:[._-].*)?$/i.test(item.name),
    )
    .map((item) => item.name)
    .sort();
  const texts = files
    .map((filename) => ({
      filename,
      text: readFileSync(join(packageDirectory, filename), 'utf8').trim(),
    }))
    .filter((item) => item.text);
  if (texts.length) licenseTexts.set(key, texts);
}
const noticeText = [
  'Study frontend third-party package notices',
  '',
  'Generated from the pinned frontend/package-lock.json. This conservative inventory',
  'includes resolved build packages as well as packages present in the browser bundle.',
  'Full license and notice texts found in installed package roots follow the inventory.',
  'Packages without an included text remain identified by their declared license and must',
  'be checked as part of any release audit.',
  '',
  ...[...notices].sort(([left], [right]) => left.localeCompare(right)).map(
    ([name, license]) => `${name}\t${license}`,
  ),
  '',
  ...[...licenseTexts]
    .sort(([left], [right]) => left.localeCompare(right))
    .flatMap(([name, texts]) =>
      texts.flatMap(({ filename, text }) => [
        `===== ${name} — ${filename} =====`,
        text,
        '',
      ]),
    ),
].join('\n');
writeFileSync(join(publicVendor, 'THIRD_PARTY_NOTICES.txt'), noticeText, 'utf8');

// Reserved by Next/vinext. Remove leftovers from older vendor layouts.
rmSync(join(frontend, 'public', '_next'), { recursive: true, force: true });

console.log('Vendored complete MathJax and Excalidraw assets for offline use.');
