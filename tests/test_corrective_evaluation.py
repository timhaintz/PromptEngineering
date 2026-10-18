"""Offline checks for task preservation, scope, immutable artifacts and resume safety."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from evaluation import corrective_evaluation as corrective


class FakeRuntime:
    def __init__(self, *, fail=False, incomplete=False, deployment="test-deployment", drift=False):
        self.calls = 0
        self.fail = fail
        self.incomplete = incomplete
        self.deployment = deployment
        self.drift = drift

    def resolve_model(self, key):
        return SimpleNamespace(deployment=self.deployment, base_url="https://example.invalid/openai/v1/",
                               auth_mode="api_key", spec=SimpleNamespace(use_responses_api=True,
                               supports_temperature_zero=True, reasoning_effort=None))

    def generate_messages(self, key, messages):
        self.calls += 1
        if self.fail:
            raise RuntimeError("Do not copy this potentially sensitive exception text")
        config = corrective.resolved_config(self, key)
        return {"text": "" if self.incomplete else "Recorded answer",
                "request": corrective.expected_request(config, messages),
                "raw_response": {"id": str(self.calls), "status": "incomplete" if self.incomplete else "completed"},
                "requested_deployment": self.deployment, "model": self.deployment,
                "returned_model": "different-version" if self.drift and self.calls > 1 else "test-version",
                "response_id": str(self.calls), "request_id": f"request-{self.calls}", "usage": {},
                "api": "responses", "auth_mode": "api_key", "base_url": "https://example.invalid/openai/v1/",
                "reasoning_effort": None, "temperature": 0.0,
                "status": "incomplete" if self.incomplete else "completed"}


def plan(tmp_path):
    corrective.save_plan(tmp_path, ["gpt-4.1"])
    return tmp_path


def test_explicit_sol_cohort_does_not_change_historical_generator_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(corrective, "make_runtime", lambda *a: pytest.fail("Plan loaded a runtime"))
    assert corrective.main(["plan", "--output-dir", str(tmp_path), "--models", "gpt-6.1-sol"]) == 0
    manifest = corrective.read_json(tmp_path / "manifest.json")
    assert manifest["model_keys"] == ["gpt-6.1-sol"]
    assert len(manifest["jobs"]) == 54
    assert {j["model_key"] for j in manifest["jobs"]} == {"gpt-6.1-sol"}
    assert manifest["model_specs"]["gpt-6.1-sol"]["reasoning_effort"] == "max"
    assert corrective.DEFAULT_MODELS == ("gpt-4.1", "gpt-5", "grok-4-fast-reasoning", "deepseek-r1-0528")


def test_offline_plan_preserves_exact_saved_prompts_and_six_task_scope(tmp_path, monkeypatch):
    monkeypatch.setattr(corrective, "make_runtime", lambda *a: pytest.fail("Plan loaded a runtime"))
    assert corrective.main(["plan", "--output-dir", str(tmp_path)]) == 0
    manifest = corrective.read_json(tmp_path / "manifest.json")
    assert len(manifest["jobs"]) == 216
    assert len({j["job_id"] for j in manifest["jobs"]}) == 216
    assert set(manifest["tasks"]) == set(corrective.TASK_IDS)
    for task_key, task in manifest["tasks"].items():
        for variant in corrective.VARIANTS:
            archived = corrective.read_json(corrective.REPO / "evaluation/results" / task_key / "gpt-4.1" / f"run_1_{variant}.json")
            messages = corrective.messages_for(task, variant)
            if variant == "naive":
                assert messages == [{"role": "user", "content": archived["prompt"]}]
            else:
                assert messages[0] == {"role": "system", "content": archived["prompt"]}
                assert messages[1] == {"role": "user", "content": task["naive_request"]}
                assert task["reference_notes"] not in messages[0]["content"]
    assert corrective.save_plan(tmp_path) == manifest
    with pytest.raises(ValueError, match="manifest differs"):
        corrective.save_plan(tmp_path, seed=1)


@pytest.mark.parametrize("old", ["evaluation/results", "evaluation/summary", "evaluation/supplementary/results"])
def test_historical_destination_rejected(old):
    with pytest.raises(ValueError, match="historical"):
        corrective.safe_output_dir(corrective.REPO / old / "new")


def test_generation_then_resume_uses_frozen_artifacts_without_new_calls(tmp_path):
    runtime = FakeRuntime()
    plan(tmp_path)
    manifest_bytes = (tmp_path / "manifest.json").read_bytes()
    assert corrective.execute(tmp_path, runtime) == {"generated": 54, "reused": 0}
    originals = {p: p.read_bytes() for p in (tmp_path / "generations").glob("*.json")}
    assert corrective.execute(tmp_path, runtime) == {"generated": 0, "reused": 54}
    assert runtime.calls == 54
    assert all(p.read_bytes() == content for p, content in originals.items())
    assert (tmp_path / "manifest.json").read_bytes() == manifest_bytes
    with pytest.raises(ValueError, match="settings changed"):
        corrective.execute(tmp_path, FakeRuntime(deployment="new-deployment"))


def test_tampered_manifest_prevents_any_generation(tmp_path):
    plan(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = corrective.read_json(manifest_path)
    manifest["jobs"][0]["messages"][-1]["content"] = "Changed input"
    manifest_path.write_text(json.dumps(manifest))
    runtime = FakeRuntime()
    with pytest.raises(ValueError, match="mismatch"):
        corrective.execute(tmp_path, runtime)
    assert runtime.calls == 0


def test_failure_is_audited_and_not_retried_or_leaked(tmp_path):
    plan(tmp_path)
    runtime = FakeRuntime(fail=True)
    with pytest.raises(RuntimeError, match="audit saved"):
        corrective.execute(tmp_path, runtime)
    failure = next((tmp_path / "failures").glob("*.json"))
    assert "potentially sensitive" not in failure.read_text()
    assert corrective.read_json(failure)["error_type"] == "RuntimeError"
    with pytest.raises(ValueError, match="earlier attempt"):
        corrective.execute(tmp_path, runtime)
    assert runtime.calls == 1


def test_incomplete_response_preserves_raw_data_and_blocks_resume(tmp_path):
    plan(tmp_path)
    runtime = FakeRuntime(incomplete=True)
    with pytest.raises(RuntimeError, match="result saved"):
        corrective.execute(tmp_path, runtime)
    record = corrective.read_json(next((tmp_path / "generations").glob("*.json")))
    assert record["raw_response"]["status"] == "incomplete"
    assert record["analysis_eligible"] is False
    with pytest.raises(ValueError, match="eligibility"):
        corrective.execute(tmp_path, runtime)
    assert runtime.calls == 1


def test_returned_model_drift_is_saved_but_excluded(tmp_path):
    plan(tmp_path)
    runtime = FakeRuntime(drift=True)
    with pytest.raises(RuntimeError, match="result saved"):
        corrective.execute(tmp_path, runtime)
    records = [corrective.read_json(p) for p in (tmp_path / "generations").glob("*.json")]
    assert len(records) == 2
    assert sum(r["analysis_eligible"] for r in records) == 1
    assert any(r["returned_model"] == "different-version" for r in records)


def test_explicit_three_generator_plan_preserves_balanced_six_task_scope(tmp_path, monkeypatch):
    from collections import Counter

    monkeypatch.setattr(corrective, "make_runtime", lambda *a: pytest.fail("Plan loaded a runtime"))
    keys = ["gpt-6.1-sol", "gpt-6-luna", "grok-4.7"]
    assert corrective.main(["plan", "--output-dir", str(tmp_path), "--models", ",".join(keys)]) == 0
    manifest = corrective.read_json(tmp_path / "manifest.json")
    assert manifest["model_keys"] == keys
    assert len(manifest["jobs"]) == len({job["job_id"] for job in manifest["jobs"]}) == 162
    assert Counter(job["model_key"] for job in manifest["jobs"]) == dict.fromkeys(keys, 54)
    assert Counter(job["pattern_key"] for job in manifest["jobs"]) == dict.fromkeys(corrective.TASK_IDS, 27)
    assert Counter(job["variant"] for job in manifest["jobs"]) == dict.fromkeys(corrective.VARIANTS, 54)
    assert Counter(job["run_index"] for job in manifest["jobs"]) == {1: 54, 2: 54, 3: 54}
    for key, effort in (("gpt-6.1-sol", "max"), ("gpt-6-luna", "max"), ("grok-4.7", None)):
        spec = manifest["model_specs"][key]
        assert (spec["use_responses_api"], spec["supports_temperature_zero"], spec["reasoning_effort"]) == (True, False, effort)
    assert corrective.DEFAULT_MODELS == ("gpt-4.1", "gpt-5", "grok-4-fast-reasoning", "deepseek-r1-0528")
