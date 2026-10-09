import { macroPreamble, prepareTikzSvg } from './study-svg.mjs';

window.studyTikzExportDone = (async () => {
    const preamble = macroPreamble(window.MathJax?.config?.tex?.macros || window.MathJax?.tex?.macros || {});
    for (const container of document.querySelectorAll('[data-tikzcd-source]')) {
        const source = container.dataset.tikzcdSource;
        if (new TextEncoder().encode(source).length > 65536) throw new Error('A diagram must be smaller than 64 KiB.');
        if (!source.includes('\\begin{tikzcd}') || !source.includes('\\end{tikzcd}')) throw new Error('Include a complete tikzcd environment.');
        let timer;
        try {
            const [svg] = await Promise.race([
                window.StudyTikzJax.render(source, {
                    texPackages: JSON.stringify({ 'tikz-cd': '', quiver: '', amsmath: '', amssymb: '' }),
                    addToPreamble: preamble,
                }),
                new Promise((_, reject) => {
                    timer = setTimeout(() => {
                        void window.StudyTikzJax.stop();
                        reject(new Error('TikZ compilation timed out. Check the code and try again.'));
                    }, 20000);
                }),
            ]);
            container.replaceChildren(prepareTikzSvg(svg));
        } finally { clearTimeout(timer); }
    }
})();
