from __future__ import annotations

import base64
import html
import json
import math
import os
import re
import uuid
from bisect import bisect_right
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.texmath import texmath_plugin
from pydantic import ValidationError

from .models import CommutativeDiagramCreate
from .store import LibraryStore, StoreError

MEDIA_RE = re.compile(r'(?P<prefix>src=")(?P<url>(?:/)?media/[^"#?]+)(?P<suffix>[^"]*)"')
COMMUTATIVE_RE = re.compile(
    r"\[\[commutative:(?P<id>[a-f0-9]{32})(?:\|width=(?P<width>\d{1,3}))?\]\]"
)
EXCALIDRAW_MARKER_RE = re.compile(
    r"^[ \t]*<!-- excalidraw:[a-f0-9]{32}\.excalidraw -->[ \t]*(?:\r?\n|$)",
    flags=re.MULTILINE,
)
MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _embed_images(rendered: str, store: LibraryStore) -> str:
    def replace(match: re.Match[str]) -> str:
        relative = match.group("url").lstrip("/")
        filename = Path(relative).name
        if relative != f"media/{filename}":
            raise StoreError(f"export image is missing or unsafe: {relative}")
        candidate = store.resolve_media_file(filename)
        if candidate is None:
            raise StoreError(f"export image is missing or unsafe: {relative}")
        mime = MEDIA_TYPES.get(candidate.suffix.casefold())
        if not mime:
            raise StoreError(f"export image has an unsupported format: {relative}")
        if candidate.stat().st_size > 100 * 1024 * 1024:
            raise StoreError(f"export image is too large: {relative}")
        encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
        width_match = re.search(r"(?:^|[#?&;])width=(\d{1,3})(?:$|[&;])", match.group("suffix"))
        width = min(100, max(10, int(width_match.group(1)))) if width_match else None
        style = f' style="width:{width}%"' if width is not None else ""
        return f'{match.group("prefix")}data:{mime};base64,{encoded}"{style}'

    return MEDIA_RE.sub(replace, rendered)


def _main(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        raise StoreError("an entry has no formulation")
    return next((item for item in items if item.get("main")), items[0])


def _load_commutative(store: LibraryStore, diagram_id: str) -> CommutativeDiagramCreate:
    path = store.resolve_commutative_file(f"{diagram_id}.commutative.json")
    if path is None:
        raise StoreError(f"commutative diagram is missing: {diagram_id}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        diagram = CommutativeDiagramCreate.model_validate(value)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        ValidationError,
    ) as exc:
        raise StoreError(f"commutative diagram is invalid: {diagram_id}") from exc
    node_ids = [node.id for node in diagram.nodes]
    if len(node_ids) != len(set(node_ids)):
        raise StoreError(f"commutative diagram has duplicate nodes: {diagram_id}")
    known = set(node_ids)
    if any(arrow.source not in known or arrow.target not in known for arrow in diagram.arrows):
        raise StoreError(f"commutative diagram has an unknown arrow endpoint: {diagram_id}")
    return diagram


def _commutative_html(store: LibraryStore, diagram_id: str, requested_width: str | None) -> str:
    diagram = _load_commutative(store, diagram_id)
    width = min(100, max(10, int(requested_width or diagram.width)))
    cell_x = 180
    cell_y = 112
    pad_x = 70
    pad_y = 50
    view_width = pad_x * 2 + max(node.column for node in diagram.nodes) * cell_x
    view_height = pad_y * 2 + max(node.row for node in diagram.nodes) * cell_y
    marker = f"arrowhead-{diagram_id}"
    node_map = {node.id: node for node in diagram.nodes}
    arrows: list[str] = []
    for arrow in diagram.arrows:
        source = node_map[arrow.source]
        target = node_map[arrow.target]
        x1 = pad_x + source.column * cell_x
        y1 = pad_y + source.row * cell_y
        x2 = pad_x + target.column * cell_x
        y2 = pad_y + target.row * cell_y
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy) or 1.0
        trim = 28
        start_x = x1 + dx / length * trim
        start_y = y1 + dy / length * trim
        end_x = x2 - dx / length * trim
        end_y = y2 - dy / length * trim
        dashed = ' stroke-dasharray="7 6"' if arrow.dashed else ""
        arrows.append(
            f'<line x1="{start_x:.2f}" y1="{start_y:.2f}" x2="{end_x:.2f}" '
            f'y2="{end_y:.2f}" class="diagram-arrow"{dashed} marker-end="url(#{marker})"/>'
        )
        if arrow.double:
            offset_x = -dy / length * 5
            offset_y = dx / length * 5
            arrows.append(
                f'<line x1="{end_x + offset_x:.2f}" y1="{end_y + offset_y:.2f}" '
                f'x2="{start_x + offset_x:.2f}" y2="{start_y + offset_y:.2f}" '
                f'class="diagram-arrow"{dashed} marker-end="url(#{marker})"/>'
            )
        if arrow.label:
            arrows.append(
                f'<foreignObject x="{(x1 + x2) / 2 - 60:.2f}" '
                f'y="{(y1 + y2) / 2 - 28:.2f}" width="120" height="40">'
                f'<div xmlns="http://www.w3.org/1999/xhtml" class="diagram-arrow-label">'
                f"{html.escape(arrow.label)}</div></foreignObject>"
            )
    nodes = "".join(
        (
            f'<foreignObject x="{pad_x + node.column * cell_x - 65}" '
            f'y="{pad_y + node.row * cell_y - 25}" width="130" height="50">'
            f'<div xmlns="http://www.w3.org/1999/xhtml" class="diagram-node">'
            f"{html.escape(node.label)}</div></foreignObject>"
        )
        for node in diagram.nodes
    )
    return (
        f'<figure class="commutative" style="width:{width}%">'
        f'<svg viewBox="0 0 {view_width} {view_height}" role="img" '
        f'aria-label="{html.escape(diagram.name)}"><defs><marker id="{marker}" '
        'markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L7,3 z" class="diagram-arrow-head"/></marker></defs>'
        f"{''.join(arrows)}{nodes}</svg><figcaption>{html.escape(diagram.name)}</figcaption></figure>"
    )


def _markdown_code_ranges(markdown: MarkdownIt, source: str) -> list[tuple[int, int]]:
    """Return fenced, indented, and inline-code source ranges."""
    line_offsets = [0]
    line_offsets.extend(match.end() for match in re.finditer("\n", source))

    def line_offset(line: int) -> int:
        return line_offsets[line] if line < len(line_offsets) else len(source)

    ranges: list[tuple[int, int]] = []
    for token in markdown.parse(source):
        if token.type in {"fence", "code_block"} and token.map:
            ranges.append((line_offset(token.map[0]), line_offset(token.map[1])))

    block_ranges: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if block_ranges and start <= block_ranges[-1][1]:
            block_ranges[-1] = (block_ranges[-1][0], max(end, block_ranges[-1][1]))
        else:
            block_ranges.append((start, end))
    block_starts = [start for start, _ in block_ranges]

    def containing_block(index: int) -> tuple[int, int] | None:
        position = bisect_right(block_starts, index) - 1
        if position >= 0:
            start, end = block_ranges[position]
            if index < end:
                return start, end
        return None

    index = 0
    while index < len(source):
        protected = containing_block(index)
        if protected:
            index = protected[1]
            continue
        if source[index] != "`":
            index += 1
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and source[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            index += 1
            continue
        run_end = index + 1
        while run_end < len(source) and source[run_end] == "`":
            run_end += 1
        run_length = run_end - index
        closing = run_end
        while closing < len(source):
            protected = containing_block(closing)
            if protected:
                closing = protected[1]
                continue
            if source[closing] != "`":
                closing += 1
                continue
            closing_end = closing + 1
            while closing_end < len(source) and source[closing_end] == "`":
                closing_end += 1
            if closing_end - closing == run_length:
                ranges.append((index, closing_end))
                index = closing_end
                break
            closing = closing_end
        else:
            index = run_end

    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def _outside_ranges(match: re.Match[str], ranges: list[tuple[int, int]]) -> bool:
    for start, end in ranges:
        if start >= match.end():
            return True
        if end > match.start():
            return False
    return True


def _render_markdown(markdown: MarkdownIt, source: str, store: LibraryStore) -> str:
    protected = _markdown_code_ranges(markdown, source)
    events: list[tuple[int, int, str, re.Match[str]]] = [
        (match.start(), match.end(), "diagram", match)
        for match in COMMUTATIVE_RE.finditer(source)
        if _outside_ranges(match, protected)
    ]
    events.extend(
        (match.start(), match.end(), "marker", match)
        for match in EXCALIDRAW_MARKER_RE.finditer(source)
        if _outside_ranges(match, protected)
    )
    events.sort(key=lambda event: (event[0], event[1]))
    pieces: list[str] = []
    cursor = 0
    for start, end, kind, match in events:
        if start < cursor:
            continue
        pieces.append(markdown.render(source[cursor:start]))
        if kind == "diagram":
            pieces.append(_commutative_html(store, match.group("id"), match.group("width")))
        cursor = end
    pieces.append(markdown.render(source[cursor:]))
    return "".join(pieces)


def _mathjax_tex(content: str, options: dict[str, Any]) -> str:
    """Preserve TeX for MathJax while keeping Markdown raw HTML disabled."""
    escaped = html.escape(content, quote=False)
    if options["display_mode"]:
        return f"\\[{escaped}\\]"
    return f"\\({escaped}\\)"


def build_export_html(
    store: LibraryStore,
    entries: list[dict[str, Any]],
    title: str,
    include_supplements: bool,
    mathjax_src: str = "/vendor/mathjax/tex-svg.js",
) -> str:
    markdown = (
        MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
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
    sections: list[str] = []
    labels = {"ax": "Axiom", "df": "Definition", "rk": "Remark", "th": "Theorem", "pb": "Problem"}
    for entry in entries:
        primary = _main(entry["formulations"])
        header = (
            _render_markdown(markdown, entry.get("header", ""), store)
            if entry.get("header")
            else ""
        )
        body = _render_markdown(markdown, primary.get("content", ""), store)
        alternatives = []
        for item in entry["formulations"]:
            if item["id"] == primary["id"]:
                continue
            alternatives.append(
                '<section class="alternative">'
                f"<h3>Alternative: {html.escape(item['label'])}</h3>"
                f"{_render_markdown(markdown, item.get('content', ''), store)}</section>"
            )
        supplements = []
        if include_supplements:
            for item in entry.get("supplements", []):
                name = "Proof" if item["kind"] == "pf" else "Solution"
                if not item.get("main"):
                    name += f" ({html.escape(item['label'])})"
                supplements.append(
                    f'<section class="supplement"><h3>{name}</h3>'
                    f"{_render_markdown(markdown, item.get('content', ''), store)}</section>"
                )
        sections.append(
            f"""<article class="entry {entry["kind"]}">
              <div class="entry-meta">{labels[entry["kind"]]} · <code>{html.escape(entry["canonical_tag"])}</code></div>
              <h2>{html.escape(entry["title"])}</h2>
              {header}<div class="entry-body">{body}</div>{"".join(alternatives)}{"".join(supplements)}
            </article>"""
        )
    body = _embed_images("".join(sections), store)
    macros = (
        json.dumps(store.get_macros(), ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    script_src = html.escape(mathjax_src, quote=True)
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{html.escape(title)}</title>
<script>window.MathJax={{loader:{{paths:{{mathjax:'/vendor/mathjax','mathjax-newcm':'/vendor/mathjax-newcm-font'}},load:['ui/safe']}},tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']],processEscapes:true,macros:{macros}}},options:{{enableMenu:false}},chtml:{{displayOverflow:'linebreak'}},svg:{{displayOverflow:'linebreak',fontCache:'local'}}}};</script>
<script id="MathJax-script" src="{script_src}"></script>
<style>
@page {{ size: Letter; margin: .72in .7in .78in; }}
body {{ margin:0; color:#17211e; font:11pt/1.56 Georgia,serif; }}
h1 {{ margin:0 0 30pt; padding-bottom:12pt; border-bottom:1px solid #bcc8c2; color:#174f45; font:600 25pt Georgia,serif; }}
h2 {{ margin:5pt 0 10pt; font-size:18pt; break-after:avoid; }} h3 {{ color:#174f45; font-size:12pt; break-after:avoid; }}
.entry {{ break-inside:avoid-page; margin:0 0 30pt; }} .entry-meta {{ color:#60716a; font:8.5pt ui-monospace,monospace; text-transform:uppercase; letter-spacing:.04em; }}
.entry-body {{ margin-top:8pt; }} .alternative,.supplement {{ margin:12pt 0 0 14pt; padding:1pt 0 1pt 13pt; border-left:2px solid #abc2b8; }}
code {{ color:#174f45; font-size:8pt; text-transform:none; }} pre {{ white-space:pre-wrap; padding:9pt; background:#f0f2ee; break-inside:avoid; }}
img {{ display:block; max-width:100%; max-height:7in; margin:12pt auto; object-fit:contain; }} table {{ width:100%; border-collapse:collapse; }} th,td {{ padding:5pt; border:1px solid #c9d0cc; }}
a {{ color:#174f45; }} mjx-container[display="true"] {{ margin:14pt 0 !important; }}
.commutative {{ margin:14pt auto; break-inside:avoid; }} .commutative > svg {{ display:block; width:100%; overflow:visible; }}
.commutative figcaption {{ margin-top:4pt; color:#60716a; font:italic 9pt Georgia,serif; text-align:center; }}
.diagram-arrow {{ stroke:#174f45; stroke-width:2; fill:none; }} .diagram-arrow-head {{ fill:#174f45; }}
.diagram-node,.diagram-arrow-label {{ box-sizing:border-box; display:grid; place-items:center; text-align:center; background:white; }}
.diagram-node {{ width:100%; height:100%; font-size:15px; font-weight:600; }}
.diagram-arrow-label {{ width:max-content; max-width:116px; height:auto; margin:9px auto; padding:0 4px; font-size:12px; }}
</style></head><body><h1>{html.escape(title)}</h1>{body}</body></html>'''


def _local_resource(url: str, roots: dict[str, Path]) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.netloc != "study.invalid":
        return None
    path = unquote(parsed.path)
    for prefix, root in roots.items():
        if not path.startswith(prefix):
            continue
        candidate = (root / path[len(prefix) :]).resolve()
        if root in candidate.parents and candidate.is_file():
            return candidate
    return None


async def export_pdf(
    store: LibraryStore,
    entries: list[dict[str, Any]],
    title: str,
    include_supplements: bool,
    mathjax_script: Path,
) -> Path:
    if not entries:
        raise StoreError("there is no matching content to export")
    mathjax_script = mathjax_script.resolve()
    mathjax_root = mathjax_script.parent
    font_root = mathjax_root.parent / "mathjax-newcm-font"
    if not mathjax_script.is_file():
        raise StoreError("the local MathJax bundle is missing")
    if not font_root.is_dir():
        raise StoreError("the local MathJax font data is missing")
    try:
        from playwright.async_api import Error as PlaywrightError
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise StoreError("PDF export requires the Playwright Python package") from exc

    document = build_export_html(
        store,
        entries,
        title,
        include_supplements,
        mathjax_src=f"/vendor/mathjax/{mathjax_script.name}",
    )
    export_id = uuid.uuid4().hex
    temporary = store.runtime_dir / f"export-{export_id}.pdf.tmp"
    target = store.exports_dir / f"{export_id}.pdf"
    roots = {
        "/vendor/mathjax/": mathjax_root,
        "/vendor/mathjax-newcm-font/": font_root,
    }
    unexpected: set[str] = set()
    browser = None
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            async def route_request(route: Any) -> None:
                request_url = route.request.url
                if request_url == "http://study.invalid/export.html":
                    await route.fulfill(body=document, content_type="text/html; charset=utf-8")
                    return
                resource = _local_resource(request_url, roots)
                if resource is not None:
                    content_type = (
                        "text/javascript; charset=utf-8"
                        if resource.suffix.casefold() == ".js"
                        else "application/octet-stream"
                    )
                    await route.fulfill(path=resource, content_type=content_type)
                    return
                unexpected.add(request_url)
                await route.abort("blockedbyclient")

            await page.route("**/*", route_request)
            await page.goto("http://study.invalid/export.html", wait_until="load")
            await page.wait_for_function(
                "() => window.MathJax && MathJax.startup && MathJax.startup.promise"
            )
            await page.evaluate(
                """async () => {
                    await MathJax.startup.promise;
                    if (MathJax.typesetPromise) await MathJax.typesetPromise();
                    if (document.fonts) await document.fonts.ready;
                    await Promise.all(Array.from(document.images, image =>
                        image.complete && image.naturalWidth > 0
                            ? Promise.resolve()
                            : image.complete
                            ? Promise.reject(new Error(`Image failed to load: ${image.alt}`))
                            : new Promise((resolve, reject) => {
                            image.addEventListener('load', resolve, {once: true});
                            image.addEventListener('error', reject, {once: true});
                        })
                    ));
                }"""
            )
            if unexpected:
                blocked = ", ".join(sorted(unexpected)[:3])
                raise StoreError(f"PDF export refused unexpected external resources: {blocked}")
            await page.pdf(
                path=str(temporary),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=False,
                outline=True,
                tagged=True,
            )
            await browser.close()
            browser = None
        os.replace(temporary, target)
    except StoreError:
        raise
    except Exception as exc:
        raise StoreError(f"PDF export failed: {exc}") from exc
    finally:
        if browser is not None:
            try:
                await browser.close()
            except PlaywrightError:
                pass
        temporary.unlink(missing_ok=True)
    return target
