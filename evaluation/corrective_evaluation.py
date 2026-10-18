"""Versioned six-task input-restoration evaluation; planning is entirely offline."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SOURCE = Path("evaluation/chapter6_evaluation.py")
PROTOCOL = "corrective-six-v1"
VARIANTS = ("naive", "peil_labelled", "peil_unlabelled")
TASK_IDS = {
    "across_comparison_attendance": "20-2-0",
    "at_calculation_math_word_problems": "31-0-0",
    "at_assessment_opinion_verification": "37-0-0",
    "beyond_logical_reasoning_premise_question": "33-1-1",
    "beyond_hypothesise_theory_of_mind": "32-26-0",
    "out_decomposed_prompting_letter_concat": "6-0-0",
}
DEFAULT_MODELS = ("gpt-4.1", "gpt-5", "grok-4-fast-reasoning", "deepseek-r1-0528")


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_new(path: Path, value: dict[str, Any]) -> None:
    """Never replace an existing artifact, including an interrupted partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_output_dir(path: Path, repo: Path = REPO) -> Path:
    resolved = path.resolve()
    for old in ("evaluation/results", "evaluation/summary", "evaluation/supplementary/results", "evaluation/supplementary/summary"):
        root = (repo / old).resolve()
        if resolved == root or root in resolved.parents:
            raise ValueError("Corrective output must be outside historical result and summary directories")
    return resolved


def source_definitions(repo: Path = REPO) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], str]:
    """Read literals without importing the legacy module or loading credentials."""
    raw = (repo / SOURCE).read_bytes()
    tree = ast.parse(raw.decode())
    tasks: dict[str, dict[str, Any]] = {}
    models: dict[str, dict[str, Any]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id not in {"PatternDefinition", "ModelSpec"}:
            continue
        fields = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
        if node.func.id == "ModelSpec":
            models[fields["key"]] = fields
        elif fields["key"] in TASK_IDS:
            tasks[fields["key"]] = fields
    if set(tasks) != set(TASK_IDS):
        raise ValueError("Expected exactly the six specified source tasks")
    for key, task in tasks.items():
        if task["source_pattern_id"] != TASK_IDS[key] or task["task_material"] != "":
            raise ValueError(f"Source task changed; review the corrective protocol: {key}")
        if not task["naive_request"].strip():
            raise ValueError(f"Missing original instance input: {key}")
    # Convert tuples to the JSON representation used by saved generation files.
    return json.loads(json.dumps(tasks)), models, hashlib.sha256(raw).hexdigest()


def messages_for(task: dict[str, Any], variant: str) -> list[dict[str, str]]:
    """Keep the exact original naive request; restore that input to PEIL's user turn."""
    user = {"role": "user", "content": task["naive_request"]}
    if variant == "naive":
        return [user]
    instructions = "\n".join(f"{i}. {text}" for i, text in enumerate(task["instructions"], 1))
    if variant == "peil_labelled":
        parts = [f"Role: {task['role'].strip()}", f"Context: {task['context'].strip()}",
                 f"Instructions:\n{instructions}", f"Techniques: {task['technique'].strip()}",
                 f"Output: {task['output'].strip()}"]
    elif variant == "peil_unlabelled":
        parts = [task["role"].strip(), task["context"].strip(), instructions,
                 task["technique"].strip(), task["output"].strip()]
    else:
        raise ValueError(f"Unknown variant: {variant}")
    return [{"role": "system", "content": "\n\n".join(parts)}, user]


def build_manifest(models: list[str] | tuple[str, ...] = DEFAULT_MODELS, seed: int = 20261018,
                   repo: Path = REPO) -> dict[str, Any]:
    tasks, model_specs, source_sha = source_definitions(repo)
    if not models or len(set(models)) != len(models) or any(m not in model_specs for m in models):
        raise ValueError("Select distinct model keys present in the source registry")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    jobs = []
    for task_key in TASK_IDS:
        for model_key in models:
            for run_index in range(1, 4):
                for variant in VARIANTS:
                    job = {"pattern_key": task_key, "source_pattern_id": TASK_IDS[task_key],
                           "model_key": model_key, "run_index": run_index, "variant": variant,
                           "messages": messages_for(tasks[task_key], variant)}
                    job["job_id"] = digest(job)
                    jobs.append(job)
    random.Random(seed).shuffle(jobs)
    manifest = {
        "schema_version": 1, "protocol_id": PROTOCOL, "cohort": PROTOCOL,
        "source": {"path": str(SOURCE), "git_commit": commit, "sha256": source_sha,
                   "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "design": {"runs": 3, "variants": list(VARIANTS), "seed": seed,
                   "schedule": "Explicit seeded shuffle of task/model/run/variant jobs",
                   "scope": "Six original task instances; no regeneration of other tasks",
                   "interpretation": "Intended configuration with restored input; role and input effects are not isolated"},
        "taxonomy": "Original task-level metadata retained as historical assignments; no parent remapping",
        "model_keys": list(models), "model_specs": {key: model_specs[key] for key in models},
        "tasks": tasks, "jobs": jobs,
    }
    manifest["manifest_sha256"] = digest(manifest)
    return manifest


def save_plan(output_dir: Path, models: list[str] | tuple[str, ...] = DEFAULT_MODELS,
              seed: int = 20261018, repo: Path = REPO) -> dict[str, Any]:
    output_dir = safe_output_dir(output_dir, repo)
    manifest = build_manifest(models, seed, repo)
    path = output_dir / "manifest.json"
    if path.exists():
        if read_json(path) != manifest:
            raise ValueError("Existing manifest differs; select a new output directory")
    else:
        write_new(path, manifest)
    return manifest


def validated_manifest(output_dir: Path, repo: Path = REPO) -> dict[str, Any]:
    output_dir = safe_output_dir(output_dir, repo)
    manifest = read_json(output_dir / "manifest.json")
    expected = build_manifest(manifest["model_keys"], manifest["design"]["seed"], repo)
    if manifest != expected:
        raise ValueError("Manifest/source/protocol mismatch; do not resume this study")
    return manifest


def resolved_config(runtime: Any, model_key: str) -> dict[str, Any]:
    resolved = runtime.resolve_model(model_key)
    spec = resolved.spec
    return {"requested_deployment": resolved.deployment,
            "base_url_sha256": digest(resolved.base_url), "auth_mode": resolved.auth_mode,
            "api": "responses" if spec.use_responses_api else "chat.completions",
            "temperature": 0.0 if spec.supports_temperature_zero else None,
            "reasoning_effort": spec.reasoning_effort}


def expected_request(config: dict[str, Any], messages: list[dict[str, str]]) -> dict[str, Any]:
    request = {"model": config["requested_deployment"]}
    if config["temperature"] is not None:
        request["temperature"] = config["temperature"]
    if config["api"] == "responses":
        request["input"] = messages
        if config["reasoning_effort"]:
            request["reasoning"] = {"effort": config["reasoning_effort"], "summary": "auto"}
    else:
        request["messages"] = messages
    return request


def execute(output_dir: Path, runtime: Any, repo: Path = REPO) -> dict[str, int]:
    """One attempt per job. Failed/uncertain attempts require review, never blind retry."""
    output_dir = safe_output_dir(output_dir, repo)
    manifest = validated_manifest(output_dir, repo)
    configs = {key: resolved_config(runtime, key) for key in manifest["model_keys"]}
    from importlib.metadata import PackageNotFoundError, version
    versions = {"python": sys.version.split()[0]}
    for package in ("openai", "azure-identity"):
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            versions[package] = "not installed"
    execution = {"manifest_sha256": manifest["manifest_sha256"], "model_configs": configs,
                 "runtime_versions": versions,
                 "returned_model_caveat": "Provider-returned identifiers may be aliases; they do not verify immutable model builds"}
    execution["execution_config_sha256"] = digest(execution)
    config_path = output_dir / "execution_config.json"
    if config_path.exists():
        if read_json(config_path) != execution:
            raise ValueError("Resolved model settings changed; do not resume this study")
    else:
        write_new(config_path, execution)
    counts = {"generated": 0, "reused": 0}
    for job in manifest["jobs"]:
        job_id = job["job_id"]
        config = configs[job["model_key"]]
        request_sha = digest({"messages": job["messages"], "model_config": config})
        path = output_dir / "generations" / f"{job_id}.json"
        attempt_path = output_dir / "attempts" / f"{job_id}.json"
        if path.exists():
            record = read_json(path)
            recorded_sha = record.pop("artifact_sha256", None)
            if recorded_sha != digest(record) or any(record.get(k) != v for k, v in {
                "manifest_sha256": manifest["manifest_sha256"], "job_id": job_id,
                "request_sha256": request_sha,
                "execution_config_sha256": execution["execution_config_sha256"],
                "analysis_eligible": True,
            }.items()):
                raise ValueError("Existing generation failed integrity/protocol/eligibility checks")
            counts["reused"] += 1
            continue
        if attempt_path.exists():
            raise ValueError("An earlier attempt has no eligible result; review it before another request")
        version_path = output_dir / "model_versions" / f"{digest(job['model_key'])}.json"
        pinned_version = read_json(version_path) if version_path.exists() else None
        write_new(attempt_path, {"timestamp_utc": now(), "job_id": job_id,
                                "manifest_sha256": manifest["manifest_sha256"],
                                "request_sha256": request_sha, "state": "started"})
        try:
            result = runtime.generate_messages(job["model_key"], job["messages"])
        except Exception as exc:
            write_new(output_dir / "failures" / f"{job_id}.json", {
                "timestamp_utc": now(), "job_id": job_id, "request_sha256": request_sha,
                "manifest_sha256": manifest["manifest_sha256"], "error_type": type(exc).__name__,
                "http_status": getattr(exc, "status_code", None), "request_id": getattr(exc, "request_id", None),
                "state": "request_failed_or_outcome_unknown", "automatic_retry": False})
            raise RuntimeError(f"Request failed for job {job_id}; audit saved, no automatic retry") from None
        returned = result.get("returned_model")
        version = {"model_key": job["model_key"], "returned_model": returned,
                   "model_config_sha256": digest(config)}
        version_matches = pinned_version is None or pinned_version == version
        actual_config = {"requested_deployment": result.get("requested_deployment"),
                         "base_url_sha256": digest(result.get("base_url")),
                         "auth_mode": result.get("auth_mode"), "api": result.get("api"),
                         "temperature": result.get("temperature"), "reasoning_effort": result.get("reasoning_effort")}
        text = result.get("text", "")
        request_matches = result.get("request") == expected_request(config, job["messages"])
        eligible = (isinstance(text, str) and bool(text.strip()) and result.get("status") in {"completed", "stop"}
                    and bool(returned) and version_matches and actual_config == config and request_matches)
        record = {**result, "schema_version": 1, "cohort": PROTOCOL, "timestamp_utc": now(),
                  "manifest_sha256": manifest["manifest_sha256"], "job_id": job_id,
                  "execution_config_sha256": execution["execution_config_sha256"],
                  "request_sha256": request_sha, "actual_request_sha256": digest(result.get("request")),
                  "pattern": manifest["tasks"][job["pattern_key"]],
                  "pattern_key": job["pattern_key"], "source_pattern_id": job["source_pattern_id"],
                  "taxonomy_assignment": "historical_task_level", "variant": job["variant"],
                  "run_index": job["run_index"], "model_key": job["model_key"],
                  "model_deployment": result.get("requested_deployment"), "messages": job["messages"],
                  "output": text, "analysis_eligible": eligible,
                  "validation": {"config_matches": actual_config == config, "returned_model_matches": version_matches,
                                 "request_matches": request_matches}}
        record["artifact_sha256"] = digest(record)
        write_new(path, record)
        if not eligible:
            raise RuntimeError(f"Incomplete/empty/model-mismatched result saved for {job_id}; review before continuing")
        if not version_path.exists():
            write_new(version_path, version)
        counts["generated"] += 1
    return counts


def make_runtime(env_file: str | None, auth_mode: str) -> Any:
    """Only explicit generation may load an explicitly named credentials file."""
    if env_file:
        from dotenv import load_dotenv
        path = Path(env_file).expanduser().resolve(strict=True)
        load_dotenv(dotenv_path=path, override=False)
    # Prevent the legacy import from searching unrelated ancestor .env files.
    previous = os.environ.get("PYTHON_DOTENV_DISABLED")
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    try:
        if str(REPO) not in sys.path:
            sys.path.insert(0, str(REPO))
        module = importlib.import_module("evaluation.chapter6_evaluation")
    finally:
        if previous is None:
            os.environ.pop("PYTHON_DOTENV_DISABLED", None)
        else:
            os.environ["PYTHON_DOTENV_DISABLED"] = previous
    return module.AzureModelRuntime(auth_mode=auth_mode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="Freeze an offline manifest; no runtime or credentials are loaded")
    plan.add_argument("--output-dir", type=Path, required=True)
    plan.add_argument("--models", default=",".join(DEFAULT_MODELS))
    plan.add_argument("--seed", type=int, default=20261018)
    generate = sub.add_parser("generate", help="Execute only the frozen six-task manifest")
    generate.add_argument("--output-dir", type=Path, required=True)
    generate.add_argument("--env-file", help="Explicit dotenv file; otherwise use inherited environment only")
    generate.add_argument("--auth-mode", choices=("auto", "api_key", "entra"), default="auto")
    args = parser.parse_args(argv)
    if args.command == "plan":
        manifest = save_plan(args.output_dir, [x.strip() for x in args.models.split(",") if x.strip()], args.seed)
        print(json.dumps({"manifest_sha256": manifest["manifest_sha256"], "jobs": len(manifest["jobs"]), "api_calls": 0}))
    else:
        # Validate before constructing a runtime or reading credentials.
        validated_manifest(args.output_dir)
        print(json.dumps(execute(args.output_dir, make_runtime(args.env_file, args.auth_mode))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
