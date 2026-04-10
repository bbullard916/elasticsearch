"""
Requirements:
- minikube OR Docker Desktop with Kubernetes enabled
- kubectl
- Mac/Linux

Usage:
  python3 local-kbn-es.py
"""

import base64
import json
import subprocess
import time

import urllib3

urllib3.disable_warnings()

IMAGE_WAIT_REASONS = {"ContainerCreating", "ErrImagePull", "ImagePullBackOff", "PodInitializing"}


def get_url(
    url: str, username: str = "", password: str = "", verify_ssl: bool = True
) -> str:
    """Get URL helper function."""
    if not verify_ssl:
        http = urllib3.PoolManager(cert_reqs="CERT_NONE")
    else:
        http = urllib3.PoolManager()
    headers = {}
    if username and password:
        auth_string = f"{username}:{password}".encode("utf-8")
        auth_header = "Basic " + base64.b64encode(auth_string).decode("utf-8")
        headers["Authorization"] = auth_header
    response = http.request("GET", url, headers=headers)
    if response.status == 200:
        data = response.data.decode("utf-8")
        return data
    print(f"Error: {response.status}")
    return ""


def run_command(command: str, suppress: bool = False):
    """Run a shell command and print the output."""
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        if not suppress:
            print(f"Error running command: {command}\n{stderr.decode()}")
        return None
    message = stdout.decode()
    if not suppress:
        print(message)
    return message


def wait_for_secret(secret_name: str, timeout_seconds: int = 240) -> bool:
    """Wait until a secret exists."""
    print(f"Waiting for secret {secret_name}...")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        secret = run_command(
            f"kubectl get secret {secret_name} -o name", suppress=True
        )
        if secret:
            return True
        time.sleep(3)
    print(f"Timed out waiting for secret: {secret_name}")
    return False


def wait_for_operator_ready(timeout_seconds: int = 420) -> bool:
    """Wait for ECK operator rollout and pod readiness."""
    print("Waiting for ECK operator rollout...")
    rollout_ok = False
    if run_command(
        "kubectl get statefulset elastic-operator -n elastic-system -o name",
        suppress=True,
    ):
        rollout_ok = bool(
            run_command(
                f"kubectl rollout status statefulset/elastic-operator -n elastic-system --timeout={timeout_seconds}s",
                suppress=True,
            )
        )
    elif run_command(
        "kubectl get deployment elastic-operator -n elastic-system -o name",
        suppress=True,
    ):
        rollout_ok = bool(
            run_command(
                f"kubectl rollout status deployment/elastic-operator -n elastic-system --timeout={timeout_seconds}s",
                suppress=True,
            )
        )

    # Label has varied between versions; try both.
    pods_ready = bool(
        run_command(
            f"kubectl wait --for=condition=Ready pod -l control-plane=elastic-operator -n elastic-system --timeout={timeout_seconds}s",
            suppress=True,
        )
    ) or bool(
        run_command(
            f"kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=elastic-operator -n elastic-system --timeout={timeout_seconds}s",
            suppress=True,
        )
    )

    if not rollout_ok and not pods_ready:
        print("Warning: operator readiness check did not fully succeed.")
    return rollout_ok or pods_ready


def wait_for_pods_ready(
    label_selector: str,
    namespace: str = "default",
    timeout_seconds: int = 900,
    description: str = "pods",
) -> bool:
    """
    Wait for pods matching the selector to become ready.

    This helps avoid racing requests while images are still pulling.
    """
    print(f"Waiting for {description} to become Ready...")
    deadline = time.time() + timeout_seconds
    last_report = 0.0

    while time.time() < deadline:
        raw = run_command(
            f"kubectl get pods -n {namespace} -l '{label_selector}' -o json",
            suppress=True,
        )
        if not raw:
            time.sleep(4)
            continue
        try:
            pod_data = json.loads(raw)
        except json.decoder.JSONDecodeError:
            time.sleep(4)
            continue

        items = pod_data.get("items", [])
        if not items:
            if time.time() - last_report > 10:
                print(f"No {description} found yet for selector: {label_selector}")
                last_report = time.time()
            time.sleep(4)
            continue

        all_ready = True
        reasons = []
        summary = []
        for pod in items:
            pod_name = pod.get("metadata", {}).get("name", "<unknown>")
            phase = pod.get("status", {}).get("phase", "Unknown")
            statuses = pod.get("status", {}).get("containerStatuses", []) or []
            pod_ready = bool(statuses) and all(cs.get("ready", False) for cs in statuses)
            if not pod_ready:
                all_ready = False
            waiting_reasons = []
            for cs in statuses:
                waiting = cs.get("state", {}).get("waiting")
                if waiting and waiting.get("reason"):
                    waiting_reasons.append(waiting["reason"])
            reasons.extend(waiting_reasons)
            summary.append(
                f"{pod_name}: phase={phase}, ready={pod_ready}, waiting={waiting_reasons or '-'}"
            )

        if time.time() - last_report > 10:
            print(" | ".join(summary))
            last_report = time.time()

        if all_ready:
            # Tiny settle window so the next step does not race startup.
            time.sleep(3)
            return True

        pull_reasons = sorted(set(r for r in reasons if r in IMAGE_WAIT_REASONS))
        if pull_reasons and time.time() - last_report > 2:
            print(f"Still waiting on container startup/image pull: {', '.join(pull_reasons)}")

        time.sleep(4)

    print(f"Timed out waiting for {description}.")
    run_command(f"kubectl get pods -n {namespace} -l '{label_selector}' -o wide")
    return False


def install_crd_operator(operator_version: str):
    """Install CRD and Operator with specified version."""
    print(f"Installing CRD and Operator version {operator_version}...")
    run_command(
        f"kubectl apply -f https://download.elastic.co/downloads/eck/{operator_version}/crds.yaml"
    )
    run_command(
        f"kubectl apply -f https://download.elastic.co/downloads/eck/{operator_version}/operator.yaml"
    )


def install_quickstart(elasticsearch_version: str):
    """Install Elasticsearch quickstart with specified version."""
    print(f"Installing Elasticsearch quickstart version {elasticsearch_version}...")
    quickstart_yaml = f"""
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: quickstart
spec:
  version: {elasticsearch_version}
  http:
    service:
      spec:
        type: NodePort
        ports:
          - port: 9200
            nodePort: 31920
            name: https
            protocol: TCP
            targetPort: 9200
  nodeSets:
  - name: default
    count: 1
    config:
      node.store.allow_mmap: false
"""
    run_command(f"echo '{quickstart_yaml}' | kubectl apply -f -")


def install_kibana(kibana_version: str):
    """Install Kibana with specified version."""
    print(f"Installing Kibana version {kibana_version}...")
    kibana_yaml = f"""
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: quickstart
spec:
  version: {kibana_version}
  http:
    service:
      spec:
        type: NodePort
        ports:
          - port: 5601
            nodePort: 31561
            name: https
            protocol: TCP
            targetPort: 5601
  count: 1
  elasticsearchRef:
    name: quickstart
"""
    run_command(f"echo '{kibana_yaml}' | kubectl apply -f -")


def get_repo_version(repo_name: str) -> str:
    """Check GitHub for latest release version."""
    try:
        response = json.loads(
            get_url(
                url=f"https://api.github.com/repos/elastic/{repo_name}/releases/latest"
            )
        )
        version = response["tag_name"].replace("v", "")
    except urllib3.exceptions.HTTPError:
        version = "UNKNOWN"
    return version


def prompt_version(repo_name: str, name: str) -> str:
    """Prompt for version to install."""
    latest_release = get_repo_version(repo_name)
    version = input(f"{name} version to install or leave blank for {latest_release}: ")
    if not version:
        version = latest_release
    return version


def prompt_yes_no(message: str, default_no: bool = True) -> bool:
    """Simple y/N prompt."""
    default_hint = "y/N" if default_no else "Y/n"
    ans = input(f"{message} [{default_hint}]: ").strip().lower()
    if ans == "" and default_no:
        return False
    if ans == "" and not default_no:
        return True
    return ans.startswith("y")


def get_elastic_password() -> str:
    """Get 'elastic' user password from secrets."""
    password = run_command(
        "kubectl get secret quickstart-es-elastic-user -o=jsonpath='{.data.elastic}' | base64 --decode; echo",
        suppress=True,
    )
    return (password or "").replace("\n", "")


def get_service_url(service: str) -> str:
    """Get service URL from Minikube or Kubernetes."""
    # Try to get the URL from Minikube
    url = run_command(
        f"minikube service quickstart-{service}-http --url --wait 10", suppress=True
    )
    if url:
        return url.replace("http://", "https://").replace("\n", "")
    print("Minikube command failed, falling back to localhost NodePort...")

    # We expose fixed NodePorts above; just return those.
    if service == "es":
        return "https://localhost:31920"
    if service == "kb":
        return "https://localhost:31561"

    return "Service URL not found"


def install_monitoring(elastic_version: str):
    """
    Install an Elastic Agent DaemonSet (standalone) that sends system + Kubernetes metrics
    to the local quickstart Elasticsearch over HTTPS with ssl.verification_mode: none.
    """
    print(f"Installing monitoring (Elastic Agent {elastic_version})...")

    # RBAC + SA
    rbac_yaml = """
apiVersion: v1
kind: ServiceAccount
metadata:
  name: elastic-agent
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: elastic-agent
rules:
- apiGroups: [""]
  resources: ["nodes", "namespaces", "pods", "services", "endpoints"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["apps"]
  resources: ["replicasets", "daemonsets", "deployments", "statefulsets"]
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: elastic-agent
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: elastic-agent
subjects:
- kind: ServiceAccount
  name: elastic-agent
  namespace: default
"""
    run_command(f"echo '{rbac_yaml}' | kubectl apply -f -")

    # ConfigMap for standalone Elastic Agent
    cfg_yaml = r"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: elastic-agent-config
  namespace: default
data:
  elastic-agent.yml: |-
    outputs:
      default:
        type: elasticsearch
        hosts: ["https://quickstart-es-http:9200"]
        username: ${ELASTIC_USERNAME}
        password: ${ELASTIC_PASSWORD}
        ssl.verification_mode: none

    inputs:
      - type: system/metrics
        use_output: default
        streams:
          - dataset: system.cpu
            period: 10s
          - dataset: system.memory
            period: 10s
          - dataset: system.filesystem
            period: 1m
          - dataset: system.load
            period: 10s
          - dataset: system.network
            period: 1m

      - type: kubernetes/metrics
        use_output: default
        namespace: kube-system
        streams:
          - dataset: kubernetes.container
            period: 30s
          - dataset: kubernetes.node
            period: 30s
          - dataset: kubernetes.pod
            period: 30s
          - dataset: kubernetes.system
            period: 30s
"""
    run_command(f"echo '{cfg_yaml}' | kubectl apply -f -")

    # DaemonSet
    ds_yaml = f"""
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: elastic-agent
  namespace: default
  labels:
    app: elastic-agent
spec:
  selector:
    matchLabels:
      app: elastic-agent
  template:
    metadata:
      labels:
        app: elastic-agent
    spec:
      serviceAccountName: elastic-agent
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: elastic-agent
        image: elastic/elastic-agent:{elastic_version}
        args: ["-e", "-c", "/etc/elastic-agent/elastic-agent.yml"]
        env:
        - name: ELASTIC_USERNAME
          value: "elastic"
        - name: ELASTIC_PASSWORD
          valueFrom:
            secretKeyRef:
              name: quickstart-es-elastic-user
              key: elastic
        volumeMounts:
        - name: agent-config
          mountPath: /etc/elastic-agent
        - name: var-run
          mountPath: /var/run
        - name: proc
          mountPath: /hostfs/proc
          readOnly: true
        - name: cgroup
          mountPath: /hostfs/sys/fs/cgroup
          readOnly: true
        securityContext:
          runAsUser: 0
      volumes:
      - name: agent-config
        configMap:
          name: elastic-agent-config
          items:
          - key: elastic-agent.yml
            path: elastic-agent.yml
      - name: var-run
        hostPath:
          path: /var/run
      - name: proc
        hostPath:
          path: /proc
      - name: cgroup
        hostPath:
          path: /sys/fs/cgroup
      tolerations:
      - operator: "Exists"
"""
    run_command(f"echo '{ds_yaml}' | kubectl apply -f -")

    print("Monitoring installed: Elastic Agent DaemonSet is rolling out...")


def main(operator_version: str, elasticsearch_version: str, enable_monitoring: bool):
    """Main function."""
    install_crd_operator(operator_version)
    # Give API server a short beat to register/propagate applied operator resources.
    time.sleep(3)
    wait_for_operator_ready()

    install_quickstart(elasticsearch_version)
    wait_for_secret("quickstart-es-elastic-user")
    wait_for_pods_ready(
        "elasticsearch.k8s.elastic.co/cluster-name=quickstart",
        description="Elasticsearch pods",
    )

    print("Waiting for Elasticsearch API Startup...")
    ready = False
    elastic_password = None
    elastic_url = None
    es_deadline = time.time() + 600

    while not ready and time.time() < es_deadline:
        try:
            elastic_password = get_elastic_password()
            if not elastic_password:
                time.sleep(3)
                continue
            elastic_url = get_service_url(service="es")
            print(elastic_url)
            health_raw = get_url(
                url=f"{elastic_url}/_cluster/health",
                username="elastic",
                password=elastic_password,
                verify_ssl=False,
            )
            if not health_raw:
                time.sleep(3)
                continue
            health = json.loads(health_raw)
            print(health.get("status"))
            if health.get("status") in ("yellow", "green"):
                # Yellow is fine for single-node while shards initialize.
                ready = True
        except (urllib3.exceptions.HTTPError, json.decoder.JSONDecodeError, AttributeError):
            time.sleep(5)
        time.sleep(1)

    if not ready:
        print("Elasticsearch did not become ready in time.")
        return

    install_kibana(elasticsearch_version)
    wait_for_pods_ready(
        "kibana.k8s.elastic.co/name=quickstart",
        description="Kibana pods",
    )

    print("Waiting for Kibana Startup...")
    ready = False
    kibana_url = None
    kibana_deadline = time.time() + 600
    while not ready and time.time() < kibana_deadline:
        try:
            kibana_url = get_service_url(service="kb")
            # Any authenticated API endpoint works as readiness probe.
            uptime_raw = get_url(
                url=f"{kibana_url}/api/uptime/settings",
                username="elastic",
                password=elastic_password,
                verify_ssl=False,
            )
            if uptime_raw:
                ready = True
        except (urllib3.exceptions.HTTPError, json.decoder.JSONDecodeError, AttributeError):
            time.sleep(5)
        time.sleep(1)

    if not ready:
        print("Kibana did not become ready in time.")
        return

    if enable_monitoring:
        install_monitoring(elasticsearch_version)
        print("You can open Kibana > Observability > Metrics to see data roll in (give it a minute).")

    print(f"To access Elasticsearch, open {elastic_url} in your browser.")
    print(f"To access Kibana, open {kibana_url} in your browser.")
    print("Your generated password:", elastic_password)


if __name__ == "__main__":
    eck_version = prompt_version(repo_name="cloud-on-k8s", name="ECK Operator")
    stack_version = prompt_version(repo_name="elasticsearch", name="Elastic Stack")
    enable_mon = prompt_yes_no(
        "Install optional monitoring (Elastic Agent: system + Kubernetes metrics)?",
        default_no=True,
    )
    main(eck_version, stack_version, enable_mon)
