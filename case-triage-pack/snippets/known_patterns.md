# Known Triage Patterns (Quick Ranking Aid)

Use this sheet to map symptoms to likely causes quickly.

| Domain | Symptom pattern | Common root cause | Fast validation | Typical remediation |
|---|---|---|---|---|
| Shard allocation | Cluster red/yellow + unassigned shards | Disk watermark, awareness/filter rules, missing nodes | `_cat/shards`, `_cluster/allocation/explain`, `_cluster/settings` | Free disk, adjust allocation rules, restore missing node/path |
| ILM / rollover | Write index not rolling over, DS growth stalls | ILM policy mismatch, alias misconfig, rollover conditions unmet | `<INDEX>/_ilm/explain`, `_ilm/policy`, `_data_stream` | Fix policy/alias, adjust size/age conditions, retry step |
| Cluster health | Master instability, frequent elections | Network partition, overloaded master-eligible nodes, GC pauses | `_cluster/health`, `_cat/nodes`, `_nodes/stats/jvm` | Stabilize networking, right-size masters, reduce load spikes |
| Ingest failures | 4xx/5xx ingest errors, rejected docs | Pipeline processor failure, mapping conflict, auth issues | `_nodes/stats/ingest`, pipeline `_simulate`, error logs | Fix processor logic, update mappings/templates, correct credentials |
| Fleet / Agent | Agents offline or unhealthy | Fleet Server unreachable, policy/artifact download failure, cert issues | Fleet Server logs, Agent logs, connectivity checks | Restore Fleet reachability, fix TLS trust, re-enroll/update policy |
| ECK / K8s auth | Pods running but auth/TLS failures | Secret mismatch, cert rotation issue, wrong service endpoint | `kubectl describe`, secret refs, operator logs | Reconcile secrets, rotate certs cleanly, update refs/endpoints |
| ECK / K8s network | Timeouts between components | DNS/service misrouting, NetworkPolicy block, CNI issue | `kubectl get svc,endpoints`, pod exec DNS/TCP checks | Fix service selectors/endpoints/policies, resolve DNS/CNI issues |
| Search performance | Sudden p95/p99 increase | Hot shards, expensive queries, cache misses, thread pool saturation | `_cat/thread_pool`, `hot_threads`, query profile | Tune queries, rebalance/resize shards, increase capacity |
| Indexing performance | Ingest lag and queue growth | Backpressure in Logstash/output, refresh/replica overhead | Logstash pipeline stats, ES thread pool/write stats | Reduce bulk pressure, tune batch/worker, adjust refresh/replicas |

## Hypothesis ranking hints
1. Prefer causes that explain **all** observed symptoms with minimal assumptions.
2. Increase confidence when at least two independent signals agree.
3. Lower confidence when evidence depends on stale snapshots only.
4. Mark unknowns explicitly; request targeted commands to close gaps.
