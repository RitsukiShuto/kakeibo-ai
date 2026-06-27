import time
from typing import Any, Optional

_DEFAULT_TTL = 300  # 5 minutes


class TTLCache:
    def __init__(self, ttl_seconds: int = _DEFAULT_TTL):
        self._store: dict[str, tuple[Any, float]] = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, ts = entry
        if time.monotonic() - ts < self.ttl:
            return value
        del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.monotonic())

    def invalidate_prefix(self, prefix: str) -> None:
        for key in [k for k in self._store if k.startswith(prefix)]:
            del self._store[key]

    def clear(self) -> None:
        self._store.clear()


# Module-level singleton shared across all routers
dashboard_cache = TTLCache(ttl_seconds=300)
