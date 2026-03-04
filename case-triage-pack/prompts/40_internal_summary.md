# 40 - Internal Engineer Summary

## Prompt
Create an internal-only case summary for handoff/escalation.

Inputs:
```text
<PASTE_CASE_DATA_AND_TRIAGE_OUTPUT>
```

Must include:
1. Ranked hypotheses with confidence and why.
2. Key evidence supporting/refuting each hypothesis.
3. Immediate risks (availability, data loss, ingestion backpressure).
4. Commands already executed and outcomes.
5. Missing evidence and blockers.
6. Recommended next 3 actions with owner and ETA.
7. Escalation recommendation: `<NONE|ENG|SRE|CLOUD>` and rationale.

Formatting:
- Bullet-heavy, high signal, no customer-facing language.
- Explicitly mark assumptions and unknowns.
