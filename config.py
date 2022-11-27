from pydantic import BaseSettings

class Settings(BaseSettings):
    santa_file: str = "santa.yaml"
    log_level: str = "INFO"
    email_server: str
    email_server_port: int
    email_account: str
    email_user: str
    email_password: str

settings = Settings()