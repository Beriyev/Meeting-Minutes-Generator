from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    temp_dir: Path = base_dir / "temp"
    uploads_dir: Path = temp_dir / "uploads"
    audio_dir: Path = temp_dir / "audio"
    output_dir: Path = temp_dir / "output"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "float16"
    whisper_model: str = "large" 

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:9b"

    max_upload_size_mb: int = 500
    allowed_video_extensions: set[str] = {".mp4", ".mov", ".mkv", ".avi"}
    allowed_audio_extensions: set[str] = {".mp3", ".wav", ".m4a"}


settings = Settings()

for d in (settings.uploads_dir, settings.audio_dir, settings.output_dir):
    d.mkdir(parents=True, exist_ok=True)