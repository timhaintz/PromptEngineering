"""Regression-style unit tests for lightweight Azure model helpers."""

import azure_models


def test_supports_streaming_matches_registry_entry():
    assert azure_models.supports_streaming("gpt-4.1") is True
    assert azure_models.supports_streaming("grok-3") is True
    assert azure_models.supports_streaming("deepseek-r1") is True
    assert azure_models.supports_streaming("embedding-3") is False


def test_get_autogen_config_returns_expected_keys():
    config = azure_models.get_autogen_config("gpt-4.1")
    assert "model" in config
    assert "azure_endpoint" in config
    assert "api_version" in config
