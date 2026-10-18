"""Verify recorded evaluation requests without contacting a provider."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from evaluation.chapter6_evaluation import (
    AzureModelRuntime, DEFAULT_EVALUATION_MODELS, DEFAULT_JUDGE_MODEL, MODEL_REGISTRY, ResolvedModel,
)


def runtime_with_response(monkeypatch, key, response):
    runtime = AzureModelRuntime("api_key")
    client = Mock()
    client.with_options.return_value = client
    client.responses.create.return_value = response
    client.chat.completions.create.return_value = response
    resolved = ResolvedModel(
        MODEL_REGISTRY[key], "https://example.openai.azure.com/openai/v1/",
        "test-deployment", "api_key", "not-a-real-key",
    )
    monkeypatch.setattr(runtime, "get_client", lambda model_key: (client, resolved))
    return runtime, client


@pytest.mark.parametrize("model_key", ["gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna"])
def test_new_models_record_roles_schema_max_reasoning_and_actual_model(monkeypatch, model_key):
    response = SimpleNamespace(
        output_text='{"score": 5}', usage=None, status="completed",
        model="reported-model-version", id="response-1", _request_id="request-1",
        model_dump=lambda **kwargs: {"model": "reported-model-version"},
    )
    runtime, client = runtime_with_response(monkeypatch, model_key, response)
    messages = [{"role": "system", "content": "Judge."}, {"role": "user", "content": "Evidence."}]
    schema = {"name": "rating", "schema": {"type": "object"}}
    result = runtime.generate_messages(model_key, messages, json_schema=schema)
    request = client.responses.create.call_args.kwargs
    assert request["input"] == messages
    assert request["reasoning"] == {"effort": "max", "summary": "auto"}
    assert "temperature" not in request
    assert request["text"]["format"]["strict"] is True
    assert result["request"] == request
    assert result["returned_model"] == "reported-model-version"
    assert result["requested_deployment"] == "test-deployment"
    assert result["request_id"] == "request-1"
    assert "not-a-real-key" not in str(result)
    client.with_options.assert_called_once_with(max_retries=0)
    assert DEFAULT_JUDGE_MODEL == "gpt-5.4-pro"
    assert MODEL_REGISTRY["gpt-5"].reasoning_effort == "medium"
    assert MODEL_REGISTRY["gpt-5.4-pro"].reasoning_effort == "medium"


def test_astra_uses_shared_resource_with_its_own_deployment(monkeypatch):
    monkeypatch.setenv("AZUREVSEASTUS2_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZUREVSEASTUS2_OPENAI_KEY", "not-a-real-key")
    monkeypatch.setenv("AZUREVSEASTUS2_OPENAI_GPT61SOL_MODEL", "sol-deployment")
    monkeypatch.setenv("AZUREVSEASTUS2_OPENAI_GPT6ASTRA_MODEL", "astra-deployment")
    resolved = AzureModelRuntime("api_key").resolve_model("gpt-6-astra")
    assert resolved.deployment == "astra-deployment"
    assert resolved.api_key_or_provider == "not-a-real-key"
    assert resolved.base_url == "https://example.openai.azure.com/openai/v1/"
    assert resolved.spec.reasoning_effort == "max"
    assert resolved.spec.use_responses_api is True
    assert resolved.spec.supports_temperature_zero is False


def test_historical_defaults_and_model_settings_are_preserved():
    assert DEFAULT_EVALUATION_MODELS == ["gpt-4.1", "gpt-5", "grok-4-fast-reasoning", "deepseek-r1-0528"]
    assert DEFAULT_JUDGE_MODEL == "gpt-5.4-pro"
    expected = {
        "gpt-4.1": ("AZUREVSEASTUS2_OPENAI_GPT41_MODEL", True, True, None),
        "gpt-5": ("AZUREVSEASTUS2_OPENAI_GPT52_MODEL", True, False, "medium"),
        "grok-4-fast-reasoning": ("AZUREVSEASTUS2_GROK4_FAST_REASONING_MODEL", False, True, None),
        "deepseek-r1-0528": ("AZUREVS_DEEPSEEK_R1_0528_MODEL", False, True, None),
        "deepseek-v3.2": ("AZUREVS_DEEPSEEK_V32_MODEL", False, True, None),
        "gpt-5.4-pro": ("AZUREVSEASTUS2_OPENAI_GPT54PRO_MODEL", True, False, "medium"),
        "gpt-6.1-sol": ("AZUREVSEASTUS2_OPENAI_GPT61SOL_MODEL", True, False, "max"),
        "embedding-3": ("AZUREVS_OPENAI_EMBEDDING3_MODEL", False, False, None),
    }
    for key, settings in expected.items():
        spec = MODEL_REGISTRY[key]
        assert (spec.deployment_env, spec.use_responses_api, spec.supports_temperature_zero, spec.reasoning_effort) == settings


def test_chat_preserves_system_message_and_temperature(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Answer"), finish_reason="stop")],
        usage=None, model="reported-chat-model", id="chat-1",
        model_dump=lambda **kwargs: {"choices": []},
    )
    runtime, client = runtime_with_response(monkeypatch, "grok-4-fast-reasoning", response)
    messages = [{"role": "system", "content": "Instructions"}, {"role": "user", "content": "Input"}]
    result = runtime.generate_messages("grok-4-fast-reasoning", messages)
    assert client.chat.completions.create.call_args.kwargs["messages"] == messages
    assert result["request"]["temperature"] == 0.0
    assert result["status"] == "stop"


def test_provider_error_has_no_retry_or_schema_fallback(monkeypatch):
    runtime, client = runtime_with_response(monkeypatch, "gpt-6.1-sol", None)
    client.responses.create.side_effect = RuntimeError("Unsupported schema")
    with pytest.raises(RuntimeError, match="Unsupported schema"):
        runtime.generate_messages("gpt-6.1-sol", [{"role": "user", "content": "Judge"}],
                                  json_schema={"name": "rating", "schema": {}})
    assert client.responses.create.call_count == 1
    assert "text" in client.responses.create.call_args.kwargs


def test_empty_chat_response_is_returned_for_audit(monkeypatch):
    response = SimpleNamespace(
        choices=[], usage=None, model="reported-chat-model", id="chat-empty",
        model_dump=lambda **kwargs: {"choices": []},
    )
    runtime, _ = runtime_with_response(monkeypatch, "grok-4-fast-reasoning", response)
    result = runtime.generate_messages("grok-4-fast-reasoning", [{"role": "user", "content": "Input"}])
    assert result["raw_response"] == {"choices": []}
    assert result["text"] == ""
    assert result["status"] is None


@pytest.mark.parametrize("messages", [[], [{"role": "tool", "content": "x"}],
                                     [{"role": "user", "content": ""}]])
def test_invalid_messages_fail_before_authentication(monkeypatch, messages):
    runtime = AzureModelRuntime("api_key")
    get_client = Mock(side_effect=AssertionError("No client should be created"))
    monkeypatch.setattr(runtime, "get_client", get_client)
    with pytest.raises(ValueError, match="role/content"):
        runtime.generate_messages("gpt-6.1-sol", messages)
    get_client.assert_not_called()


def test_grok47_uses_responses_without_optional_reasoning_or_temperature(monkeypatch):
    response = SimpleNamespace(
        output_text="Answer", usage=None, status="completed", model="grok-4.7", id="grok-response-1",
        model_dump=lambda **kwargs: {"model": "grok-4.7"},
    )
    runtime, client = runtime_with_response(monkeypatch, "grok-4.7", response)
    messages = [{"role": "system", "content": "Instructions"}, {"role": "user", "content": "Input"}]
    result = runtime.generate_messages("grok-4.7", messages)
    request = client.responses.create.call_args.kwargs
    assert request == {"model": "test-deployment", "input": messages}
    assert "reasoning" not in request
    assert result["api"] == "responses"
    assert result["reasoning_effort"] is None
    assert result["temperature"] is None
    assert result["returned_model"] == "grok-4.7"
    client.with_options.assert_called_once_with(max_retries=0)
    client.chat.completions.create.assert_not_called()


@pytest.mark.parametrize(("key", "deployment_env", "effort"), [
    ("gpt-6-luna", "AZUREVSEASTUS2_OPENAI_GPT6LUNA_MODEL", "max"),
    ("grok-4.7", "AZUREVSEASTUS2_GROK47_MODEL", None),
])
def test_current_generators_resolve_distinct_deployment_names(monkeypatch, key, deployment_env, effort):
    monkeypatch.setenv("AZUREVSEASTUS2_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZUREVSEASTUS2_OPENAI_KEY", "not-a-real-key")
    monkeypatch.setenv(deployment_env, f"test-{key}-deployment")
    resolved = AzureModelRuntime("api_key").resolve_model(key)
    assert resolved.deployment == f"test-{key}-deployment"
    assert resolved.base_url == "https://example.openai.azure.com/openai/v1/"
    assert (resolved.spec.use_responses_api, resolved.spec.supports_temperature_zero,
            resolved.spec.reasoning_effort) == (True, False, effort)
