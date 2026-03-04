# 70 - Ingest / Fleet / Logstash Case Prompt

## Prompt
Analyze this ingest pipeline case and produce a triage report.

Case evidence:
```text
<PASTE_INGEST_CASE_EVIDENCE>
```

Focus areas:
- Ingest pipeline processor failures
- Fleet Server enrollment/policy distribution problems
- Elastic Agent unhealthy/offline states
- Logstash pipeline backpressure, queue saturation, output failures
- Mapping conflicts and rejected documents

Required commands (customize placeholders):
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_ingest/pipeline/<PIPELINE_ID>?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats/ingest?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/indices?v=true&s=docs.count,store.size"
curl -sS -u <USER>:<PASS> "<ES_URL>/<INDEX>/_search?size=0&track_total_hits=true"
curl -sS "http://<LOGSTASH_HOST>:9600/_node/stats/pipelines?pretty"
curl -sS "http://<LOGSTASH_HOST>:9600/_node/hot_threads?pretty"
kubectl -n <NAMESPACE> get pods -l app=fleet-server -o wide
kubectl -n <NAMESPACE> logs <POD> --tail=200
```

Output format:
1) Top hypotheses (ranked)  
2) Immediate risk checks  
3) Commands to run  
4) Likely remediation paths  
5) Customer-safe explanation  
6) Internal engineer notes
