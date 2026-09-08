"""Read Study references from Markdown prose without interpreting rendered HTML.

Tokenization deliberately preserves escape/entity tokens until after references
are extracted. An escaped or encoded @ must never become an incoming link.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from markdown_it import MarkdownIt
from markdown_it.rules_block.fence import make_fence_rule
from mdit_py_plugins.dollarmath import dollarmath_plugin

REFERENCE_PATTERN = re.compile(r"@(?:\[([^\[\]\r\n]+)\])?([a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)*)")
CONTINUATION = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:_-")
IDENTIFIER = frozenset(".!#$%&'*+/=?^_`{|}~@-\\")


def _identifier_character(value: str) -> bool:
    return value in IDENTIFIER or unicodedata.category(value)[0] in "LNM"


def _references_in_text(value: str, protected: set[int]) -> set[str]:
    references = set()
    for match in REFERENCE_PATTERN.finditer(value):
        start, end = match.span()
        label = match[1]
        if (
            start in protected
            or (start and _identifier_character(value[start - 1]))
            or (end < len(value) and value[end] in CONTINUATION)
            or (
                label is not None
                and (
                    not label.strip()
                    or start + 1 in protected
                    or start + match[0].index("]") in protected
                )
            )
        ):
            continue
        references.add(match[2])
    return references


def _parser() -> MarkdownIt:
    # Enable the same prose structures as remark-gfm. HTML is tokenized (and
    # ignored below), never rendered; the reader likewise skips raw HTML nodes.
    parser = MarkdownIt(
        "commonmark",
        {
            "html": True,
            "linkify": True,
            "strikethrough_single_tilde": True,
        },
    )
    parser.enable(["table", "strikethrough", "linkify"])
    parser.use(
        dollarmath_plugin,
        allow_labels=False,
        allow_space=True,
        allow_digits=True,
        allow_blank_lines=True,
        double_inline=True,
    )
    # remark-math uses fenced block rules: the closing dollar run must be on
    # its own line and at least as long as the opener. An unclosed block owns
    # the remaining parent block. Additional dollars on the opening line
    # prevent a block opener, allowing same-line inline math instead.
    parser.block.ruler.at(
        "math_block",
        make_fence_rule(
            markers=("$",),
            token_type="math_block",
            disallow_marker_in_info=("$",),
            min_markers=2,
        ),
        {"alt": ["paragraph", "reference", "blockquote", "list"]},
    )
    parser.disable("text_join")
    parser.inline.ruler2.disable("fragments_join")
    return parser


def _escaped(source: str, index: int) -> bool:
    preceding = 0
    while index > 0 and source[index - 1] == "\\":
        preceding += 1
        index -= 1
    return preceding % 2 == 1


def _normalize_slash_math(source: str, parser: MarkdownIt) -> str:
    if "\\(" not in source and "\\[" not in source:
        return source
    # Match the reader's preprocessing: slash-delimited math cannot start
    # inside code or cross any code span, even if a later closer exists.
    offsets = [0, *(match.end() for match in re.finditer("\n", source)), len(source)]
    protected = [
        (offsets[token.map[0]], offsets[token.map[1]])
        for token in parser.parse(source)
        if token.type in {"fence", "code_block"} and token.map
    ]
    runs = list(re.finditer(r"`+", source))
    cursor = 0
    while cursor < len(runs):
        opening = runs[cursor]
        if _escaped(source, opening.start()) or any(
            start <= opening.start() < end for start, end in protected
        ):
            cursor += 1
            continue
        closing = next(
            (
                candidate
                for candidate in range(cursor + 1, len(runs))
                if len(runs[candidate][0]) == len(opening[0])
                and not any(start <= runs[candidate].start() < end for start, end in protected)
            ),
            None,
        )
        if closing is None:
            cursor += 1
        else:
            protected.append((opening.start(), runs[closing].end()))
            cursor = closing + 1
    protected.sort()
    pieces = []
    index = 0
    while index < len(source):
        containing = next((end for start, end in protected if start <= index < end), None)
        if containing is not None:
            pieces.append(source[index:containing])
            index = containing
            continue
        inline = source.startswith("\\(", index) and not _escaped(source, index)
        display = source.startswith("\\[", index) and not _escaped(source, index)
        if inline or display:
            close = "\\)" if inline else "\\]"
            end = index + 2
            while end < len(source) - 1:
                if any(start <= end < stop for start, stop in protected):
                    break
                if inline and source[end] == "\n":
                    break
                if source.startswith(close, end) and not _escaped(source, end):
                    delimiter = "$" if inline else "$$"
                    pieces.append(delimiter + source[index + 2 : end] + delimiter)
                    index = end + 2
                    break
                end += 1
            else:
                end = len(source)
            if index == end + 2:
                continue
        pieces.append(source[index])
        index += 1
    return "".join(pieces)


def markdown_references(source: str) -> tuple[str, ...]:
    """Return distinct literal tags in prose, independent of lexical resolution.

    Cache by source text, not paths: edits produce a fresh result while unchanged
    Markdown can reuse parsing when a library snapshot is replaced.
    """
    if "@" not in source:
        return ()
    return _cached_markdown_references(source)


@lru_cache(maxsize=8192)
def _cached_markdown_references(source: str) -> tuple[str, ...]:
    references: set[str] = set()
    parser = _parser()
    for block in parser.parse(_normalize_slash_math(source, parser)):
        if block.type != "inline":
            continue
        text = ""
        protected: set[int] = set()
        link_depth = 0

        def flush() -> None:
            nonlocal text, protected
            references.update(_references_in_text(text, protected))
            text = ""
            protected = set()

        for token in block.children or ():
            if token.type == "link_open":
                flush()
                link_depth += 1
            elif token.type == "link_close":
                link_depth -= 1
            elif link_depth:
                continue
            elif token.type in {"text", "text_special"}:
                if token.type == "text_special":
                    protected.update(
                        len(text) + index
                        for index, character in enumerate(token.content)
                        if character in "@[]"
                    )
                text += token.content
            elif token.type == "softbreak":
                text += "\n"
            else:
                flush()
        flush()
    return tuple(sorted(references))
