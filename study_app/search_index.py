from __future__ import annotations

import re
import unicodedata
from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

REFERENCE_RE = re.compile(r"^[a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)*$")
SPACE_RE = re.compile(r"\s+")


class SearchIndexError(ValueError):
    pass


def normalize_search_text(value: str) -> str:
    """Normalize without changing the source retained by Study."""
    return SPACE_RE.sub(" ", unicodedata.normalize("NFKC", value).casefold()).strip()


def normalize_reference(value: str) -> str:
    reference = value.strip().removeprefix("@")
    reference = reference.casefold()
    if not REFERENCE_RE.fullmatch(reference):
        raise SearchIndexError(
            "a reference must be @ followed by lowercase tag segments separated by colons"
        )
    return reference


def _trigrams(value: str) -> frozenset[str]:
    if len(value) < 3:
        return frozenset()
    return frozenset(value[index : index + 3] for index in range(len(value) - 2))


@dataclass(frozen=True)
class ReferenceTarget:
    key: str
    entry_id: str
    variant_id: str
    folder_id: str
    folder_namespace: str
    kind: str
    title: str
    raw_tag: str
    local_reference: str
    canonical_tag: str
    header: str
    target_type: str
    label: str
    main: bool
    content: str
    main_variant_id: str
    main_label: str
    main_canonical_tag: str
    main_content: str
    authored_order: int

    def compact(self, resolution_status: str | None = None) -> dict[str, Any]:
        value: dict[str, Any] = {
            "entry_id": self.entry_id,
            "variant_id": self.variant_id,
            "folder_id": self.folder_id,
            "folder_namespace": self.folder_namespace,
            "kind": self.kind,
            "title": self.title,
            "tag": self.raw_tag,
            "reference_tag": self.local_reference,
            "canonical_tag": self.canonical_tag,
            "header": self.header,
            "target_type": self.target_type,
            "label": self.label,
            "main": self.main,
        }
        if resolution_status is not None:
            value["resolution_status"] = resolution_status
        return value

    def preview(self) -> dict[str, Any]:
        return {
            **self.compact(),
            "content": self.content,
            "main_formulation": {
                "id": self.main_variant_id,
                "label": self.main_label,
                "canonical_tag": self.main_canonical_tag,
                "content": self.main_content,
            },
        }


@dataclass(frozen=True)
class EntryDocument:
    entry_id: str
    folder_id: str
    folder_namespace: str
    kind: str
    title: str
    raw_tag: str
    canonical_tag: str
    header: str
    metadata_text: str
    search_text: str
    normalized_title: str
    normalized_raw_tag: str
    normalized_canonical_tag: str
    authored_order: int


@dataclass(frozen=True)
class TargetDocument:
    target: ReferenceTarget
    metadata_text: str
    search_text: str
    normalized_title: str
    normalized_local_reference: str
    normalized_canonical_tag: str


@dataclass(frozen=True)
class VisibleReference:
    local_reference: str
    matched_folder_id: str
    scope_distance: int
    precedence: int
    resolution: str
    target_keys: tuple[str, ...]


class LibrarySearchIndex:
    """Immutable structural and trigram indexes for one library snapshot."""

    def __init__(
        self,
        library: dict[str, Any],
        folder_namespaces: dict[str, str],
        content_by_path: dict[str, str],
    ):
        self.folder_by_id = {folder["id"]: folder for folder in library["folders"]}
        self.ancestry_by_folder = {
            folder_id: self._ancestry(folder_id) for folder_id in self.folder_by_id
        }
        (
            self._folder_rank,
            self._subtree_end,
            self._root_by_folder,
        ) = self._folder_layout()
        self.targets: dict[str, ReferenceTarget] = {}
        self.entry_documents: dict[str, EntryDocument] = {}
        self.target_documents: dict[str, TargetDocument] = {}
        scope_buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
        canonical_buckets: dict[str, list[str]] = defaultdict(list)

        entries = sorted(
            library["entries"],
            key=lambda entry: (
                self._folder_rank.get(entry["folder_id"], len(self._folder_rank)),
                int(entry.get("order", 0)),
                entry.get("title", "").casefold(),
                entry["id"],
            ),
        )
        for entry_order, entry in enumerate(entries):
            namespace = folder_namespaces[entry["folder_id"]]
            canonical_entry = f"{namespace}:{entry['kind']}:{entry['tag']}"
            formulations = entry.get("formulations", [])
            main_formulation = next(
                (variant for variant in formulations if variant.get("main")),
                formulations[0] if formulations else None,
            )
            if main_formulation is None:
                continue
            main_content = content_by_path.get(main_formulation["file"], "")
            main_canonical = canonical_entry + (
                f":{main_formulation['subtag']}" if main_formulation.get("subtag") else ""
            )
            all_content: list[str] = []
            labels: list[str] = []
            variants: list[tuple[dict[str, Any], str, str, str]] = []
            for formulation in formulations:
                subtag = formulation.get("subtag")
                local_reference = entry["tag"] + (f":{subtag}" if subtag else "")
                canonical = canonical_entry + (f":{subtag}" if subtag else "")
                variants.append((formulation, local_reference, canonical, "formulation"))
            for supplement in entry.get("supplements", []):
                supplement_kind = supplement["kind"]
                subtag = supplement.get("subtag")
                local_reference = f"{entry['tag']}:{supplement_kind}" + (
                    f":{subtag}" if subtag else ""
                )
                canonical = f"{canonical_entry}:{supplement_kind}" + (
                    f":{subtag}" if subtag else ""
                )
                variants.append((supplement, local_reference, canonical, "supplement"))

            for variant_order, (variant, local_reference, canonical, target_type) in enumerate(
                variants
            ):
                content = content_by_path.get(variant["file"], "")
                all_content.append(content)
                label = variant.get("label", "")
                labels.extend((label, variant.get("subtag") or ""))
                target = ReferenceTarget(
                    key=f"{entry['id']}::{variant['id']}",
                    entry_id=entry["id"],
                    variant_id=variant["id"],
                    folder_id=entry["folder_id"],
                    folder_namespace=namespace,
                    kind=entry["kind"],
                    title=entry["title"],
                    raw_tag=entry["tag"],
                    local_reference=local_reference,
                    canonical_tag=canonical,
                    header=entry.get("header", ""),
                    target_type=target_type,
                    label=label,
                    main=bool(variant.get("main")),
                    content=content,
                    main_variant_id=main_formulation["id"],
                    main_label=main_formulation.get("label", ""),
                    main_canonical_tag=main_canonical,
                    main_content=main_content,
                    authored_order=entry_order * 1000 + variant_order,
                )
                self.targets[target.key] = target
                scope_buckets[(target.folder_id, target.local_reference)].append(target.key)
                canonical_buckets[target.canonical_tag].append(target.key)
                target_metadata = normalize_search_text(
                    f"{target.title} {target.raw_tag} {target.local_reference} "
                    f"{target.canonical_tag} {target.header} {target.label}"
                )
                self.target_documents[target.key] = TargetDocument(
                    target=target,
                    metadata_text=target_metadata,
                    search_text=normalize_search_text(f"{target_metadata} {target.content}"),
                    normalized_title=normalize_search_text(target.title),
                    normalized_local_reference=normalize_search_text(target.local_reference),
                    normalized_canonical_tag=normalize_search_text(target.canonical_tag),
                )

            metadata = normalize_search_text(
                " ".join(
                    (
                        entry["title"],
                        entry["tag"],
                        canonical_entry,
                        entry.get("header", ""),
                        *labels,
                    )
                )
            )
            self.entry_documents[entry["id"]] = EntryDocument(
                entry_id=entry["id"],
                folder_id=entry["folder_id"],
                folder_namespace=namespace,
                kind=entry["kind"],
                title=entry["title"],
                raw_tag=entry["tag"],
                canonical_tag=canonical_entry,
                header=entry.get("header", ""),
                metadata_text=metadata,
                search_text=normalize_search_text(" ".join((metadata, *all_content))),
                normalized_title=normalize_search_text(entry["title"]),
                normalized_raw_tag=normalize_search_text(entry["tag"]),
                normalized_canonical_tag=normalize_search_text(canonical_entry),
                authored_order=entry_order,
            )

        self.scope_buckets = {
            key: tuple(sorted(values, key=self._target_order))
            for key, values in scope_buckets.items()
        }
        references_by_scope: dict[str, list[str]] = defaultdict(list)
        for scope_id, reference in self.scope_buckets:
            references_by_scope[scope_id].append(reference)
        self.references_by_scope = {
            scope_id: tuple(
                sorted(
                    references,
                    key=lambda reference: (
                        self._target_order(self.scope_buckets[(scope_id, reference)][0]),
                        reference,
                    ),
                )
            )
            for scope_id, references in references_by_scope.items()
        }
        self.canonical_buckets = {
            key: tuple(sorted(values, key=self._target_order))
            for key, values in canonical_buckets.items()
        }
        reference_rank_targets: dict[str, list[tuple[int, str]]] = defaultdict(list)
        for (target_folder_id, reference), keys in self.scope_buckets.items():
            rank = self._folder_rank[target_folder_id]
            reference_rank_targets[reference].extend((rank, key) for key in keys)
        self.reference_rank_targets = {
            reference: tuple(sorted(rows))
            for reference, rows in reference_rank_targets.items()
        }
        self.entry_postings = self._build_postings(
            {key: document.search_text for key, document in self.entry_documents.items()}
        )
        self.target_postings = self._build_postings(
            {key: document.search_text for key, document in self.target_documents.items()}
        )
        # These wrappers are per immutable index snapshot. They are thread-safe,
        # bounded, and disappear with the snapshot after any library change.
        self._cached_entry_keys = lru_cache(maxsize=512)(self._ranked_entry_keys)
        self._cached_visible_group = lru_cache(maxsize=8192)(
            self._resolve_visible_group
        )
        self._cached_visible_target_keys = lru_cache(maxsize=512)(
            self._ranked_visible_target_keys
        )

    def _ancestry(self, folder_id: str) -> tuple[str, ...]:
        result: list[str] = []
        seen: set[str] = set()
        current: str | None = folder_id
        while current is not None:
            if current in seen:
                raise SearchIndexError("folder cycle detected")
            seen.add(current)
            folder = self.folder_by_id.get(current)
            if folder is None:
                raise SearchIndexError("folder not found")
            result.append(current)
            current = folder.get("parent_id")
        return tuple(result)

    def _folder_layout(self) -> tuple[dict[str, int], dict[str, int], dict[str, str]]:
        children: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
        for folder in self.folder_by_id.values():
            children[folder.get("parent_id")].append(folder)
        for values in children.values():
            values.sort(
                key=lambda folder: (
                    int(folder.get("order", 0)),
                    folder.get("name", "").casefold(),
                    folder["id"],
                )
            )
        ordered: list[str] = []
        subtree_end: dict[str, int] = {}
        root_by_folder: dict[str, str] = {}
        seen: set[str] = set()
        for root in children.get(None, []):
            root_id = root["id"]
            if root_id in seen:
                continue
            pending: list[tuple[dict[str, Any], bool]] = [(root, False)]
            while pending:
                folder, exiting = pending.pop()
                folder_id = folder["id"]
                if exiting:
                    subtree_end[folder_id] = len(ordered)
                    continue
                if folder_id in seen:
                    continue
                seen.add(folder_id)
                ordered.append(folder_id)
                root_by_folder[folder_id] = root_id
                pending.append((folder, True))
                pending.extend(
                    (child, False)
                    for child in reversed(children.get(folder_id, []))
                    if child["id"] not in seen
                )
        # Invalid cyclic/orphaned input is rejected by library validation. Keep
        # direct index construction bounded too, so malformed graphs cannot loop.
        for folder_id in sorted(set(self.folder_by_id) - seen):
            ordered.append(folder_id)
            subtree_end[folder_id] = len(ordered)
            root_by_folder[folder_id] = folder_id
        return (
            {folder_id: rank for rank, folder_id in enumerate(ordered)},
            subtree_end,
            root_by_folder,
        )

    def _target_order(self, key: str) -> tuple[int, str]:
        target = self.targets[key]
        return (target.authored_order, target.canonical_tag)

    @staticmethod
    def _build_postings(documents: dict[str, str]) -> dict[str, frozenset[str]]:
        postings: dict[str, set[str]] = defaultdict(set)
        for key, text in documents.items():
            for trigram in _trigrams(text):
                postings[trigram].add(key)
        return {trigram: frozenset(keys) for trigram, keys in postings.items()}

    @staticmethod
    def _posting_candidates(
        query: str,
        documents: dict[str, EntryDocument] | dict[str, TargetDocument],
        postings: dict[str, frozenset[str]],
    ) -> set[str]:
        grams = _trigrams(query)
        if not grams:
            return set(documents)
        ordered = sorted((postings.get(gram, frozenset()) for gram in grams), key=len)
        if not ordered or not ordered[0]:
            return set()
        candidates = set(ordered[0])
        for values in ordered[1:]:
            candidates.intersection_update(values)
            if not candidates:
                break
        return candidates

    def _keys_in_rank_ranges(
        self, reference: str, ranges: tuple[tuple[int, int], ...]
    ) -> tuple[str, ...]:
        rows = self.reference_rank_targets.get(reference, ())
        keys: list[str] = []
        for start, end in ranges:
            if start >= end:
                continue
            first = bisect_left(rows, (start, ""))
            last = bisect_left(rows, (end, ""))
            keys.extend(key for _, key in rows[first:last])
        return tuple(sorted(keys, key=self._target_order))

    def _resolve_visible_group(
        self, folder_id: str, reference: str
    ) -> VisibleReference | None:
        branch_start = self._folder_rank[folder_id]
        branch_end = self._subtree_end[folder_id]
        for distance, scope_id in enumerate(self.ancestry_by_folder[folder_id]):
            direct = self.scope_buckets.get((scope_id, reference))
            if direct:
                return VisibleReference(
                    local_reference=reference,
                    matched_folder_id=scope_id,
                    scope_distance=distance,
                    precedence=distance * 2,
                    resolution="scoped",
                    target_keys=direct,
                )

            scope_start = self._folder_rank[scope_id]
            scope_end = self._subtree_end[scope_id]
            if distance == 0:
                ranges = ((scope_start + 1, scope_end),)
            else:
                # The prior branch produced no match. Search only the sibling
                # subtrees newly visible from this ancestor level.
                ranges = (
                    (scope_start + 1, branch_start),
                    (branch_end, scope_end),
                )
            descendant_keys = self._keys_in_rank_ranges(reference, ranges)
            if descendant_keys:
                return VisibleReference(
                    local_reference=reference,
                    matched_folder_id=scope_id,
                    scope_distance=distance,
                    precedence=distance * 2 + 1,
                    resolution="subtree",
                    target_keys=descendant_keys,
                )
            branch_start = scope_start
            branch_end = scope_end
        return None

    @staticmethod
    def _result(
        reference: str,
        resolution: str,
        matched_folder_id: str | None,
        scope_distance: int | None,
        targets: tuple[ReferenceTarget, ...],
    ) -> dict[str, Any]:
        status = "resolved" if len(targets) == 1 else "ambiguous" if targets else "missing"
        return {
            "status": status,
            "reference": f"@{reference}",
            "resolution": resolution,
            "matched_folder_id": matched_folder_id,
            "scope_distance": scope_distance,
            "match": targets[0].preview() if len(targets) == 1 else None,
            "candidates": [target.compact("ambiguous") for target in targets]
            if len(targets) > 1
            else [],
        }

    def resolve(self, folder_id: str, value: str) -> dict[str, Any]:
        if folder_id not in self.folder_by_id:
            raise SearchIndexError("folder not found")
        reference = normalize_reference(value)
        exact = self.canonical_buckets.get(reference)
        if exact is not None:
            targets = tuple(self.targets[key] for key in exact)
            return self._result(reference, "canonical", None, None, targets)
        group = self._cached_visible_group(folder_id, reference)
        if group is not None:
            targets = tuple(self.targets[key] for key in group.target_keys)
            return self._result(
                reference,
                group.resolution,
                group.matched_folder_id,
                group.scope_distance,
                targets,
            )
        return self._result(reference, "scoped", None, None, ())

    @staticmethod
    def _match_rank(
        query: str,
        normalized_title: str,
        normalized_raw_tag: str,
        normalized_canonical_tag: str,
        metadata_text: str,
        search_text: str,
    ) -> tuple[int, int]:
        if query == normalized_canonical_tag:
            category = 0
        elif query == normalized_raw_tag:
            category = 1
        elif query == normalized_title:
            category = 2
        elif normalized_raw_tag.startswith(query):
            category = 3
        elif normalized_title.startswith(query):
            category = 4
        elif normalized_canonical_tag.startswith(query):
            category = 5
        elif query in metadata_text:
            category = 6
        else:
            category = 7
        return category, search_text.find(query)

    def _ranked_entry_keys(self, query: str, folder_id: str | None) -> tuple[str, ...]:
        scope_distance = {
            ancestor_id: distance
            for distance, ancestor_id in enumerate(self.ancestry_by_folder.get(folder_id, ()))
        }
        candidates = self._posting_candidates(query, self.entry_documents, self.entry_postings)
        matches = [
            self.entry_documents[key]
            for key in candidates
            if query in self.entry_documents[key].search_text
        ]
        matches.sort(
            key=lambda document: (
                *self._match_rank(
                    query,
                    document.normalized_title,
                    document.normalized_raw_tag,
                    document.normalized_canonical_tag,
                    document.metadata_text,
                    document.search_text,
                ),
                scope_distance.get(document.folder_id, len(scope_distance) + 1),
                document.authored_order,
                document.canonical_tag,
            )
        )
        return tuple(document.entry_id for document in matches)

    def search_entries(
        self, value: str, limit: int, folder_id: str | None = None
    ) -> list[dict[str, Any]]:
        query = normalize_search_text(value)
        if not query:
            return []
        if folder_id is not None and folder_id not in self.folder_by_id:
            raise SearchIndexError("folder not found")
        keys = self._cached_entry_keys(query, folder_id)
        return [
            {
                "id": document.entry_id,
                "title": document.title,
                "kind": document.kind,
                "tag": document.raw_tag,
                "canonical_tag": document.canonical_tag,
                "folder_id": document.folder_id,
                "folder_namespace": document.folder_namespace,
                "header": document.header,
            }
            for document in (self.entry_documents[key] for key in keys[:limit])
        ]

    def _ranked_visible_target_keys(self, folder_id: str, query: str) -> tuple[str, ...]:
        if query:
            candidates = self._posting_candidates(
                query, self.target_documents, self.target_postings
            )
        else:
            candidates = set(self.target_documents)
        root_id = self._root_by_folder[folder_id]
        root_start = self._folder_rank[root_id]
        root_end = self._subtree_end[root_id]
        rows: list[tuple[tuple[Any, ...], str]] = []
        for key in candidates:
            document = self.target_documents[key]
            if query and query not in document.search_text:
                continue
            target = document.target
            target_rank = self._folder_rank[target.folder_id]
            if not root_start <= target_rank < root_end:
                continue
            group = self._cached_visible_group(folder_id, target.local_reference)
            if group is None or key not in group.target_keys:
                continue
            match_rank = (
                self._match_rank(
                    query,
                    document.normalized_title,
                    document.normalized_local_reference,
                    document.normalized_canonical_tag,
                    document.metadata_text,
                    document.search_text,
                )
                if query
                else (0, 0)
            )
            rows.append(
                (
                    (
                        *match_rank,
                        group.precedence,
                        target.authored_order,
                        target.canonical_tag,
                    ),
                    key,
                )
            )
        rows.sort(key=lambda item: item[0])
        return tuple(key for _, key in rows)

    def search_visible_references(
        self, folder_id: str, value: str, limit: int
    ) -> list[dict[str, Any]]:
        if folder_id not in self.folder_by_id:
            raise SearchIndexError("folder not found")
        query = normalize_search_text(value)
        rows: list[dict[str, Any]] = []
        for key in self._cached_visible_target_keys(folder_id, query)[:limit]:
            document = self.target_documents[key]
            target = document.target
            group = self._cached_visible_group(folder_id, target.local_reference)
            if group is None:
                continue
            ambiguous = len(group.target_keys) > 1
            value = {
                **target.compact("ambiguous" if ambiguous else "resolved"),
                "scope_distance": group.scope_distance,
                "matched_folder_id": group.matched_folder_id,
                "insert_text": f"@{target.canonical_tag}"
                if ambiguous
                else f"@{group.local_reference}",
            }
            rows.append(value)
        return rows
