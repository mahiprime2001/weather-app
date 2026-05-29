"""A tiny file-based cache with per-entry time-to-live.

API responses are written as JSON files named by a hash of the request key.
Each file stores the fetch time, so we can treat entries older than the TTL as
misses. This keeps repeated CLI calls fast and avoids hammering the API.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional


class TTLCache:
    def __init__(self, directory: Path, ttl: int) -> None:
        self.directory = Path(directory)
        self.ttl = ttl

    def _path_for(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return self.directory / f"{digest}.json"

    def get(self, key: str) -> Optional[Any]:
        """Return the cached value for ``key`` if present and fresh, else None."""
        if self.ttl <= 0:
            return None
        path = self._path_for(key)
        if not path.exists():
            return None
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - entry.get("fetched_at", 0) > self.ttl:
            return None
        return entry.get("value")

    def set(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key`` with the current timestamp."""
        if self.ttl <= 0:
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        entry = {"fetched_at": time.time(), "value": value}
        self._path_for(key).write_text(json.dumps(entry), encoding="utf-8")
