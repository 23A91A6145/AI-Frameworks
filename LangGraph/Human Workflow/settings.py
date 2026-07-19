from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    app_name: str = "Humaan Email Drafter"
    app_version: str = "1.0.0"

    provider: str = Field(default="ollama", description="LLM provider")
    model_name: str = Field(default="llama3.2:3b", description="Model name")
    api_key: str = Field(default="", description="Provider API key")
    api_base_url: str = Field(default="", description="Optional base URL override")

    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")

    max_revisions: int = Field(default=3, ge=1, le=10)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def outputs_dir(self) -> Path:
        return self.base_dir / "outputs"

    @property
    def drafts_dir(self) -> Path:
        return self.outputs_dir / "drafts"

    @property
    def approved_dir(self) -> Path:
        return self.outputs_dir / "approved"

    @property
    def checkpoints_dir(self) -> Path:
        return self.base_dir / "checkpoints"

    @property
    def prompts_dir(self) -> Path:
        return self.base_dir / "prompts"

    def ensure_dirs(self) -> None:
        for d in [self.outputs_dir, self.drafts_dir, self.approved_dir, self.checkpoints_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
