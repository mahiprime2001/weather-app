"""Unit tests for the models, WMO mapping, and the TTL cache."""

from __future__ import annotations

import time

from weather_app.cache import TTLCache
from weather_app.models import Location, describe_code


def test_describe_code_known_and_unknown():
    assert describe_code(0)[0] == "Clear sky"
    assert describe_code(95)[0] == "Thunderstorm"
    assert describe_code(12345) == ("Unknown", "❓")


def test_location_label_parts():
    loc = Location(name="London", admin1="England", country="United Kingdom",
                   latitude=51.5, longitude=-0.1)
    assert loc.label == "London, England, United Kingdom"

    bare = Location(name="Atlantis", latitude=0, longitude=0)
    assert bare.label == "Atlantis"


def test_cache_set_and_get(tmp_path):
    cache = TTLCache(tmp_path, ttl=60)
    assert cache.get("k") is None
    cache.set("k", {"v": 1})
    assert cache.get("k") == {"v": 1}


def test_cache_expiry(tmp_path):
    cache = TTLCache(tmp_path, ttl=1)
    cache.set("k", "value")
    assert cache.get("k") == "value"
    # Force the stored timestamp into the past.
    time.sleep(0.01)
    cache.ttl = 0  # ttl<=0 disables reads entirely
    assert cache.get("k") is None


def test_cache_disabled_when_ttl_zero(tmp_path):
    cache = TTLCache(tmp_path, ttl=0)
    cache.set("k", "value")  # no-op
    assert cache.get("k") is None
