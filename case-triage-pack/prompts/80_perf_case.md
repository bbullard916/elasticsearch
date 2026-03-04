# 80 - Search / Performance Case Prompt

## Prompt
Analyze this search/indexing performance case and produce a triage report.

Case evidence:
```text
<PASTE_PERF_CASE_EVIDENCE>
```

Focus areas:
- Query latency and throughput regression
- Hot nodes, GC pressure, heap/circuit breaker pressure
- Slow logs/profile output
- Shard sizing/oversharding and cache behavior
- Thread pool rejection and queue saturation

Required commands (customize placeholders):
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/health?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/nodes?v=true&h=name,heap.percent,ram.percent,cpu,load_1m,node.role,master"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats/jvm,fs,thread_pool,indices,breaker?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/hot_threads?threads=3&ignore_idle_threads=true"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/thread_pool/search?v=true&s=queue:desc,rejected:desc"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/shards?v=true&s=index,store"
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" \
  "<ES_URL>/<INDEX>/_search?pretty&profile=true" \
  -d '{"query":{"match_all":{}},"size":10}'
```

Output format:
1) Top hypotheses (ranked)  
2) Immediate risk checks  
3) Commands to run  
4) Likely remediation paths  
5) Customer-safe explanation  
6) Internal engineer notes
