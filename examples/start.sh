#!/usr/bin/env bash
set -euo pipefail
readonly MAX_ENTRIES=128
service="${1:-api}"

describe() {
  local name="$1"
  if [[ "$name" =~ ^[a-z]+$ ]]; then
    printf '%s: capacity=%d\n' "$name" "$MAX_ENTRIES"
  fi
}

describe "$service"
