# 60 - ECK / Kubernetes Case Prompt

## Prompt
Analyze this ECK/Kubernetes Elastic Stack case and produce a triage report.

Case evidence:
```text
<PASTE_ECK_K8S_EVIDENCE>
```

Focus areas:
- Pod scheduling, restarts, readiness/liveness
- Service DNS/network path failures between components
- TLS/auth secret mismatches
- Operator reconciliation errors
- Fleet Server / Agent communication issues inside Kubernetes

Required commands (customize placeholders):
```bash
kubectl config current-context
kubectl -n <NAMESPACE> get pods -o wide
kubectl -n <NAMESPACE> get svc,endpoints
kubectl -n <NAMESPACE> describe pod <POD>
kubectl -n <NAMESPACE> logs <POD> --tail=200
kubectl -n <NAMESPACE> get events --sort-by=.lastTimestamp | tail -n 50
kubectl -n <NAMESPACE> get elasticsearch,kibana,agent,fleetserver -o yaml
kubectl -n <NAMESPACE> describe elasticsearch <ES_RESOURCE_NAME>
kubectl -n <NAMESPACE> logs deploy/elastic-operator --tail=200
curl -sS -u <USER>:<PASS> "<ES_URL>/_cluster/health?pretty"
```

Output format:
1) Top hypotheses (ranked)  
2) Immediate risk checks  
3) Commands to run  
4) Likely remediation paths  
5) Customer-safe explanation  
6) Internal engineer notes
