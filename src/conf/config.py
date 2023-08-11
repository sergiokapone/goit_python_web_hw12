import pathlib
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


file_env = pathlib.Path(__file__).parent.parent.parent.joinpath(".env")


class Settings(BaseSettings):
    """
    Settings for the project.
    """

    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    
    model_config = ConfigDict(env_file = file_env, env_file_encoding = "utf-8")

    # class Config:
    #     """
    #     Configuration for the settings.
    #     """
    #     env_file = file_env
    #     env_file_encoding = "utf-8"


settings = Settings()
