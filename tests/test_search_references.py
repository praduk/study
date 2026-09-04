from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from study_app.app import create_app
from study_app.search_index import LibrarySearchIndex
from study_app.store import SEARCH_STALENESS_SECONDS, LibraryStore


def _hierarchy(store: LibraryStore):
    root = store.create_folder("Mathematics", "math", None)
    algebra = store.create_folder("Algebra", "algebra", root["id"])
    linear = store.create_folder("Linear algebra", "linear", algebra["id"])
    sibling = store.create_folder("Topology", "topology", root["id"])
    return root, algebra, linear, sibling


def test_reference_resolution_expands_through_nearest_subtrees(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    root, algebra, linear, sibling = _hierarchy(store)
    root_group = store.create_entry(
        root["id"], "df", "Root group", "group", "Root header", "Root formulation"
    )
    local_group = store.create_entry(
        algebra["id"], "df", "Algebra group", "group", "Local header", "Local formulation"
    )
    root_field = store.create_entry(
        root["id"], "df", "Field", "field", "", "A field has two operations."
    )
    store.create_entry(sibling["id"], "th", "Sibling only", "compactness", "", "Body")

    nearest = store.resolve_reference(linear["id"], "@group")
    assert nearest["status"] == "resolved"
    assert nearest["scope_distance"] == 1
    assert nearest["match"]["entry_id"] == local_group["id"]
    assert nearest["match"]["content"] == "Local formulation\n"
    assert nearest["match"]["main_formulation"]["id"] == local_group["formulations"][0]["id"]

    parent_fallback = store.resolve_reference(linear["id"], "field")
    assert parent_fallback["status"] == "resolved"
    assert parent_fallback["scope_distance"] == 2
    assert parent_fallback["match"]["entry_id"] == root_field["id"]

    sibling_fallback = store.resolve_reference(linear["id"], "compactness")
    assert sibling_fallback["status"] == "resolved"
    assert sibling_fallback["resolution"] == "subtree"
    assert sibling_fallback["scope_distance"] == 2
    assert store.resolve_reference(root["id"], "group")["match"]["entry_id"] == root_group["id"]


def test_subtree_resolution_stops_at_first_nonempty_stage_and_never_guesses(
    tmp_path: Path,
):
    store = LibraryStore(tmp_path / "data")
    root = store.create_folder("Mathematics", "math", None)
    current = store.create_folder("Algebra", "algebra", root["id"])
    first_child = store.create_folder("Groups", "groups", current["id"])
    second_child = store.create_folder("Rings", "rings", current["id"])
    unrelated = store.create_folder("Physics", "physics", None)
    far = store.create_entry(root["id"], "df", "Far object", "object", "", "Far")
    first = store.create_entry(
        first_child["id"], "df", "Group object", "object", "", "First"
    )
    second = store.create_entry(
        second_child["id"], "th", "Ring object", "object", "", "Second"
    )
    store.create_entry(unrelated["id"], "df", "Outside", "outside", "", "Outside")

    ambiguous = store.resolve_reference(current["id"], "object")
    assert ambiguous["status"] == "ambiguous"
    assert ambiguous["resolution"] == "subtree"
    assert {candidate["entry_id"] for candidate in ambiguous["candidates"]} == {
        first["id"],
        second["id"],
    }
    assert far["id"] not in {candidate["entry_id"] for candidate in ambiguous["candidates"]}
    assert store.resolve_reference(current["id"], "outside")["status"] == "missing"
    assert store.resolve_reference(current["id"], far["canonical_tag"])["match"][
        "entry_id"
    ] == far["id"]

    candidates = store.reference_candidates(current["id"], "object")
    collisions = [item for item in candidates if item["reference_tag"] == "object"]
    assert len(collisions) == 2
    assert all(item["insert_text"] == f"@{item['canonical_tag']}" for item in collisions)

    local = store.create_entry(current["id"], "ax", "Local object", "object", "", "Local")
    resolved = store.resolve_reference(current["id"], "object")
    assert resolved["status"] == "resolved"
    assert resolved["match"]["entry_id"] == local["id"]


def test_same_scope_cross_kind_collision_is_ambiguous_and_never_guessed(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    root, algebra, linear, _sibling = _hierarchy(store)
    store.create_entry(root["id"], "df", "Root object", "object", "", "Root")
    definition = store.create_entry(
        algebra["id"], "df", "Local object definition", "object", "", "Definition"
    )
    theorem = store.create_entry(
        algebra["id"], "th", "Local object theorem", "object", "", "Theorem"
    )

    result = store.resolve_reference(linear["id"], "@object")
    assert result["status"] == "ambiguous"
    assert result["match"] is None
    assert result["matched_folder_id"] == algebra["id"]
    assert {candidate["entry_id"] for candidate in result["candidates"]} == {
        definition["id"],
        theorem["id"],
    }

    exact = store.resolve_reference(linear["id"], theorem["canonical_tag"])
    assert exact["status"] == "resolved"
    assert exact["resolution"] == "canonical"
    assert exact["match"]["entry_id"] == theorem["id"]

    candidates = store.reference_candidates(linear["id"], "object")
    collisions = [item for item in candidates if item["reference_tag"] == "object"]
    assert len(collisions) == 2
    assert all(item["resolution_status"] == "ambiguous" for item in collisions)
    assert all(item["insert_text"] == f"@{item['canonical_tag']}" for item in collisions)


def test_alternative_formulations_and_proofs_have_scoped_reference_tags(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    root, algebra, linear, _sibling = _hierarchy(store)
    theorem = store.create_entry(
        algebra["id"], "th", "Orbit theorem", "orbit", "", "Main statement"
    )
    theorem = store.add_formulation(
        theorem["id"],
        {
            "label": "Categorical",
            "subtag": "category",
            "content": "Categorical formulation",
            "main": False,
        },
    )
    theorem = store.add_supplement(
        theorem["id"],
        {"kind": "pf", "label": "Proof", "content": "Main proof", "main": True},
    )
    theorem = store.add_supplement(
        theorem["id"],
        {
            "kind": "pf",
            "label": "Action proof",
            "subtag": "action",
            "content": "Alternative proof",
            "main": False,
        },
    )

    formulation = store.resolve_reference(linear["id"], "orbit:category")
    assert formulation["status"] == "resolved"
    assert formulation["match"]["content"] == "Categorical formulation\n"
    assert formulation["match"]["main_formulation"]["content"] == "Main statement\n"
    proof = store.resolve_reference(linear["id"], "@orbit:pf")
    assert proof["match"]["content"] == "Main proof\n"
    alternate_proof = store.resolve_reference(linear["id"], "orbit:pf:action")
    assert alternate_proof["match"]["content"] == "Alternative proof\n"

    canonical = next(
        item["canonical_tag"]
        for item in theorem["supplements"]
        if item.get("subtag") == "action"
    )
    assert canonical == "math:algebra:th:orbit:pf:action"
    assert store.resolve_reference(root["id"], canonical)["status"] == "resolved"


def test_reference_index_invalidates_after_move_tag_and_namespace_changes(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    root, algebra, linear, sibling = _hierarchy(store)
    entry = store.create_entry(algebra["id"], "df", "Module", "module", "", "Body")
    root_scalar = store.create_entry(root["id"], "df", "Root scalar", "scalar", "", "Root")
    sibling_scalar = store.create_entry(
        sibling["id"], "df", "Sibling scalar", "scalar", "", "Sibling"
    )

    assert store.resolve_reference(linear["id"], "module")["status"] == "resolved"
    assert store.resolve_reference(linear["id"], "scalar")["match"]["entry_id"] == root_scalar["id"]
    changed = store.update_entry(entry["id"], {"tag": "left-module"})
    assert store.resolve_reference(linear["id"], "module")["status"] == "missing"
    assert store.resolve_reference(linear["id"], "left-module")["status"] == "resolved"

    store.move_item("entry", entry["id"], sibling["id"], 0)
    assert store.resolve_reference(linear["id"], "left-module")["match"][
        "entry_id"
    ] == entry["id"]
    assert store.resolve_reference(sibling["id"], "left-module")["status"] == "resolved"

    assert changed["canonical_tag"] == "math:algebra:df:left-module"
    old_canonical = store.get_entry(entry["id"])["canonical_tag"]
    assert old_canonical == "math:topology:df:left-module"
    renamed = store.update_folder(sibling["id"], {"slug": "point-set"})
    assert renamed["namespace"] == "math:point-set"
    assert store.resolve_reference(root["id"], old_canonical)["status"] == "missing"
    new_canonical = "math:point-set:df:left-module"
    assert store.resolve_reference(root["id"], new_canonical)["status"] == "resolved"

    store.move_item("folder", linear["id"], sibling["id"], 0)
    moved_scope = store.resolve_reference(linear["id"], "scalar")
    assert moved_scope["match"]["entry_id"] == sibling_scalar["id"]
    assert moved_scope["scope_distance"] == 1


def test_trigram_content_search_is_ranked_verified_and_reuses_cache(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    exact_tag = store.create_entry(folder["id"], "df", "Other title", "abelian", "", "First")
    exact_title = store.create_entry(
        folder["id"], "th", "Abelian", "commutator", "", "Second"
    )
    body_hit = store.create_entry(
        folder["id"],
        "rk",
        "Background",
        "background",
        "",
        "This paragraph mentions abelian groups and a unique-search-needle.",
    )

    ranked = store.search("ABELIAN")
    assert [item["id"] for item in ranked[:3]] == [
        exact_tag["id"],
        exact_title["id"],
        body_hit["id"],
    ]
    assert [item["id"] for item in store.search("unique-search-needle")] == [body_hit["id"]]
    assert store.search("unique-search-needlf") == []

    first_stats = store.search_index_stats()
    store.search("groups")
    store.reference_candidates(folder["id"], "group")
    store.resolve_reference(folder["id"], "abelian")
    second_stats = store.search_index_stats()
    assert second_stats["builds"] == first_stats["builds"]
    assert second_stats["content_reads"] == first_stats["content_reads"]


def test_content_writes_and_bounded_manual_file_checks_refresh_search(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Analysis", "analysis", None)
    entry = store.create_entry(
        folder["id"], "df", "Continuity", "continuity", "", "old-index-token"
    )
    variant = entry["formulations"][0]
    assert store.search("old-index-token")
    initial = store.search_index_stats()

    store.write_variant_content(entry["id"], variant["id"], "new-index-token")
    assert store.search("old-index-token") == []
    assert store.search("new-index-token")
    after_api_write = store.search_index_stats()
    assert after_api_write["builds"] == initial["builds"] + 1

    source_path = store.data_dir / variant["file"]
    source_path.write_text("manual-index-token\n", encoding="utf-8")
    time.sleep(SEARCH_STALENESS_SECONDS + 0.05)
    assert store.search("new-index-token") == []
    assert store.search("manual-index-token")
    assert store.search_index_stats()["builds"] == after_api_write["builds"] + 1


def test_resolution_never_rewrites_markdown_math_or_code(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Logic", "logic", None)
    source = "$x@tag$\n\n```text\n@tag\n```\n\nRefer to @tag in prose."
    entry = store.create_entry(folder["id"], "df", "Tag", "tag", "", source)
    path = store.data_dir / entry["formulations"][0]["file"]
    before = path.read_bytes()

    assert store.resolve_reference(folder["id"], "@tag")["status"] == "resolved"
    store.search("@tag")
    store.reference_candidates(folder["id"], "tag")
    assert path.read_bytes() == before


def test_reference_and_search_endpoints_are_authenticated_and_include_review_scope(
    settings_factory,
):
    server_settings = settings_factory()
    with TestClient(
        create_app(server_settings, local_mode=False),
        base_url="http://study.test",
        client=("192.0.2.10", 50000),
    ) as client:
        assert client.get(
            "/api/references/resolve", params={"folder_id": "none", "tag": "tag"}
        ).status_code == 401
        assert client.get("/api/references/candidates", params={"folder_id": "none"}).status_code == 401
        assert client.get("/api/search", params={"q": "tag"}).status_code == 401

    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    folder = app.state.store.create_folder("Geometry", "geometry", None)
    entry = app.state.store.create_entry(
        folder["id"], "df", "Metric", "metric", "", "Distance axioms"
    )
    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        resolved = client.get(
            "/api/references/resolve",
            params={"folder_id": folder["id"], "tag": "@metric"},
        )
        assert resolved.status_code == 200
        assert resolved.json()["match"]["entry_id"] == entry["id"]
        candidates = client.get(
            "/api/references/candidates",
            params={"folder_id": folder["id"], "q": "metric"},
        ).json()["results"]
        assert candidates[0]["insert_text"] == "@metric"
        assert client.get("/api/search", params={"q": "distance"}).json()["results"][0][
            "id"
        ] == entry["id"]
        cards = client.get("/api/review/queue").json()["cards"]
        assert cards and all(card["folder_id"] == folder["id"] for card in cards)
        null_slug = client.patch(
            f"/api/folders/{folder['id']}",
            json={"slug": None},
            headers={"origin": "http://127.0.0.1", "x-study-csrf": "local"},
        )
        assert null_slug.status_code == 422
        assert app.state.store.snapshot()["folders"][0]["slug"] == "geometry"


def test_reference_endpoint_accepts_long_valid_canonical_tags(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    parent_id = None
    for index in range(64):
        initial = chr(ord("a") + index % 26)
        folder = app.state.store.create_folder(
            f"Level {index}", f"{initial}{'x' * 63}", parent_id
        )
        parent_id = folder["id"]
    entry = app.state.store.create_entry(
        parent_id, "th", "Deep result", "r" * 80, "", "Deep content"
    )
    assert len(entry["canonical_tag"]) > 4000

    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        response = client.get(
            "/api/references/resolve",
            params={"folder_id": parent_id, "tag": entry["canonical_tag"]},
        )
    assert response.status_code == 200
    assert response.json()["match"]["entry_id"] == entry["id"]


def test_search_index_folder_ranking_does_not_use_python_recursion() -> None:
    folders = []
    namespaces = {}
    parent_id = None
    for index in range(1500):
        folder_id = f"folder-{index}"
        folders.append(
            {
                "id": folder_id,
                "name": f"Folder {index}",
                "parent_id": parent_id,
                "order": 0,
            }
        )
        namespaces[folder_id] = f"namespace-{index}"
        parent_id = folder_id

    index = LibrarySearchIndex(
        {"folders": folders, "entries": []}, namespaces, content_by_path={}
    )
    assert len(index.ancestry_by_folder[parent_id]) == 1500
    assert index._folder_rank[parent_id] == 1499
