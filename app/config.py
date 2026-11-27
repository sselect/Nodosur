"""Configuración central de NodoSur (12-factor: todo por variables de entorno)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULTS = {"", "admin", "changeme", "dev-secret-change-me", "dev-agent-token"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NodoSur"
    env: str = "dev"  # dev | test | prod
    public_base_url: str = "http://localhost:8000"

    database_url: str = "sqlite:///./nodosur.db"

    secret_key: str = "dev-secret-change-me"
    admin_email: str = "admin@nodosur.cl"
    admin_password: str = "admin"
    agent_token: str = "dev-agent-token"

    # Correo saliente (Gmail: smtp.gmail.com + contraseña de aplicación)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    notify_to: str = ""  # destino por defecto de alertas de empleo
    contact_to: str = ""  # destino de leads de la landing

    enable_scheduler: bool = False  # True solo si el servicio está siempre encendido
    http_timeout: float = 20.0

    # Asistente IA de la landing (si no hay API key, responde con el modo básico sin modelo)
    anthropic_api_key: str = ""
    assistant_model: str = "claude-haiku-5-5"
    assistant_max_tokens: int = 450

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    def validate_for_prod(self) -> None:
        """En producción no se permite arrancar con secretos por defecto."""
        if not self.is_prod:
            return
        weak = [
            name
            for name in ("secret_key", "admin_password", "agent_token")
            if getattr(self, name) in INSECURE_DEFAULTS or len(getattr(self, name)) < 12
        ]
        if weak:
            raise RuntimeError(f"Configuración insegura en prod: define {', '.join(weak).upper()} (mín. 12 caracteres)")


@lru_cache
def get_settings() -> Settings:
    return Settings()
