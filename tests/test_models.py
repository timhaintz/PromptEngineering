"""Unit tests validating the model registry configuration helpers."""

from typing import Iterable

import pytest

import azure_models
from azure_models import ModelRegistry, ModelType


@pytest.mark.parametrize(
    ("model_name", "expected_type"),
    [
        ("gpt-4.1", ModelType.AZURE_OPENAI),
        ("gpt-5", ModelType.AZURE_OPENAI),
        ("grok-3", ModelType.AZURE_FOUNDRY),
        ("deepseek-r1", ModelType.DIRECT_API),
    ],
)
def test_model_registry_contains_expected_models(model_name: str, expected_type: ModelType):
    """The registry should return the registered config with the expected type."""
    config = ModelRegistry.get_model(model_name)
    assert config.name == model_name
    assert config.model_type == expected_type


def test_get_available_models_includes_key_variants():
    models: Iterable[str] = azure_models.get_available_models()
    assert "gpt-4.1" in models
    assert "deepseek-r1" in models


def test_get_model_info_returns_metadata():
    info = azure_models.get_model_info("gpt-4.1")
    assert info["name"] == "gpt-4.1"
    assert info["type"] == ModelType.AZURE_OPENAI.value
    assert "supported_features" in info
