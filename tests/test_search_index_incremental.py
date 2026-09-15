from __future__ import annotations

import gc
import random
import weakref
from pathlib import Path

import pytest

import study_app.search_index as search_module
from study_app.search_index import LibrarySearchIndex
from study_app.store import LibraryStore


def _index_inputs(store: LibraryStore):
    library = store._read()
    content = {
        variant["file"]: store._read_content(variant["file"])
        for entry in library["entries"]
        for variant in entry["formulations"] + entry["supplements"]
    }
    return library, store._folder_namespaces(library), content


def _assert_same_results(actual: LibrarySearchIndex, expected: LibrarySearchIndex):
    assert actual.entry_documents == expected.entry_documents
    assert actual.target_documents == expected.target_documents
    assert actual.entry_postings == expected.entry_postings
    assert actual.target_postings == expected.target_postings
    queries = ["", "a", "co", "common", "bodyold", "bodynew", "retitled", "object",
               "alternate", "proof", "source", "physics", "missing-token"]
    references = {"object", "another", "source", "object:alternate", "missing"}
    references.update(target.canonical_tag for target in expected.targets.values())
    references.update(target.local_reference for target in expected.targets.values())
    for query in queries:
        assert actual.search_entries(query, 200) == expected.search_entries(query, 200)
    for folder_id in expected.folder_by_id:
        for query in queries:
            assert actual.search_entries(query, 200, folder_id) == expected.search_entries(
                query, 200, folder_id
            )
            assert actual.search_visible_references(
                folder_id, query, 200
            ) == expected.search_visible_references(folder_id, query, 200)
        for reference in references:
            assert actual.resolve(folder_id, reference) == expected.resolve(folder_id, reference)
    for entry_id in expected.entry_documents:
        actual_links = actual.linked_items(entry_id)
        expected_links = expected.linked_items(entry_id)
        actual_links.pop("revision")
        expected_links.pop("revision")
        assert actual_links == expected_links


def test_incremental_postings_match_full_build_for_add_remove_change_and_empty_text():
    # Deterministic varied documents exercise shared grams and short/empty text,
    # including keys removed then reintroduced across consecutive snapshots.
    randomizer = random.Random(1847)
    old_documents: dict[str, str] = {}
    old_postings = LibrarySearchIndex._build_postings(old_documents)
    for _ in range(80):
        documents = {
            f"entry-{key}": "".join(
                randomizer.choices("abc commonXYZ ", k=randomizer.randrange(70))
            )
            for key in range(10)
            if randomizer.random() < 0.7
        }
        # Keep some documents byte-for-byte unchanged while others change.
        documents.update({key: text for key, text in old_documents.items()
                          if randomizer.random() < 0.4})
        original_postings = old_postings.copy()
        actual = LibrarySearchIndex._build_postings(
            documents, previous_documents=old_documents, previous_postings=old_postings
        )
        assert actual == LibrarySearchIndex._build_postings(documents)
        assert old_postings == original_postings
        old_documents, old_postings = documents, actual
    assert LibrarySearchIndex._build_postings(
        {}, previous_documents=old_documents, previous_postings=old_postings
    ) == {}


def test_incremental_index_reuses_immutable_sets_without_retokenizing_unchanged_documents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    edited = store.create_entry(folder["id"], "df", "First", "first", "", "Common body")
    store.create_entry(folder["id"], "df", "Untouched", "untouched", "", "Unique zebra")
    previous = LibrarySearchIndex(*_index_inputs(store))
    original_entry_postings = previous.entry_postings.copy()
    original_target_postings = previous.target_postings.copy()
    store.update_entry(edited["id"], {"title": "Retitled"})
    inputs = _index_inputs(store)
    calls: list[str] = []
    trigrams = search_module._trigrams

    def record_trigrams(text: str):
        calls.append(text)
        return trigrams(text)

    monkeypatch.setattr(search_module, "_trigrams", record_trigrams)
    current = LibrarySearchIndex(*inputs, previous=previous)
    assert calls and all("untouched" not in text for text in calls)
    assert current.entry_postings is not previous.entry_postings
    assert current.entry_postings["zeb"] is previous.entry_postings["zeb"]
    assert current.target_postings["zeb"] is previous.target_postings["zeb"]
    assert previous.entry_postings == original_entry_postings
    assert previous.target_postings == original_target_postings
    calls.clear()
    unchanged = LibrarySearchIndex(*inputs, previous=current)
    assert calls == []
    assert unchanged.revision != current.revision
    assert all(unchanged.entry_postings[key] is value
               for key, value in current.entry_postings.items())

    # Sharing sets must not create a retained chain of prior index snapshots.
    previous_reference = weakref.ref(previous)
    del previous
    gc.collect()
    assert previous_reference() is None


def test_incremental_index_rebuilds_metadata_scope_variants_and_backlinks(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    root = store.create_folder("Mathematics", "math", None)
    algebra = store.create_folder("Algebra", "algebra", root["id"])
    topology = store.create_folder("Topology", "topology", root["id"])
    child = store.create_folder("Modules", "modules", algebra["id"])
    other = store.create_folder("Physics", "physics", None)
    item = store.create_entry(
        algebra["id"], "th", "Object", "object", "@another", "Common bodyold"
    )
    item = store.add_formulation(item["id"], {
        "label": "Alternate", "subtag": "alternate", "content": "Common alternate"
    })
    alternate_id = item["formulations"][-1]["id"]
    item = store.add_supplement(item["id"], {
        "kind": "pf", "label": "Proof", "content": "Proof using @another"
    })
    other_object = store.create_entry(
        other["id"], "df", "Other object", "object", "", "Common physics"
    )
    store.create_entry(root["id"], "df", "Another", "another", "", "Common base")
    source = store.create_entry(
        child["id"], "rk", "Source", "source", "@object", "Uses @object and @another"
    )
    previous = LibrarySearchIndex(*_index_inputs(store))
    _assert_same_results(previous, previous)  # Populate query and incoming-link caches.

    def check_change():
        nonlocal previous
        old_entries = previous.entry_postings.copy()
        old_targets = previous.target_postings.copy()
        inputs = _index_inputs(store)
        current = LibrarySearchIndex(*inputs, previous=previous)
        assert current._incoming_by_entry is None
        assert current._cached_entry_keys.cache_info().currsize == 0
        assert current._cached_visible_group.cache_info().currsize == 0
        assert current._cached_visible_target_keys.cache_info().currsize == 0
        _assert_same_results(current, LibrarySearchIndex(*inputs))
        assert previous.entry_postings == old_entries
        assert previous.target_postings == old_targets
        previous = current

    store.update_entry(item["id"], {"title": "Retitled", "header": "New @source header"})
    check_change()
    store.update_entry(item["id"], {"title": "RETITLED"})
    check_change()  # Equal normalized text still requires current display metadata.
    store.write_variant_content(item["id"], item["formulations"][0]["id"], "Common bodynew")
    check_change()
    store.update_variant(item["id"], alternate_id, {"main": True})
    check_change()
    store.update_entry(item["id"], {"folder_id": topology["id"]})
    check_change()
    store.update_folder(topology["id"], {"slug": "spaces"})
    check_change()
    store.update_folder(child["id"], {"parent_id": other["id"]})
    check_change()
    assert previous.resolve(child["id"], "object")["match"]["entry_id"] == other_object["id"]
    store.create_entry(other["id"], "rk", "New remark", "new-remark", "", "Common @object")
    check_change()
    store.delete_entry(item["id"])
    check_change()
    store.delete_entry(source["id"])
    check_change()
    for entry in store.snapshot(include_tree=False)["entries"]:
        store.delete_entry(entry["id"])
    check_change()
    assert previous.entry_postings == previous.target_postings == {}
