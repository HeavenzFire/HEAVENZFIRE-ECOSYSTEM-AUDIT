#!/usr/bin/env python3
"""Validate a bounded microtask manifest; standard-library only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "task-manifest.json"
STATUSES = {"PLANNED", "RUNNING", "PASS", "FAIL", "UNKNOWN"}
REQUIRED = {
    "task_id", "title", "repository", "depends_on", "scope",
    "outputs", "acceptance", "test_command", "timeout_seconds",
    "status", "evidence",
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
        if task.get("status") not in STATUSES:
            errors.append(f"{task_id}: invalid status {task.get('status')!r}")
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
            "branch": "test/branch",
        }]
    }
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
    print("SELF-TEST PASS: valid case accepted; four invalid cases rejected.")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_MANIFEST
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
