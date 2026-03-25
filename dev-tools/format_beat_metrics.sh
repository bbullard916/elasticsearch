#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    printf 'Usage: %s <beat_metrics.json>\n' "$(basename "$0")"
    exit 1
fi

INPUT_FILE="$1"

if [ ! -f "${INPUT_FILE}" ]; then
    echo >&2 "Input file '${INPUT_FILE}' does not exist."
    exit 1
fi

jq -r '
    [paths(scalars) as $p | {key: ($p | join(".")), val: (getpath($p) | tostring)}]
    | group_by(.key | split(".")[0])
    | .[]
    | (
        "───────────────────────────────────────────────────────────────────────────────",
        (.[0].key | split(".")[0] | ascii_upcase),
        "───────────────────────────────────────────────────────────────────────────────",
        (
            .[]
            | .key
                + (" " * (56 - (.key | length) | if . < 1 then 1 else . end))
                + " │ "
                + .val
        )
    )
' "${INPUT_FILE}"
