"""Time Study API actions against a disposable copy of the authored library.

Run with the checkout's development environment. No source library or Git writes
are performed. Git status is measured read-only against --source-root. Results
contain timings/counts, not authored text, answers, or review records.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import statistics
import sys
import tempfile
import time
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


def summarize(samples):
    ordered = sorted(samples)
    return {
        "n": len(samples),
        "median_ms": round(statistics.median(samples), 2),
        "min_ms": round(ordered[0], 2),
        "max_ms": round(ordered[-1], 2),
        "samples_ms": [round(value, 2) for value in samples],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--git-root", type=Path, help="Read-only Git status root; defaults to source"
    )
    parser.add_argument("--samples", type=int, default=7)
    parser.add_argument("--interactive", action="store_true",
                        help="Use the current UI's navigation bootstrap and small move responses")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    if args.samples < 1:
        parser.error("--samples must be positive")
    source = args.source_root.resolve()
    git_root = (args.git_root or source).resolve()
    sys.path.insert(0, str(source))
    from fastapi.testclient import TestClient
    from PIL import Image

    import study_app.app as app_module
    from study_app.auth import make_password_hash
    from study_app.config import Settings
    from study_app.git_ops import GitRepository

    results = {"actions": {}, "method": "TestClient, gzip, disposable data copy"}
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def record(name, action, count=None, pause=0):
        samples = []
        result = None
        for _ in range(count or args.samples):
            if pause:
                time.sleep(pause)
            start = time.perf_counter()
            result = action()
            samples.append((time.perf_counter() - start) * 1000)
        results["actions"][name] = summarize(samples)
        print(name, results["actions"][name]["median_ms"], flush=True)
        args.output.write_text(json.dumps(results, indent=2) + "\n")
        return result

    with tempfile.TemporaryDirectory(prefix="study-api-benchmark-") as temporary:
        root = Path(temporary)
        shutil.copytree(
            source / "data", root / "data", ignore=shutil.ignore_patterns("runtime", "exports")
        )
        settings = Settings(root, 8765, "127.0.0.1", ("127.0.0.1",), "", 30, False, 12, 32)
        # GitRepository.status is read-only. Never invoke commit/pull here.
        with patch.object(
            app_module, "GitRepository", lambda *unused: GitRepository(git_root, git_root / "data")
        ):
            app = record("application_startup", lambda: app_module.create_app(settings, True), 1)
        store = app.state.store
        snapshot = store.snapshot()
        results["library"] = {
            "entries": len(snapshot["entries"]),
            "folders": len(snapshot["folders"]),
        }
        target = next(entry for entry in snapshot["entries"] if entry["supplements"])
        entry_id, folder_id = target["id"], target["folder_id"]
        headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local", "accept-encoding": "gzip"}
        with TestClient(
            app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000), headers=headers
        ) as client:

            def request(method, url, **kwargs):
                if args.interactive:
                    if url == "/api/bootstrap?compact=true":
                        url += "&navigation=true"
                    elif method == "POST" and url.startswith("/api/items/") and url.endswith("/move"):
                        url += "?include_library=false"
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            reads = {
                "session": "/api/session",
                "bootstrap_compact": "/api/bootstrap?compact=true",
                "bootstrap_full": "/api/bootstrap",
                "entry_read": f"/api/entries/{entry_id}",
                "linked_items": f"/api/entries/{entry_id}/linked-items",
                "search": "/api/search?q=group&limit=40",
                "reference": f"/api/references/resolve?folder_id={folder_id}&tag={target['canonical_tag']}",
                "reference_batch": f"/api/references/resolve-batch?folder_id={folder_id}&tag={target['canonical_tag']}&tag=group",
                "reference_picker": f"/api/references/candidates?folder_id={folder_id}&q=group",
                "review_queue": "/api/review/queue?limit=200",
                "calendar": "/api/review/calendar?timezone=America%2FDenver",
                "git_status": "/api/git/status",
                "drawing_templates": "/api/excalidraw/library",
            }
            for name, url in reads.items():
                response = record(name + "_first", lambda url=url: request("GET", url), 1)
                if name == "bootstrap_compact":
                    results["bootstrap_bytes"] = {
                        "decoded": len(response.content),
                        "gzip": int(response.headers.get("content-length", 0)),
                    }
                record(name, lambda url=url: request("GET", url))
                if name in {
                    "bootstrap_compact",
                    "entry_read",
                    "linked_items",
                    "search",
                    "review_queue",
                    "calendar",
                }:
                    record(name + "_after_idle", lambda url=url: request("GET", url), 5, 0.3)

            for kind, identifier in (("folders", folder_id), ("entries", entry_id)):
                current = next(item for item in snapshot[kind] if item["id"] == identifier)[
                    "review_enabled"
                ]
                state = [current]

                def toggle(state=state, kind=kind, identifier=identifier):
                    state[0] = not state[0]
                    return request(
                        "PATCH",
                        f"/api/{kind}/{identifier}?include_review_stats=true",
                        json={"review_enabled": state[0]},
                    )

                record(kind + "_review_toggle", toggle, 6)
                record(kind + "_search_after_toggle", lambda: request("GET", reads["search"]), 1)
                record(
                    kind + "_linked_items_after_toggle",
                    lambda: request("GET", reads["linked_items"]),
                    1,
                )

            # An isolated fixture keeps synthetic review attempts out of real history.
            folder = record(
                "folder_create",
                lambda: request(
                    "POST",
                    "/api/folders",
                    json={"name": "Performance fixture", "slug": "performance-fixture"},
                ),
                1,
            ).json()
            fixture = record(
                "entry_create",
                lambda: request(
                    "POST",
                    "/api/entries",
                    json={
                        "folder_id": folder["id"],
                        "kind": "th",
                        "title": "Performance fixture",
                        "tag": "performance-fixture",
                        "content": "For $x=1$, $x^2=1$.",
                        "review_enabled": False,
                    },
                ),
                1,
            ).json()
            item_url = f"/api/entries/{fixture['id']}"
            original = fixture["formulations"][0]
            sequence = [0]

            def edit_title():
                sequence[0] += 1
                return request(
                    "PATCH", item_url, json={"title": f"Performance fixture {sequence[0]}"}
                )

            record("entry_title_save", edit_title, 3)

            def edit_content():
                sequence[0] += 1
                return request(
                    "PUT",
                    f"{item_url}/content/{original['id']}",
                    json={"content": f"For $x=1$, $x^2=1$.\n\nFixture edit {sequence[0]}."},
                )

            record("content_save", edit_content, 3)
            record(
                "content_unchanged_save",
                lambda: request(
                    "PUT",
                    f"{item_url}/content/{original['id']}",
                    json={"content": f"For $x=1$, $x^2=1$.\n\nFixture edit {sequence[0]}."},
                ),
                3,
            )
            record("search_after_save", lambda: request("GET", "/api/search?q=fixture"), 1)
            record("linked_items_after_save", lambda: request("GET", f"{item_url}/linked-items"), 1)
            variant = record(
                "formulation_add",
                lambda: request(
                    "POST",
                    item_url + "/formulations",
                    json={"label": "Equivalent", "subtag": "equivalent", "content": "$1^2=1$."},
                ),
                1,
            ).json()
            record(
                "supplement_add",
                lambda: request(
                    "POST",
                    item_url + "/supplements",
                    json={"kind": "pf", "label": "Proof", "main": True, "content": "$1\\cdot1=1$."},
                ),
                1,
            )
            variant_id = variant["formulations"][-1]["id"]
            record(
                "variant_promote",
                lambda: request("PATCH", f"{item_url}/variants/{variant_id}", json={"main": True}),
                1,
            )
            record(
                "entry_tag_rename",
                lambda: request("PATCH", item_url, json={"tag": "performance-renamed"}),
                1,
            )
            record(
                "folder_rename",
                lambda: request(
                    "PATCH",
                    f"/api/folders/{folder['id']}",
                    json={"name": "Renamed fixture", "slug": "performance-renamed"},
                ),
                1,
            )
            record(
                "entry_move",
                lambda: request(
                    "POST",
                    f"/api/items/entry/{fixture['id']}/move",
                    json={"destination_folder_id": folder_id, "index": 0},
                ),
                1,
            )
            request(
                "POST",
                f"/api/items/entry/{fixture['id']}/move",
                json={"destination_folder_id": folder["id"], "index": 0},
            )
            record(
                "folder_move",
                lambda: request(
                    "POST",
                    f"/api/items/folder/{folder['id']}/move",
                    json={"destination_folder_id": folder_id, "index": 0},
                ),
                1,
            )
            neighbor = request(
                "POST",
                "/api/entries",
                json={
                    "folder_id": folder["id"],
                    "kind": "df",
                    "title": "Reorder fixture",
                    "tag": "reorder-fixture",
                    "content": "Benchmark fixture.",
                    "review_enabled": False,
                },
            ).json()
            record(
                "entry_reorder",
                lambda: request(
                    "PUT",
                    f"/api/folders/{folder['id']}/order",
                    json={"entry_ids": [neighbor["id"], fixture["id"]]},
                ),
                1,
            )
            request("DELETE", f"/api/entries/{neighbor['id']}")
            record(
                "macros_save",
                lambda: request("PUT", "/api/macros", json={"macros": snapshot["macros"]}),
                1,
            )
            preview = io.BytesIO()
            Image.new("RGB", (128, 128), "white").save(preview, format="PNG")
            image = record(
                "image_upload",
                lambda: request(
                    "POST",
                    item_url + "/images",
                    files={"image": ("fixture.png", preview.getvalue(), "image/png")},
                ),
                1,
            ).json()
            record(
                "image_read", lambda: request("GET", image["markdown"].split("(")[1].split("#")[0])
            )
            record(
                "drawing_save",
                lambda: request(
                    "POST",
                    item_url + "/diagrams/excalidraw",
                    data={"scene": json.dumps({"type": "excalidraw", "elements": []})},
                    files={"preview": ("fixture.png", preview.getvalue(), "image/png")},
                ),
                1,
            )
            record(
                "commutative_save",
                lambda: request(
                    "POST",
                    item_url + "/diagrams/commutative",
                    json={"nodes": [{"id": "a", "label": "A", "row": 0, "column": 0}]},
                ),
                1,
            )
            record(
                "drawing_templates_save",
                lambda: request("PUT", "/api/excalidraw/library", json={"libraryItems": []}),
                1,
            )
            request("PATCH", item_url, json={"review_enabled": True})
            card = fixture["id"] + "::statement"
            for _ in range(3):
                attempt = record(
                    "review_reveal_" + str(_),
                    lambda: request(
                        "POST",
                        f"/api/review/{card}/reveal",
                        json={
                            "attempt": "Synthetic benchmark",
                            "confidence": 2,
                            "elapsed_ms": 0,
                            "overt": True,
                        },
                    ),
                    1,
                ).json()
                record(
                    "review_grade_" + str(_),
                    lambda attempt=attempt: request(
                        "POST",
                        f"/api/review/{card}/grade",
                        json={"attempt_id": attempt["attempt_id"], "grade": 2},
                    ),
                    1,
                )
            if args.pdf:
                response = record(
                    "pdf_export",
                    lambda: request(
                        "POST",
                        "/api/export/pdf",
                        json={"folder_id": folder["id"], "title": "Performance verification"},
                    ),
                    1,
                )
                args.output.with_suffix(".pdf").write_bytes(response.content)
            record("entry_delete", lambda: request("DELETE", item_url), 1)
            record("folder_delete", lambda: request("DELETE", f"/api/folders/{folder['id']}"), 1)
            results["validated_copy"] = store.check_data()

        # Exercise password verification/session revocation using an ephemeral
        # benchmark credential, never the owner's configuration or sessions.
        server_settings = replace(settings, password_hash=make_password_hash("benchmark-fixture"))
        server_app = app_module.create_app(server_settings, local_mode=False)
        with TestClient(
            server_app, base_url="http://127.0.0.1", client=("127.0.0.1", 50001)
        ) as auth_client:
            assert auth_client.get("/api/bootstrap").status_code == 401
            for index in range(3):
                login = record(
                    "login_" + str(index),
                    lambda: auth_client.post(
                        "/api/login",
                        json={"password": "benchmark-fixture"},
                        headers={"origin": "http://127.0.0.1"},
                    ),
                    1,
                )
                login.raise_for_status()
                token = login.json()["csrf"]
                logout = record(
                    "logout_" + str(index),
                    lambda token=token: auth_client.post(
                        "/api/logout", headers={"origin": "http://127.0.0.1", "x-study-csrf": token}
                    ),
                    1,
                )
                logout.raise_for_status()
                assert auth_client.get("/api/bootstrap").status_code == 401
    args.output.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
