from __future__ import annotations

import os
import subprocess
import tempfile
import threading
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


class GitError(RuntimeError):
    pass


class GitRepository:
    """Fixed, non-shell Git operations exposed by the application."""

    def __init__(self, root: Path, data_dir: Path, mutation_lock: Any | None = None):
        self.root = root.resolve()
        self.data_dir = data_dir.resolve()
        try:
            relative = self.data_dir.relative_to(self.root)
        except ValueError as exc:
            raise GitError("data_dir must be inside the associated Git repository") from exc
        if not relative.parts:
            raise GitError("data_dir cannot be the Git repository root")
        self.data_relative = relative.as_posix()
        runtime = f"{self.data_relative}/runtime"
        # Defense in depth: .gitignore keeps these untracked in the normal case,
        # while explicit pathspecs keep a force-tracked credential or transient
        # file out of an in-app content commit.
        self._protected_pathspecs = (
            f"{runtime}/sessions.sqlite3",
            f"{runtime}/sessions.sqlite3-*",
            f"{runtime}/*.tmp",
            f"{runtime}/export-*.pdf",
        )
        self._lock = mutation_lock or threading.RLock()

    def _run(
        self,
        args: list[str],
        timeout: int = 45,
        check: bool = True,
        environment_overrides: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = {
            **os.environ,
            "GIT_TERMINAL_PROMPT": "0",
            **(environment_overrides or {}),
        }
        try:
            result = subprocess.run(
                ["git", "-C", str(self.root), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=environment,
                check=False,
            )
        except FileNotFoundError as exc:
            raise GitError("Git is not installed or is not on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise GitError("Git operation timed out") from exc
        if check and result.returncode != 0:
            message = (result.stderr or result.stdout or "Git command failed").strip()
            raise GitError(message)
        return result

    def _repository_problem(self) -> str | None:
        result = self._run(["rev-parse", "--show-toplevel"], check=False)
        if result.returncode != 0:
            return (result.stderr or "the application directory is not a Git repository").strip()
        try:
            repository_root = Path(result.stdout.strip()).resolve()
        except (OSError, ValueError):
            return "Git returned an invalid repository root"
        if repository_root != self.root:
            return "the Study application directory must be the Git repository root"
        return None

    def _ensure_repository(self) -> None:
        problem = self._repository_problem()
        if problem:
            raise GitError(problem)

    def _ensure_no_operation_in_progress(self) -> None:
        result = self._run(["rev-parse", "--absolute-git-dir"])
        git_dir = Path(result.stdout.strip())
        markers = (
            git_dir / "MERGE_HEAD",
            git_dir / "CHERRY_PICK_HEAD",
            git_dir / "REVERT_HEAD",
            git_dir / "rebase-apply",
            git_dir / "rebase-merge",
        )
        if any(marker.exists() for marker in markers):
            raise GitError(
                "Git operation refused while a merge, rebase, or cherry-pick is in progress"
            )

    def _content_pathspecs(self) -> list[str]:
        return [f":(top,literal){self.data_relative}"]

    def _protected_tree_pathspecs(self) -> list[str]:
        return [f":(top,glob){path}" for path in self._protected_pathspecs]

    @staticmethod
    def _under(path: str, directory: str) -> bool:
        return path == directory or path.startswith(directory + "/")

    @staticmethod
    def _display_remote(value: str) -> str:
        """Return a useful remote identifier without URL credentials or query secrets."""
        if "://" in value:
            parsed = urlsplit(value)
            if parsed.hostname:
                host = parsed.hostname
                if ":" in host:
                    host = f"[{host}]"
                try:
                    port = parsed.port
                except ValueError:
                    port = None
                if port is not None:
                    host += f":{port}"
                return urlunsplit((parsed.scheme, host, parsed.path, "", ""))
        if "@" in value:
            prefix, suffix = value.split("@", 1)
            if ":" in suffix and "/" not in prefix:
                return suffix
        return value

    def _is_authored_content(self, path: str) -> bool:
        runtime_root = f"{self.data_relative}/runtime"
        runtime = f"{runtime_root}/"
        if not self._under(path, self.data_relative):
            return False
        if path == runtime_root:
            return False
        if not path.startswith(runtime):
            return True
        name = path.removeprefix(runtime)
        first_component = name.split("/", 1)[0]
        return not (
            first_component == "sessions.sqlite3"
            or first_component.startswith("sessions.sqlite3-")
            or first_component.endswith(".tmp")
            or (
                first_component.startswith("export-")
                and first_component.endswith(".pdf")
            )
        )

    def _protected_paths_in_tree(self, revision: str) -> list[str]:
        result = self._run(
            ["ls-tree", "-r", "--name-only", "-z", revision, "--", f"{self.data_relative}/runtime"],
        )
        return sorted(
            path
            for path in result.stdout.split("\0")
            if path and not self._is_authored_content(path)
        )

    def _protected_paths_in_index(self, environment_overrides: dict[str, str]) -> list[str]:
        result = self._run(
            ["ls-files", "-z", "--", f"{self.data_relative}/runtime"],
            environment_overrides=environment_overrides,
        )
        return sorted(
            path
            for path in result.stdout.split("\0")
            if path and not self._is_authored_content(path)
        )

    def _validate_candidate_checkout(
        self, revision: str, validate_data: Callable[[Path], None]
    ) -> None:
        """Validate the exact fetched checkout, including configured smudge filters."""
        with tempfile.TemporaryDirectory(prefix="study-pull-") as temporary_root:
            temporary = Path(temporary_root)
            checkout = temporary / "checkout"
            empty_hooks = temporary / "hooks"
            empty_hooks.mkdir(mode=0o700)
            self._run(
                [
                    "-c",
                    f"core.hooksPath={empty_hooks}",
                    "worktree",
                    "add",
                    "--detach",
                    str(checkout),
                    revision,
                ],
                timeout=120,
            )
            try:
                candidate_data = checkout.joinpath(*Path(self.data_relative).parts)
                if candidate_data.is_symlink() or not candidate_data.is_dir():
                    raise GitError("pull refused: upstream does not contain a safe data directory")
                validate_data(candidate_data)
            except GitError:
                raise
            except Exception as exc:
                raise GitError(f"pull refused: upstream Study data is invalid: {exc}") from exc
            finally:
                removed = self._run(
                    ["worktree", "remove", "--force", str(checkout)],
                    timeout=120,
                    check=False,
                )
                if removed.returncode != 0:
                    self._run(["worktree", "prune"], check=False)

    def status(self) -> dict[str, Any]:
        try:
            problem = self._repository_problem()
        except GitError as exc:
            return {"available": False, "message": str(exc)}
        if problem:
            return {"available": False, "message": problem}

        branch = (
            self._run(["branch", "--show-current"], check=False).stdout.strip() or "detached HEAD"
        )
        status_result = self._run(
            ["status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all"],
            check=False,
        )
        if status_result.returncode != 0:
            return {
                "available": False,
                "message": (status_result.stderr or "Git status failed").strip(),
            }

        changed: list[dict[str, str]] = []
        data_changed: list[dict[str, str]] = []
        for record in status_result.stdout.split("\0"):
            if len(record) < 4:
                continue
            item = {"status": record[:2], "path": record[3:]}
            changed.append(item)
            if self._is_authored_content(item["path"]):
                data_changed.append(item)

        upstream_result = self._run(
            ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], check=False
        )
        upstream = upstream_result.stdout.strip() if upstream_result.returncode == 0 else ""
        remote_name = ""
        remote = ""
        if branch != "detached HEAD":
            remote_name = self._run(
                ["config", "--get", f"branch.{branch}.remote"], check=False
            ).stdout.strip()
            if remote_name and remote_name != ".":
                remote = self._run(
                    ["remote", "get-url", "--", remote_name], check=False
                ).stdout.strip()
                remote = self._display_remote(remote)

        ahead = behind = None
        divergence = self._run(
            ["rev-list", "--left-right", "--count", "@{upstream}...HEAD"], check=False
        )
        if divergence.returncode == 0:
            pieces = divergence.stdout.split()
            if len(pieces) == 2:
                behind, ahead = (int(pieces[0]), int(pieces[1]))
        return {
            "available": True,
            "branch": branch,
            "remote": remote or None,
            "upstream": upstream or None,
            "dirty": bool(changed),
            "content_dirty": bool(data_changed),
            "changed": changed,
            "content_changed": data_changed,
            "ahead": ahead,
            "behind": behind,
        }

    def ensure_no_operation_in_progress(self) -> None:
        """Fail before an out-of-band data rewrite during an unfinished Git operation."""
        with self._lock:
            self._ensure_repository()
            self._ensure_no_operation_in_progress()

    def commit_content(self, message: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_repository()
            self._ensure_no_operation_in_progress()
            before = self.status()
            if not before.get("content_dirty"):
                raise GitError("there are no authored-content changes to commit")

            pathspecs = self._content_pathspecs()
            git_dir = Path(self._run(["rev-parse", "--absolute-git-dir"]).stdout.strip())
            temporary_index = git_dir / f"study-index-{uuid.uuid4().hex}"
            empty_hooks = git_dir / f"study-hooks-{uuid.uuid4().hex}"
            isolated = {"GIT_INDEX_FILE": str(temporary_index)}
            old_revision = ""
            new_revision = ""
            try:
                empty_hooks.mkdir(mode=0o700)
                has_head = self._run(["rev-parse", "--verify", "HEAD"], check=False)
                if has_head.returncode == 0:
                    old_revision = has_head.stdout.strip()
                self._run(
                    ["read-tree", "HEAD"] if has_head.returncode == 0 else ["read-tree", "--empty"],
                    environment_overrides=isolated,
                )
                self._run(["add", "-A", "--", *pathspecs], environment_overrides=isolated)
                self._run(
                    [
                        "rm",
                        "-r",
                        "--cached",
                        "--ignore-unmatch",
                        "--",
                        *self._protected_tree_pathspecs(),
                    ],
                    environment_overrides=isolated,
                )
                protected = self._protected_paths_in_index(isolated)
                if protected:
                    raise GitError(
                        "content commit refused: protected runtime path could not be excluded: "
                        + ", ".join(protected[:3])
                    )
                staged = self._run(
                    ["diff", "--cached", "--quiet", "--", *pathspecs],
                    check=False,
                    environment_overrides=isolated,
                )
                if staged.returncode == 0:
                    raise GitError("there are no authored-content changes to commit")
                if staged.returncode != 1:
                    raise GitError(
                        (staged.stderr or "Git could not inspect staged content").strip()
                    )
                result = self._run(
                    ["-c", f"core.hooksPath={empty_hooks}", "commit", "-m", message],
                    timeout=90,
                    environment_overrides=isolated,
                )
                new_revision = self._run(["rev-parse", "HEAD"]).stdout.strip()
            finally:
                temporary_index.unlink(missing_ok=True)
                Path(f"{temporary_index}.lock").unlink(missing_ok=True)
                try:
                    empty_hooks.rmdir()
                except FileNotFoundError:
                    pass

            # The isolated index keeps unrelated staged work untouched. Align
            # only authored data in the real index with the new commit.
            try:
                self._run(["reset", "-q", "HEAD", "--", *pathspecs])
            except GitError as cleanup_error:
                if old_revision:
                    rollback = self._run(
                        ["update-ref", "-m", "Study commit rollback", "HEAD", old_revision, new_revision],
                        check=False,
                    )
                else:
                    head_ref = self._run(["symbolic-ref", "-q", "HEAD"], check=False).stdout.strip()
                    rollback = (
                        self._run(["update-ref", "-d", head_ref, new_revision], check=False)
                        if head_ref
                        else subprocess.CompletedProcess([], 1, "", "HEAD is not symbolic")
                    )
                if rollback.returncode == 0:
                    raise GitError(
                        "content commit aborted because the real Git index could not be updated; "
                        f"HEAD was restored: {cleanup_error}"
                    ) from cleanup_error
                raise GitError(
                    f"content commit {new_revision[:12]} succeeded, but the real Git index could "
                    f"not be updated or safely rolled back: {cleanup_error}"
                ) from cleanup_error
            revision = new_revision[:12]
            return {
                "revision": revision,
                "summary": result.stdout.strip(),
                "status": self.status(),
            }

    def pull_fast_forward(
        self, validate_data: Callable[[Path], None] | None = None
    ) -> dict[str, Any]:
        with self._lock:
            self._ensure_repository()
            self._ensure_no_operation_in_progress()
            status = self.status()
            if status.get("dirty"):
                raise GitError("pull refused: commit or otherwise resolve local changes first")
            if not status.get("upstream"):
                raise GitError("pull refused: the current branch has no upstream")
            fetch = self._run(["fetch", "--no-recurse-submodules"], timeout=120)
            upstream_revision = self._run(["rev-parse", "@{upstream}"]).stdout.strip()
            protected = sorted(
                set(self._protected_paths_in_tree("HEAD"))
                | set(self._protected_paths_in_tree(upstream_revision))
            )
            if protected:
                shown = ", ".join(protected[:3])
                raise GitError(
                    "pull refused: upstream tracks protected session or transient files: " + shown
                )
            if validate_data is not None:
                self._validate_candidate_checkout(upstream_revision, validate_data)
            # Fetch does not touch the worktree, but recheck before applying the
            # exact revision in case another process changed local files.
            if self.status().get("dirty"):
                raise GitError("pull refused: local changes appeared while fetching")
            result = self._run(["merge", "--ff-only", upstream_revision], timeout=120)
            return {
                "summary": result.stdout.strip() or fetch.stdout.strip() or result.stderr.strip(),
                "status": self.status(),
            }
