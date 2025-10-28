"""Unit tests for Azure credential caching helpers."""

import uuid

import pytest

from azure_models import AzureCredentialManager


@pytest.fixture
def unique_cache_name():
    cache_name = f"pytest-{uuid.uuid4()}"
    try:
        yield cache_name
    finally:
        # Cleanup to keep the class-level cache tidy between tests
        AzureCredentialManager._credential_cache.pop(cache_name, None)


def test_get_credential_returns_cached_instance(unique_cache_name):
    """Repeated calls with the same cache name should reuse the cached credential."""
    first = AzureCredentialManager.get_credential(cache_name=unique_cache_name)
    second = AzureCredentialManager.get_credential(cache_name=unique_cache_name)
    assert first is second


def test_get_credential_creates_new_instance_for_new_cache_name():
    """Different cache names must produce different credential objects."""
    cache_name_1 = f"pytest-{uuid.uuid4()}"
    cache_name_2 = f"pytest-{uuid.uuid4()}"

    cred_one = AzureCredentialManager.get_credential(cache_name=cache_name_1)
    cred_two = AzureCredentialManager.get_credential(cache_name=cache_name_2)

    try:
        assert cred_one is not cred_two
    finally:
        AzureCredentialManager._credential_cache.pop(cache_name_1, None)
        AzureCredentialManager._credential_cache.pop(cache_name_2, None)
