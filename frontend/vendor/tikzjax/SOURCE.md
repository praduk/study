# TikZJax runtime

TikZJax 1.0.8 is pinned in package-lock.json (`@planktimerr/tikzjax`, GPL-3.0-or-later).
Source: https://github.com/maker-jr/tikzjax

The published runtime and all its TeX/font files are copied by copy-vendor.mjs.
The script exposes the existing worker API and disables document scanning and
injected CSS; Study loads the local font stylesheet and owns each rendered SVG.
Study's helper modules are separate source files here. Quiver 1.4.2's MIT-licensed
stylesheet is added to the TeX filesystem for compatible curved-arrow exports.
