# Continuous Execution and Independent Verification Protocol

Status: proposed governance control  
Scope: repository changes, agent tasks, test execution, evidence collection, and integration  
Last reviewed: 2026-10-21

## Mission

Keep authorized work moving through implementation, test, repair, and evidence capture. Do not turn ordinary engineering decisions into repeated user-approval requests. A blocked task must produce a specific blocker and continue with independent, non-blocked tasks.

This protocol does not authorize bypassing repository permissions, security controls, required reviews, or explicit approval gates for high-impact actions.

## Execution state machine

Each task must be in one explicit state:

1. `READY` — dependencies and acceptance criteria are known.
2. `BUILDING` — implementation is in progress.
3. `VERIFYING` — tests and independent checks are running.
4. `REPAIRING` — a failure is being corrected; preserve the failing evidence.
5. `INTEGRATING` — verified changes are being committed, pushed, and reconciled.
6. `DONE` — acceptance criteria pass and evidence is linked.
7. `BLOCKED` — a concrete external dependency, permission boundary, or unresolved high-severity defect prevents this task from progressing.

A task must not remain in `BLOCKED` without a recorded reason, owner/dependency, evidence, and next retry or fallback. A blocked task does not stop unrelated work. Do not report `DONE` on the basis of intention, source inspection alone, or a successful syntax check when runtime behavior is required.

## Routine execution versus approval gates

Proceed without another user prompt for routine, reversible work within the authorized repository scope: reading project files, editing task-scoped files, adding tests, running safe checks, creating a branch, committing, pushing, opening a pull request, and repairing failures.

Require the applicable explicit approval or repository policy for destructive data changes, credential or permission changes, administrator-level operations, public network exposure, production deployments, purchases, and other high-impact external effects. Do not bypass protected-branch rules or required independent reviews. If a gate blocks one action, continue safe preparatory work and report the exact gate.

## Three-valued evidence verdict (ternary)

Every acceptance criterion and material claim must be classified as exactly one of:

- `PASS` — direct evidence supports the criterion; record the source, command/test, timestamp or commit, and result.
- `FAIL` — direct evidence contradicts the criterion; record the failing output and remediation.
- `UNKNOWN` — evidence is missing, stale, ambiguous, or insufficient. Unknown is not a pass and must not be silently converted to fail without evidence.

For compound criteria, report each subcriterion separately. A task can continue while some criteria are unknown, but release claims must not exceed the verified subset. A failed check should trigger diagnosis and repair, not a request for the user to restate the task.

## Cross-reference and consensus procedure

For every non-trivial implementation:

1. Trace the requirement to a repository artifact, issue, or explicit task statement.
2. Trace each acceptance criterion to a test or observable result.
3. Cross-check relevant interfaces against their callers, configuration, dependency manifests, and workflow permissions.
4. Where a claim depends on external technical facts, consult primary documentation and/or peer-reviewed evidence; record source links and dates.
5. Compare builder conclusions against verifier findings. Record disagreements, evidence, and resolution. Consensus means an evidence-supported resolution, not unanimous wording or majority vote.
6. Keep evidence provenance attached to each result; do not copy conclusions between projects as if they were fresh verification.

## Independent reviewer requirement

For security-sensitive, architectural, or release-significant changes, obtain review from a genuinely independent non-GPT reviewer when such a reviewer is available (for example, a separately identified non-GPT model, maintainer, or domain reviewer). Record reviewer identity/role, tool or model and version where available, commit reviewed, findings, and disposition.

A second pass performed by the same GPT instance is not an external review. A literature search or consensus summary is supporting evidence, not a code review. If no independent reviewer is available, mark external review `UNKNOWN`, continue non-blocked implementation and tests, and do not claim independent approval. Do not invent a reviewer or fabricate review results. Unresolved critical/high findings block release; they do not halt unrelated safe tasks.

## Minimum task evidence record

For each completed task, record:

- task ID and objective;
- base and resulting commit SHA;
- changed paths;
- acceptance criteria and `PASS` / `FAIL` / `UNKNOWN` verdicts;
- exact checks run and observed outputs or linked CI run;
- independent-review status and findings;
- unresolved risks and rollback/revert path;
- next dependency-aware task.

Never put tokens, passwords, private keys, or other secrets in the record. Redact sensitive output.

## Commit, push, and integration rule

After a scoped change passes its required checks, commit and push it to the task branch, then open/update a pull request and verify the remote state. Do not say a push or merge succeeded until the repository API confirms it. Do not merge around required checks or required reviewers. Where repository settings require a human or non-GPT review, keep the PR ready and continue other tasks rather than repeatedly asking the user to authorize the same routine action.

## Stop conditions

Stop only the affected action when:
- an explicit permission or approval gate applies;
- the target repository/branch cannot be verified;
- a destructive or externally visible action has ambiguous scope;
- secrets or sensitive data may be exposed;
- a critical/high severity finding remains unresolved for the proposed release;
- test infrastructure is unavailable and no valid fallback exists.

When stopping an action, preserve logs, state the precise blocker, and continue independent work. Never conceal failures or fabricate green status.

## Completion definition

The workflow is operational only when these controls themselves are tested: state/evidence records are generated, ternary verdicts are enforced in reports, failures remain visible, routine changes reach a remote branch, required reviews are respected, and the final remote commit/CI state is independently re-read.
