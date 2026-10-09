import { getSharedMathMacros } from '@/lib/mathjax';
import { macroPreamble } from '@/lib/tikzcd';

type Runtime = { render: (source: string, options: Record<string, string>) => Promise<[string, string]>; stop: () => Promise<void> };
let loading: Promise<Runtime> | null = null;
let chain = Promise.resolve<unknown>(undefined);
const cache = new Map<string, string>();

function loadRuntime() {
  if (loading) return loading;
  loading = new Promise<Runtime>((resolve, reject) => {
    const css = document.createElement('link');
    css.rel = 'stylesheet'; css.href = '/vendor/tikzjax/fonts.css';
    if (!document.querySelector('link[href="/vendor/tikzjax/fonts.css"]')) document.head.appendChild(css);
    const script = document.createElement('script');
    script.id = 'study-tikzjax'; script.src = '/vendor/tikzjax/tikzjax.js';
    script.onload = () => window.StudyTikzJax ? resolve(window.StudyTikzJax) : reject(new Error('TikZ could not start.'));
    script.onerror = () => { loading = null; script.remove(); reject(new Error('The local TikZ renderer could not load.')); };
    document.head.appendChild(script);
  });
  return loading;
}

/** Compile in the worker, serially; malformed TeX must not block the next diagram forever. */
export function renderTikzCd(source: string, signal?: AbortSignal) {
  const preamble = macroPreamble(getSharedMathMacros());
  const key = `${preamble}\n${source}`;
  const result = chain.catch(() => undefined).then(async () => {
    if (signal?.aborted) throw new DOMException('Cancelled', 'AbortError');
    if (new TextEncoder().encode(source).length > 65536) throw new Error('A diagram must be smaller than 64 KiB.');
    if (!source.includes('\\begin{tikzcd}') || !source.includes('\\end{tikzcd}')) throw new Error('Include a complete tikzcd environment.');
    const cached = cache.get(key);
    if (cached) return cached;
    const runtime = await loadRuntime();
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      const [svg] = await Promise.race([
        runtime.render(source, { texPackages: JSON.stringify({ 'tikz-cd': '', quiver: '', amsmath: '', amssymb: '' }), addToPreamble: preamble }),
        new Promise<never>((_resolve, reject) => {
          timer = setTimeout(() => {
            void runtime.stop(); loading = null;
            document.getElementById('study-tikzjax')?.remove();
            reject(new Error('TikZ compilation timed out. Check the code and try again.'));
          }, 20000);
        }),
      ]);
      if (!svg.includes('<svg')) throw new Error('TikZ could not render this diagram. Check its LaTeX code.');
      cache.set(key, svg);
      if (cache.size > 32) cache.delete(cache.keys().next().value!);
      return svg;
    } catch (error) {
      // TeX's mutable worker filesystem can retain a failed job's log/state.
      // Start clean for the next attempt rather than reusing a broken session.
      await runtime.stop().catch(() => undefined);
      loading = null;
      document.getElementById('study-tikzjax')?.remove();
      throw error;
    } finally { if (timer) clearTimeout(timer); }
  });
  chain = result;
  return result;
}

export { prepareTikzSvg } from '../vendor/tikzjax/study-svg.mjs';
