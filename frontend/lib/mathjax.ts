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
