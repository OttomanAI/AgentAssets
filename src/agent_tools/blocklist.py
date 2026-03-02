"""JSON-file blocklist that tracks guardrail violations per chat."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class Blocklist:
    """Track guardrail violations and auto-block chats that exceed a daily threshold.

    Parameters
    ----------
    path:
        File path for the JSON store. Created automatically on first write.
    max_violations_per_day:
        Number of BLOCKED verdicts in a rolling 24-hour window before the chat
        is permanently blocked. Default is 5.
    """

    def __init__(self, path: str | Path = "blocklist.json", max_violations_per_day: int = 5) -> None:
        self._path = Path(path)
        self._threshold = max_violations_per_day
        self._data: dict = {"blocked": [], "violations": {}}
        if self._path.exists():
            text = self._path.read_text(encoding="utf-8").strip()
            if text:
                self._data = json.loads(text)

    def is_blocked(self, chat_id: int | str) -> bool:
        """Return True if the chat is permanently blocked."""
        return str(chat_id) in self._data["blocked"]

    def record_violation(self, chat_id: int | str) -> bool:
        """Record a guardrail violation and return True if the chat is now blocked."""
        key = str(chat_id)
        now = datetime.now(timezone.utc).isoformat()

        violations = self._data["violations"].setdefault(key, [])
        violations.append(now)

        # Count violations in the last 24 hours
        cutoff = datetime.now(timezone.utc).timestamp() - 86400
        recent = [v for v in violations if datetime.fromisoformat(v).timestamp() > cutoff]
        self._data["violations"][key] = recent

        if len(recent) >= self._threshold and key not in self._data["blocked"]:
            self._data["blocked"].append(key)

        self._write()
        return self.is_blocked(key)

    def _write(self) -> None:
        self._path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
