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
