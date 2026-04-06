import argparse

from .config import load_settings
from .downloader import ensure_model
from .server import build_server_command, run_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download a Gemma 4 GGUF from Hugging Face and serve it with llama.cpp."
    )
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="Only download or resume the model, without starting the API server.",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the final llama-server command before execution.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings()
    if args.print_command:
        print(" ".join(build_server_command(settings, settings.model_path)))
        if not args.download_only:
            return 0

    model_path = ensure_model(settings)
    if args.download_only:
        print(model_path)
        return 0

    return run_server(settings, model_path)


if __name__ == "__main__":
    raise SystemExit(main())
