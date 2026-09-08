# SPDX-License-Identifier: Apache-2.0
"""Real-server regressions shared by standalone and Sentinel profiles."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from meridian_storage.errors import ValidationError
from meridian_storage.registry import ResourceRef
from meridian_storage.spi import PhysicalResource

from tests.conftest import RESOURCE, SCHEMA, operation_context


def verify_real_cache_contract(runtime):
    cache = runtime.cache
    context = operation_context()
    resource = ResourceRef.parse(RESOURCE)
    with pytest.raises(ValidationError, match="non-Cache"):
        runtime.verify_physical(
            (
                PhysicalResource(
                    ResourceRef.parse("structured:demo.items"),
                    "sha256:" + "3" * 64,
                    SCHEMA,
                    "structured",
                ),
            )
        )
    with pytest.raises(ValidationError):
        runtime.verify_physical(
            (PhysicalResource(resource, "sha256:" + "3" * 64, "sha256:" + "4" * 64, "cache"),)
        )

    cache.delete(context, resource, "pifa-race")
    barrier = threading.Barrier(8)

    def insert(index):
        barrier.wait(timeout=10)
        return cache.put_if_absent(context, resource, "pifa-race", index)[0]

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(insert, range(8))) == 1
    original = cache.put(context, resource, "cas-race", "initial")
    barrier = threading.Barrier(8)

    def swap(index):
        barrier.wait(timeout=10)
        return cache.compare_and_set(
            context, resource, "cas-race", original.envelope_version, index
        )[0].swapped

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(swap, range(8))) == 1

    cache.delete(context, resource, "stampede")
    barrier = threading.Barrier(8)
    loaded = []

    def loader():
        loaded.append(True)
        time.sleep(0.01)
        return "from-authority"

    def read(_index):
        barrier.wait(timeout=10)
        return cache.get_or_load(context, resource, "stampede", loader).value

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert list(pool.map(read, range(8))) == ["from-authority"] * 8
    assert len(loaded) == 1
    cache.put(context, resource, "ttl-expiry", 1, requested_ttl_ms=20)
    time.sleep(0.03)
    assert not cache.lookup(context, resource, "ttl-expiry").hit
