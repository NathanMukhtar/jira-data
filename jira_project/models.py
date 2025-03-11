from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class WorklogEntry(BaseModel):
    """Model for worklog entries."""
    author: str = Field(description="Display name of the worklog author")
    time_spent: str = Field(description="Time spent in Jira format (e.g., '1h', '30m')")
    comment: Optional[str] = Field(default=None, description="Optional worklog comment")
    created: datetime = Field(description="Timestamp when worklog was created")

    @field_validator('time_spent')
    @classmethod
    def validate_time_spent_format(cls, v: str) -> str:
        """Validate time_spent follows Jira format."""
        if not any(unit in v.lower() for unit in ['w', 'd', 'h', 'm']):
            raise ValueError('time_spent must contain w(weeks), d(days), h(hours), or m(minutes)')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "author": "John Doe",
                    "time_spent": "2h",
                    "comment": "Initial implementation",
                    "created": "2025-03-11T10:00:00Z"
                }
            ]
        }
    }

class JiraIssue(BaseModel):
    """Model for Jira issues."""
    key: str = Field(
        pattern=r'^[A-Z]+-\d+$',
        description="Jira issue key (e.g., 'PROJECT-123')"
    )
    summary: str = Field(min_length=1, description="Issue summary")
    worklogs: List[WorklogEntry] = Field(default_factory=list, description="List of worklog entries")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "key": "TEST-123",
                    "summary": "Implement feature X",
                    "worklogs": [
                        {
                            "author": "John Doe",
                            "time_spent": "2h",
                            "comment": "Initial implementation",
                            "created": "2025-03-11T10:00:00Z"
                        }
                    ]
                }
            ]
        }
    }