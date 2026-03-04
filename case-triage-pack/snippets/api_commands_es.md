# Elasticsearch API Command Snippets

Replace placeholders before running:
- `<ES_URL>` e.g. `https://es-prod.example.com:9200`
- `<USER>` / `<PASS>`
- `<INDEX>`, `<DATA_STREAM>`, `<NODE_ID>`

## Core cluster triage
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/health?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/nodes?v=true&h=name,ip,node.role,master,heap.percent,ram.percent,cpu,load_1m,disk.used_percent"
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/shards?v=true&s=state,index,shard,prirep,node,unassigned.reason"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats?pretty"
```

## Shard allocation
```bash
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" \
  "<ES_URL>/_cluster/allocation/explain?pretty" \
  -d '{"index":"<INDEX>","shard":0,"primary":false}'

curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/settings?include_defaults=true&pretty"
```

## ILM / rollover / data streams
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/<INDEX>/_ilm/explain?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_ilm/policy?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_data_stream?pretty"
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" \
  "<ES_URL>/<INDEX>/_rollover?dry_run=true&pretty" \
  -d '{}'
```

## Ingest diagnostics
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_ingest/pipeline?pretty"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats/ingest?pretty"
curl -sS -u <USER>:<PASS> -H "Content-Type: application/json" \
  "<ES_URL>/_ingest/pipeline/<PIPELINE_ID>/_simulate?pretty" \
  -d '{"docs":[{"_source":{"message":"sample"}}]}'
```

## Search/performance quick checks
```bash
curl -sS -u <USER>:<PASS> "<ES_URL>/_cat/thread_pool/search?v=true&s=queue:desc,rejected:desc"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/hot_threads?threads=3&ignore_idle_threads=true"
curl -sS -u <USER>:<PASS> "<ES_URL>/_nodes/stats/jvm,thread_pool,breaker,fs,indices?pretty"
```
