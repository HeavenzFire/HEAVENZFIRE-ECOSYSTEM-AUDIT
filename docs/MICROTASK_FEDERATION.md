# Microtask Federation Contract

**Status:** implemented as a proposed contract; no GitHub Codespaces or independent worker processes are created by this document alone.

## Objective

Increase parallel throughput without confusing parallel task records with running workers. Each lane owns a bounded deliverable, a branch/workspace, a dependency list, acceptance checks, and evidence. Shared integration happens only after task outputs are reviewable.

## Work lanes for the vortex-braid consensus test

| Lane | Task | Repository issue | Dependency |
|---|---|---|---|
| A | Hopf state norm and amplitude invariants | [#14](https://github.com/HeavenzFire/The-Tesla-Hulse-Resonance-Field-Grid/issues/14) | None |
| B | Braid metric contract and event semantics | [#15](https://github.com/HeavenzFire/The-Tesla-Hulse-Resonance-Field-Grid/issues/15) | None |
| C | Ring+2 topology and edge convention | [#16](https://github.com/HeavenzFire/The-Tesla-Hulse-Resonance-Field-Grid/issues/16) | None |
| D | Paired seeded intervention experiment | [#17](https://github.com/HeavenzFire/The-Tesla-Hulse-Resonance-Field-Grid/issues/17) | A, B, C |
| E | Shared task contract and validation | [#5](https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT/issues/5) | None |

A, B, C, and E are independently actionable. D should finalize after A–C settle the state and metric contract.

## Task envelope

Every work item must specify:
- stable `task_id` and optional `parent_task_id`;
- repository and `base_ref` (the commit line on which work starts), plus an isolated branch/workspace;
- bounded scope and a non-empty `permitted_paths` allowlist of relative paths that cannot escape the repository;
- declared dependency task IDs;
- concrete outputs and acceptance checks;
- timeout and test command;
- state: `PLANNED`, `RUNNING`, `PASS`, `FAIL`, or `UNKNOWN`;
- evidence URLs or command output, `execution_evidence` for any `RUNNING` task, and a rollback/revert reference. A planned/unknown task with no merged changes must state `not-applicable: no changes merged` rather than inventing a rollback SHA.

A task cannot be marked `PASS` without a test result or other directly inspectable evidence. Missing artifacts or unavailable execution environments mean `UNKNOWN`, not pass.

## Isolation and concurrency rules

1. One branch/workspace per active lane; no two lanes edit the same path concurrently.
2. Parallelize independent analysis, tests, and isolated file changes. Serialize dependent integration and shared-path writes.
3. Use explicit dependency edges; do not infer completion from issue creation or branch existence.
4. The integrator reviews diffs, runs the complete available checks, reconciles disagreements, and records accepted/rejected findings.
5. Bound retries and runtime. Never create hidden persistence, commit secrets, or widen network privileges as a shortcut.
6. Treat GitHub issues and branches as coordination artifacts, not proof of running Codespaces or agents. A real Codespace/worker is RUNNING only when its provider reports a concrete instance and observable execution.
7. Do not merge or release automatically. A successful CI run is evidence for only the checks that actually ran.

## Four-role review handoff

- **Architect:** dependencies, scope, interfaces, threats, and acceptance criteria.
- **Builder:** minimal diff and reproducible test instructions.
- **Adversarial verifier:** independent challenge of math, state handling, failure paths, and evidence.
- **Integrator:** merges only after review gates; reports exact commit, tests, risks, and rollback.

If separate model agents are unavailable, execute these as sequential review passes and label them honestly; do not represent role labels as separate processes.

## Completion gate

A lane is complete only when its issue links to a branch/PR, changed paths, test command/output, evidence artifacts, and unresolved risks. The experiment is not considered reproducible until its seed, configuration, source revision, `mesh_history.json`, and `final_states.json` can be replayed or independently checked.
