from time import sleep

import pytest


def test_sync_cache__set_and_get(dynamics_cache):
    dynamics_cache.set("foo", "bar", 0.5)
    assert dynamics_cache.get("foo") == "bar"
    sleep(0.5)
    assert dynamics_cache.get("foo") is None


def test_sync_cache__set_bad_value(dynamics_cache):
    with pytest.raises(AttributeError):
        dynamics_cache.set("foo", lambda x: 100, 0.5)


def test_sync_cache__clear(dynamics_cache):
    dynamics_cache.set("foo", "bar", 10)
    assert dynamics_cache.get("foo") == "bar"
    dynamics_cache.clear()
    assert dynamics_cache.get("foo") is None


def test_sync_cache__close(dynamics_cache):
    assert dynamics_cache.connections != {}
    dynamics_cache.close()
    assert dynamics_cache.connections == {}


@pytest.mark.asyncio
async def test_async_cache__get_or_set(async_dynamics_cache):
    await async_dynamics_cache.set("foo", "bar", 0.5)
    assert (await async_dynamics_cache.get("foo")) == "bar"
    sleep(0.5)
    assert (await async_dynamics_cache.get("foo")) is None


@pytest.mark.asyncio
async def test_async_cache__set_bad_value(async_dynamics_cache):
    with pytest.raises(AttributeError):
        await async_dynamics_cache.set("foo", lambda x: 100, 0.5)


@pytest.mark.asyncio
async def test_async_cache__clear(async_dynamics_cache):
    await async_dynamics_cache.set("foo", "bar", 0.5)
    assert (await async_dynamics_cache.get("foo")) == "bar"
    await async_dynamics_cache.clear()
    assert (await async_dynamics_cache.get("foo")) is None


@pytest.mark.asyncio
async def test_async_cache__close(async_dynamics_cache):
    assert async_dynamics_cache.connections != {}
    await async_dynamics_cache.close()
    assert async_dynamics_cache.connections == {}


@pytest.mark.asyncio
async def test_async_cache__remove_connections(async_dynamics_cache, dynamics_cache):
    # Assure all connections are closed
    await async_dynamics_cache.close()
    dynamics_cache.close()
    assert async_dynamics_cache.connections == {}
    assert dynamics_cache.connections == {}

    # Test async connection is cleared when sync connection is established
    await async_dynamics_cache.clear()
    assert async_dynamics_cache.connections != {}
    assert dynamics_cache.connections == {}
    dynamics_cache.clear()
    assert async_dynamics_cache.connections == {}
    assert dynamics_cache.connections != {}

    # Assure all connections are closed
    await async_dynamics_cache.close()
    dynamics_cache.close()
    assert async_dynamics_cache.connections == {}
    assert dynamics_cache.connections == {}

    # Test sync connection is cleared when async connection is established
    dynamics_cache.clear()
    assert async_dynamics_cache.connections == {}
    assert dynamics_cache.connections != {}
    await async_dynamics_cache.clear()
    assert async_dynamics_cache.connections != {}
    assert dynamics_cache.connections == {}
