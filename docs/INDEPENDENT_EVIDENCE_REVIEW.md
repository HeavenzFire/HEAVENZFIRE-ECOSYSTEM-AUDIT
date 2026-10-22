# Independent Evidence Review Notes

**Date:** 2026-10-21  
**Reviewer system:** Consensus research agent (independent research service)  
**Review scope:** workflow-governance design principles, not source-code correctness  
**Repository implementation status:** not assessed by the research agent

## Findings

- **PASS — continue unrelated work:** dependency-aware fault-tolerant scheduling research supports isolating blocked tasks instead of halting an entire workflow. The evidence comes mainly from cloud, edge, and scientific workflows, so transfer to repository agents is indirect.
- **PASS — ternary evidence labels:** three-valued model checking provides a sound conceptual basis for PASS/FAIL/UNKNOWN. UNKNOWN means evidence or abstraction is insufficient, not that the criterion passed.
- **PASS — independent verification:** IV&V and verification-witness literature support separating implementation from validation and preserving reviewable evidence.
- **UNKNOWN — non-GPT code review:** this review assessed research and governance principles. It did not inspect the implementation diff as a code reviewer, and it is not a substitute for a separately operated non-GPT model or maintainer review.
- **HIGH priority — define UNKNOWN behavior:** specify which unknowns merely defer a task and which block a release; require owner, evidence needed, and escalation.
- **HIGH priority — operationalize independence:** record reviewer identity/role, exact commit reviewed, tool/model and version when applicable, author relationship, findings, and disposition. A different model label alone does not guarantee independent reasoning.
- **HIGH priority — disagreement handling:** retain conflicting findings and resolve them with discriminating tests or primary sources. Do not treat majority vote as proof.
- **HIGH priority — separation of duties:** the authoring agent must not independently approve its own significant change; release-sensitive changes need an independently authorized reviewer.

## Limits

The research supports design direction, not correctness of this repository, its tests, its inventory, or a deployed multi-agent system. The evidence includes work on formal verification, workflow scheduling, IV&V, and emerging agentic QA; external validity for this exact workflow remains uncertain.

## References

- [Full Consensus research thread](https://consensus.app/search/independently-evaluate-the-design-principles-in-th/Gy6ZSaDbSjK82rNocELPrg/)
- [Parameterised three-valued model checking (2016)](https://doi.org/10.1016/j.scico.2016.01.006)
- [Three-valued bounded model checking with cause-guided abstraction refinement (2019)](https://doi.org/10.1016/j.scico.2019.02.002)
- [Independent Verification & Validation for Agile Developed Projects (2024)](https://doi.org/10.1109/aero58975.2024.10521415)
- [Verification Witnesses (2022)](https://doi.org/10.1145/3477579)
- [Consensus in multi-agent systems: a review (2021)](https://doi.org/10.1007/s10462-021-10097-x)
