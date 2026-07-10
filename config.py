from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "itheima"
    DEEPSEEK_API_KEY: str = ""
    
    class Config:
        env_file = ".env"  # 自动去根目录加载 .env

settings = Settings()