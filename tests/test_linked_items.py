from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from study_app.app import create_app
from study_app.markdown_references import markdown_references
from study_app.store import SEARCH_STALENESS_SECONDS, LibraryStore, StoreError


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("@group and @[the theorem]math:th:result:pf", ("group", "math:th:result:pf")),
        (r"\@group &#64;group @[label]group", ("group",)),
        (r"\@group &#64;group &commat;group", ()),
        (r"@[x\]y]group @[x&#93;y]group @[x&#91;y]group", ()),
        (r"@[   ]group @[a *formatted* label]group", ()),
        (r"person@group.org x@group \@group @groupX @group: @group_foo", ()),
        (r"$@group$ $$ @group $$ \(@group\) \[ @group \]", ()),
        ("$$x\ny$$\n\n@group", ()),
        ("$$\n@hidden\n$$\n\n@group", ("group",)),
        ("$$\n@hidden\n$$ trailing\n\n@group", ()),
        ("$$$\n@hidden\n$$\n\n@group", ()),
        ("$$\n@hidden\n$$$$\n\n@group", ("group",)),
        ("$$ @hidden $$\n\n@group", ("group",)),
        ("> $$\n> @hidden\n\n@group", ("group",)),
        ("- $$\n  @hidden\n\n@group", ("group",)),
        ("$$\n@hidden\n    $$\n\n@group", ()),
        ("@group\n$$\n@hidden", ("group",)),
        (r"\( @group `code` \)", ("group",)),
        (r"\$ @group \$", ("group",)),
        (r"[See @group](https://example.com) ![alt @group](image.png)", ()),
        ("[@group][source]\n\n[source]: https://example.com", ()),
        (r"<https://example.com/(@group)> https://example.com/(@group)", ()),
        (r"www.example.com/(@group)", ()),
        ("```\n@group\n```\n\n    @group\n\n`@group`", ()),
        ("<div>\n@group\n</div>", ()),
        ("<b>@group</b>", ("group",)),
        ("**@group** ~@other~ ~~@third~~", ("group", "other", "third")),
        ("| A | B |\n| - | - |\n| @group | @other |", ("group", "other")),
        ("> @group\n> @other", ("group", "other")),
        ("@group\n@other", ("group", "other")),
        (r"@[word &amp; word]group", ("group",)),
        (r"&#92;@group", ()),
    ],
)
def test_references_are_literal_markdown_prose(source, expected):
    assert markdown_references(source) == expected


def test_incoming_links_use_lexical_resolution_and_exact_variant_navigation(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    math = store.create_folder("Mathematics", "math", None)
    physics = store.create_folder("Physics", "physics", None)
    target = store.create_entry(math["id"], "th", "Target", "target", "", "Statement")
    proof = store.add_supplement(
        target["id"], {"kind": "pf", "label": "Proof", "content": "Proof body"}
    )["supplements"][0]
    alt = store.add_formulation(
        target["id"], {"label": "Other", "subtag": "other", "content": "Alternative"}
    )["formulations"][-1]
    source = store.create_entry(
        physics["id"],
        "th",
        "Source",
        "source",
        "Uses @target.",
        f"@[the alternative]{alt['canonical_tag']} twice @target @target. "
        "Missing @absent and code `@absent`.",
    )
    store.add_supplement(
        source["id"], {"kind": "pf", "label": "Proof", "content": f"Use @{proof['canonical_tag']}."}
    )
    later = store.create_entry(physics["id"], "th", "Later", "later", "", "No references")
    later_proof = store.add_supplement(
        later["id"], {"kind": "pf", "label": "Proof", "content": "Apply @target:pf."}
    )["supplements"][0]
    result = store.linked_items(target["id"], limit=1)
    assert result["total"] == 2
    assert result["next_offset"] == 1
    assert result["items"][0]["entry_id"] == source["id"]
    assert result["items"][0]["source"] == "header"
    assert result["items"][0]["variant_id"] is None
    assert result["items"][0]["reference_count"] == 3
    second = store.linked_items(target["id"], offset=1, limit=1)
    assert second["revision"] == result["revision"]
    assert second["next_offset"] is None
    assert second["items"][0]["canonical_tag"] == later_proof["canonical_tag"]
    assert second["items"][0]["variant_id"] == later_proof["id"]
    # A local target now shadows the global short name but cannot shadow the
    # explicit canonical alternative/proof references in Source.
    local = store.create_entry(physics["id"], "df", "Local", "target", "", "Local")
    changed = store.linked_items(target["id"])
    assert changed["revision"] != result["revision"]
    assert changed["items"][0]["reference_count"] == 2
    assert changed["items"][0]["source"] == "formulation"
    assert store.linked_items(local["id"])["items"][0]["entry_id"] == source["id"]
    # Cross-kind ambiguity at the first nonempty stage creates no guessed edge.
    store.create_entry(physics["id"], "rk", "Ambiguous", "target", "", "Other")
    assert store.linked_items(local["id"])["total"] == 0


def test_incoming_links_reuse_snapshot_and_detect_disk_and_api_changes(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Math", "math", None)
    target = store.create_entry(folder["id"], "df", "Target", "target", "", "A definition")
    source = store.create_entry(folder["id"], "rk", "Source", "source", "", "@target")
    first = store.linked_items(target["id"])
    stats = store.search_index_stats()
    for _ in range(3):
        assert store.linked_items(target["id"])["revision"] == first["revision"]
    assert store.search_index_stats()["content_reads"] == stats["content_reads"]
    assert store.search_index_stats()["builds"] == stats["builds"]
    file = tmp_path / "data" / source["formulations"][0]["file"]
    file.write_text("`@target`\n", encoding="utf-8")
    time.sleep(SEARCH_STALENESS_SECONDS + 0.02)
    second = store.linked_items(target["id"])
    assert second["revision"] != first["revision"]
    assert second["total"] == 0
    store.update_entry(source["id"], {"header": "@target"})
    assert store.linked_items(target["id"])["total"] == 1
    store.update_entry(target["id"], {"tag": "renamed"})
    assert store.linked_items(target["id"])["total"] == 0


def test_read_apis_batch_once_with_bounded_authenticated_results(settings_factory, monkeypatch):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Math", "math", None)
    target = store.create_entry(folder["id"], "df", "Target", "target", "", "A definition")
    source = store.create_entry(folder["id"], "rk", "Source", "source", "", "@target")
    calls = 0
    original = store._ensure_search_index

    def ensure():
        nonlocal calls
        calls += 1
        return original()

    monkeypatch.setattr(store, "_ensure_search_index", ensure)
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        response = client.get(
            "/api/references/resolve-batch",
            params=[
                ("folder_id", folder["id"]),
                ("tag", "@target"),
                ("tag", "@missing"),
            ],
        )
        assert response.status_code == 200
        assert calls == 1
        payload = response.json()
        assert [row["tag"] for row in payload["results"]] == ["@target", "@missing"]
        assert [row["result"]["status"] for row in payload["results"]] == ["resolved", "missing"]
        linked = client.get(f"/api/entries/{target['id']}/linked-items").json()
        assert linked["revision"] == payload["revision"]
        assert linked["items"][0]["entry_id"] == source["id"]
        for query in ({"offset": -1}, {"limit": 0}, {"limit": 201}):
            assert (
                client.get(f"/api/entries/{target['id']}/linked-items", params=query).status_code
                == 422
            )
        for tags in ([], ["x"] * 101, ["x" * 8193]):
            assert (
                client.get(
                    "/api/references/resolve-batch",
                    params=[
                        ("folder_id", folder["id"]),
                        *[("tag", tag) for tag in tags],
                    ],
                ).status_code
                == 422
            )
        assert client.get("/api/entries/absent/linked-items").status_code == 422
    with pytest.raises(StoreError, match="65536"):
        store.resolve_references(folder["id"], ["x" * 8192] * 9)
    server = create_app(settings_factory(password_hash="unused"), local_mode=False)
    with TestClient(server, base_url="http://study.test", client=("192.0.2.1", 50000)) as remote:
        assert remote.get(f"/api/entries/{target['id']}/linked-items").status_code == 401
        assert (
            remote.get(
                "/api/references/resolve-batch",
                params={
                    "folder_id": folder["id"],
                    "tag": "@target",
                },
            ).status_code
            == 401
        )
