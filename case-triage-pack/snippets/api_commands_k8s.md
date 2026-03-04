# Kubernetes / ECK Command Snippets

Replace placeholders:
- `<NAMESPACE>`
- `<POD>`
- `<ES_RESOURCE_NAME>`
- `<KIBANA_RESOURCE_NAME>`

## Cluster context and workload health
```bash
kubectl config current-context
kubectl -n <NAMESPACE> get pods -o wide
kubectl -n <NAMESPACE> get svc,endpoints
kubectl -n <NAMESPACE> get events --sort-by=.lastTimestamp
```

## Pod-level diagnostics
```bash
kubectl -n <NAMESPACE> describe pod <POD>
kubectl -n <NAMESPACE> logs <POD> --tail=200
kubectl -n <NAMESPACE> logs <POD> --previous --tail=200
kubectl -n <NAMESPACE> top pod <POD>
```

## ECK custom resources
```bash
kubectl -n <NAMESPACE> get elasticsearch,kibana,agent,fleetserver
kubectl -n <NAMESPACE> describe elasticsearch <ES_RESOURCE_NAME>
kubectl -n <NAMESPACE> describe kibana <KIBANA_RESOURCE_NAME>
kubectl -n <NAMESPACE> get elasticsearch <ES_RESOURCE_NAME> -o yaml
```

## Operator and reconciliation checks
```bash
kubectl -n <NAMESPACE> logs deploy/elastic-operator --tail=200
kubectl -n <NAMESPACE> get secrets
kubectl -n <NAMESPACE> get configmaps
```

## Connectivity and DNS checks from a pod
```bash
kubectl -n <NAMESPACE> exec -it <POD> -- sh -c "getent hosts <SERVICE_NAME>"
kubectl -n <NAMESPACE> exec -it <POD> -- sh -c "nc -vz <SERVICE_NAME> 9200"
kubectl -n <NAMESPACE> exec -it <POD> -- sh -c "curl -k -I https://<SERVICE_NAME>:9200"
```
