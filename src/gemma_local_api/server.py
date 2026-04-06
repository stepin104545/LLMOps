import subprocess
from typing import List

from .config import Settings


def build_server_command(settings: Settings, model_path: str) -> List[str]:
    return [
        settings.llama_server_bin,
        "--host",
        settings.host,
        "--port",
        str(settings.port),
        "-m",
        model_path,
    ]


def run_server(settings: Settings, model_path: str) -> int:
    return subprocess.run(build_server_command(settings, model_path), check=True).returncode
