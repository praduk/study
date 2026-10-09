# Quiver source

Vendored from https://github.com/varkor/quiver at commit
`2f289ecbae9b7e5a473e04b924750c538ed5c4cf` (MIT license).

The upstream modules are preserved here. `scripts/copy-vendor.mjs` applies the
Study integration: local MathJax label rendering, a same-origin message bridge,
a distinct settings key, and no service worker or external runtime imports.
`index.html`, `study-bridge.mjs`, `mathjax-renderer.mjs`, and `study.css` are Study files.

The TeX compatibility stylesheet is Quiver 1.4.2, pinned to
`3facbd567f5b4ecf0fc46a35208d45e276bdfd56`. It supports the classic
TikZ-CD styles without requiring newer LaTeX libraries absent from TikZJax.
The bridge targets that export version and preserves import warnings.
