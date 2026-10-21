# HeavenzFire Ecosystem Audit & Governance

This repository is the evidence-led audit workspace for the HeavenzFire portfolio. It separates verified repository facts from plans and claims that still require reproducible proof.

## Current status

See [Implementation Status](docs/IMPLEMENTATION_STATUS.md) for the verified baseline and completion plan.

## Governance and execution

- [Agent governance contract](AGENTS.md)
- [Continuous execution and independent verification protocol](docs/CONTINUOUS_EXECUTION_PROTOCOL.md)
- [Independent evidence review notes](docs/INDEPENDENT_EVIDENCE_REVIEW.md)

The protocol defines fail-forward task states, ternary PASS/FAIL/UNKNOWN evidence verdicts, routine branch-based delivery, approval boundaries, and independent review requirements. The evidence review supports the design direction but is not a source-code review or proof that the ecosystem is production-ready.

## Repository inventory

- [Public repository inventory snapshot](inventory/repositories.json)
- [Paginated inventory generator](scripts/build_inventory.py)

The snapshot is public-only and search-derived. Run the generator with GitHub API access to refresh it; its metadata records pagination and completeness limits. It excludes private repositories by design.

## Validation

Run from the repository root:

```bash
python scripts/validate_docs.py
python -m py_compile scripts/validate_docs.py scripts/build_inventory.py
python -m unittest discover -s tests -v
```

GitHub Actions runs documentation validation and inventory unit tests on pushes and pull requests. Passing these checks does not prove that the full HeavenzFire ecosystem is production-ready.

## Roadmap

1. Reconcile the search-derived snapshot against the paginated GitHub REST API output.
2. Classify repositories using source, dependency manifests, tests, CI, releases, and deployment configuration.
3. Derive an architecture graph from observable dependencies and label inferences.
4. Implement and test one minimal control-plane integration with typed task contracts, provider adapters, bounded retries, and redacted audit events.
5. Roll out shared controls through small, independently reviewed pull requests.

Do not claim regulatory compliance, production readiness, quantum advantage, or cross-provider shared state without evidence that directly supports the specific claim.
