# Elastic Support Case Triage Pack

Reusable templates, prompts, and command snippets for fast triage of:
- Elasticsearch
- Kibana
- ECK / Kubernetes
- Fleet / Elastic Agent
- Logstash
- Elastic Cloud

## Structure
```text
case-triage-pack/
  prompts/
  templates/
  cases/
  snippets/
```

## Quick start
1. Fill `templates/case_intake.md` with customer evidence.
2. Use `prompts/00_rules.md` + a domain prompt (`50`-`80`) in your assistant workflow.
3. Copy commands from `snippets/` and replace placeholders (`<ES_URL>`, `<INDEX>`, `<POD>`, `<NAMESPACE>`).
4. Save final output using `templates/triage_output.md`.

## Placeholder conventions
- Elasticsearch: `<ES_URL>`, `<INDEX>`, `<DATA_STREAM>`
- Kubernetes/ECK: `<NAMESPACE>`, `<POD>`
- Logstash: `<LOGSTASH_HOST>`, `<LOGSTASH_PORT>`
