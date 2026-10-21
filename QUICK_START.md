# Quick Start: Audit Repository

This repository currently contains the governance contract, documentation validator, CI workflow, this guide, and the implementation status record. It does **not** currently contain a complete multi-repository inventory, orchestrator, Docker stack, Helm chart, or deployment scripts. Do not follow unverified commands copied from older descriptions.

## 1. Clone the repository

```bash
git clone https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT.git
cd HEAVENZFIRE-ECOSYSTEM-AUDIT
```

## 2. Read the operating contract

Review [AGENTS.md](AGENTS.md) before making changes. Review [Implementation Status](docs/IMPLEMENTATION_STATUS.md) to understand the verified baseline and remaining acceptance gates.

## 3. Run the current checks

Prerequisite: Python 3.10 or newer.

```bash
python scripts/validate_docs.py
python -m py_compile scripts/validate_docs.py
```

The validator checks relative Markdown links and image paths without network access. GitHub Actions runs the same checks on pushes and pull requests.

## 4. Contribute safely

1. Create a feature branch.
2. Make a small, scoped change and add or update tests.
3. Run the checks above.
4. Inspect the diff for secrets, private data, unsafe defaults, and claims without evidence.
5. Open a pull request describing behavior, test results, risks, and any checks not run.

Do not add a GitHub token to a committed `.env` file. Use a local, ignored environment file or the platform's secret store only when a future tool genuinely requires credentials.

## 5. Next implementation milestone

Build a fresh, paginated GitHub repository inventory with source URLs and collection metadata, then classify repositories using their actual files, tests, CI, dependencies, and release configuration. See [the implementation plan](docs/IMPLEMENTATION_STATUS.md).

## Support

- [Issues](https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT/issues)
- [Repository](https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT)
