from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "sqlite:///./sungai.db"
    jwt_secret: str = "development-secret-change-me"
    jwt_expire_minutes: int = 720
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    seed_admin_username: str = "admin"
    seed_admin_password: str = "Admin123!Change"
    seed_petugas_username: str = "petugas"
    seed_petugas_password: str = "Petugas123!Change"
    node_api_key: str = "demo-node-key-change-me"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
