import extensions from '../../study_app/mathjax_extensions.json' with { type: 'json' };
import runtime from './mathjax-runtime.json' with { type: 'json' };

/** @param {Record<string, string | (string | number)[]>} macros */
export function mathJaxOptions(macros) {
  return {
    loader: {
      paths: { mathjax: '/vendor/mathjax', 'mathjax-newcm': '/vendor/mathjax-newcm-font', fonts: '/vendor/mathjax-fonts' },
      load: ['study-extensions'],
      source: { 'study-extensions': `/vendor/mathjax/study-extensions.js?v=${runtime.extensionsVersion}` },
      dependencies: { 'study-extensions': ['input/tex', 'output/svg'] },
      provides: {
        'study-extensions': ['ui/safe', ...extensions.enabled.map((name) => `[tex]/${name}`), ...runtime.fontComponents],
      },
    },
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      packages: { '[+]': extensions.enabled },
      macros,
    },
    options: { enableMenu: false },
    svg: { displayOverflow: 'linebreak', fontCache: 'local' },
    startup: { typeset: false },
  };
}
