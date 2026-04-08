#!/usr/bin/env bash
set -euo pipefail

ANNOTATION_KEY="eck.k8s.elastic.co/managed"

usage() {
    cat <<'EOF'
Remove the ECK managed annotation from Elastic resources.

Usage:
  remove_eck_managed_annotation.sh resource <resource-type> <name> [-n <namespace>]
  remove_eck_managed_annotation.sh namespace [<namespace>]
  remove_eck_managed_annotation.sh all-namespaces

Examples:
  # Remove the annotation from a single Elasticsearch resource named "quickstart"
  remove_eck_managed_annotation.sh resource elasticsearch quickstart

  # Remove the annotation from all Elastic resources in the current namespace
  remove_eck_managed_annotation.sh namespace

  # Remove the annotation from all Elastic resources in a specific namespace
  remove_eck_managed_annotation.sh namespace elastic-system

  # Remove the annotation from all Elastic resources in all namespaces
  remove_eck_managed_annotation.sh all-namespaces
EOF
}

run_kubectl_annotate() {
    local -a command=(kubectl annotate --overwrite "$@")

    printf '+ '
    printf '%q ' "${command[@]}"
    printf '\n'

    "${command[@]}"
}

remove_from_resource() {
    local resource_type="$1"
    local resource_name="$2"
    shift 2

    run_kubectl_annotate "$resource_type" "$resource_name" "${ANNOTATION_KEY}-" "$@"
}

remove_from_namespace() {
    local namespace="${1:-}"
    local -a namespace_args=()

    if [[ -n "$namespace" ]]; then
        namespace_args=(-n "$namespace")
    fi

    run_kubectl_annotate elastic --all "${ANNOTATION_KEY}-" "${namespace_args[@]}"
}

remove_from_all_namespaces() {
    local namespace
    mapfile -t namespaces < <(kubectl get ns -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}')

    for namespace in "${namespaces[@]}"; do
        if [[ -z "$namespace" ]]; then
            continue
        fi

        echo "Processing namespace: ${namespace}"
        run_kubectl_annotate elastic --all "${ANNOTATION_KEY}-" -n "$namespace"
    done
}

main() {
    case "${1:-}" in
        resource|single)
            if [[ $# -ne 3 && $# -ne 5 ]]; then
                usage
                exit 1
            fi

            if [[ $# -eq 5 && "$4" != "-n" ]]; then
                usage
                exit 1
            fi

            remove_from_resource "$2" "$3" "${@:4}"
            ;;
        namespace)
            if [[ $# -gt 2 ]]; then
                usage
                exit 1
            fi

            remove_from_namespace "${2:-}"
            ;;
        all-namespaces)
            if [[ $# -ne 1 ]]; then
                usage
                exit 1
            fi

            remove_from_all_namespaces
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
