# Local Gemma 4 API with Hugging Face

This project downloads a Gemma 4 GGUF model from Hugging Face into a local cache and serves it locally through `llama-server`.

## Project structure

```text
.
|-- bin/
|   |-- load_test_10_tps.sh
|   `-- test_api.sh
|-- models/
|-- src/gemma_local_api/
|   |-- cli.py
|   |-- config.py
|   |-- downloader.py
|   |-- load_test.py
|   `-- server.py
|-- pyproject.toml
`-- run_local_api.sh
```

The shell entrypoint is only a thin wrapper now. The real logic lives in the Python package under `src/gemma_local_api`.

## Default model

The server defaults to:

- `MODEL_ID=bartowski/google_gemma-4-E4B-it-GGUF`
- `MODEL_FILE=google_gemma-4-E4B-it-Q2_K_L.gguf`

This is a Hugging Face-hosted GGUF conversion of Google's `google/gemma-4-E4B-it`, chosen because it is much easier to run locally on this machine than the original checkpoint format.

As of April 6, 2026, the `llama.cpp` conversion path for Gemma 4 is still new enough that some community GGUF builds carry warning notes. This setup is the most practical local API path on this machine, but if you need exact parity with Google's official checkpoint behavior, use the original Hugging Face weights with a supported Transformers or vLLM stack on stronger hardware.

If you want a different Gemma 4 quantization, set:

```bash
export MODEL_ID="bartowski/google_gemma-4-E4B-it-GGUF"
export MODEL_FILE="google_gemma-4-E4B-it-Q2_K_L.gguf"
```

## Start

```bash
chmod +x /Users/niranjankumarm/Documents/New\ project/run_local_api.sh
/Users/niranjankumarm/Documents/New\ project/run_local_api.sh
```

Optional environment variables:

```bash
export HOST="0.0.0.0"
export PORT="8000"
export MODEL_CACHE_DIR="/Users/niranjankumarm/Documents/New project/models"
export HF_TOKEN="your-hugging-face-token"
export MODEL_ID="bartowski/google_gemma-4-E4B-it-GGUF"
export MODEL_FILE="google_gemma-4-E4B-it-Q2_K_L.gguf"
export LLAMA_SERVER_BIN="llama-server"
```

You can also use the package entrypoint directly:

```bash
cd /Users/niranjankumarm/Documents/New\ project
PYTHONPATH=src /usr/bin/python3 -m gemma_local_api.cli --print-command
PYTHONPATH=src /usr/bin/python3 -m gemma_local_api.cli
```

Download without starting the server:

```bash
cd /Users/niranjankumarm/Documents/New\ project
PYTHONPATH=src /usr/bin/python3 -m gemma_local_api.cli --download-only
```

## Test

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-local",
    "messages": [
      {"role": "user", "content": "Write a haiku about local model serving."}
    ],
    "max_tokens": 120,
    "temperature": 0.7
  }'
```

Or run:

```bash
chmod +x /Users/niranjankumarm/Documents/LLMOps/bin/test_api.sh
/Users/niranjankumarm/Documents/LLMOps/bin/test_api.sh
```

## 10 TPS load

Send 10 requests per second to the local API for 10 seconds:

```bash
chmod +x /Users/niranjankumarm/Documents/LLMOps/bin/load_test_10_tps.sh
/Users/niranjankumarm/Documents/LLMOps/bin/load_test_10_tps.sh
```

Run it for a different duration:

```bash
/Users/niranjankumarm/Documents/LLMOps/bin/load_test_10_tps.sh 30
```

Or use the Python entrypoint directly:

```bash
cd /Users/niranjankumarm/Documents/LLMOps
PYTHONPATH=src /usr/bin/python3 -m gemma_local_api.load_test --tps 10 --duration 10
```
