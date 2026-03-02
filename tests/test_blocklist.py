"""Tests for agent_tools.blocklist.Blocklist."""

from __future__ import annotations

from pathlib import Path

from agent_tools.blocklist import Blocklist


def test_not_blocked_initially(tmp_path: Path) -> None:
    bl = Blocklist(path=tmp_path / "bl.json")
    assert bl.is_blocked(123) is False


def test_record_violation_below_threshold(tmp_path: Path) -> None:
    bl = Blocklist(path=tmp_path / "bl.json", max_violations_per_day=3)
    bl.record_violation(123)
    bl.record_violation(123)
    assert bl.is_blocked(123) is False


def test_blocked_after_threshold(tmp_path: Path) -> None:
    bl = Blocklist(path=tmp_path / "bl.json", max_violations_per_day=3)
    for _ in range(3):
        bl.record_violation(123)
    assert bl.is_blocked(123) is True


def test_separate_chats(tmp_path: Path) -> None:
    bl = Blocklist(path=tmp_path / "bl.json", max_violations_per_day=2)
    bl.record_violation(111)
    bl.record_violation(222)
    bl.record_violation(222)
    assert bl.is_blocked(111) is False
    assert bl.is_blocked(222) is True


def test_persists_to_disk(tmp_path: Path) -> None:
    path = tmp_path / "bl.json"
    bl = Blocklist(path=path, max_violations_per_day=1)
    bl.record_violation(99)

    bl2 = Blocklist(path=path, max_violations_per_day=1)
    assert bl2.is_blocked(99) is True
