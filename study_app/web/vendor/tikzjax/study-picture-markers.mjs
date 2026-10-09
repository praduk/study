/** Translate PGF picture markers in order, including paired markers in one DVI special.
 * @param {string} source
 * @param {{svgDepth: number, paperwidth: number, paperheight: number}} machine
 */
export function svgPictureMarkers(source, machine) {
  return source.replace(/<\/?svg(?:\s[^>]*|)>/g, (tag) => {
    if (tag.startsWith('</')) {
      if (machine.svgDepth === 0) throw new Error('Unbalanced SVG picture markers.');
      machine.svgDepth--;
      return tag === '</svg endpicture>' ? (machine.svgDepth === 0 ? '</svg>' : '') : tag;
    }
    const outer = machine.svgDepth++ === 0;
    if (tag !== '<svg beginpicture>') return tag;
    if (!outer) return '';
    return `<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${machine.paperwidth}pt" height="${machine.paperheight}pt" viewBox="-72 -72 ${machine.paperwidth} ${machine.paperheight}">`;
  });
}
