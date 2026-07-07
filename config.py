from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_URL = f'sqlite+aiosqlite:///{BASE_DIR}/vuzoparser.db'
UNIVERSITIES = ["НГУ", "НГТУ НЭТИ", "ТГУ"]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR/'.env')
    USER_AGENT : str
    BOT_TOKEN: str
    PROXY_TG: str
    DB_URL: str = DB_URL
    NOTIFICATION_TIME: int = 10
    
settings = Settings()