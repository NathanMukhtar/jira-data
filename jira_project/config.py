from pydantic import BaseModel, Field, SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings

class JiraSettings(BaseSettings):
    jira_url: AnyHttpUrl = Field(
        description="Full URL of your Jira instance"
    )
    jira_username: str = Field(
        description="Jira username (usually email)"
    )
    jira_api_token: SecretStr = Field(
        description="Jira API token for authentication"
    )
    jira_project: str = Field(
        pattern=r'^[A-Z]+$',
        description="Jira project key"
    )
    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of results per page"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = JiraSettings()
