import pytest
from jira_project.data_quality import validate_issues, validate_worklogs
from jira_project.models import JiraIssue, WorklogEntry

def test_validate_issues_pass():
    issues = [JiraIssue(key="TEST-1", summary="Valid Issue", worklogs=[])]
    validate_issues(issues)

def test_validate_issues_fail():
    issues = [JiraIssue(key="invalid_key", summary="Missing Project Key", worklogs=[])]
    with pytest.raises(ValueError):
        validate_issues(issues)

def test_validate_worklogs_pass():
    worklogs = [WorklogEntry(author="John Doe", time_spent="1h", comment="Worked on feature")]
    validate_worklogs(worklogs)
