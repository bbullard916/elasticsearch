# Logstash Command Snippets

Replace placeholders:
- `<LOGSTASH_HOST>`
- `<LOGSTASH_PORT>` (default `9600`)
- `<PIPELINE_ID>`
- `<SERVICE_NAME>`

## Node and pipeline stats
```bash
curl -sS "http://<LOGSTASH_HOST>:<LOGSTASH_PORT>/_node?pretty"
curl -sS "http://<LOGSTASH_HOST>:<LOGSTASH_PORT>/_node/stats?pretty"
curl -sS "http://<LOGSTASH_HOST>:<LOGSTASH_PORT>/_node/stats/pipelines?pretty"
curl -sS "http://<LOGSTASH_HOST>:<LOGSTASH_PORT>/_node/hot_threads?pretty"
```

## Pipeline-focused checks
```bash
curl -sS "http://<LOGSTASH_HOST>:<LOGSTASH_PORT>/_node/stats/pipelines/<PIPELINE_ID>?pretty"
curl -sS "http://<LOGSTASH_HOST>:<LOGSTASH_PORT>/_node/pipelines?pretty"
```

## Common service-level checks (systemd)
```bash
sudo systemctl status <SERVICE_NAME>
sudo journalctl -u <SERVICE_NAME> --since "30 minutes ago"
```

## Queue/backpressure signals to inspect
- `events.in` vs `events.out` divergence
- `queue_push_duration_in_millis` growth
- persistent queue settings and disk usage
- output plugin error/retry counters
