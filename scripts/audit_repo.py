#!/usr/bin/env python3
"""Evidence-based repository operational-integrity scanner (stdlib only).

This tool inventories observable engineering evidence. Heuristic markers are leads,
not proof that a repository is a mock or that a capability works.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_SUFFIXES = {".py", ".rs", ".go", ".js", ".jsx", ".ts", ".tsx", ".java", ".cs", ".cpp", ".c", ".h", ".hpp", ".ps1", ".sh"}
MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod",
    "pom.xml", "build.gradle", "Gemfile", "composer.json", "deno.json",
}
TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs"}
CI_DIRS = {".github/workflows", ".gitlab-ci.yml", ".circleci", "azure-pipelines.yml"}
DEPLOY_MARKERS = {"Dockerfile", "docker-compose.yml", "compose.yaml", "kubernetes", "k8s", "terraform", "fly.toml", "render.yaml"}
MOCK_PATTERNS = [
    (re.compile(r"\\b(mock|mocked|mocking|fixture|stub)\\b", re.I), "mock/stub terminology"),
    (re.compile(r"\\b(simulat(?:e|ed|ion|ing))\\b", re.I), "simulation terminology"),
    (re.compile(r"\\b(todo|fixme|not implemented|placeholder|coming soon)\\b", re.I), "unfinished-work marker"),
]
NETWORK_PATTERNS = re.compile(r"(https?://|\\b(fetch|axios|requests\\.|http\\.|websocket|websocketserver|grpc|mqtt|socket\\.)\\b)", re.I)
ARRAY_PATTERNS = re.compile(r"(ndarray|numpy|tensor|multidimensional|multi.?dimensional|array\\[|\\[\\[|Array\\.from|Float32Array|Uint8Array)", re.I)
NETWORK_GRAPH_PATTERNS = re.compile(r"(graph|adjacency|neighbor|neighbour|edge_index|mycel|mesh|voxel|pixel.?grid|cellular autom)", re.I)
MAX_FILE_BYTES = 1_000_000
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__", ".next"}


def _run_git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True,
            timeout=5, check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if path.is_file() and path.stat().st_size <= MAX_FILE_BYTES:
            result.append(path)
    return result


def audit_repository(root: str | Path) -> dict[str, Any]:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    files = _files(root)
    rels = {p.relative_to(root).as_posix() for p in files}
    names = {p.name for p in files}
    source_files = [p for p in files if p.suffix.lower() in SOURCE_SUFFIXES]
    test_files = [
        p for p in files
        if p.name.lower().startswith(("test_", "spec_"))
        or any(part.lower() in TEST_DIRS for part in p.relative_to(root).parts[:-1])
    ]
    manifest_files = sorted(rels & MANIFESTS)
    ci_files = sorted(
        rel for rel in rels
        if rel.startswith(".github/workflows/") or rel in CI_DIRS
        or rel.startswith(".circleci/")
    )
    deploy_files = sorted(
        rel for rel in rels
        if Path(rel).name in DEPLOY_MARKERS
        or any(marker in rel.lower().split("/") for marker in {"kubernetes", "k8s", "terraform"})
    )

    findings: list[dict[str, str]] = []
    counts = {"mock_stub_terms": 0, "simulation_terms": 0, "unfinished_markers": 0}
    array_evidence: list[str] = []
    network_evidence: list[str] = []
    graph_evidence: list[str] = []
    source_text_files = 0

    for path in source_files:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        source_text_files += 1
        for pattern, label in MOCK_PATTERNS:
            matches = list(pattern.finditer(content))
            if matches:
                key = {
                    "mock/stub terminology": "mock_stub_terms",
                    "simulation terminology": "simulation_terms",
                    "unfinished-work marker": "unfinished_markers",
                }[label]
                counts[key] += len(matches)
                findings.append({
                    "type": "heuristic",
                    "file": rel,
                    "signal": label,
                    "count": str(len(matches)),
                    "note": "Review context manually; a match is not proof of a nonfunctional feature.",
                })
        if ARRAY_PATTERNS.search(content):
            array_evidence.append(rel)
        if NETWORK_PATTERNS.search(content):
            network_evidence.append(rel)
        if NETWORK_GRAPH_PATTERNS.search(content):
            graph_evidence.append(rel)

    has_git = (root / ".git").exists()
    git_head = _run_git(root, "rev-parse", "HEAD") if has_git else None
    git_branch = _run_git(root, "branch", "--show-current") if has_git else None
    tracked_changes = _run_git(root, "status", "--short") if has_git else None

    gates = {
        "source_code_present": bool(source_files),
        "dependency_manifest_present": bool(manifest_files),
        "tests_present": bool(test_files),
        "ci_present": bool(ci_files),
        "deployment_evidence_present": bool(deploy_files),
        "git_revision_available": bool(git_head),
        "network_integration_evidence": bool(network_evidence),
        "multidimensional_array_or_tensor_evidence": bool(array_evidence),
        "graph_or_mycelium_network_evidence": bool(graph_evidence),
    }
    if not source_files:
        status = "NO_SOURCE_EVIDENCE"
    elif not test_files:
        status = "IMPLEMENTATION_UNVERIFIED_NO_TESTS"
    elif not ci_files:
        status = "IMPLEMENTATION_PRESENT_CI_UNVERIFIED"
    else:
        status = "ENGINEERING_EVIDENCE_PRESENT_RUNTIME_NOT_PROVEN"

    return {
        "schema_version": "1.0",
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_path": str(root),
        "git": {
            "is_git_repository": has_git,
            "head": git_head,
            "branch": git_branch,
            "working_tree_status": tracked_changes,
        },
        "inventory": {
            "files_scanned": len(files),
            "source_files": len(source_files),
            "source_text_files_read": source_text_files,
            "test_files": len(test_files),
            "dependency_manifests": manifest_files,
            "ci_files": ci_files,
            "deployment_files": deploy_files,
        },
        "capability_evidence": {
            "network_integration_files": sorted(set(network_evidence)),
            "array_or_tensor_files": sorted(set(array_evidence)),
            "graph_or_mycelium_files": sorted(set(graph_evidence)),
        },
        "heuristic_signals": counts,
        "gates": gates,
        "status": status,
        "findings": findings,
        "limitations": [
            "Static inspection cannot prove a feature works at runtime.",
            "Network-related strings do not prove a live service or valid credentials.",
            "Array/graph terminology does not prove multidimensional computation or a biologically inspired network is operational.",
            "Mock/simulation/TODO matches are review signals and may occur in tests, documentation, or legitimate simulators.",
            "Run tests and a controlled end-to-end check before declaring operational status.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Repository directory to audit")
    parser.add_argument("--output", "-o", help="Write JSON report to this path (default: stdout)")
    args = parser.parse_args()
    try:
        report = audit_repository(args.path)
    except ValueError as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Report written: {output.resolve()}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
