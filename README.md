# HeavenzFire Ecosystem Audit & Governance

This repository is the evidence-led audit workspace for the HeavenzFire portfolio. It separates verified repository facts from plans and claims that still require reproducible proof.

## Current verified state

At the baseline review on 2026-10-21, the GitHub tree for `main` contained `README.md` and `QUICK_START.md`. The earlier README referenced inventory, architecture, deployment, observability, and schema files that were not present in that tree. Those artifacts and the stated production/compliance claims must not be treated as verified until they are committed and tested.

See [Verified Baseline and Completion Plan](docs/IMPLEMENTATION_STATUS.md).

## Governance contract

All agents and contributors must follow [AGENTS.md](AGENTS.md). The contract requires small reviewable changes, least privilege, explicit approval for high-impact actions, redaction of secrets, and evidence-backed claims.

## Validation

Run locally from the repository root:

```bash
python scripts/validate_docs.py
python -m py_compile scripts/validate_docs.py
```

GitHub Actions runs the same checks on pushes and pull requests. These checks validate local Markdown links and Python syntax; they do not prove that services work or that the ecosystem is production-ready.

## Roadmap

1. **Inventory:** generate a fresh, paginated GitHub API inventory and retain collection metadata and errors.
2. **Evidence classification:** assess each repository using source, dependency manifests, tests, CI, release/deployment configuration, and activity. A repository name or README claim alone is insufficient.
3. **Architecture graph:** derive edges from observable dependencies and label inferred relationships separately.
4. **Minimal working integration:** choose one control-plane repository and implement a typed task contract, provider adapters, bounded retries/timeouts, redacted audit events, and deterministic tests.
5. **Enforcement:** add security checks and branch protections after inspecting current repository settings and ensuring required CI check names match.
6. **Portfolio rollout:** adopt the shared contract through small pull requests, with per-repository acceptance evidence.

## Evidence labels

Use these terms consistently:

- **Verified:** directly observed from a source, API response, or reproducible command.
- **Tested:** an automated or documented test was run, with its result recorded.
- **Planned:** proposed but not implemented.
- **Unknown:** not yet established.

Do not claim HIPAA, GDPR, SOC 2, production readiness, quantum advantage, or cross-provider shared state without evidence that directly supports the specific claim.

## Project links

- [GitHub repository](https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT)
- [Quick start](QUICK_START.md)
- [Implementation status](docs/IMPLEMENTATION_STATUS.md)
- [Governance contract](AGENTS.md)
- [Documentation validator](scripts/validate_docs.py)


## Public inventory and bounded microtask federation

- [Public repository inventory snapshot](inventory/repositories.json) is search-derived and explicitly non-exhaustive; its metadata records the query and collection limits.
- [Inventory generator](scripts/build_inventory.py) supports a fresh paginated collection; refresh it with GitHub API access rather than treating the checked-in snapshot as live.
- [Continuous execution protocol](docs/CONTINUOUS_EXECUTION_PROTOCOL.md) defines READY/BUILDING/VERIFYING/REPAIRING/INTEGRATING/DONE/BLOCKED states and PASS/FAIL/UNKNOWN evidence verdicts.
- [Independent evidence review](docs/INDEPENDENT_EVIDENCE_REVIEW.md) separates observed implementation from hypotheses and unverified claims.
- [Microtask federation contract](docs/MICROTASK_FEDERATION.md) defines bounded, isolated task lanes and acceptance evidence.
- [Task manifest](task-manifest.json) is validated by [scripts/validate_task_manifest.py](scripts/validate_task_manifest.py); it does not claim that a worker or Codespace exists merely because a task is listed.

The combined governance workflow validates local documentation, compiles the Python validators, runs inventory unit tests, validates the task manifest, and executes its validator self-test. These checks do not certify the wider portfolio as production-ready.
