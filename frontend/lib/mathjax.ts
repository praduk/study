import { mathJaxOptions } from './mathjax-options.mjs';

let sharedMacros: Record<string, string | (string | number)[]> = {};
export function getSharedMathMacros() { return sharedMacros; }

let typesetChain = Promise.resolve<unknown>(undefined);
let mathJaxReady: Promise<void> | undefined;

/** Set macros before the first typeset, including for the separate TikZ renderer. */
export function configureMathJax(macros: Record<string, string | (string | number)[]>) {
  if (!mathJaxReady) sharedMacros = macros;
}

function waitForMathJax() {
  mathJaxReady ??= new Promise<void>((resolve, reject) => {
    if (window.MathJax?.startup?.promise) {
      resolve(window.MathJax.startup.promise.then(() => undefined));
      return;
    }
    window.MathJax = mathJaxOptions(sharedMacros);
    const script = document.createElement('script');
    script.id = 'study-mathjax';
    script.src = '/vendor/mathjax/tex-svg.js';
    script.async = true;
    script.addEventListener('load', () => resolve(window.MathJax?.startup?.promise?.then(() => undefined)), { once: true });
    script.addEventListener('error', () => reject(new Error('The local MathJax bundle could not be loaded.')), { once: true });
    document.head.appendChild(script);
  });
  return mathJaxReady;
}

export function typesetWithMathJax(element: HTMLElement) {
  typesetChain = typesetChain
    .catch(() => undefined)
    .then(async () => {
      if (!element.isConnected) return;
      await waitForMathJax();
      if (!element.isConnected) return;
      window.MathJax?.typesetClear?.([element]);
      await window.MathJax?.typesetPromise?.([element]);
    });
  return typesetChain;
}

export function clearMathJax(element: HTMLElement) {
  typesetChain = typesetChain
    .catch(() => undefined)
    .then(async () => {
      if (!mathJaxReady) return;
      await mathJaxReady;
      window.MathJax?.typesetClear?.([element]);
    });
  return typesetChain;
}

/** Render with the reader's macro configuration and queue; embed all SVG glyphs. */
export function renderEquationSvg(latex: string) {
  const result = typesetChain.catch(() => undefined).then(async () => {
    await waitForMathJax();
    const wrapper = await window.MathJax?.tex2svgPromise?.(latex, { display: true });
    const svg = wrapper?.querySelector('svg');
    if (!wrapper || !svg) throw new Error('MathJax is not ready yet.');
    const invalid = svg.querySelector('[data-mml-node="merror"]');
    if (invalid) throw new Error(invalid.getAttribute('data-mjx-error') || 'Invalid LaTeX.');
    wrapper.style.cssText = 'position:fixed;left:-100000px;top:0;font-size:24px;visibility:hidden;';
    document.body.appendChild(wrapper);
    try {
      const bounds = svg.getBoundingClientRect();
      const width = Math.max(20, Math.ceil(bounds.width));
      const height = Math.max(20, Math.ceil(bounds.height));
      svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      svg.setAttribute('width', String(width));
      svg.setAttribute('height', String(height));
      svg.style.color = '#1e1e1e';
      return { svg: new XMLSerializer().serializeToString(svg), width, height };
    } finally {
      wrapper.remove();
    }
  });
  typesetChain = result;
  return result;
}
