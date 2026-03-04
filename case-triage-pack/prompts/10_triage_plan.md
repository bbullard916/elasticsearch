# 10 - Build Triage Plan from Evidence

## Prompt
Using the evidence below, create a triage plan and a draft report.

Inputs:
- Case intake:
  ```text
  <PASTE_CASE_INTAKE>
  ```
- Logs / errors:
  ```text
  <PASTE_LOG_SNIPPETS>
  ```
- Commands already run:
  ```text
  <PASTE_EXISTING_COMMANDS_AND_OUTPUTS>
  ```

Tasks:
1. Identify the most likely failure domain(s).
2. Generate 3-5 ranked hypotheses with confidence and rationale.
3. List immediate risk checks (data loss, availability, ingestion).
4. Provide a command plan:
   - first pass (5-10 minutes)
   - deep dive (30-60 minutes)
5. For each hypothesis, map:
   - validation signal
   - disconfirming signal
   - likely remediation path
6. Draft customer-safe explanation and internal-only notes separately.

Output format:
1) Top hypotheses (ranked)  
2) Immediate risk checks  
3) Commands to run  
4) Likely remediation paths  
5) Customer-safe explanation  
6) Internal engineer notes
