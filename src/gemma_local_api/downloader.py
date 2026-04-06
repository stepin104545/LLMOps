import os
import subprocess
from typing import List

from .config import Settings


def _build_download_command(settings: Settings) -> List[str]:
    command = [
        "curl",
        "--fail",
        "--location",
        "--continue-at",
        "-",
        "--output",
        settings.model_path,
    ]
    if settings.hf_token:
        command.extend(["--header", f"Authorization: Bearer {settings.hf_token}"])
    command.append(settings.model_url)
    return command


def ensure_model(settings: Settings) -> str:
    os.makedirs(settings.model_cache_dir, exist_ok=True)
    subprocess.run(_build_download_command(settings), check=True)
    if not os.path.isfile(settings.model_path):
        raise FileNotFoundError(
            "Model file was not downloaded successfully: "
            f"{settings.model_path}"
        )
    return settings.model_path
