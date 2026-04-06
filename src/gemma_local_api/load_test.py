import argparse
import concurrent.futures
import json
import time
from typing import Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_API_URL = "http://127.0.0.1:8000/v1/chat/completions"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send fixed-rate requests to the local Gemma API."
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help="Chat completions endpoint to call.",
    )
    parser.add_argument(
        "--tps",
        type=float,
        default=10.0,
        help="Target requests per second.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="How long to send traffic, in seconds.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=32,
        help="Max tokens per request.",
    )
    parser.add_argument(
        "--model",
        default="gemma-4-local",
        help="Model field to send in the request body.",
    )
    parser.add_argument(
        "--prompt",
        default="Reply with exactly: API OK",
        help="Prompt sent to each request.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Thread pool size used to maintain the target TPS.",
    )
    return parser


def make_payload(model: str, prompt: str, max_tokens: int) -> bytes:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }
    return json.dumps(body).encode("utf-8")


def send_request(api_url: str, payload: bytes, timeout: float) -> Dict[str, object]:
    started_at = time.perf_counter()
    request = Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            latency_ms = (time.perf_counter() - started_at) * 1000
            return {
                "ok": True,
                "status": response.status,
                "latency_ms": latency_ms,
                "body": body,
            }
    except HTTPError as exc:
        latency_ms = (time.perf_counter() - started_at) * 1000
        return {
            "ok": False,
            "status": exc.code,
            "latency_ms": latency_ms,
            "body": exc.read().decode("utf-8", errors="replace"),
        }
    except URLError as exc:
        latency_ms = (time.perf_counter() - started_at) * 1000
        return {
            "ok": False,
            "status": None,
            "latency_ms": latency_ms,
            "body": str(exc),
        }


def percentile(values: List[float], ratio: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int((len(ordered) - 1) * ratio)
    return ordered[index]


def run_load_test(
    api_url: str,
    tps: float,
    duration: float,
    model: str,
    prompt: str,
    max_tokens: int,
    timeout: float,
    workers: int,
) -> Tuple[int, int, List[float], List[Dict[str, object]]]:
    total_requests = max(1, int(tps * duration))
    interval = 1.0 / tps
    payload = make_payload(model, prompt, max_tokens)
    results: List[Dict[str, object]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        start = time.perf_counter()
        for index in range(total_requests):
            target_time = start + (index * interval)
            sleep_for = target_time - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)
            futures.append(executor.submit(send_request, api_url, payload, timeout))

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    latencies = [float(item["latency_ms"]) for item in results]
    success_count = sum(1 for item in results if item["ok"])
    return total_requests, success_count, latencies, results


def main() -> int:
    args = build_parser().parse_args()
    total, success_count, latencies, results = run_load_test(
        api_url=args.api_url,
        tps=args.tps,
        duration=args.duration,
        model=args.model,
        prompt=args.prompt,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        workers=args.workers,
    )

    print(f"api_url={args.api_url}")
    print(f"target_tps={args.tps}")
    print(f"duration_seconds={args.duration}")
    print(f"requests_sent={total}")
    print(f"requests_succeeded={success_count}")
    print(f"requests_failed={total - success_count}")
    print(f"p50_latency_ms={percentile(latencies, 0.50):.2f}")
    print(f"p95_latency_ms={percentile(latencies, 0.95):.2f}")
    print(f"max_latency_ms={max(latencies) if latencies else 0.0:.2f}")

    failed = [item for item in results if not item["ok"]]
    if failed:
        first_error = failed[0]
        print(f"first_error_status={first_error['status']}")
        print(f"first_error_body={first_error['body']}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
