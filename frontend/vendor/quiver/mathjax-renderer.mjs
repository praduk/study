const renderer = {
    async render(latex, element) {
        const wrapper = document.createElement('span');
        wrapper.className = 'katex';
        element.replaceChildren(wrapper);
        try {
            const image = await window.studyRenderMath(latex);
            if (!wrapper.isConnected) return;
            const svg = new DOMParser().parseFromString(image.svg, 'image/svg+xml').documentElement;
            svg.style.color = 'inherit';
            wrapper.appendChild(document.importNode(svg, true));
        } catch (error) {
            wrapper.className = 'katex-error';
            wrapper.textContent = latex;
            wrapper.title = error.message;
        }
    },
};

export default renderer;
