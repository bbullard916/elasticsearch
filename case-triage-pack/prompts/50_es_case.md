# 50 - Elasticsearch Case Prompt

## Prompt
Analyze this Elasticsearch case and produce a triage report.

Case evidence:
```text
<PASTE_ES_CASE_EVIDENCE>
```

Focus areas:
- Cluster health and node state
- Shard allocation / unassigned shards
- ILM / rollover / data stream lifecycle
- Mapping or disk watermark constraints
- Security/auth failures impacting API calls

Required commands (customize with placeholders):
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/health?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/nodes?v=true&h=name,ip,node.role,master,heap.percent,ram.percent,cpu,load_1m,disk.used_percent"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/shards?v=true&s=state,index,shard,prirep,node"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/indices?v=true&s=health,status,index"
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" "<ES_URL>/_cluster/allocation/explain?pretty" -d '{"index":"<INDEX>","shard":0,"primary":false}'
curl -sS -u <USER>:<PASS> "<ES_URL>/<INDEX>/_ilm/explain?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_data_stream?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats?pretty"
```

Output format:
1) Top hypotheses (ranked)  
2) Immediate risk checks  
3) Commands to run  
4) Likely remediation paths  
5) Customer-safe explanation  
6) Internal engineer notes
