#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-http://127.0.0.1:8000}"

curl -s "${HOST}/health"
echo
curl -s "${HOST}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-local",
    "messages": [
      {"role": "user", "content": "Reply with exactly: API OK"}
    ],
    "max_tokens": 16,
    "temperature": 0.1
  }'
echo
