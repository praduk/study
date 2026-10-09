import extensions from '../../study_app/mathjax_extensions.json' with { type: 'json' };

/** @param {Record<string, string | (string | number)[]>} macros */
export function mathJaxOptions(macros) {
  return {
    loader: {
      paths: { mathjax: '/vendor/mathjax', 'mathjax-newcm': '/vendor/mathjax-newcm-font', fonts: '/vendor/mathjax-fonts' },
      load: ['ui/safe', ...extensions.enabled.map((name) => `[tex]/${name}`)],
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
