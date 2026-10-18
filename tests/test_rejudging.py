"""Offline contract tests; no Azure client or credentials are needed."""

import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from evaluation import rejudging as judge


def saved(tmp_path, variant="naive", run=1, **extra):
    path = tmp_path / "sources" / "task" / "model" / f"run_{run}_{variant}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"pattern": {"key": "private_task", "logic": "PRIVATE_LOGIC", "subcategory": "PRIVATE_CATEGORY",
                           "source_pattern_id": "private_id", "task_description": "Candidate description",
                           "reference_notes": "UNVERIFIED", "output": "Candidate format"},
               "variant": variant, "run_index": run, "model_key": "PRIVATE_MODEL",
               "prompt": "Value: 7", "output": "The answer is 7.", **extra}
    if payload.get("cohort", "original") != "original":
        payload["artifact_sha256"] = judge.digest(payload)
    path.write_text(json.dumps(payload))
    return path


def prepared(tmp_path, *, approved=True, **saved_fields):
    source = saved(tmp_path, **saved_fields)
    collection = judge.collect_responses([source.parent.parent.parent])
    audit = judge.draft_reference_audit(collection["records"])
    if approved:
        item = audit["tasks"]["private_task"]
        item.update(status="approved", reviewed_by="reviewer", reviewed_at="2026-10-18", audit_note="Reviewed source and requirements",
                    common_task="Return the given number", input_facts="Value: 7", reference_facts=["The number is 7"],
                    common_requirements=["Return 7"], input_checks=["Value: 7"],
                    format_requirements={v: ["A readable answer; no special format required"] for v in judge.VARIANTS})
    plan = judge.build_plan(collection, audit)
    path = tmp_path / "judging-v3" / "plan.json"
    judge.write_new_json(path, plan)
    return source, path, plan


def rating():
    return {"scores": {m: {"score": 5, "rationale": "Meets requirement", "evidence_quotes": ["7"]} for m in judge.METRICS},
            "answer_status": "answered", "appropriate_clarification": False, "needs_human_review": False, "review_reasons": []}


class FakeRuntime:
    def __init__(self, text=None, status="completed"):
        self.calls = []
        self.text = text if text is not None else json.dumps(rating())
        self.status = status
        self.deployment = "test-deployment"
        self.returned_model = "test-model"
        self.mutate_request = False
        self.reasoning_effort = "max"
        self.returned_reasoning_effort = None

    def resolve_model(self, model_key):
        return SimpleNamespace(deployment=self.deployment, base_url="https://example.invalid/v1/", auth_mode="api_key",
                               spec=SimpleNamespace(use_responses_api=True, supports_temperature_zero=False, reasoning_effort=self.reasoning_effort))

    def generate_messages(self, model_key, messages, *, json_schema):
        self.calls.append((model_key, messages, json_schema))
        request = judge.expected_judge_request(judge.resolved_config(self, model_key), messages, json_schema)
        if self.mutate_request:
            request["input"] = [{"role": "user", "content": "changed"}]
        return {"text": self.text, "status": self.status, "reasoning_effort": self.returned_reasoning_effort or self.reasoning_effort, "requested_deployment": self.deployment,
                "returned_model": self.returned_model, "request": request, "raw_response": {"text": self.text},
                "base_url": "https://example.invalid/v1/", "auth_mode": "api_key", "api": "responses", "temperature": None}


@pytest.mark.parametrize("effort", ["medium", "xhigh"])
def test_lower_reasoning_is_rejected_before_request(tmp_path, effort):
    _, path, plan = prepared(tmp_path)
    assert plan["reasoning_effort"] == "max"
    runtime = FakeRuntime()
    runtime.reasoning_effort = effort
    with pytest.raises(ValueError, match="Responses with max reasoning"):
        judge.execute_plan(path, runtime)
    assert not runtime.calls
    assert not (path.parent / "execution_config.json").exists()


def test_reported_reasoning_mismatch_is_saved_not_scored(tmp_path):
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime()
    runtime.returned_reasoning_effort = "medium"
    with pytest.raises(ValueError, match="Actual judge request/settings"):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 1
    assert list((path.parent / "raw_judgements").glob("*.json"))
    assert not (path.parent / "ratings").exists()


def test_pending_audit_blocks_every_request(tmp_path):
    _, path, plan = prepared(tmp_path, approved=False)
    runtime = FakeRuntime()
    assert not plan["ready_for_execution"]
    assert plan["jobs"][0]["messages"] is None
    with pytest.raises(ValueError, match="audit is incomplete"):
        judge.execute_plan(path, runtime)
    assert not runtime.calls


@pytest.mark.parametrize("old_version", ["single-response-judge-v1", "single-response-judge-v2"])
def test_v3_uses_astra_and_blocks_old_audits(tmp_path, old_version):
    _, _, plan = prepared(tmp_path)
    assert plan["version"] == "single-response-judge-v3"
    assert plan["judge_model"] == "gpt-6-astra"
    assert plan["reasoning_effort"] == "max"
    audit = deepcopy(plan["reference_audit"])
    audit["version"] = old_version
    audit.pop("answer_status_policy")
    collection = judge.collect_responses([tmp_path / "sources"])
    blocked = judge.build_plan(collection, audit)
    assert not blocked["ready_for_execution"]
    assert blocked["jobs"][0]["messages"] is None
    assert any("current protocol, formatting policy and answer-status policy" in p for p in blocked["audit_problems"])


@pytest.mark.parametrize("old_version", ["single-response-judge-v1", "single-response-judge-v2"])
def test_old_plan_is_not_reused_under_v3(tmp_path, old_version):
    _, path, plan = prepared(tmp_path)
    plan["version"] = old_version
    plan["plan_sha256"] = judge.digest({k: v for k, v in plan.items() if k != "plan_sha256"})
    path.write_text(json.dumps(plan))
    runtime = FakeRuntime()
    with pytest.raises(ValueError, match="integrity/version"):
        judge.execute_plan(path, runtime)
    assert not runtime.calls


@pytest.mark.parametrize("policy", [None, {"version": "obsolete"}])
def test_current_version_audit_still_requires_matching_answer_status_policy(tmp_path, policy):
    _, _, plan = prepared(tmp_path)
    audit = deepcopy(plan["reference_audit"])
    audit["answer_status_policy"] = policy
    blocked = judge.build_plan(judge.collect_responses([tmp_path / "sources"]), audit)
    assert not blocked["ready_for_execution"]
    assert all(job["messages"] is None for job in blocked["jobs"])
    assert any("answer-status policy" in p for p in blocked["audit_problems"])


def test_current_version_plan_cannot_change_answer_status_policy(tmp_path):
    _, path, plan = prepared(tmp_path)
    plan["answer_status_policy"] = {"version": "obsolete"}
    plan["plan_sha256"] = judge.digest({k: v for k, v in plan.items() if k != "plan_sha256"})
    path.write_text(json.dumps(plan))
    runtime = FakeRuntime()
    with pytest.raises(ValueError, match="Runner/runtime/rubric changed"):
        judge.execute_plan(path, runtime)
    assert not runtime.calls


def test_answer_status_policy_is_shared_by_schema_prompt_plan_and_audit(tmp_path):
    _, _, plan = prepared(tmp_path)
    policy = judge.ANSWER_STATUS_POLICY
    assert plan["answer_status_policy"] == policy
    assert plan["reference_audit"]["answer_status_policy"] == policy
    system, user = plan["jobs"][0]["messages"]
    assert json.loads(user["content"])["answer_status_policy"] == policy
    assert json.dumps(policy, ensure_ascii=False, sort_keys=True) in system["content"]
    properties = plan["json_schema"]["schema"]["properties"]
    for key in ("basis", "answered", "clarification", "no_answer", "hypotheticals"):
        assert policy[key] in properties["answer_status"]["description"]
    assert properties["appropriate_clarification"]["description"] == policy["appropriate_clarification"]
    # Check the distinctions without pinning the entire human-readable wording.
    assert "wrong or unsupported" in policy["answered"]
    assert "follow-up" in policy["appropriate_clarification"]
    assert "actual task asks for an illustration" in policy["hypotheticals"]
    assert "Unmarked invented task inputs" in policy["hypotheticals"]


@pytest.mark.parametrize("answer_status", ["answered", "no_answer"])
def test_contradictory_clarification_flag_is_preserved_without_rating(tmp_path, answer_status):
    _, path, _ = prepared(tmp_path)
    value = rating()
    value.update(answer_status=answer_status, appropriate_clarification=True)
    if answer_status == "no_answer":
        value["scores"]["accuracy"]["score"] = 1
        value["scores"]["completeness"]["score"] = 1
    runtime = FakeRuntime(json.dumps(value))
    with pytest.raises(ValueError, match="Clarification flag and status disagree"):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 1
    raw = json.loads(next((path.parent / "raw_judgements").glob("*.json")).read_text())
    assert json.loads(raw["runtime_result"]["text"]) == value
    assert not (path.parent / "ratings").exists()


def test_partial_actual_answer_with_question_accepts_false_flag(tmp_path):
    response = "The first result is 7. Please provide the second input."
    _, path, _ = prepared(tmp_path, output=response)
    value = rating()
    value["scores"]["accuracy"]["score"] = 3
    value["scores"]["completeness"]["score"] = 2
    runtime = FakeRuntime(json.dumps(value))
    assert judge.execute_plan(path, runtime) == 1
    result = json.loads(next((path.parent / "ratings").glob("*.json")).read_text())
    assert result["rating"]["answer_status"] == "answered"
    assert result["rating"]["appropriate_clarification"] is False


def test_wrong_actual_attempt_is_not_forced_to_no_answer():
    value = rating()
    value["scores"]["accuracy"]["score"] = 1
    value["scores"]["completeness"]["score"] = 1
    judge.validate_rating(value, "The answer is 7.")
    assert value["answer_status"] == "answered"


def test_hypothetical_illustration_and_missing_input_request_accept_true_flag(tmp_path):
    response = "Please supply the actual number. For illustration only, a hypothetical input of 7 would return 7."
    _, path, plan = prepared(tmp_path, output=response, prompt="Return the number when supplied.")
    assert json.loads(plan["jobs"][0]["messages"][1]["content"])["essential_input_status"] == "missing"
    value = rating()
    value.update(answer_status="clarification", appropriate_clarification=True)
    value["scores"]["accuracy"]["score"] = 1
    value["scores"]["completeness"]["score"] = 1
    assert judge.execute_plan(path, FakeRuntime(json.dumps(value))) == 1
    result = json.loads(next((path.parent / "ratings").glob("*.json")).read_text())
    assert result["rating"]["appropriate_clarification"] is True
    assert result["rating"]["scores"]["fabrication_avoidance"]["score"] == 5
    assert result["rating"]["scores"]["formatting"]["score"] == 5


def test_clarification_format_policy_is_shared_without_answer_only_penalty(tmp_path):
    _, _, plan = prepared(tmp_path)
    item = deepcopy(plan["reference_audit"]["tasks"]["private_task"])
    item["input_checks"] = ["missing required input"]
    item["format_requirements"] = {v: ["Return the computed number only"] for v in judge.VARIANTS}
    record = judge.collect_responses([tmp_path / "sources"])["records"][0]
    record["output"] = "Please supply the missing number."
    for variant in judge.VARIANTS:
        record["variant"] = variant
        system, user = judge.build_messages(record, item)
        data = json.loads(user["content"])
        assert data["formatting_policy"] == judge.FORMAT_POLICY
        assert data["essential_input_status"] == "missing"
        assert "Missing substantive task content alone is not a formatting failure" in system["content"]
        assert "need not follow answer-only output constraints" in system["content"]
        assert "accuracy 1 and completeness 1" in system["content"]
    value = rating()
    value.update(answer_status="clarification", appropriate_clarification=True)
    for metric in value["scores"]:
        value["scores"][metric]["evidence_quotes"] = []
    value["scores"]["accuracy"]["score"] = 1
    value["scores"]["completeness"]["score"] = 1
    judge.validate_rating(value, record["output"])
    assert value["scores"]["formatting"]["score"] == 5


@pytest.mark.parametrize("answer_status", ["clarification", "no_answer"])
def test_nonanswer_attainment_violation_is_preserved_not_scored(tmp_path, answer_status):
    _, path, _ = prepared(tmp_path)
    value = rating()
    value.update(answer_status=answer_status, appropriate_clarification=answer_status == "clarification")
    with pytest.raises(ValueError, match="No substantive answer"):
        judge.execute_plan(path, FakeRuntime(json.dumps(value)))
    assert list((path.parent / "raw_judgements").glob("*.json"))
    assert not (path.parent / "ratings").exists()


def test_payload_masks_metadata_and_uses_applicable_formats(tmp_path):
    _, _, plan = prepared(tmp_path)
    text = json.dumps(plan["jobs"][0]["messages"])
    for forbidden in ("PRIVATE_MODEL", "PRIVATE_LOGIC", "PRIVATE_CATEGORY", "private_task", "private_id", "UNVERIFIED", "naive", "PEIL"):
        assert forbidden not in text
    data = json.loads(plan["jobs"][0]["messages"][1]["content"])
    assert data["applicable_format_requirements"] == ["A readable answer; no special format required"]
    assert data["essential_input_status"] == "present_or_not_required"


def test_run_scope_and_schedule_are_deterministic(tmp_path):
    for run in (1, 2, 3):
        for variant in judge.VARIANTS:
            saved(tmp_path, variant, run)
    root = tmp_path / "sources"
    assert len(judge.collect_responses([root], "run1")["records"]) == 3
    collection = judge.collect_responses([root])
    audit = judge.draft_reference_audit(collection["records"])
    a = judge.build_plan(collection, audit, seed=42)
    collection["records"].reverse()
    b = judge.build_plan(collection, audit, seed=42)
    assert a == b
    c = judge.build_plan(collection, audit, seed=43)
    assert [j["job_id"] for j in a["jobs"]] != [j["job_id"] for j in c["jobs"]]


def test_raw_is_preserved_before_bad_json_rejected(tmp_path):
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime("not JSON")
    with pytest.raises(json.JSONDecodeError):
        judge.execute_plan(path, runtime)
    assert len(list((path.parent / "raw_judgements").glob("*.json"))) == 1
    assert not (path.parent / "ratings").exists()
    with pytest.raises(FileExistsError):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 1


def test_incomplete_response_is_saved_not_scored(tmp_path):
    _, path, _ = prepared(tmp_path)
    with pytest.raises(ValueError, match="Incomplete"):
        judge.execute_plan(path, FakeRuntime(status="incomplete"))
    assert list((path.parent / "raw_judgements").glob("*.json"))
    assert not (path.parent / "ratings").exists()


def test_changed_source_stops_before_request(tmp_path):
    source, path, _ = prepared(tmp_path)
    source.write_text(source.read_text() + "\n")
    runtime = FakeRuntime()
    with pytest.raises(ValueError, match="Source changed"):
        judge.execute_plan(path, runtime)
    assert not runtime.calls


@pytest.mark.parametrize("score", [True, "5", 5.0, 0, 6])
def test_scores_are_not_coerced(score):
    value = rating()
    value["scores"]["accuracy"]["score"] = score
    with pytest.raises(ValueError, match="integer score"):
        judge.validate_rating(value, "The answer is 7.")


def test_fabricated_evidence_and_extra_fields_rejected():
    value = rating()
    value["scores"]["accuracy"]["evidence_quotes"] = ["not in the response"]
    with pytest.raises(ValueError, match="quote"):
        judge.validate_rating(value, "The answer is 7.")
    value = rating()
    value["bonus"] = 5
    with pytest.raises(ValueError, match="unexpected"):
        judge.validate_rating(value, "The answer is 7.")


def test_successful_rating_is_separate_and_never_overwritten(tmp_path):
    source, path, _ = prepared(tmp_path)
    original = source.read_bytes()
    runtime = FakeRuntime()
    assert judge.execute_plan(path, runtime) == 1
    result = json.loads(next((path.parent / "ratings").glob("*.json")).read_text())
    assert result["review_status"] == "no_flag"
    assert source.read_bytes() == original
    assert judge.execute_plan(path, runtime) == 0
    assert len(runtime.calls) == 1


def test_corrective_messages_and_ineligible_records(tmp_path):
    source = saved(tmp_path, prompt=None, messages=[{"role": "system", "content": "Instructions"}, {"role": "user", "content": "Value: 7"}], cohort="corrective-six-v1")
    target = tmp_path / "corrective" / "generations" / "job.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    collection = judge.collect_responses([target.parent.parent])
    assert collection["records"][0]["submitted_prompt"] == "Instructions\nValue: 7"
    saved(tmp_path, "peil_labelled", analysis_eligible=False)
    collection = judge.collect_responses([tmp_path / "sources"])
    assert len(collection["records"]) == 1
    assert len(collection["skipped"]) == 1


def test_missing_inputs_are_explicit_and_format_requirements_match(tmp_path):
    _, _, plan = prepared(tmp_path)
    audit = deepcopy(plan["reference_audit"])
    item = audit["tasks"]["private_task"]
    item["input_checks"] = ["absent input"]
    record = judge.collect_responses([tmp_path / "sources"])["records"][0]
    data = json.loads(judge.build_messages(record, item)[1]["content"])
    assert data["essential_input_status"] == "missing"
    item["format_requirements"]["peil_unlabelled"] = ["Different"]
    assert any("identical formatting" in p for p in judge.audit_problems("private_task", audit))


def test_unknown_attempt_cannot_be_retried(tmp_path):
    _, path, plan = prepared(tmp_path)
    attempt = path.parent / "attempts" / f"{plan['jobs'][0]['job_id']}.json"
    judge.write_new_json(attempt, {"state": "started"})
    runtime = FakeRuntime()
    with pytest.raises(FileExistsError, match="attempt"):
        judge.execute_plan(path, runtime)
    assert not runtime.calls


def test_request_mismatch_is_preserved_not_scored(tmp_path):
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime()
    runtime.mutate_request = True
    with pytest.raises(ValueError, match="Actual judge request"):
        judge.execute_plan(path, runtime)
    assert list((path.parent / "attempts").glob("*.json"))
    assert list((path.parent / "raw_judgements").glob("*.json"))
    assert not (path.parent / "ratings").exists()


def test_deployment_change_cannot_resume(tmp_path):
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime()
    judge.execute_plan(path, runtime)
    runtime.deployment = "different-deployment"
    with pytest.raises(ValueError, match="deployment/settings/dependencies changed"):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 1


def test_limit_resume_and_returned_model_drift(tmp_path):
    saved(tmp_path, "peil_labelled")
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime()
    assert judge.execute_plan(path, runtime, max_jobs=1) == 1
    runtime.returned_model = "changed-provider-build"
    with pytest.raises(ValueError, match="Returned judge model changed"):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 2
    assert len(list((path.parent / "ratings").glob("*.json"))) == 1
    assert len(list((path.parent / "raw_judgements").glob("*.json"))) == 2


def test_protocol_or_dependency_change_stops_resume(tmp_path, monkeypatch):
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime()
    judge.execute_plan(path, runtime)
    monkeypatch.setattr(judge, "runtime_versions", lambda: {"python": "different"})
    with pytest.raises(ValueError, match="dependencies changed"):
        judge.execute_plan(path, runtime)
    monkeypatch.setattr(judge, "protocol_sources", lambda: {"changed": "hash"})
    with pytest.raises(ValueError, match="Runner/runtime/rubric changed"):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 1


def test_historical_output_directories_are_protected():
    protected = Path(judge.__file__).parent / "results" / "unwanted.json"
    with pytest.raises(ValueError, match="historical"):
        judge.write_new_json(protected, {})
    assert not protected.exists()


def test_corrective_integrity_is_checked(tmp_path):
    source = saved(tmp_path, cohort="corrective-six-v1")
    payload = json.loads(source.read_text())
    payload["output"] = "tampered"
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="artifact integrity"):
        judge.collect_responses([tmp_path / "sources"])


def test_review_flags_are_preserved_not_silent_exclusions(tmp_path):
    _, path, _ = prepared(tmp_path)
    value = rating()
    value.update(needs_human_review=True, review_reasons=["Reference ambiguity needs adjudication"])
    assert judge.execute_plan(path, FakeRuntime(json.dumps(value))) == 1
    result = json.loads(next((path.parent / "ratings").glob("*.json")).read_text())
    assert result["review_status"] == "needs_resolution"
    assert "analysis_eligible" not in result


def test_edited_rating_cannot_resume(tmp_path):
    _, path, _ = prepared(tmp_path)
    runtime = FakeRuntime()
    judge.execute_plan(path, runtime)
    rating_path = next((path.parent / "ratings").glob("*.json"))
    result = json.loads(rating_path.read_text())
    result["rating"]["scores"]["accuracy"]["score"] = 4
    rating_path.write_text(json.dumps(result))
    with pytest.raises(ValueError, match="differs from the saved raw"):
        judge.execute_plan(path, runtime)
    assert len(runtime.calls) == 1


def test_provider_error_text_is_not_exposed(tmp_path):
    _, path, _ = prepared(tmp_path)

    class FailingRuntime(FakeRuntime):
        def generate_messages(self, *args, **kwargs):
            error = RuntimeError("sensitive-provider-detail")
            error.status_code = 429
            error.request_id = "request-example"
            raise error

    with pytest.raises(RuntimeError, match="audit saved") as caught:
        judge.execute_plan(path, FailingRuntime())
    assert "sensitive-provider-detail" not in str(caught.value)
    raw = json.loads(next((path.parent / "raw_judgements").glob("*.json")).read_text())
    assert raw["http_status"] == 429
    assert raw["request_id"] == "request-example"
    assert "sensitive-provider-detail" not in json.dumps(raw)
