"""Exercise the ordinary AG2 entry point without model or Docker execution."""

import json
from pathlib import Path
import runpy
import sys

import pytest


ENTRYPOINT = Path(__file__).resolve().parents[1] / "autogen02_two_agents.py"
DEFAULT_PROMPT = "Please tell me the weather in Seattle"


@pytest.mark.parametrize("config_source", ["environment_json", "environment_path", "default_file"])
@pytest.mark.parametrize("prompt", [None, "Return a short local compatibility check."])
def test_two_agent_entrypoint_loads_config_and_dispatches_prompt(tmp_path, monkeypatch, config_source, prompt):
    from autogen import AssistantAgent, UserProxyAgent
    from autogen.agentchat import conversable_agent

    # Real AG2 config loading and constructors must work after retrieval retires.
    configs = [
        {"model": f"offline-model-{index}", "api_key": "offline-placeholder",
         "base_url": "https://example.invalid/v1/"}
        for index in range(6)
    ]
    serialized = json.dumps(configs)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OAI_CONFIG_LIST", raising=False)
    if config_source == "environment_json":
        monkeypatch.setenv("OAI_CONFIG_LIST", serialized)
    elif config_source == "environment_path":
        config_file = tmp_path / "local-models.json"
        config_file.write_text(serialized, encoding="utf-8")
        monkeypatch.setenv("OAI_CONFIG_LIST", str(config_file))
    else:
        (tmp_path / "OAI_CONFIG_LIST").write_text(serialized, encoding="utf-8")

    docker_checks = []
    dispatches = []

    def check_docker(use_docker):
        docker_checks.append(use_docker)

    def capture_dispatch(sender, recipient, **kwargs):
        dispatches.append((sender, recipient, kwargs))

    # Keep constructors/configuration real; stop at the two external boundaries.
    monkeypatch.setattr(conversable_agent, "check_can_use_docker_or_throw", check_docker)
    monkeypatch.setattr(UserProxyAgent, "initiate_chat", capture_dispatch)
    argv = [str(ENTRYPOINT)]
    if prompt is not None:
        argv.extend(["--prompt", prompt])
    monkeypatch.setattr(sys, "argv", argv)

    namespace = runpy.run_path(str(ENTRYPOINT), run_name="__main__")

    assert len(dispatches) == 1
    sender, recipient, kwargs = dispatches[0]
    assert isinstance(sender, UserProxyAgent)
    assert isinstance(recipient, AssistantAgent)
    assert sender is namespace["user_proxy"]
    assert recipient is namespace["assistant"]
    assert kwargs == {"message": DEFAULT_PROMPT if prompt is None else prompt}
    assert [config["model"] for config in namespace["config_list"]] == [
        config["model"] for config in configs
    ]
    selected = recipient.llm_config.model_dump()["config_list"]
    assert len(selected) == 1
    assert selected[0]["model"] == "offline-model-5"
    assert selected[0]["api_key"] == "offline-placeholder"
    assert selected[0]["base_url"] == "https://example.invalid/v1/"
    assert sender.name == "user_proxy"
    assert recipient.name == "assistant"
    assert sender.llm_config is False
    assert sender.human_input_mode == "ALWAYS"
    assert sender.use_docker is True
    assert sender._code_execution_config["work_dir"] == "AutoGen/TwoAgents"
    assert docker_checks == [True]


def test_ag2_agents_exchange_one_local_turn_without_retrieval():
    from autogen import AssistantAgent, UserProxyAgent

    assistant = AssistantAgent(
        "local_assistant", llm_config=False, code_execution_config=False,
        default_auto_reply="Local reply.",
    )
    user_proxy = UserProxyAgent(
        "local_user", llm_config=False, code_execution_config=False,
        human_input_mode="NEVER",
    )

    result = user_proxy.initiate_chat(
        assistant, message="Local question.", max_turns=1, silent=True,
        summary_method="last_msg", cache=None,
    )

    assert [message["content"] for message in result.chat_history] == [
        "Local question.", "Local reply.",
    ]
    assert result.summary == "Local reply."
    assert result.human_input == []
