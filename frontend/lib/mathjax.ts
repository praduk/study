let typesetChain = Promise.resolve<unknown>(undefined);
let markMathJaxReady: () => void;
let markMathJaxFailed: (reason: unknown) => void;
const mathJaxReady = new Promise<void>((resolve, reject) => {
  markMathJaxReady = resolve;
  markMathJaxFailed = reject;
});

async function finishMathJaxStartup() {
  try {
    await window.MathJax?.startup?.promise;
    markMathJaxReady();
  } catch (reason) {
    markMathJaxFailed(reason);
  }
}

export async function waitForMathJax() {
  await mathJaxReady;
}

export function typesetWithMathJax(element: HTMLElement) {
  typesetChain = typesetChain
    .catch(() => undefined)
    .then(async () => {
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
      await waitForMathJax();
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

export function configureMathJax(macros: Record<string, string | (string | number)[]>) {
  if (typeof window === 'undefined') return;
  const existing = document.getElementById('study-mathjax') as HTMLScriptElement | null;
  if (existing) {
    if (window.MathJax?.startup?.promise) void finishMathJaxStartup();
    else existing.addEventListener('load', () => void finishMathJaxStartup(), { once: true });
    return;
  }
  window.MathJax = {
    loader: {
      paths: {
        mathjax: '/vendor/mathjax',
        'mathjax-newcm': '/vendor/mathjax-newcm-font',
      },
      load: ['ui/safe'],
    },
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      macros,
    },
    options: { enableMenu: false },
    svg: { displayOverflow: 'linebreak', fontCache: 'local' },
    startup: { typeset: false },
  };
  const script = document.createElement('script');
  script.id = 'study-mathjax';
  script.src = '/vendor/mathjax/tex-svg.js';
  script.async = true;
  script.addEventListener('load', () => void finishMathJaxStartup(), { once: true });
  script.addEventListener('error', () => markMathJaxFailed(new Error('The local MathJax bundle could not be loaded.')), { once: true });
  document.head.appendChild(script);
}
