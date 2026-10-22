# Operational Integrity Auditor

This feature adds a dependency-free Python scanner for a local repository. It inventories source files, dependency manifests, tests, CI workflows, deployment files, Git revision state, and code signals related to network integration, multidimensional arrays/tensors, graph or mycelium structures, mocks, simulations, and unfinished markers.

## Run

From the repository root:

```powershell
python scripts/audit_repo.py C:\path\to\repository --output operational-integrity-report.json
python -m unittest discover -s tests -v
python -m py_compile scripts/audit_repo.py tests/test_audit_repo.py
```

The report is triage evidence, not certification. It does not label a project real or fake based on keywords. Operational status requires executing the program, validating dependencies/configuration, and running tests against a controlled service or hardware target.

## Acceptance criteria

- **Multidimensional arrays:** document tensor shape, dtype, memory layout, bounds, expected outputs, and deterministic tests for nontrivial dimensions.
- **Pixelated mycelium network:** represent pixels/cells as nodes; define neighbor/edge rules; store edge weights and state; implement propagation/update rules; test connectivity, boundaries, determinism, and scaling. A canvas animation alone is visualization, not the computational network.
- **External connectivity:** make a bounded request to a configured endpoint; test timeouts, authentication failure, retry limits, and secret redaction. A URL string is not proof.
- **Persistence:** write and reload state; verify schema/version handling and corruption recovery.
- **Deployment:** build a reproducible artifact and health-check the deployed process.
- **AI/agent features:** invoke the configured model/tool adapter and test success, timeout, invalid output, and unavailable-provider paths.
- **UI:** test real state transitions and user-visible errors, not just that the page renders.
- **Hardware/radio/sensor features:** require actual device discovery and captured readings. Simulated data must be labeled simulated.

## Portfolio rollout

1. Generate a paginated inventory from the authenticated GitHub API and retain errors.
2. Run the scanner on each repository in a controlled local workspace.
3. Add language-specific build/test adapters only when the corresponding toolchain and dependency state are known.
4. Record separate statuses for static evidence, tests, build, integration, deployment, and hardware verification.
5. Fix one repository at a time on a feature branch; preserve a known-good revision and require diff/test evidence before merge.

The scanner uses Python's standard library. Passing its unit tests verifies only the scanner paths covered by those tests, not every repository it scans.