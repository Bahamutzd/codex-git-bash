#!/usr/bin/env bash
set -euo pipefail

git ls-remote --tags --refs https://github.com/openai/codex.git \
  | awk -F/ '$3 ~ /^rust-v[0-9]+\.[0-9]+\.[0-9]+$/ { print $3 }' \
  | sort -V \
  | tail -n 1
