from pydantic import BaseModel
from typing import List, Optional

class WorklogEntry(BaseModel):
    """Model for worklog entries."""
    author: str
    time_spent: str
    comment: Optional[str]

class JiraIssue(BaseModel):
    """Model for Jira issues."""
    key: str
    summary: str
    worklogs: List[WorklogEntry] = []