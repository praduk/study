from __future__ import annotations

import html
import re
from typing import Any

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.texmath import texmath_plugin

from .export import _mathjax_tex, _render_markdown
from .store import LibraryStore

_IMAGE_RE = re.compile(
    r'<img src="(?P<path>/?media/[a-f0-9]{64}\.(?:png|jpe?g|webp))'
    r'(?P<fragment>#[^"]*)?" alt="(?P<alt>[^"]*)"\s*/?>'
)


def _markdown_renderer() -> MarkdownIt:
    """Create the single safe renderer used by the no-build browser shell."""
    markdown = (
        MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
        .enable(["table", "strikethrough"])
        .use(tasklists_plugin)
        .use(
            dollarmath_plugin,
            allow_labels=False,
            allow_blank_lines=False,
            renderer=_mathjax_tex,
        )
        .use(texmath_plugin, delimiters="brackets")
    )

    def render_mathjax(
        _renderer: Any,
        tokens: list[Any],
        index: int,
        _options: Any,
        _environment: Any,
    ) -> str:
        return _mathjax_tex(
            tokens[index].content,
            {"display_mode": tokens[index].type.startswith("math_block")},
        )

    markdown.add_render_rule("math_inline", render_mathjax)
    markdown.add_render_rule("math_block", render_mathjax)
    markdown.add_render_rule("math_block_eqno", render_mathjax)
    return markdown


def _decorate_images(rendered: str) -> str:
    """Turn validated Study image fragments into safe display attributes."""

    def replace(match: re.Match[str]) -> str:
        fragment = html.unescape(match.group("fragment") or "")
        width_match = re.search(r"(?:^|[#&;])width=(\d{1,3})(?:$|[&;])", fragment)
        width = min(100, max(10, int(width_match.group(1)))) if width_match else 76
        invert = bool(re.search(r"(?:^|[#&;])invert=lightness(?:$|[&;])", fragment))
        classes = "content-image invert-lightness" if invert else "content-image"
        return (
            f'<img src="{match.group("path")}" alt="{match.group("alt")}" '
            f'class="{classes}" style="width:{width}%">'
        )

    return _IMAGE_RE.sub(replace, rendered)


def render_markdown_fragment(store: LibraryStore, source: str) -> str:
    """Render untrusted authored Markdown without allowing authored raw HTML."""
    return _decorate_images(_render_markdown(_markdown_renderer(), source, store))
