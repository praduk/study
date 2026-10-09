/** @param {Record<string, string | (string | number)[]>} macros */
export function macroPreamble(macros) {
  return Object.entries(macros).map(([name, definition]) => {
    const value = Array.isArray(definition) ? String(definition[0]) : definition;
    const count = Array.isArray(definition) ? Number(definition[1] || 0) : 0;
    const optional = Array.isArray(definition) && definition.length > 2 ? `[${definition[2]}]` : '';
    return `\\providecommand{\\${name}}{}\\renewcommand{\\${name}}${count ? `[${count}]` : ''}${optional}{${value}}`;
  }).join('\n');
}

/** @param {string} source */
/** The worker output is data: reject active content and external resource references. */
export function prepareTikzSvg(source) {
  const document = new DOMParser().parseFromString(source, 'image/svg+xml');
  const svg = document.documentElement;
  if (svg.localName !== 'svg' || document.querySelector('parsererror')) throw new Error('TikZ returned invalid SVG.');
  svg.querySelectorAll('a').forEach((node) => node.replaceWith(...Array.from(node.childNodes)));
  const allowed = new Set(['svg', 'g', 'path', 'defs', 'clippath', 'text', 'tspan', 'rect', 'circle', 'ellipse',
    'line', 'polyline', 'polygon', 'use', 'title', 'desc', 'marker', 'mask', 'pattern', 'lineargradient', 'radialgradient', 'stop']);
  svg.querySelectorAll('*').forEach(node => {
    if (node.namespaceURI !== 'http://www.w3.org/2000/svg' || !allowed.has(node.localName.toLowerCase())) node.remove();
  });
  const random = crypto.getRandomValues(new Uint8Array(12));
  const prefix = `tikz-${Array.from(random, n => n.toString(16).padStart(2, '0')).join('')}-`;
  const ids = new Map();
  svg.querySelectorAll('[id]').forEach((node) => { const id = node.id; ids.set(id, `${prefix}${id}`); node.id = ids.get(id); });
  for (const node of [svg, ...Array.from(svg.querySelectorAll('*'))]) {
    for (const attribute of Array.from(node.attributes)) {
      if (/^on/i.test(attribute.name) || (/(?:^|:)href$/i.test(attribute.name) && !attribute.value.startsWith('#'))
        || [...attribute.value.matchAll(/url\(([^)]*)\)/gi)].some(m => !m[1].trim().replace(/^['"]|['"]$/g, '').startsWith('#'))) { node.removeAttribute(attribute.name); continue; }
      let value = attribute.value;
      if (['fill', 'stroke', 'color'].includes(attribute.name) && /^(?:black|#000(?:000)?|rgb\(0%?,\s*0%?,\s*0%?\))$/i.test(value)) value = 'currentColor';
      if (attribute.name === 'style') value = value.replace(/(fill|stroke|color):\s*(?:black|#000(?:000)?|rgb\(0%?,\s*0%?,\s*0%?\))/gi, '$1:currentColor');
      value = value.replace(/url\((['"]?)#([^'")]+)\1\)/g, (_match, quote, id) => `url(${quote}#${ids.get(id) || id}${quote})`);
      if (value.startsWith('#') && ids.has(value.slice(1))) value = `#${ids.get(value.slice(1))}`;
      node.setAttribute(attribute.name, value);
    }
  }
  svg.setAttribute('fill', 'currentColor');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', 'Commutative diagram');
  // TikZJax's document uses 10 TeX points; dvisvgm writes physical SVG points
  // (72/in, versus TeX's 72.27/in). Express the natural width in em so its
  // object labels inherit the surrounding text size in every display/export.
  const width = svg.getAttribute('width') || '';
  if (/^\d+(?:\.\d+)?pt$/.test(width)) {
    svg.setAttribute('width', `${parseFloat(width) / (10 * 72 / 72.27)}em`);
    // Let the viewBox supply the aspect ratio. A retained physical height would
    // constrain preserveAspectRatio and keep the glyphs at their old size.
    svg.removeAttribute('height');
  }
  return svg;
}
