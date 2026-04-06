from dataclasses import dataclass
import os


DEFAULT_MODEL_ID = "bartowski/google_gemma-4-E4B-it-GGUF"
DEFAULT_MODEL_FILE = "google_gemma-4-E4B-it-Q2_K_L.gguf"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    model_id: str
    model_file: str
    model_cache_dir: str
    llama_server_bin: str
    hf_token: str

    @property
    def model_url(self) -> str:
        return (
            "https://huggingface.co/"
            f"{self.model_id}/resolve/main/{self.model_file}?download=true"
        )

    @property
    def model_path(self) -> str:
        return os.path.join(self.model_cache_dir, self.model_file)


def load_settings() -> Settings:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return Settings(
        host=os.getenv("HOST", DEFAULT_HOST),
        port=int(os.getenv("PORT", str(DEFAULT_PORT))),
        model_id=os.getenv("MODEL_ID", DEFAULT_MODEL_ID),
        model_file=os.getenv("MODEL_FILE", DEFAULT_MODEL_FILE),
        model_cache_dir=os.getenv("MODEL_CACHE_DIR", os.path.join(root_dir, "models")),
        llama_server_bin=os.getenv("LLAMA_SERVER_BIN", "llama-server"),
        hf_token=os.getenv("HF_TOKEN", ""),
    )
