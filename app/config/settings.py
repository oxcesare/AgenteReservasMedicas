"""Application Settings"""
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Carga las variables definidas en .env al entorno del proceso.
# pydantic-settings también lee .env directamente (ver model_config),
# pero se deja explícito con python-dotenv para mayor claridad y
# para que otras partes del código puedan usar os.getenv si lo requieren.
load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings"""

    # API Configuration
    API_TITLE: str = "Medical Appointments API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para crear, reservar, cambiar y consultar citas médicas"
    DEBUG: bool = True

    # Database Configuration
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "reserva_citas_db"
    DB_USER: str = "root"
    DB_PASS: str = ""
    DATABASE_URL: str | None = None

    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def database_url(self) -> str:
        """Return full database URL from DATABASE_URL or DB_* variables."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
