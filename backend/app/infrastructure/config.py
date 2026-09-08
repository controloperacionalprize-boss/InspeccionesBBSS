from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Rechaza el placeholder de .env.example; el secreto real solo vive en el entorno.
_JWT_SECRET_PLACEHOLDER = "cambiar-esta-clave-en-produccion"


class Settings(BaseSettings):
    """Configuración cargada desde el entorno. Sin secretos embebidos."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def _validar_jwt_secret(cls, valor: str) -> str:
        if valor == _JWT_SECRET_PLACEHOLDER:
            raise ValueError(
                "JWT_SECRET_KEY no puede ser el valor de ejemplo de .env.example. "
                "Genera uno propio, por ejemplo con: python -c \"import secrets; "
                "print(secrets.token_hex(32))\""
            )
        if len(valor) < 32:
            raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
        return valor

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def es_produccion(self) -> bool:
        return self.APP_ENV.lower() == "production"


settings = Settings()
