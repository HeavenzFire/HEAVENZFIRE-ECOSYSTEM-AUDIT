# Free/Open-Source Replacement Program

**Status:** Roadmap and acceptance contract; replacements are not yet deployed merely because they are listed here.  
**Owner/project:** HeavenzFire Unified Field  
**Last reviewed:** 2026-10-21

## Objective

Replace recurring fees, credit-metered agents, proprietary hosted dependencies, and paywalled developer workflows with self-hostable or genuinely free/open-source components wherever technically and legally feasible. Preserve user data, existing work, security controls, and interoperability.

“Free” has two separate meanings and must be recorded separately:
- **Zero license cost:** no required paid license for the chosen use.
- **Zero operating cost:** not guaranteed. Hardware, electricity, domains, bandwidth, hosting, and maintenance can still cost money.

Do not call a replacement complete until required workflows pass acceptance tests and the old paid dependency can be disabled without breaking them.

## Rules of engagement

1. **Inventory before replacement.** Record each paid service, the exact feature used, frequency, spend/credit limit, data handled, export path, and failure impact.
2. **Prefer local-first and self-hostable.** Use local execution for private data and deterministic tasks; use remote services only through explicit adapters and policy.
3. **Verify licensing per release.** Confirm the upstream license, dependency licenses, trademark constraints, commercial-use terms, and whether any feature is enterprise-only. “Source available” is not automatically open source.
4. **No stealth, evasion, or paywall circumvention.** Replace a dependency with independently implemented, lawful software; do not bypass another provider's billing, authentication, usage controls, or access restrictions.
5. **Exportability is mandatory.** Keep portable files, documented schemas, and an exit path.
6. **Fail closed on secrets and authority.** No tokens or private keys in source control. No unauthenticated public listeners. Destructive, privileged, financial, or externally visible actions require explicit approval.
7. **Evidence, not labels.** Every item has status UNKNOWN, IN_PROGRESS, PASS, or BLOCKED; record commit, test output, and rollback path.
8. **Do not mass-migrate blindly.** Replace one workflow at a time and retain the old path until the replacement passes.

## Initial candidate map

These are candidates to evaluate, not claims that they are installed or equivalent in every feature. Verify upstream licensing and the exact release before adoption.

| Paid / restricted capability | Candidate replacement | Intended scope | Required proof before retiring old service |
|---|---|---|---|
| Credit-metered browser agents / website automation | Playwright plus a HeavenzFire-owned, allowlisted task runner | Browser navigation, form interaction, downloads, screenshots, deterministic smoke tests | Local execution; explicit domain allowlist; timeout; audit log; no secret leakage; controlled-site test passes |
| Paid cloud LLM/API usage for routine private tasks | Ollama or llama.cpp with locally downloaded, license-compatible models | Local inference, offline tasks, private prompt processing | Model license recorded; memory/latency benchmark; prompt/data isolation; quality thresholds; graceful model-unavailable handling |
| Provider-specific LLM API coupling | OpenAI-compatible adapter boundary; optionally evaluate LiteLLM under its current license | Swap providers without rewriting task logic; local endpoint first | Contract tests against mock and local endpoint; no silent external fallback; redacted telemetry |
| Hosted Git forge / paid collaboration features | Forgejo or Gitea, self-hosted | Git repositories, issues, pull requests, webhooks | Backup/restore test; access control; branch workflow; migration export; upgrade and recovery runbook |
| Paid CI minutes / hosted build dependency | Local runners plus Forgejo Actions or another verified self-hosted CI runner | Tests and packaging on owned hardware | Isolated runner; no untrusted PR secrets; reproducible test output; clean teardown |
| Paid uptime / hosted telemetry | Prometheus and Grafana, or a lighter local metrics/logging stack | Service health, resource usage, test history | Local retention policy; disk cap; redaction; alert test; no public exposure by default |
| Proprietary hosted identity features | Evaluate Authentik or Authelia for the specific access pattern | Self-hosted identity or reverse-proxy access controls | Threat model, MFA/recovery test, least-privilege roles, lockout recovery, backups |
| Paid cloud object storage | Evaluate SeaweedFS or another actively maintained, license-compatible self-hosted object store | Artifacts, run evidence, backups | Integrity checks, encryption plan, restore drill, quota enforcement, no public bucket |
| Paid workflow orchestration | Evaluate an OSI-licensed workflow engine or implement a small bounded queue in the existing control plane | Retries, timeouts, task states, cancellation | Duplicate-delivery tests, idempotency, crash recovery, bounded retries, audit events |
| Paid project-specific AI review | Local static analysis, tests, and at least one independent reviewer/tool that can actually run | Code quality and adversarial review | Review provenance recorded; reviewer inspected the diff; findings resolved or documented |

### First known friction point

A prior attempt to use TinyFish for an external AI Studio review stopped because the available wallet balance was insufficient. That establishes a credit dependency for that attempted workflow—not that every TinyFish function requires payment. The replacement target is the underlying workflow (browser navigation, controlled test execution, evidence capture), not TinyFish's proprietary implementation. Start with a local Puppeteer Core runner and a controlled test page; do not claim it can operate every third-party site until tested.

## Inventory schema

Create one record per paid dependency or paywalled feature:
- id
- service_and_feature
- workflow_owner
- why_needed
- billing_model (subscription, credits, usage, seat, hosted compute, other)
- known_cost_and_period (or UNKNOWN)
- data_sensitivity
- current_integration_and_secrets_location (never store secret values)
- export_path
- candidate_replacement
- license_verified_at and license_source
- local_hardware_requirements
- compatibility_gaps
- migration_steps
- acceptance_tests
- rollback_steps
- status
- evidence_links

Do not invent spend figures or claim a dependency is paid without a receipt, account setting, usage limit, or user-provided evidence.

## Rollout order

### Phase 0 — Discover and baseline
- Enumerate actual subscriptions, credit-metered tools, API keys, hosted CI limits, and paid-only features used by the current Unified Field workflow.
- Inspect repository manifests, workflows, environment-variable names (not values), endpoints, and local services.
- Produce a dependency graph from observed imports/configuration; label inferred edges.
- Record current end-to-end behavior and resource use before replacing anything.

**Exit gate:** every identified dependency has an owner, purpose, data classification, export path, candidate, and status.

### Phase 1 — Remove avoidable credit dependency
- Build a small local browser task runner on Puppeteer Core or Playwright, with the selected library and license pinned.
- Add task manifests with domain allowlists, timeouts, explicit approvals for high-impact actions, redacted append-only evidence, and a kill switch.
- Use local inference for private or routine model calls where hardware and model licenses permit.
- Make remote-provider fallback opt-in and visible; never silently send local data to a hosted model.

**Exit gate:** a complete, repeatable browser task and inference task pass without paid credits; tests prove no unexpected outbound request.

### Phase 2 — Own the development plane
- Evaluate self-hosted Git forge, CI, artifact storage, and monitoring.
- Test backup, restore, upgrade, credential recovery, and hardware-failure behavior before moving authoritative data.
- Keep GitHub as a remote mirror if useful; self-hosting does not remove all hosting or bandwidth costs.

**Exit gate:** a fresh machine can restore the project and run the required test suite from documented instructions.

### Phase 3 — Migrate remaining services one by one
- Compare functional coverage, security, maintenance burden, hardware cost, and licensing.
- Reject candidates that merely move a paywall, require an unapproved paid add-on, or make data export difficult.
- Keep adapters thin so another replacement can be substituted later.

**Exit gate:** old service can be disabled for the migrated workflow and the workflow still passes.

### Phase 4 — Audit and maintain
- Run a monthly dependency/license review and a quarterly restore/replacement drill.
- Track cost avoided and ongoing operating costs separately.
- Publish a replacement ledger with evidence and known gaps.

## Definition of done for each replacement

A replacement is PASS only when all apply:
1. The selected release's license and dependency obligations are verified from authoritative sources.
2. The needed workflow is a reproducible test, not a marketing claim.
3. Tests pass on the intended target hardware and runtime.
4. The replacement works without a paid key, credit, or paid-only feature for that workflow.
5. Outbound network calls are observed and match an explicit allowlist.
6. Authentication, permissions, logging, data export, backup, and rollback are tested as applicable.
7. A reviewer other than the implementation author checks the diff and test evidence, or review status remains UNKNOWN.
8. Documentation states what remains unsupported.

A candidate is BLOCKED when its license, hardware feasibility, security model, or required feature is incompatible. An unrun test is UNKNOWN, never PASS.

## Current status

- Program charter: documented in this file
- Full paid-service inventory: UNKNOWN; not yet completed
- Local service audit (2026-10-22): Coder on 127.0.0.1:3001 reports Ollama configured and OpenAI/Gemini unconfigured; gateway on 127.0.0.1:3000 is unavailable. This is a local endpoint snapshot, not a complete account/subscription inventory.
- Credential containment: a public committed environment file was found in HeavenzFire/EntangledMultimodalSystem-3; cleanup PR #221 removes it from the current tree and adds a safe template. Provider-side rotation and historical cleanup remain outstanding.
- Local browser automation: implemented in [HeavenzFire/HeavenzFire PR #78](https://github.com/HeavenzFire/HeavenzFire/pull/78); local Edge fixture tests pass 2/2; existing BrowserBridge regression passes 1/1; PR review/CI pending
- Local inference: live smoke test passed on 2026-10-22 against 127.0.0.1:11800 using heavenzfire-qwen-0.5b; exact response LOCAL_OK verified; broader quality and workflow coverage remain UNKNOWN
- Self-hosted Git/CI/storage stack: candidate only; not yet migrated
- Any claim that every paywall has been eliminated: NOT ESTABLISHED

The first implementation slice is now a Puppeteer Core-based local runner under HeavenzFire/HeavenzFire PR #78; subsequent work should integrate it into approved workflows only after review with an explicit task manifest, domain allowlist, timeout, redacted audit record, and controlled local test page. Do not retire any existing service until that slice passes its tests.
