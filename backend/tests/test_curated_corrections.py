import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from app import apply_curated_corrections as corrections
from app.database import find_product, initialize_database
from app.validate_curated import CuratedDataError


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def batch(tmp_path):
    previous = []
    registry = []
    for ean in ("96385074", "2000000000039"):
        expected = {
            "ean": ean, "product_name": "Old name", "brand": "Old brand",
            "company": "Old company", "company_role": "manufacturer",
            "sources": [
                {"title": "Old source", "url": "https://example.com/retained",
                 "checked_on": "2024-02-29", "supports": "Old scope"},
                {"title": "Remove me", "url": "https://example.com/removed",
                 "checked_on": "2023-01-01", "supports": "Old fact"},
            ],
        }
        replacement = copy.deepcopy(expected)
        replacement.update(product_name=" Crème Äänekoski ", brand="München",
                           company="Mäkelä Yhtiö", company_role=None)
        replacement["sources"] = [
            {"title": "Yhtiö", "url": "https://example.com/retained",
             "checked_on": "2024-02-29", "supports": "Mäkelä – Crème"},
            {"title": "Äänekoski", "url": "https://EXAMPLE.com/added",
             "checked_on": "2025-03-04", "supports": " München "},
        ]
        previous.append(expected)
        registry.append({"ean": ean, "reason": "Reviewed facts and supporting sources",
                         "expected": expected, "replacement": replacement})
    curated = tmp_path / "curated.json"
    history = tmp_path / "corrections.json"
    database = tmp_path / "test.sqlite3"
    write_json(curated, previous)
    initialize_database(database, curated)
    write_json(curated, [c["replacement"] for c in registry])
    write_json(history, registry)
    return database, curated, history, registry


def run(batch, **kwargs):
    return corrections.run_corrections(*batch[:3], **kwargs)


def state(batch, index=0):
    return corrections.reviewed_state(find_product(batch[0], batch[3][index]["ean"]))


def test_preview_is_read_only_and_classifies_complete_batch(batch):
    before = batch[0].read_bytes()
    files = {p: p.read_bytes() for p in batch[0].parent.iterdir()}
    assert [r["outcome"] for r in run(batch)] == ["needs_application"] * 2
    assert batch[0].read_bytes() == before
    assert {p: p.read_bytes() for p in batch[0].parent.iterdir()} == files


def test_apply_preserves_exact_utf8_facts_sources_and_explicit_dates(batch):
    assert [r["outcome"] for r in run(batch, apply=True)] == ["applied"] * 2
    for index, correction in enumerate(batch[3]):
        assert state(batch, index) == corrections.reviewed_state(correction["replacement"])
        assert find_product(batch[0], correction["ean"])["is_demo"] is False
    assert find_product(batch[0], "2000000000015")["product_name"] == "Demo Oat Drink"


def test_repeat_apply_is_noop_even_if_updates_would_fail(batch):
    run(batch, apply=True)
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("""CREATE TRIGGER reject_update BEFORE UPDATE ON products
            BEGIN SELECT RAISE(ABORT, 'unexpected update'); END""")
    before = batch[0].read_bytes()
    assert [r["outcome"] for r in run(batch, apply=True)] == ["already_applied"] * 2
    assert batch[0].read_bytes() == before


@pytest.mark.parametrize("sql", [
    "UPDATE products SET company = 'Local edit' WHERE ean = '2000000000039'",
    "UPDATE product_sources SET supports = 'Local edit' WHERE ean = '2000000000039'",
    "DELETE FROM product_sources WHERE ean = '2000000000039'",
    "UPDATE products SET is_demo = 1 WHERE ean = '2000000000039'",
    "DELETE FROM products WHERE ean = '2000000000039'",
])
@pytest.mark.parametrize("apply", [False, True])
def test_any_unsafe_target_blocks_entire_batch(batch, sql, apply):
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(sql)
    before = batch[0].read_bytes()
    results = run(batch, apply=apply)
    assert results[0]["outcome"] == "needs_application"
    assert results[1]["outcome"] == ("missing_product" if sql.startswith("DELETE FROM products") else "conflict")
    assert batch[0].read_bytes() == before
    assert state(batch) == corrections.reviewed_state(batch[3][0]["expected"])


def test_late_insert_failure_rolls_back_entire_batch(batch):
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("""CREATE TRIGGER reject_source BEFORE INSERT ON product_sources
            WHEN NEW.ean = '2000000000039'
            BEGIN SELECT RAISE(ABORT, 'test source failure'); END""")
    before = batch[0].read_bytes()
    with pytest.raises(sqlite3.IntegrityError, match="test source failure"):
        run(batch, apply=True)
    assert batch[0].read_bytes() == before
    for i, c in enumerate(batch[3]):
        assert state(batch, i) == corrections.reviewed_state(c["expected"])


def test_apply_enforces_foreign_keys_and_rolls_back(batch):
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("""CREATE TRIGGER orphan_source AFTER UPDATE ON products
            BEGIN INSERT INTO product_sources VALUES
            ('missing', 'title', 'https://example.com', '2024-01-01', 'scope'); END""")
    before = batch[0].read_bytes()
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        run(batch, apply=True)
    assert batch[0].read_bytes() == before


def test_apply_holds_writer_lock_before_inspection(batch, monkeypatch):
    original = corrections._current_state
    attempts = []

    def inspect(connection, ean):
        other = sqlite3.connect(batch[0], timeout=0)
        try:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                other.execute("UPDATE products SET company = 'racing edit'")
            attempts.append(ean)
        finally:
            other.close()
        return original(connection, ean)

    monkeypatch.setattr(corrections, "_current_state", inspect)
    assert [r["outcome"] for r in run(batch, apply=True)] == ["applied"] * 2
    assert len(attempts) == 2


def test_source_order_is_insignificant_and_files_are_not_modified(batch):
    registry = batch[3]
    for c in registry:
        c["expected"]["sources"].reverse()
        c["replacement"]["sources"].reverse()
    write_json(batch[2], registry)
    before = [p.read_bytes() for p in batch[1:3]]
    assert [r["outcome"] for r in run(batch, apply=True)] == ["applied"] * 2
    assert [p.read_bytes() for p in batch[1:3]] == before


def test_empty_replacement_sources_remove_old_sources(batch):
    for c in batch[3]:
        c["replacement"]["sources"] = []
    write_json(batch[1], [c["replacement"] for c in batch[3]])
    write_json(batch[2], batch[3])
    run(batch, apply=True)
    assert state(batch)["sources"] == []


def test_source_only_correction_and_mixed_already_applied_batch(batch):
    for c in batch[3]:
        for field in corrections.PRODUCT_FIELDS:
            c["replacement"][field] = c["expected"][field]
    write_json(batch[1], [c["replacement"] for c in batch[3]])
    write_json(batch[2], [batch[3][0]])
    assert run(batch, apply=True)[0]["outcome"] == "applied"
    write_json(batch[2], batch[3])
    assert [r["outcome"] for r in run(batch, apply=True)] == ["already_applied", "applied"]
    for i, c in enumerate(batch[3]):
        assert state(batch, i) == corrections.reviewed_state(c["replacement"])


def test_unexpected_extra_source_is_a_conflict(batch):
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("INSERT INTO product_sources VALUES (?, ?, ?, ?, ?)",
                           (batch[3][0]["ean"], "Extra", "https://example.com/extra",
                            "2024-01-01", "Locally reviewed fact"))
    before = batch[0].read_bytes()
    assert run(batch, apply=True)[0]["outcome"] == "conflict"
    assert batch[0].read_bytes() == before


def test_commit_failure_rolls_back_facts_and_sources(batch):
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("""CREATE TABLE deferred_check (
            ean TEXT REFERENCES products(ean) DEFERRABLE INITIALLY DEFERRED)""")
        connection.execute("""CREATE TRIGGER fail_at_commit AFTER UPDATE ON products
            BEGIN INSERT INTO deferred_check VALUES ('missing'); END""")
    before = batch[0].read_bytes()
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        run(batch, apply=True)
    assert batch[0].read_bytes() == before


@pytest.mark.parametrize("mutation", [
    lambda cs: cs.append(copy.deepcopy(cs[0])),
    lambda cs: cs[1].pop("reason"),
    lambda cs: cs[1].update(reason=" \t"),
    lambda cs: cs[1].update(reason=42),
    lambda cs: cs[1].update(ean="invalid"),
    lambda cs: cs[1].update(ean=[]),
    lambda cs: cs[1].update(expected=None),
    lambda cs: cs[1]["expected"].pop("company_role"),
    lambda cs: cs[1]["replacement"].update(company=None),
    lambda cs: cs[1]["expected"].update(ean="6430051512933"),
    lambda cs: cs[1]["replacement"].update(ean="2000000000038"),
    lambda cs: cs[1]["replacement"].update(product_name="Not the curated value"),
    lambda cs: cs[1]["replacement"]["sources"][0].update(supports="Not the curated scope"),
    lambda cs: cs[1]["expected"].update(is_demo=True),
    lambda cs: cs[1]["expected"]["sources"][0].update(url="file:///bad"),
    lambda cs: cs[1]["replacement"]["sources"][0].update(checked_on="2026-02-30"),
    lambda cs: cs[1]["expected"]["sources"].append(copy.deepcopy(cs[1]["expected"]["sources"][0])),
    lambda cs: cs[1]["expected"]["sources"][0].update(extra="ignored?"),
])
def test_invalid_later_correction_never_opens_database(batch, monkeypatch, mutation):
    mutation(batch[3])
    write_json(batch[2], batch[3])
    before = batch[0].read_bytes()
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("database accessed"))
    with pytest.raises(CuratedDataError):
        run(batch, apply=True)
    assert batch[0].read_bytes() == before


@pytest.mark.parametrize("text", ['{"broken":', '{}', '[null]', '[1]', 'null'])
def test_invalid_registry_json_or_shape_never_opens_database(batch, monkeypatch, text):
    batch[2].write_text(text, encoding="utf-8")
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("database accessed"))
    with pytest.raises(CuratedDataError):
        run(batch, apply=True)


def test_invalid_curated_dataset_never_opens_database(batch, monkeypatch):
    data = [c["replacement"] for c in batch[3]]
    data.append({"ean": "invalid"})
    write_json(batch[1], data)
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("database accessed"))
    with pytest.raises(CuratedDataError):
        run(batch, apply=True)


def test_missing_curated_replacement_is_rejected(batch):
    write_json(batch[1], [])
    with pytest.raises(CuratedDataError, match="replacement must match"):
        run(batch, apply=True)


def test_demo_ean_rejected_even_with_matching_curated_entry(batch):
    c = batch[3][0]
    c["ean"] = c["expected"]["ean"] = c["replacement"]["ean"] = "2000000000015"
    write_json(batch[1], [c["replacement"]])
    write_json(batch[2], [c])
    with pytest.raises(CuratedDataError, match="demo EAN"):
        run(batch, apply=True)


@pytest.mark.parametrize("apply", [False, True])
def test_missing_database_is_not_created(batch, apply):
    missing = batch[0].parent / "nonexistent.sqlite3"
    with pytest.raises(sqlite3.OperationalError):
        corrections.run_corrections(missing, *batch[1:3], apply=apply)
    assert not missing.exists()


def test_startup_keeps_existing_facts_and_sources_despite_desired_change(batch):
    before = [state(batch, i) for i in range(2)]
    initialize_database(batch[0], batch[1])
    assert [state(batch, i) for i in range(2)] == before


def cli(batch, *args):
    environment = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]),
                       PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, "-B", "-m", "app.apply_curated_corrections",
         "--database", str(batch[0]), "--curated", str(batch[1]),
         "--corrections", str(batch[2]), *args],
        cwd=batch[0].parent, env=environment, capture_output=True,
        encoding="utf-8", timeout=20,
    )


def test_cli_default_preview_explicit_apply_and_idempotency(batch):
    before = batch[0].read_bytes()
    result = cli(batch)
    assert result.returncode == 0
    assert "needs_application" in result.stdout and "Preview only" in result.stdout
    assert batch[0].read_bytes() == before
    result = cli(batch, "--apply")
    assert result.returncode == 0 and "Applied 2" in result.stdout
    result = cli(batch, "--apply")
    assert result.returncode == 0 and "already_applied" in result.stdout
    assert "Applied 0" in result.stdout


def test_cli_conflict_returns_two_and_changes_nothing(batch):
    with sqlite3.connect(batch[0]) as connection:
        connection.execute("UPDATE products SET company = 'Local edit'")
    before = batch[0].read_bytes()
    result = cli(batch, "--apply")
    assert result.returncode == 2 and "conflict" in result.stdout
    assert "no corrections applied" in result.stdout
    assert "Traceback" not in result.stderr
    assert batch[0].read_bytes() == before


def test_cli_invalid_registry_returns_one_without_traceback(batch):
    batch[2].write_text("invalid JSON", encoding="utf-8")
    before = batch[0].read_bytes()
    result = cli(batch, "--apply")
    assert result.returncode == 1 and "Invalid correction data" in result.stderr
    assert "Traceback" not in result.stderr
    assert batch[0].read_bytes() == before


def test_cli_database_failure_returns_one_without_traceback(batch):
    batch[0].unlink()
    result = cli(batch, "--apply")
    assert result.returncode == 1 and "no corrections committed" in result.stderr
    assert "Traceback" not in result.stderr
    assert not batch[0].exists()


def test_cli_validate_only_does_not_need_database(batch):
    batch[0].unlink()
    result = cli(batch, "--validate-only")
    assert result.returncode == 0 and "no database accessed" in result.stdout
    assert not batch[0].exists()


def test_repository_registry_is_valid():
    corrections.load_corrections()
