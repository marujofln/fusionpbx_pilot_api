from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )
    # TODO add a validator to url.
    fusionpbx_url: str

    fusionpbx_user: str
    fusionpbx_password: str
    restapi_host: str = '0.0.0.0'
    restapi_port: int = 8000
    fief_base_url: str = 'https://auth.example.com'
    fief_authorize_path: str = '/authorize'
    fief_token_path: str = '/api/token'
    fief_client_id: str
    fief_client_secret: str
    redis_host: str = 'redis'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ''
    redis_username: str = ''
    selenium_grid_url: str = 'http://selenium-hub:4444/wd/hub'

config = Settings()
