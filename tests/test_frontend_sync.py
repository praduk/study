from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class SyncSandbox:
    script: Path
    bundle: Path
    remote: Path
    log: Path
    environment: dict[str, str]

    def run(self, *, fail_transfer: bool = False) -> subprocess.CompletedProcess[str]:
        environment = dict(self.environment)
        if fail_transfer:
            environment["STUDY_TEST_FAIL_TRANSFER"] = "1"
        return subprocess.run(
            ["bash", str(self.script)],
            cwd=self.script.parent.parent,
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def calls(self) -> list[dict]:
        return [json.loads(line) for line in self.log.read_text().splitlines()]


@pytest.fixture
def sync_sandbox(tmp_path: Path) -> SyncSandbox:
    checkout = tmp_path / "checkout with spaces"
    bundle = checkout / "study_app" / "web"
    contents = {
        "index.html": (
            '<link rel="stylesheet" href="/_next/static/css/site.css?v=1#style">'
            '<script type="module" src="/_next/static/chunks/app.js"></script>'
            '<link rel="icon" href="/favicon.svg">'
        ),
        "_next/static/chunks/app.js": 'import("./lazy.js");',
        "_next/static/chunks/lazy.js": "export default 1;",
        "_next/static/css/site.css": "body { color: black; }",
        "vendor/mathjax/tex-svg.js": "/* bundled vendor */",
        "favicon.svg": "<svg></svg>",
    }
    for relative, content in contents.items():
        path = bundle / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    script = checkout / "sync.sh"
    shutil.copyfile(Path(__file__).resolve().parents[1] / "sync.sh", script)

    remote = tmp_path / "remote" / "git" / "study" / "study_app" / "web"
    remote.mkdir(parents=True)
    (remote / "index.html").write_text("old page", encoding="utf-8")
    (remote / "old-hashed.js").write_text("old asset", encoding="utf-8")
    log = tmp_path / "ssh.jsonl"
    log.write_text("", encoding="utf-8")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    fake_ssh = binaries / "ssh"
    fake_ssh.write_text(
        f"#!{sys.executable}\n"
        """import json
import os
import subprocess
import sys
from pathlib import Path

assert len(sys.argv) == 3 and sys.argv[1] == 'pradu.us', sys.argv
target = Path(os.environ['STUDY_TEST_REMOTE'])
command = sys.argv[2]
remote_path = '$HOME/git/study/study_app/web'
assert remote_path in command, command
log = Path(os.environ['STUDY_TEST_SSH_LOG'])
prior = log.read_text().splitlines()
with log.open('a') as stream:
    stream.write(json.dumps({
        'index_before': (target / 'index.html').read_text(),
        'files_before': sorted(str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()),
    }) + '\\n')
payload = sys.stdin.buffer.read()
if not prior and os.environ.get('STUDY_TEST_FAIL_TRANSFER'):
    sys.exit(79)
# Substitute only the remote destination; never invoke a real SSH connection.
result = subprocess.run(
    ['/bin/bash', '-c', command.replace(remote_path, str(target))], input=payload, check=False,
)
sys.exit(result.returncode)
""",
        encoding="utf-8",
    )
    fake_ssh.chmod(0o755)
    # A working upload must not depend on rsync being installed.
    fake_rsync = binaries / "rsync"
    fake_rsync.write_text("#!/bin/sh\nexit 78\n", encoding="utf-8")
    fake_rsync.chmod(0o755)
    environment = dict(os.environ)
    environment.update({
        "PATH": f"{binaries}{os.pathsep}{environment['PATH']}",
        "STUDY_TEST_REMOTE": str(remote),
        "STUDY_TEST_SSH_LOG": str(log),
    })
    return SyncSandbox(script, bundle, remote, log, environment)


@pytest.mark.parametrize("missing", ["_next/static/chunks/app.js", "_next/static/css/site.css"])
def test_sync_rejects_missing_initial_asset_before_ssh(sync_sandbox: SyncSandbox, missing: str):
    (sync_sandbox.bundle / missing).unlink()

    result = sync_sandbox.run()

    assert result.returncode != 0
    assert "Frontend bundle is incomplete" in result.stderr
    assert missing in result.stderr
    assert sync_sandbox.calls() == []
    assert (sync_sandbox.remote / "index.html").read_text() == "old page"


def test_sync_copies_complete_bundle_and_publishes_index_last_without_rsync(
    sync_sandbox: SyncSandbox,
):
    result = sync_sandbox.run()

    assert result.returncode == 0, result.stderr
    source_files = sorted(path for path in sync_sandbox.bundle.rglob("*") if path.is_file())
    for source in source_files:
        assert (sync_sandbox.remote / source.relative_to(sync_sandbox.bundle)).read_bytes() == (
            source.read_bytes()
        )
    calls = sync_sandbox.calls()
    assert len(calls) == 2
    assert [call["index_before"] for call in calls] == ["old page", "old page"]
    assert "_next/static/chunks/app.js" not in calls[0]["files_before"]
    assert all(
        str(source.relative_to(sync_sandbox.bundle)) in calls[1]["files_before"]
        for source in source_files if source.name != "index.html"
    )
    assert (sync_sandbox.remote / "old-hashed.js").read_text() == "old asset"
    assert not list(sync_sandbox.remote.glob(".index.*"))


def test_sync_failed_asset_transfer_keeps_published_index(sync_sandbox: SyncSandbox):
    result = sync_sandbox.run(fail_transfer=True)

    assert result.returncode == 79
    assert len(sync_sandbox.calls()) == 1
    assert (sync_sandbox.remote / "index.html").read_text() == "old page"
    assert not list(sync_sandbox.remote.glob(".index.*"))
