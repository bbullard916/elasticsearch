# Elastic Support Triage Output

Use this template for final triage reports. Keep commands copy/paste ready.

## 1) Top hypotheses (ranked)

| Rank | Hypothesis | Confidence (0-100) | Evidence for | Evidence against | Validation command(s) |
|---|---|---:|---|---|---|
| 1 | `<HYPOTHESIS_1>` | `<CONF>` | `<WHY>` | `<WHY_NOT>` | `<CMD>` |
| 2 | `<HYPOTHESIS_2>` | `<CONF>` | `<WHY>` | `<WHY_NOT>` | `<CMD>` |
| 3 | `<HYPOTHESIS_3>` | `<CONF>` | `<WHY>` | `<WHY_NOT>` | `<CMD>` |

## 2) Immediate risk checks
- Service/data risk: `<NONE|LOW|MEDIUM|HIGH|CRITICAL>`
- Data loss risk: `<YES|NO|UNKNOWN>`
- Ongoing ingestion impact: `<NONE|PARTIAL|FULL_STOP>`
- Customer-visible outage risk in next 24h: `<ASSESSMENT>`
- Recommended immediate safeguards:
  1. `<SAFEGUARD_1>`
  2. `<SAFEGUARD_2>`

## 3) Commands to run

### Elasticsearch core checks
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/health?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/nodes?v=true&h=name,ip,heap.percent,ram.percent,cpu,load_1m,node.role,master"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/shards?v=true&s=state,index,shard"
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" \
  "<ES_URL>/_cluster/allocation/explain?pretty" \
  -d '{"index":"<INDEX>","shard":0,"primary":false}'
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/<INDEX>/_ilm/explain?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_data_stream?pretty"
```

### Kubernetes / ECK checks (if applicable)
```bash
kubectl -n <NAMESPACE> get pods -o wide
kubectl -n <NAMESPACE> describe pod <POD>
kubectl -n <NAMESPACE> logs <POD> --tail=200
kubectl -n <NAMESPACE> get elasticsearch,kibana,agent,fleetserver
```

### Ingest / Logstash / Agent checks (if applicable)
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_ingest/pipeline/<PIPELINE_ID>?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats/ingest?pretty"
curl -sS "http://<LOGSTASH_HOST>:9600/_node/stats/pipelines?pretty"
```

## 4) Likely remediation paths
1. **Path A (least risk):** `<ACTION_SET>`  
   - Preconditions: `<PRECHECKS>`
   - Rollback: `<ROLLBACK_STEPS>`
2. **Path B (faster but higher risk):** `<ACTION_SET>`  
   - Preconditions: `<PRECHECKS>`
   - Rollback: `<ROLLBACK_STEPS>`
3. **Path C (structural fix):** `<ACTION_SET>`

## 5) Customer-safe explanation
`<Explain current state, likely cause, and next actions in plain language without internal-only details. Include expected timelines and what evidence is being collected next.>`

## 6) Internal engineer notes
- Internal assessment details: `<NOTES>`
- What to avoid saying externally yet: `<SENSITIVE_NOTES>`
- Escalation recommendation: `<NONE|ENG|SRE|CLOUD>`
- Next internal checkpoint: `<DATE_TIME>`
