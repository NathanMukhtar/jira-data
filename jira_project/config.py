import os
from pydantic_settings import BaseSettings  # ✅ Correct for Pydantic v2
from pydantic import SecretStr


class JiraSettings(BaseSettings):
    jira_url: str
    jira_username: str
    jira_api_token: SecretStr
    jira_project: str
    max_results: int = 50  

    class Config:
        env_file = ".env"

settings = JiraSettings()
