# TikZJax runtime

TikZJax 1.0.8 is pinned in package-lock.json (`@planktimerr/tikzjax`, GPL-3.0-or-later).
Source: https://github.com/maker-jr/tikzjax

The published runtime and all its TeX/font files are copied by copy-vendor.mjs.
The script exposes the existing worker API and disables document scanning and
injected CSS; Study loads the local font stylesheet and owns each rendered SVG.
Study's helper modules are separate source files here. Quiver 1.4.2's MIT-licensed
stylesheet is added to the TeX filesystem for compatible curved-arrow exports.

Study also patches the bundled DVI-to-SVG converter's picture-marker handling.
Nested pictures that open and close in a single DVI special (including empty
TikZ-CD matrix cells) must update nesting depth in order, rather than emitting
extra SVG roots based on the final depth. The source patch is
`study-picture-markers.mjs`, injected by `copy-vendor.mjs`.

The build fingerprints the patched runtime and worker in
`frontend/lib/tikz-runtime.json`. Study requests the runtime with this version,
which also propagates to the worker URL, so browser caches cannot retain an
older worker after a changed renderer is deployed.
