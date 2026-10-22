#!/usr/bin/env python3
"""Validate a bounded microtask manifest; standard-library only."""

from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "task-manifest.json"
STATUSES = {"PLANNED", "RUNNING", "PASS", "FAIL", "UNKNOWN"}
REQUIRED = {
    "task_id", "title", "repository", "depends_on", "scope",
    "outputs", "acceptance", "test_command", "timeout_seconds",
    "status", "evidence", "base_ref", "permitted_paths", "rollback_ref", "execution_evidence",
}


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return ["tasks must be a non-empty list"]

    by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"tasks[{index}] must be an object")
            continue
        missing = sorted(REQUIRED - task.keys())
        if missing:
            errors.append(f"tasks[{index}] missing fields: {', '.join(missing)}")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"tasks[{index}] task_id must be a non-empty string")
        elif task_id in by_id:
            errors.append(f"duplicate task_id: {task_id}")
        else:
            by_id[task_id] = task
        status = task.get("status")
        if status not in STATUSES:
            errors.append(f"{task_id}: invalid status {status!r}")
        base_ref = task.get("base_ref")
        if not isinstance(base_ref, str) or not base_ref.strip() or any(ch.isspace() for ch in base_ref):
            errors.append(f"{task_id}: base_ref must be a non-empty ref without whitespace")
        permitted = task.get("permitted_paths")
        if not isinstance(permitted, list) or not permitted or not all(isinstance(item, str) and item.strip() for item in permitted):
            errors.append(f"{task_id}: permitted_paths must be a non-empty list of relative path patterns")
        else:
            for item in permitted:
                normalized = PurePosixPath(item.replace("\\", "/"))
                if normalized.is_absolute() or ".." in normalized.parts or re.match(r"^[A-Za-z]:", item):
                    errors.append(f"{task_id}: permitted path must stay relative to the repository: {item}")
        rollback_ref = task.get("rollback_ref")
        if not isinstance(rollback_ref, str) or not rollback_ref.strip():
            errors.append(f"{task_id}: rollback_ref must be a non-empty commit/URL or explicit not-applicable reason")
        elif rollback_ref.startswith("not-applicable:"):
            if status not in {"PLANNED", "UNKNOWN"}:
                errors.append(f"{task_id}: not-applicable rollback is allowed only before verified work")
        elif not (
            re.fullmatch(r"[0-9a-fA-F]{7,40}", rollback_ref)
            or rollback_ref.startswith("refs/heads/")
            or rollback_ref.startswith("https://github.com/")
        ):
            errors.append(f"{task_id}: rollback_ref must be a commit SHA, branch ref, GitHub URL, or allowed not-applicable reason")
        execution = task.get("execution_evidence")
        if execution is not None and not isinstance(execution, dict):
            errors.append(f"{task_id}: execution_evidence must be an object or null")
        if status == "RUNNING":
            if not isinstance(task.get("branch"), str) or not task.get("branch", "").strip():
                errors.append(f"{task_id}: RUNNING requires a concrete branch/workspace reference")
            required_execution = ("provider", "instance_id", "observed_at", "status", "evidence_url")
            if not isinstance(execution, dict) or any(
                not isinstance(execution.get(field), str) or not execution[field].strip()
                for field in required_execution
            ):
                errors.append(f"{task_id}: RUNNING requires provider-reported instance and observable execution evidence")
            elif execution.get("provider") not in {"github-actions", "codespaces", "local-worker"} or execution.get("status") != "running" or not execution.get("evidence_url", "").startswith("https://"):
                errors.append(f"{task_id}: execution_evidence must identify an allowed provider, running status, and HTTPS evidence URL")
        for field in ("scope", "outputs", "acceptance"):
            value = task.get(field)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                errors.append(f"{task_id}: {field} must be a non-empty list of strings")
        dependencies = task.get("depends_on")
        if not isinstance(dependencies, list) or not all(
            isinstance(dep, str) for dep in dependencies
        ):
            errors.append(f"{task_id}: depends_on must be a list of task IDs")
        elif task_id in dependencies:
            errors.append(f"{task_id}: task cannot depend on itself")
        timeout = task.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            errors.append(f"{task_id}: timeout_seconds must be a positive integer")
        evidence = task.get("evidence")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            errors.append(f"{task_id}: evidence must be a list of strings")
        elif task.get("status") == "PASS" and not evidence:
            errors.append(f"{task_id}: PASS requires at least one evidence item")
        if task.get("status") == "RUNNING" and not task.get("branch"):
            errors.append(
                f"{task_id}: RUNNING requires a concrete branch/workspace reference; "
                "a task issue alone is not execution evidence"
            )

    for task_id, task in by_id.items():
        for dependency in task.get("depends_on", []):
            if dependency not in by_id:
                errors.append(f"{task_id}: unknown dependency {dependency}")
    # Detect cycles with depth-first traversal.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"dependency cycle includes {task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        task = by_id[task_id]
        for dependency in task.get("depends_on", []):
            if dependency in by_id:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in by_id:
        visit(task_id)
    return errors


def self_test() -> int:
    good = {
        "tasks": [{
            "task_id": "T", "title": "test", "repository": "o/r",
            "depends_on": [], "scope": ["scope"], "outputs": ["output"],
            "acceptance": ["testable condition"], "test_command": "python -m unittest",
            "timeout_seconds": 30, "status": "PASS", "evidence": ["https://example.test/evidence"],
            "branch": "test/branch", "base_ref": "main", "permitted_paths": ["src/**"],
            "rollback_ref": "0123456789abcdef0123456789abcdef01234567", "execution_evidence": None,
        }]}

    if validate(good):
        print("SELF-TEST FAIL: valid manifest rejected")
        return 1
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["evidence"] = []
    if not any("PASS requires" in item for item in validate(bad)):
        print("SELF-TEST FAIL: PASS without evidence accepted")
        return 1
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["depends_on"] = ["MISSING"]
    if not any("unknown dependency" in item for item in validate(bad)):
        print("SELF-TEST FAIL: missing dependency accepted")
        return 1
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["acceptance"] = []
    if not any("acceptance must be" in item for item in validate(bad)):
        print("SELF-TEST FAIL: missing acceptance criteria accepted")
        return 1
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["depends_on"] = ["T"]
    if not any("cannot depend on itself" in item for item in validate(bad)):
        print("SELF-TEST FAIL: self-dependency accepted")
        return 1
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["status"] = "RUNNING"
    bad["tasks"][0]["execution_evidence"] = None
    if not any("RUNNING requires provider-reported" in item for item in validate(bad)):
        print("SELF-TEST FAIL: RUNNING without provider evidence accepted")
        return 1
    bad = json.loads(json.dumps(good))
    bad["tasks"][0]["permitted_paths"] = ["../outside"]
    if not any("must stay relative" in item for item in validate(bad)):
        print("SELF-TEST FAIL: path escape accepted")
        return 1
    print("SELF-TEST PASS: valid case accepted; invalid contract cases rejected.")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        if argv != ["--self-test"]:
            print("Expected --self-test alone", file=sys.stderr)
            return 2
        return self_test()
    if len(argv) > 1:
        print("Expected at most one manifest path", file=sys.stderr)
        return 2
    path = Path(argv[0]) if argv else DEFAULT_MANIFEST
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Unable to read manifest: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        print("Manifest validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"Manifest validation passed: {len(data['tasks'])} task(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
