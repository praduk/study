#!/usr/bin/env bash
set -euo pipefail

study_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bundle="$study_root/study_app/web"

python3 - "$bundle" <<'PY'
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

root = Path(sys.argv[1])


class Assets(HTMLParser):
    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "script":
            url = fields.get("src")
        elif tag == "link" and fields.get("rel") in {"stylesheet", "modulepreload", "preload", "icon"}:
            url = fields.get("href")
        else:
            return
        if not url:
            return
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return
        name = unquote(parts.path).lstrip("/")
        path = (root / name).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            missing.add(name)


missing = set()
try:
    Assets().feed((root / "index.html").read_text(encoding="utf-8"))
except (OSError, UnicodeError):
    missing.add("index.html")
if missing:
    sys.exit("Frontend bundle is incomplete: " + ", ".join(sorted(missing)))
PY

# Publish the new entry point after all its assets are available.
COPYFILE_DISABLE=1 tar --exclude=./index.html -C "$bundle" -czf - . |
    ssh pradu.us 'set -eu; web="$HOME/git/study/study_app/web"; mkdir -p "$web"; tar -xzf - -C "$web"'
ssh pradu.us 'set -eu; web="$HOME/git/study/study_app/web"; tmp=$(mktemp "$web/.index.XXXXXX"); trap '\''rm -f "$tmp"'\'' EXIT; cat > "$tmp"; chmod 644 "$tmp"; mv -f "$tmp" "$web/index.html"' < "$bundle/index.html"
