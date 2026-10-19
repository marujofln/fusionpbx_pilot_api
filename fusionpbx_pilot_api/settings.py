from pydantic_settings import BaseSettings, SettingsConfigDict


class FusionPBXSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='fusionpbx_',
        extra='allow',
    )
    url: str
    user: str
    password: str
    wss_port: int = 7443
    udp_port: int = 5060
    tcp_port: int = 5060
    tls_port: int = 5061


class RestAPISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='restapi_',
        extra='allow',
    )
    host: str = '0.0.0.0'
    port: int = 8000
    origins: list[str] = [
        'http://localhost',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://127.0.0.1:8080',
        'http://localhost:8080',
    ]


class FiefSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='fief_',
        extra='allow',
    )

    base_url: str
    authorize_path: str = '/authorize'
    token_path: str = '/api/token'
    userinfo_path: str = '/api/userinfo'
    client_id: str
    client_secret: str


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='redis_',
        extra='allow',
    )

    host: str = 'redis'
    port: int = 6379
    db: int = 0
    password: str = ''
    username: str = ''


class SeniumSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='selenium_',
        extra='allow',
    )

    grid_url: str = 'http://selenium-hub:4444/wd/hub'
    headless: bool = True


class config:
    fusionpbx: FusionPBXSettings = FusionPBXSettings()
    restapi: RestAPISettings = RestAPISettings()
    fief: FiefSettings = FiefSettings()
    redis: RedisSettings = RedisSettings()
    selenium: SeniumSettings = SeniumSettings()

    @classmethod
    def reload(cls):
        cls.fusionpbx = FusionPBXSettings()
        cls.restapi = RestAPISettings()
        cls.fief = FiefSettings()
        cls.redis = RedisSettings()
        cls.selenium = SeniumSettings()
