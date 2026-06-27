import time
import pytest
from src.api.cache import TTLCache


def test_cache_set_and_get():
    cache = TTLCache(ttl_seconds=60)
    cache.set("key1", {"value": 42})
    assert cache.get("key1") == {"value": 42}


def test_cache_miss_returns_none():
    cache = TTLCache(ttl_seconds=60)
    assert cache.get("nonexistent") is None


def test_cache_expires_after_ttl():
    cache = TTLCache(ttl_seconds=0)
    cache.set("key1", "data")
    # TTL=0 so the entry expires immediately on next access
    time.sleep(0.01)
    assert cache.get("key1") is None


def test_cache_invalidate_prefix():
    cache = TTLCache(ttl_seconds=60)
    cache.set("kpi:monthly:current", 100)
    cache.set("kpi:weekly:current", 50)
    cache.set("budget-actual:monthly:current:", 200)

    cache.invalidate_prefix("kpi:")
    assert cache.get("kpi:monthly:current") is None
    assert cache.get("kpi:weekly:current") is None
    assert cache.get("budget-actual:monthly:current:") == 200


def test_cache_clear():
    cache = TTLCache(ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_cache_overwrite():
    cache = TTLCache(ttl_seconds=60)
    cache.set("key", "old")
    cache.set("key", "new")
    assert cache.get("key") == "new"
