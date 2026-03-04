# 20 - Targeted Questions and Commands

## Prompt
Given the case evidence, produce:
1) the minimum high-value follow-up questions for the customer, and  
2) exact commands to collect missing evidence.

Case evidence:
```text
<PASTE_EVIDENCE>
```

Requirements:
- Ask no more than 12 questions.
- Prioritize questions that change hypothesis ranking.
- Group commands by domain:
  - Elasticsearch
  - Kubernetes/ECK
  - Fleet/Agent
  - Logstash/Ingest
- Use placeholders like `<ES_URL>`, `<INDEX>`, `<POD>`, `<NAMESPACE>`.
- For each command, explain what signal it validates.

Also include core Elasticsearch checks:
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/health?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/nodes?v=true"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/shards?v=true"
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" "<ES_URL>/_cluster/allocation/explain?pretty" -d '{"index":"<INDEX>","shard":0,"primary":false}'
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/<INDEX>/_ilm/explain?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_data_stream?pretty"
```
