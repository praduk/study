import { cpSync, existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { brotliCompressSync, constants } from 'node:zlib';

const frontend = dirname(dirname(fileURLToPath(import.meta.url)));
const source = join(frontend, 'dist', 'client');
const packageRoot = join(frontend, '..', 'study_app');
const target = join(packageRoot, 'web');
const staging = join(packageRoot, `.web-stage-${process.pid}`);
const backup = join(packageRoot, `.web-backup-${process.pid}`);
const required = ['index.html', '_next', 'vendor', 'favicon.svg'];
const compressibleRoots = [
  '_next/static',
  'vendor/excalidraw',
  'vendor/mathjax/tex-svg.js',
  'vendor/mathjax/study-extensions.js',
  'vendor/mathjax-fonts',
  'vendor/mathjax-newcm-font/svg/dynamic',
  'vendor/quiver',
  'vendor/tikzjax',
];

function precompress(path, highQuality = false) {
  const stat = lstatSync(path);
  if (stat.isDirectory()) {
    for (const name of readdirSync(path)) precompress(join(path, name), highQuality);
    return;
  }
  if (!stat.isFile() || stat.size < 32 * 1024 || !/\.(?:css|m?js)$/.test(path)) return;
  const sourceBytes = readFileSync(path);
  const compressed = brotliCompressSync(sourceBytes, {
    params: { [constants.BROTLI_PARAM_QUALITY]: highQuality ? 11 : 9 },
  });
  if (compressed.length < sourceBytes.length) writeFileSync(`${path}.br`, compressed);
}

const transient = readdirSync(packageRoot, { withFileTypes: true });
for (const item of transient) {
  if (item.isDirectory() && item.name.startsWith('.web-stage-')) {
    rmSync(join(packageRoot, item.name), { recursive: true, force: true });
  }
}
const staleBackups = transient
  .filter((item) => item.isDirectory() && item.name.startsWith('.web-backup-'))
  .map((item) => join(packageRoot, item.name))
  .sort((left, right) => statSync(right).mtimeMs - statSync(left).mtimeMs);
if (!existsSync(target) && staleBackups.length > 0) {
  renameSync(staleBackups.shift(), target);
}
for (const path of staleBackups) {
  rmSync(path, { recursive: true, force: true });
}

for (const name of required) {
  if (!existsSync(join(source, name))) {
    throw new Error(`frontend build is missing ${name}`);
  }
}

mkdirSync(staging, { recursive: true });
for (const name of required) {
  cpSync(join(source, name), join(staging, name), { recursive: true });
}

let backedUp = false;
try {
  for (const path of compressibleRoots) {
    // These two scripts dominate transfer to the ordinary math reader.
    precompress(join(staging, path), path.startsWith('vendor/mathjax/'));
  }
  if (existsSync(target)) {
    renameSync(target, backup);
    backedUp = true;
  }
  renameSync(staging, target);
  if (backedUp) rmSync(backup, { recursive: true, force: true });
} catch (error) {
  if (!existsSync(target) && backedUp && existsSync(backup)) renameSync(backup, target);
  rmSync(staging, { recursive: true, force: true });
  throw error;
}

console.log('Staged the complete Study frontend in study_app/web.');
