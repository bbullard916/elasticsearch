# 30 - Customer Reply Draft

## Prompt
Draft a customer-safe update based on triage findings.

Inputs:
```text
<PASTE_TRIAGE_FINDINGS>
```

Constraints:
- Do not include internal-only speculation, escalation notes, or sensitive platform details.
- Use plain language and short paragraphs.
- Include:
  1. Current understanding of impact
  2. Most likely cause (framed as preliminary if needed)
  3. Exactly what we are asking the customer to run/provide next
  4. Expected next update time
- Keep tone calm, accountable, and action-oriented.

Output sections:
- Subject line
- Customer message
- Requested commands/evidence block
- Next update ETA
