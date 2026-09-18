"""Measure structural HTTP writes on a disposable copy; never edit the source library."""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import socket
import statistics
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source_root.resolve()))
    import uvicorn

    import study_app.app as app_module
    from study_app.config import Settings
    from study_app.git_ops import GitRepository

    report = {"method": "HTTP over loopback, gzip, disposable data copy, three samples", "actions": {}}

    def record(name, samples):
        report["actions"][name] = {
            "median_ms": round(statistics.median(samples), 2),
            "samples_ms": [round(value, 2) for value in samples],
        }
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(name, json.dumps(report["actions"][name]), flush=True)

    with tempfile.TemporaryDirectory(prefix="study-structure-benchmark-") as temporary:
        root = Path(temporary)
        shutil.copytree(args.data_root, root / "data", ignore=shutil.ignore_patterns("runtime", "exports"))
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        settings = Settings(root, port, "127.0.0.1", ("127.0.0.1",), "", 30, False, 12, 32)
        with patch.object(app_module, "GitRepository", lambda *unused: GitRepository(args.data_root.parent, args.data_root)):
            app = app_module.create_app(settings, True)
        report["library"] = app.state.store.check_data()
        server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        deadline = time.monotonic() + 60
        while not server.started:
            if not thread.is_alive() or time.monotonic() > deadline:
                raise RuntimeError("benchmark server did not start")
            time.sleep(0.05)
        base = f"http://127.0.0.1:{port}"

        def request(method, path, payload=None):
            req = urllib.request.Request(
                base + path, method=method,
                data=None if payload is None else json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Origin": base,
                         "X-Study-CSRF": "local", "Accept-Encoding": "gzip"},
            )
            begin = time.perf_counter()
            with urllib.request.urlopen(req, timeout=90) as response:
                data = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
            elapsed = (time.perf_counter() - begin) * 1000
            return (json.loads(data) if data else None), elapsed

        try:
            folders, entries, samples = [], [], []
            for i in range(3):
                item, elapsed = request("POST", "/api/folders", {"name": f"Timing {i}", "slug": f"timing-fixture-{i}"})
                folders.append(item)
                samples.append(elapsed)
            record("folder_create", samples)
            samples = []
            for i in range(3):
                item, elapsed = request("POST", "/api/entries", {
                    "folder_id": folders[0]["id"], "kind": "df", "title": f"Timing {i}",
                    "tag": f"timing-{i}", "content": "Temporary fixture.", "review_enabled": False,
                })
                entries.append(item)
                samples.append(elapsed)
            record("entry_create", samples)
            samples = []
            entry = entries[0]
            for i in range(3):
                _, elapsed = request("PUT", f"/api/entries/{entry['id']}/content/{entry['formulations'][0]['id']}", {"content": f"Temporary edit {i}."})
                samples.append(elapsed)
            record("content_save", samples)
            samples, refresh = [], []
            for i in range(3):
                _, elapsed = request("POST", f"/api/items/entry/{entry['id']}/move?include_library=false", {
                    "destination_folder_id": folders[1 if i % 2 == 0 else 0]["id"], "index": 0,
                })
                samples.append(elapsed)
                _, elapsed = request("GET", "/api/bootstrap?compact=true&navigation=true")
                refresh.append(elapsed)
            record("entry_move", samples)
            record("navigation_after_move", refresh)
            samples = []
            for i in range(3):
                _, elapsed = request("PATCH", f"/api/folders/{folders[0]['id']}", {"name": f"Renamed {i}", "slug": f"renamed-fixture-{i}"})
                samples.append(elapsed)
            record("populated_folder_rename", samples)
            samples = []
            for i in range(3):
                _, elapsed = request("POST", f"/api/items/folder/{folders[0]['id']}/move?include_library=false", {
                    "destination_folder_id": folders[1 + i % 2]["id"], "index": 0,
                })
                samples.append(elapsed)
            record("populated_folder_move", samples)
            report["validated_copy"] = app.state.store.check_data()
            args.output.write_text(json.dumps(report, indent=2) + "\n")
        finally:
            server.should_exit = True
            thread.join(timeout=30)
            sock.close()


if __name__ == "__main__":
    main()
