from __future__ import annotations

from onuki2007_companion import cli
from onuki2007_companion.checks import CHECKS


def test_public_check_ids_are_unique_and_reference_existing_scripts() -> None:
    root = cli.repository_root()
    assert len(CHECKS) == 18
    assert len({check.check_id for check in CHECKS}) == len(CHECKS)
    assert all(root.joinpath(check.script).is_file() for check in CHECKS)


def test_list_and_show_are_deterministic(capsys) -> None:
    assert cli.main(["list"]) == 0
    listing = capsys.readouterr().out
    assert "b-b3" in listing
    assert "section-iid" in listing
    assert "canonical_only" in listing
    assert cli.main(["show", "b-b3"]) == 0
    assert "dimensional-source B3 factor residual" in capsys.readouterr().out


def test_dimensions_selects_only_dimensional_checks(monkeypatch) -> None:
    called: list[str] = []
    monkeypatch.setattr(cli, "run", lambda check: called.append(check.check_id) or 0)
    assert cli.main(["dimensions"]) == 0
    assert called
    assert all(check.dimensional for check in CHECKS if check.check_id in called)


def test_public_aggregate_excludes_canonical_scaffold(monkeypatch) -> None:
    called: list[str] = []
    monkeypatch.setattr(cli, "run", lambda check: called.append(check.check_id) or 0)
    assert cli.main(["python-all"]) == 0
    assert "scaffold" not in called
    assert len(called) == len([check for check in CHECKS if check.public])
