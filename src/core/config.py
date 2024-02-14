import logging
import os
from logging import config as logging_config

from pydantic import SecretStr
from pydantic_settings import BaseSettings

from .logger import LOGGING

logging_config.dictConfig(LOGGING)
logger = logging.getLogger()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZIP = ['zip', '7z', 'tar']


class AppSettings(BaseSettings):
    app_title: str
    project_name: str
    project_host: str
    project_port: int

    bearer_secret: SecretStr
    manager_secret: SecretStr

    db_user: str
    db_password: SecretStr
    db_name: str
    db_host: str
    db_port: str

    db_user_test: str
    db_password_test: SecretStr
    db_name_test: str
    db_host_test: str
    db_port_test: str

    base_upload_dir: str
    temp_directory: str
    arch_directory: str

    @property
    def db_dsn(self):
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def db_dsn_test(self):
        return f'postgresql+asyncpg://{self.db_user_test}:{self.db_password_test.get_secret_value()}@' \
               f'{self.db_host_test}:{self.db_port_test}/{self.db_name_test}'
    
    @property
    def temp_dir(self):
        return os.path.join(self.base_upload_dir, self.temp_directory)

    @property
    def arch_dir(self):
        return os.path.join(self.base_upload_dir, self.arch_directory)

    class Config:
        env_file = '.env'


app_settings = AppSettings()
