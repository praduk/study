import base64
import hashlib
import hmac
import importlib.util
import io
import ipaddress
import json
import os
import re
import time
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlsplit

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from PIL import Image, ImageOps, UnidentifiedImageError

from .auth import COOKIE_NAME, CSRF_HEADER, LoginThrottle, Session, SessionStore, verify_password
from .config import Settings
from .export import export_pdf
from .git_ops import GitError, GitRepository
from .library_validation import IMAGE_DECODE_LOCK, MAX_REFERENCE_QUERY_LENGTH
from .models import (
    CommutativeDiagramCreate,
    ContentUpdate,
    EntryCreate,
    EntryUpdate,
    ExportRequest,
    FolderCreate,
    FolderUpdate,
    GitCommitRequest,
    LoginRequest,
    MacrosUpdate,
    MarkdownRenderRequest,
    MoveRequest,
    ReorderRequest,
    ReviewGrade,
    ReviewReveal,
    SupplementCreate,
    VariantCreate,
    VariantUpdate,
)
from .review import ReviewEngine
from .store import LibraryStore, StoreError
from .web_render import render_markdown_fragment

SAFE_FILE = re.compile(r"^[a-f0-9]{64}\.(?:png|jpe?g|webp)$")
SAFE_DIAGRAM = re.compile(r"^[a-f0-9]{32}\.excalidraw$")
SAFE_COMMUTATIVE = re.compile(r"^[a-f0-9]{32}\.commutative\.json$")
INLINE_SCRIPT = re.compile(
    r"<script\b(?P<attributes>[^>]*)>(?P<body>.*?)</script\s*>",
    flags=re.IGNORECASE | re.DOTALL,
)
SCRIPT_SRC = re.compile(r"(?:^|\s)src\s*=", flags=re.IGNORECASE)
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
_IMAGE_DECODE_LOCK = IMAGE_DECODE_LOCK


def _host_and_port(value: str, scheme: str | None = None) -> tuple[str, int | None] | None:
    value = value.strip().casefold()
    if not value or any(character.isspace() for character in value) or "/" in value:
        return None
    port: int | None = None
    if value.startswith("["):
        closing = value.find("]")
        if closing < 0:
            return None
        host = value[1:closing]
        remainder = value[closing + 1 :]
        if remainder:
            if not remainder.startswith(":") or not remainder[1:].isdigit():
                return None
            port = int(remainder[1:])
    else:
        if value.count(":") > 1:
            return None
        if ":" in value:
            host, port_text = value.rsplit(":", 1)
            if not port_text.isdigit():
                return None
            port = int(port_text)
        else:
            host = value
    host = host.rstrip(".")
    if not host or (port is not None and not 1 <= port <= 65535):
        return None
    if port is None and scheme in {"http", "https"}:
        port = 80 if scheme == "http" else 443
    return host, port


def _configured_host(value: str) -> str:
    return (
        value[1:-1].casefold()
        if value.startswith("[") and value.endswith("]")
        else value.casefold()
    )


def _same_origin(request: Request) -> bool:
    fetch_site = request.headers.get("sec-fetch-site")
    if fetch_site and fetch_site.casefold() != "same-origin":
        return False
    source = request.headers.get("origin") or request.headers.get("referer")
    if not source:
        return False
    try:
        parsed = urlsplit(source)
        source_port = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.username is not None
        or parsed.password is not None
        or not parsed.hostname
    ):
        return False
    request_scheme = request.url.scheme.casefold()
    if parsed.scheme.casefold() != request_scheme:
        return False
    request_target = _host_and_port(request.headers.get("host", ""), request_scheme)
    if request_target is None:
        return False
    source_target = (
        parsed.hostname.casefold().rstrip("."),
        source_port or (80 if parsed.scheme == "http" else 443),
    )
    return source_target == request_target


def _is_loopback_client(request: Request) -> bool:
    if request.client is None:
        return False
    try:
        return ipaddress.ip_address(request.client.host).is_loopback
    except ValueError:
        return request.client.host.casefold() == "localhost"


def _safe_existing_file(directory: Path, filename: str) -> Path | None:
    root = directory.resolve()
    candidate = (root / filename).resolve()
    if root not in candidate.parents or not candidate.is_file():
        return None
    return candidate


def _pdf_export_available() -> bool:
    return importlib.util.find_spec("playwright") is not None


def _atomic_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _markdown_alt(value: str) -> str:
    return re.sub(r"\s+", " ", value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _inline_script_sources(html: str) -> tuple[str, ...]:
    """Return exact CSP hashes for inline scripts in one HTML response body."""
    sources: list[str] = []
    for match in INLINE_SCRIPT.finditer(html):
        if SCRIPT_SRC.search(match.group("attributes")):
            continue
        digest = hashlib.sha256(match.group("body").encode("utf-8")).digest()
        sources.append(f"'sha256-{base64.b64encode(digest).decode('ascii')}'")
    return tuple(dict.fromkeys(sources))


def _content_security_policy(inline_script_sources: tuple[str, ...] = ()) -> str:
    script_policy = " ".join(("'self'", "'wasm-unsafe-eval'", *inline_script_sources))
    return (
        f"default-src 'self'; script-src {script_policy}; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
        "font-src 'self' data:; connect-src 'self'; worker-src 'self' blob:; "
        "object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )


def _frontend_html_response(path: Path, *, cache_control: str | None = None) -> Response:
    """Serve and authorize the same immutable snapshot of an HTML file."""
    try:
        body = path.read_bytes()
        html = body.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return HTMLResponse("<h1>Study frontend is unreadable</h1>", status_code=503)
    headers = {"Content-Security-Policy": _content_security_policy(_inline_script_sources(html))}
    if cache_control is not None:
        headers["Cache-Control"] = cache_control
    return Response(content=body, media_type="text/html", headers=headers)


def create_app(settings: Settings, local_mode: bool = False) -> FastAPI:
    store = LibraryStore(settings.data_dir)
    # Warm the immutable search snapshot so the first editor picker/hover has
    # no disk-indexing latency.
    store.reload_search_index()
    review = ReviewEngine(store)
    sessions = SessionStore(
        store.runtime_dir / "sessions.sqlite3",
        settings.session_days,
        settings.session_generation,
    )
    def validate_candidate_data(candidate_data: Path) -> None:
        for required_name in ("library.json", "macros.json", "review.json"):
            required = candidate_data / required_name
            if required.is_symlink() or not required.is_file():
                raise StoreError(f"upstream data is missing safe {required_name}")
        candidate_store = LibraryStore(candidate_data)
        candidate_store.reload_search_index()
        candidate_store.get_macros()
        candidate_review = ReviewEngine(candidate_store)

        log_path = candidate_data / "review-log.jsonl"
        if log_path.exists():
            if log_path.is_symlink() or not log_path.is_file():
                raise StoreError("upstream review log is unsafe")
            try:
                with log_path.open(encoding="utf-8") as stream:
                    for line_number, line in enumerate(stream, 1):
                        if line.strip() and not isinstance(json.loads(line), dict):
                            raise StoreError(
                                f"upstream review log line {line_number} is not an object"
                            )
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise StoreError("upstream review log is unreadable or invalid") from exc

        # Rebuild from the candidate's complete history so malformed schedules,
        # observations, or checkpoints are rejected before Git advances HEAD.
        candidate_review.validate_log()
        candidate_review.queue(include_not_due=True, limit=500)

        library_path = candidate_data / "excalidraw" / "library.excalidrawlib"
        if library_path.exists():
            if library_path.is_symlink() or not library_path.is_file():
                raise StoreError("upstream Excalidraw library is unsafe")
            try:
                template_library = json.loads(library_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise StoreError("upstream Excalidraw library is unreadable or invalid") from exc
            if not isinstance(template_library, dict) or not isinstance(
                template_library.get("libraryItems"), list
            ):
                raise StoreError("upstream Excalidraw library has an invalid structure")

    git = GitRepository(settings.root, settings.data_dir, store.mutation_lock)
    throttle = LoginThrottle()
    app = FastAPI(title="Study", version="0.1.0", docs_url=None, redoc_url=None)
    allowed_hosts = {
        _configured_host(host)
        for host in (LOOPBACK_HOSTS if local_mode else settings.allowed_hosts)
    }
    app.state.settings = settings
    app.state.local_mode = local_mode
    app.state.store = store
    app.state.review = review
    app.state.sessions = sessions

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        request_host = _host_and_port(request.headers.get("host", ""))
        if request_host is None or request_host[0] not in allowed_hosts:
            response = JSONResponse(status_code=400, content={"detail": "invalid Host header"})
        elif local_mode and not _is_loopback_client(request):
            response = JSONResponse(
                status_code=403, content={"detail": "local mode accepts loopback clients only"}
            )
        else:
            response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            _content_security_policy(),
        )
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    def current_session(request: Request) -> Session | None:
        if local_mode:
            return None
        token = request.cookies.get(COOKIE_NAME)
        session = sessions.get(token)
        if session is None:
            raise HTTPException(status_code=401, detail="authentication required")
        return session

    def mutation_session(request: Request) -> Session | None:
        session = current_session(request)
        if not _same_origin(request):
            raise HTTPException(status_code=403, detail="cross-origin request refused")
        expected = "local" if local_mode else session.csrf if session else ""
        provided = request.headers.get(CSRF_HEADER, "")
        if not hmac.compare_digest(provided, expected):
            raise HTTPException(status_code=403, detail="invalid CSRF token")
        return session

    Auth = Annotated[Session | None, Depends(current_session)]
    Mutation = Annotated[Session | None, Depends(mutation_session)]

    @app.exception_handler(StoreError)
    async def store_error_handler(_request: Request, exc: StoreError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(GitError)
    async def git_error_handler(_request: Request, exc: GitError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/session")
    def session_info(request: Request, response: Response) -> dict[str, Any]:
        if local_mode:
            return {
                "authenticated": True,
                "auth_required": False,
                "csrf": "local",
                "local_mode": True,
            }
        cookie = request.cookies.get(COOKIE_NAME)
        session = sessions.get(cookie)
        if cookie and session is None:
            response.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=settings.secure_cookie,
                httponly=True,
                samesite="strict",
            )
        return {
            "authenticated": session is not None,
            "auth_required": True,
            "csrf": session.csrf if session else None,
            "local_mode": False,
        }

    @app.post("/api/login")
    def login(request: Request, payload: LoginRequest, response: Response) -> dict[str, Any]:
        if local_mode:
            return {"authenticated": True, "csrf": "local"}
        if not _same_origin(request):
            raise HTTPException(status_code=403, detail="cross-origin request refused")
        if not settings.password_hash:
            raise HTTPException(status_code=503, detail="server mode has no configured password")
        remote = request.client.host if request.client else "unknown"
        if not throttle.check(remote):
            raise HTTPException(
                status_code=429,
                detail="too many login attempts; try again later",
                headers={"Retry-After": "300"},
            )
        if not verify_password(payload.password, settings.password_hash):
            throttle.fail(remote)
            time.sleep(0.35)
            raise HTTPException(status_code=401, detail="incorrect password")
        throttle.succeed(remote)
        sessions.revoke(request.cookies.get(COOKIE_NAME))
        session = sessions.create()
        response.set_cookie(
            COOKIE_NAME,
            session.token,
            httponly=True,
            secure=settings.secure_cookie,
            samesite="strict",
            max_age=settings.session_days * 86400,
            path="/",
        )
        return {"authenticated": True, "csrf": session.csrf}

    @app.post("/api/logout")
    def logout(request: Request, response: Response, _session: Mutation) -> dict[str, bool]:
        sessions.revoke(request.cookies.get(COOKIE_NAME))
        response.delete_cookie(
            COOKIE_NAME,
            path="/",
            secure=settings.secure_cookie,
            httponly=True,
            samesite="strict",
        )
        return {"authenticated": False}

    @app.get("/api/bootstrap")
    def bootstrap(_session: Auth) -> dict[str, Any]:
        return {
            **store.snapshot(),
            "review": review.stats(),
            "git": git.status(),
            "capabilities": {
                "editing": True,
                "pdf_export": _pdf_export_available(),
                "excalidraw": True,
                "commutative_diagrams": True,
                "local_mode": local_mode,
            },
        }

    @app.get("/api/entries/{entry_id}")
    def get_entry(entry_id: str, _session: Auth) -> dict[str, Any]:
        return store.get_entry(entry_id)

    @app.get("/api/search")
    def search(
        q: Annotated[str, Query(min_length=1, max_length=1000)],
        _session: Auth,
        folder_id: Annotated[str | None, Query(max_length=128)] = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 40,
    ) -> dict[str, Any]:
        return {"results": store.search(q, limit, folder_id)}

    @app.get("/api/references/resolve")
    def resolve_reference(
        folder_id: Annotated[str, Query(min_length=1, max_length=128)],
        tag: Annotated[str, Query(min_length=1, max_length=MAX_REFERENCE_QUERY_LENGTH)],
        _session: Auth,
    ) -> dict[str, Any]:
        return store.resolve_reference(folder_id, tag)

    @app.get("/api/references/candidates")
    def reference_candidates(
        folder_id: Annotated[str, Query(min_length=1, max_length=128)],
        _session: Auth,
        q: Annotated[str, Query(max_length=1000)] = "",
        limit: Annotated[int, Query(ge=1, le=200)] = 40,
    ) -> dict[str, Any]:
        return {"results": store.reference_candidates(folder_id, q, limit)}

    @app.post("/api/folders")
    def create_folder(payload: FolderCreate, _session: Mutation) -> dict[str, Any]:
        return store.create_folder(payload.name, payload.slug, payload.parent_id, payload.index)

    @app.patch("/api/folders/{folder_id}")
    def update_folder(folder_id: str, payload: FolderUpdate, _session: Mutation) -> dict[str, Any]:
        return store.update_folder(folder_id, payload.model_dump(exclude_unset=True))

    @app.delete("/api/folders/{folder_id}")
    def delete_folder(
        folder_id: str,
        _session: Mutation,
        recursive: Annotated[bool, Query()] = False,
    ) -> dict[str, Any]:
        deletion = store.delete_folder(folder_id, recursive=recursive)
        return {"ok": True, "deletion": deletion, "library": store.snapshot()}

    @app.post("/api/entries")
    def create_entry(payload: EntryCreate, _session: Mutation) -> dict[str, Any]:
        return store.create_entry(
            payload.folder_id,
            payload.kind,
            payload.title,
            payload.tag,
            payload.header,
            payload.content,
            payload.review_modes,
            payload.index,
        )

    @app.patch("/api/entries/{entry_id}")
    def update_entry(entry_id: str, payload: EntryUpdate, _session: Mutation) -> dict[str, Any]:
        return store.update_entry(entry_id, payload.model_dump(exclude_unset=True))

    @app.delete("/api/entries/{entry_id}")
    def delete_entry(entry_id: str, _session: Mutation) -> dict[str, Any]:
        deletion = store.delete_entry(entry_id)
        return {"ok": True, "deletion": deletion, "library": store.snapshot()}

    @app.put("/api/entries/{entry_id}/content/{variant_id}")
    def update_content(entry_id: str, variant_id: str, payload: ContentUpdate, _session: Mutation):
        return store.write_variant_content(entry_id, variant_id, payload.content)

    @app.post("/api/entries/{entry_id}/formulations")
    def add_formulation(entry_id: str, payload: VariantCreate, _session: Mutation):
        return store.add_formulation(entry_id, payload.model_dump())

    @app.post("/api/entries/{entry_id}/supplements")
    def add_supplement(entry_id: str, payload: SupplementCreate, _session: Mutation):
        return store.add_supplement(entry_id, payload.model_dump())

    @app.patch("/api/entries/{entry_id}/variants/{variant_id}")
    def update_variant(entry_id: str, variant_id: str, payload: VariantUpdate, _session: Mutation):
        return store.update_variant(entry_id, variant_id, payload.model_dump(exclude_unset=True))

    @app.post("/api/items/{item_type}/{item_id}/move")
    def move_item(item_type: str, item_id: str, payload: MoveRequest, _session: Mutation):
        store.move_item(item_type, item_id, payload.destination_folder_id, payload.index)
        return {"ok": True, "library": store.snapshot()}

    @app.put("/api/folders/{folder_id}/order")
    def reorder(folder_id: str, payload: ReorderRequest, _session: Mutation):
        store.reorder_entries(folder_id, payload.entry_ids)
        return {"ok": True, "library": store.snapshot()}

    @app.put("/api/macros")
    def update_macros(payload: MacrosUpdate, _session: Mutation):
        return store.set_macros(payload.macros)

    @app.post("/api/render/markdown")
    def render_markdown(payload: MarkdownRenderRequest, _session: Auth) -> dict[str, str]:
        return {"html": render_markdown_fragment(store, payload.source)}

    async def prepare_image(upload: UploadFile) -> tuple[str, int, int, bytes]:
        limit = settings.max_upload_mb * 1024 * 1024
        try:
            raw = await upload.read(limit + 1)
        finally:
            await upload.close()
        if len(raw) > limit:
            raise HTTPException(
                status_code=413, detail=f"image exceeds {settings.max_upload_mb} MB"
            )
        if not raw:
            raise HTTPException(status_code=415, detail="the uploaded image is empty")
        pixel_limit = settings.max_image_megapixels * 1_000_000
        try:
            with _IMAGE_DECODE_LOCK:
                previous_limit = Image.MAX_IMAGE_PIXELS
                Image.MAX_IMAGE_PIXELS = pixel_limit
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("error", Image.DecompressionBombWarning)
                        with Image.open(io.BytesIO(raw)) as opened:
                            if opened.format not in ALLOWED_IMAGE_FORMATS:
                                raise UnidentifiedImageError("image format is not allowed")
                            if getattr(opened, "is_animated", False):
                                raise UnidentifiedImageError("animated images are not allowed")
                            source_width, source_height = opened.size
                            if (
                                source_width <= 0
                                or source_height <= 0
                                or source_width * source_height > pixel_limit
                            ):
                                raise HTTPException(
                                    status_code=413, detail="decoded image is too large"
                                )
                            opened.verify()
                        with Image.open(io.BytesIO(raw)) as opened:
                            image = ImageOps.exif_transpose(opened)
                            width, height = image.size
                            if width <= 0 or height <= 0 or width * height > pixel_limit:
                                raise HTTPException(
                                    status_code=413, detail="decoded image is too large"
                                )
                            image.load()
                            if image.mode not in {"RGB", "RGBA"}:
                                has_alpha = "A" in image.getbands() or "transparency" in image.info
                                image = image.convert("RGBA" if has_alpha else "RGB")
                            output = io.BytesIO()
                            image.save(output, format="PNG", optimize=True)
                            normalized = output.getvalue()
                finally:
                    Image.MAX_IMAGE_PIXELS = previous_limit
        except (MemoryError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise HTTPException(status_code=413, detail="decoded image is too large") from exc
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(status_code=415, detail="unsupported or unsafe image") from exc
        digest = hashlib.sha256(normalized).hexdigest()
        filename = f"{digest}.png"
        return filename, width, height, normalized

    @app.post("/api/entries/{entry_id}/images")
    async def upload_image(
        entry_id: str,
        _session: Mutation,
        image: Annotated[UploadFile, File()],
        alt: Annotated[str, Form()] = "Pasted image",
        width: Annotated[int, Form()] = 70,
        invert_lightness: Annotated[bool, Form()] = False,
    ):
        filename, pixels_wide, pixels_high, normalized = await prepare_image(image)
        width = min(100, max(10, width))
        asset = {
            "id": uuid.uuid4().hex,
            "kind": "image",
            "path": f"media/{filename}",
            "alt": alt.strip()[:240] or "Image",
            "width": width,
            "invert_lightness": invert_lightness,
            "pixels": [pixels_wide, pixels_high],
        }
        image_path = store.media_dir / filename
        with store.mutation_lock:
            store.get_entry(entry_id)
            created = not image_path.exists()
            if created:
                _atomic_bytes(image_path, normalized)
            try:
                store.register_asset(entry_id, asset)
            except Exception:
                if created:
                    image_path.unlink(missing_ok=True)
                raise
        fragment = f"width={width}" + ("&invert=lightness" if invert_lightness else "")
        asset["markdown"] = f"![{_markdown_alt(asset['alt'])}](/media/{filename}#{fragment})"
        return asset

    @app.post("/api/entries/{entry_id}/diagrams/excalidraw")
    async def save_excalidraw(
        entry_id: str,
        _session: Mutation,
        scene: Annotated[str, Form()],
        preview: Annotated[UploadFile, File()],
        name: Annotated[str, Form()] = "Diagram",
        width: Annotated[int, Form()] = 76,
        invert_lightness: Annotated[bool, Form()] = True,
    ):
        if len(scene.encode("utf-8")) > 8 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Excalidraw scene is too large")
        try:
            parsed = json.loads(scene)
        except (json.JSONDecodeError, RecursionError) as exc:
            raise HTTPException(status_code=422, detail="invalid Excalidraw JSON") from exc
        if not isinstance(parsed, dict) or not isinstance(parsed.get("elements", []), list):
            raise HTTPException(status_code=422, detail="invalid Excalidraw scene")
        diagram_id = uuid.uuid4().hex
        source_name = f"{diagram_id}.excalidraw"
        preview_name, pixels_wide, pixels_high, normalized = await prepare_image(preview)
        source_path = store.diagram_dir / source_name
        preview_path = store.media_dir / preview_name
        width = min(100, max(10, width))
        asset = {
            "id": diagram_id,
            "kind": "excalidraw",
            "source": f"diagrams/{source_name}",
            "path": f"media/{preview_name}",
            "alt": name.strip()[:240] or "Diagram",
            "width": width,
            "invert_lightness": invert_lightness,
            "pixels": [pixels_wide, pixels_high],
        }
        with store.mutation_lock:
            store.get_entry(entry_id)
            preview_created = not preview_path.exists()
            if preview_created:
                _atomic_bytes(preview_path, normalized)
            _atomic_json(source_path, parsed)
            try:
                store.register_asset(entry_id, asset)
            except Exception:
                source_path.unlink(missing_ok=True)
                if preview_created:
                    preview_path.unlink(missing_ok=True)
                raise
        fragment = f"width={width}" + ("&invert=lightness" if invert_lightness else "")
        asset["markdown"] = (
            f"![{_markdown_alt(asset['alt'])}](/media/{preview_name}#{fragment})\n"
            f"<!-- excalidraw:{source_name} -->"
        )
        return asset

    @app.get("/api/diagrams/{filename}")
    def get_diagram(filename: str, _session: Auth):
        if not SAFE_DIAGRAM.fullmatch(filename):
            raise HTTPException(status_code=404)
        path = _safe_existing_file(store.diagram_dir, filename)
        if path is None:
            raise HTTPException(status_code=404)
        return FileResponse(
            path, media_type="application/json", headers={"Cache-Control": "no-store"}
        )

    @app.get("/api/excalidraw/library")
    def get_excalidraw_library(_session: Auth):
        root = store.data_dir / "excalidraw"
        configured_path = root / "library.excalidrawlib"
        path = _safe_existing_file(root, "library.excalidrawlib")
        if path is None and not configured_path.exists() and not configured_path.is_symlink():
            return {"type": "excalidrawlib", "version": 2, "libraryItems": []}
        if path is None:
            raise HTTPException(status_code=500, detail="the Excalidraw template library is unsafe")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise HTTPException(
                status_code=500, detail="the Excalidraw template library is invalid"
            ) from exc

    @app.put("/api/excalidraw/library")
    async def put_excalidraw_library(request: Request, _session: Mutation):
        raw = await request.body()
        if len(raw) > 8 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="template library is too large")
        try:
            value = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise HTTPException(status_code=422, detail="invalid template library JSON") from exc
        if not isinstance(value, dict) or not isinstance(value.get("libraryItems"), list):
            raise HTTPException(status_code=422, detail="invalid Excalidraw template library")
        value["type"] = "excalidrawlib"
        value["version"] = 2
        path = store.data_dir / "excalidraw" / "library.excalidrawlib"
        with store.mutation_lock:
            _atomic_json(path, value)
        return {"ok": True, "items": len(value["libraryItems"])}

    @app.post("/api/entries/{entry_id}/diagrams/commutative")
    def save_commutative(entry_id: str, payload: CommutativeDiagramCreate, _session: Mutation):
        node_ids = [node.id for node in payload.nodes]
        if len(set(node_ids)) != len(node_ids):
            raise HTTPException(status_code=422, detail="diagram node ids must be unique")
        known = set(node_ids)
        if any(arrow.source not in known or arrow.target not in known for arrow in payload.arrows):
            raise HTTPException(
                status_code=422, detail="every arrow endpoint must name a diagram node"
            )
        diagram_id = uuid.uuid4().hex
        filename = f"{diagram_id}.commutative.json"
        diagram = {"version": 1, **payload.model_dump()}
        source_path = store.diagram_dir / filename
        asset = {
            "id": diagram_id,
            "kind": "commutative",
            "source": f"diagrams/{filename}",
            "alt": payload.name,
            "width": payload.width,
        }
        with store.mutation_lock:
            store.get_entry(entry_id)
            _atomic_json(source_path, diagram)
            try:
                store.register_asset(entry_id, asset)
            except Exception:
                source_path.unlink(missing_ok=True)
                raise
        asset["markdown"] = f"[[commutative:{diagram_id}|width={payload.width}]]"
        return asset

    @app.get("/api/commutative/{filename}")
    def get_commutative(filename: str, _session: Auth):
        if not SAFE_COMMUTATIVE.fullmatch(filename):
            raise HTTPException(status_code=404)
        path = _safe_existing_file(store.diagram_dir, filename)
        if path is None:
            raise HTTPException(status_code=404)
        return FileResponse(
            path, media_type="application/json", headers={"Cache-Control": "private, max-age=60"}
        )

    @app.get("/media/{filename}")
    def media(filename: str, _session: Auth):
        if not SAFE_FILE.fullmatch(filename):
            raise HTTPException(status_code=404)
        path = _safe_existing_file(store.media_dir, filename)
        if path is None:
            raise HTTPException(status_code=404)
        media_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }[path.suffix.casefold()]
        return FileResponse(
            path,
            media_type=media_type,
            headers={"Cache-Control": "private, max-age=31536000, immutable"},
        )

    @app.get("/api/review/queue")
    def review_queue(_session: Auth, include_not_due: bool = False, limit: int = 100):
        return {
            "cards": review.queue(include_not_due=include_not_due, limit=min(500, max(1, limit)))
        }

    @app.get("/api/review/calendar")
    def review_calendar(
        _session: Auth,
        start: datetime | None = None,
        end: datetime | None = None,
        include_inactive: bool = False,
        timezone_name: Annotated[
            str, Query(alias="timezone", min_length=1, max_length=128)
        ] = "UTC",
    ):
        return review.calendar(
            start=start,
            end=end,
            include_inactive=include_inactive,
            timezone_name=timezone_name,
        )

    @app.post("/api/review/{card_id:path}/reveal")
    def reveal(card_id: str, payload: ReviewReveal, _session: Mutation):
        if payload.overt and not payload.attempt.strip():
            raise HTTPException(
                status_code=422,
                detail="a written attempt cannot be empty",
            )
        return review.reveal(card_id, payload.model_dump())

    @app.post("/api/review/{card_id:path}/grade")
    def grade(card_id: str, payload: ReviewGrade, _session: Mutation):
        return review.grade(card_id, payload.attempt_id, payload.grade)

    @app.get("/api/git/status")
    def git_status(_session: Auth):
        return git.status()

    @app.post("/api/git/commit")
    def git_commit(payload: GitCommitRequest, _session: Mutation):
        return git.commit_content(payload.message)

    @app.post("/api/git/pull")
    def git_pull(_session: Mutation):
        with store.mutation_lock:
            result = git.pull_fast_forward(validate_candidate_data)
            store.ensure_layout()
            store.reload_search_index()
            review.rebuild_calibration()
            review.stats()
            return result

    @app.post("/api/export/pdf")
    async def create_pdf(payload: ExportRequest, _session: Mutation):
        entries = store.ordered_entries(
            folder_id=payload.folder_id,
            recursive=payload.recursive,
            kinds=set(payload.kinds),
        )
        title = payload.title or "Study export"
        built_mathjax = settings.frontend_public / "vendor" / "mathjax" / "tex-svg.js"
        fallback_mathjax = (
            settings.no_build_frontend / "vendor" / "mathjax" / "tex-chtml.js"
        )
        mathjax = (
            built_mathjax
            if settings.rich_frontend and built_mathjax.is_file()
            else fallback_mathjax
        )
        target = await export_pdf(store, entries, title, payload.include_supplements, mathjax)
        safe_title = re.sub(r"[^A-Za-z0-9._-]+", "-", title).strip("-") or "study"
        return FileResponse(target, media_type="application/pdf", filename=f"{safe_title}.pdf")

    @app.get("/api/webmcp/library-summary")
    def webmcp_summary(_session: Auth):
        snapshot = store.snapshot()
        return {
            "folders": len(snapshot["folders"]),
            "entries": len(snapshot["entries"]),
            "due": review.stats()["due"],
        }

    @app.get("/{path:path}")
    def frontend(path: str):
        if path in {"api", "media"} or path.startswith(("api/", "media/")):
            raise HTTPException(status_code=404, detail="API route not found")
        built_index = (
            _safe_existing_file(settings.built_frontend, "index.html")
            if settings.rich_frontend
            else None
        )
        root = settings.built_frontend if built_index is not None else settings.no_build_frontend
        candidate = (root / path).resolve()
        if root.exists() and root.resolve() in candidate.parents and candidate.is_file():
            if candidate.suffix.casefold() == ".html":
                return _frontend_html_response(candidate)
            return FileResponse(candidate)
        index = _safe_existing_file(root, "index.html")
        if index is not None:
            return _frontend_html_response(index, cache_control="no-cache")
        return HTMLResponse("<h1>Study interface is missing</h1>", status_code=503)

    return app
