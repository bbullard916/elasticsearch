# Elastic Support Case Intake

Use this form to gather consistent, high-signal evidence before triage.

## 1) Case metadata
- Case ID: `<CASE_ID>`
- Severity / priority: `<SEV>`
- Product area: `<Elasticsearch|Kibana|ECK|Fleet|Logstash|Elastic Cloud>`
- Deployment type: `<Elastic Cloud|Self-managed|ECK|ECE>`
- Customer timezone / contact window: `<TZ>`
- Escalation status: `<None|Eng|SRE|Cloud>`

## 2) Environment snapshot
- ES URL: `<ES_URL>`
- Kibana URL: `<KIBANA_URL>`
- Cluster name / UUID: `<CLUSTER_NAME> / <CLUSTER_UUID>`
- Version(s): `<STACK_VERSION>`
- Node count and roles: `<NODES_AND_ROLES>`
- Orchestrator (if any): `<Kubernetes|ECK|VM|Bare metal>`
- Namespace / cluster context (K8s): `<NAMESPACE> / <KUBE_CONTEXT>`

## 3) Problem statement
- What is broken? `<ONE_SENTENCE_PROBLEM>`
- Business impact: `<IMPACT>`
- Start time (UTC): `<YYYY-MM-DDTHH:MM:SSZ>`
- Last known good: `<TIMESTAMP>`
- Scope: `<ALL_USERS|SOME_USERS|ONE_INDEX|ONE_AGENT|ONE_NAMESPACE>`

## 4) Symptoms and observed signals
- Error messages (exact):  
  ```text
  <PASTE_EXACT_ERRORS>
  ```
- Health state(s): `<green|yellow|red|unknown>`
- Affected indices / data streams: `<INDEX_OR_DS_LIST>`
- Affected pods / agents / pipelines: `<POD|AGENT|PIPELINE>`

## 5) Evidence already collected
List command + timestamp + result summary.

| Time (UTC) | Command / API | Key result |
|---|---|---|
| `<TIME>` | `<curl|kubectl|logstash API>` | `<RESULT>` |

## 6) Reproduction and timeline
1. `<STEP_1>`
2. `<STEP_2>`
3. `<STEP_3>`

## 7) Domain checkboxes (mark all that apply)
- [ ] Shard allocation / unassigned shards
- [ ] ILM / rollover / data streams
- [ ] Cluster health / master / node instability
- [ ] Ingest pipeline failures
- [ ] Fleet / Elastic Agent enrollment or policy issues
- [ ] ECK / Kubernetes networking, DNS, TLS, auth
- [ ] Search/query/indexing performance
- [ ] Logstash pipeline / queue / output errors

## 8) Constraints and guardrails
- Change window: `<YES|NO>`
- Can restart services/pods? `<YES|NO>`
- Can run diagnostic APIs? `<YES|NO>`
- Security restrictions / redaction needs: `<DETAILS>`

## 9) Desired outcome
- Short-term restore target: `<TARGET>`
- Long-term fix target: `<TARGET>`
- Deadline / milestone: `<DATE_TIME>`
