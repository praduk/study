import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
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
// package keeps those requests same-origin and lets Study work offline.
cpSync(join(frontend, 'node_modules', 'mathjax'), join(publicVendor, 'mathjax'), {
  recursive: true,
});
cpSync(
  join(frontend, 'node_modules', '@mathjax', 'mathjax-newcm-font', 'svg', 'dynamic'),
  join(publicVendor, 'mathjax-newcm-font', 'svg', 'dynamic'),
  { recursive: true },
);

// Excalidraw's JavaScript is bundled by Vite, but its fonts are runtime assets.
cpSync(
  excalidrawFonts,
  excalidrawPublic,
  { recursive: true },
);
// Keep the stylesheet as a separate same-origin asset and rewrite its font
// references to stable public URLs for both development and static builds.
// Excalidraw's runtime also uses the direct copy above via its asset path.
cpSync(excalidrawFonts, join(excalidrawPublic, 'fonts'), { recursive: true });
const excalidrawCss = readFileSync(
  join(frontend, 'node_modules', '@excalidraw', 'excalidraw', 'dist', 'prod', 'index.css'),
  'utf8',
).replaceAll('url("./fonts/', 'url("/vendor/excalidraw/fonts/');
writeFileSync(join(excalidrawPublic, 'index.css'), excalidrawCss, 'utf8');

// Reserved by Next/vinext. Remove leftovers from older vendor layouts.
rmSync(join(frontend, 'public', '_next'), { recursive: true, force: true });

console.log('Vendored MathJax and Excalidraw assets for offline use.');
