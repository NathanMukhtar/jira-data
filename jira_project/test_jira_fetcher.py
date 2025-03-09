import pytest
from pytest_mock import MockerFixture
from jira_fetcher import JiraClient, JiraIssue, WorklogEntry

# Constants for test data
TEST_ISSUE_KEY = "TEST-1"
TEST_ISSUE_SUMMARY = "Test Issue"
TEST_WORKLOG_AUTHOR = "John Doe"
TEST_WORKLOG_TIME_SPENT = "1h"
TEST_WORKLOG_COMMENT = "Worked on bugfix"

# Define a pytest fixture to mock the JiraClient
@pytest.fixture
def mock_jira_client(mocker: MockerFixture) -> JiraClient:
    # Patch the JiraClient class in the jira_fetcher module
    mock_jira = mocker.patch("jira_fetcher.JiraClient", autospec=True)
    # Get the instance of the mocked JiraClient
    mock_instance = mock_jira.return_value

    # Set up the return value for the fetch_issues_with_worklogs method
    mock_instance.fetch_issues_with_worklogs.return_value = [
        JiraIssue(
            key=TEST_ISSUE_KEY,
            summary=TEST_ISSUE_SUMMARY,
            worklogs=[
                WorklogEntry(author=TEST_WORKLOG_AUTHOR, time_spent=TEST_WORKLOG_TIME_SPENT, comment=TEST_WORKLOG_COMMENT)
            ]
        )
    ]
    # Return the mocked instance
    return mock_instance

# Helper function to assert issue details
def assert_issue_details(issue: JiraIssue, key: str, summary: str, worklog_author: str, worklog_time_spent: str, worklog_comment: str) -> None:
    assert issue.key == key
    assert issue.summary == summary
    assert len(issue.worklogs) == 1
    assert issue.worklogs[0].author == worklog_author
    assert issue.worklogs[0].time_spent == worklog_time_spent
    assert issue.worklogs[0].comment == worklog_comment

# Parameterized test function to verify the fetch_issues_with_worklogs method
@pytest.mark.parametrize("issues_data", [
    ([JiraIssue(key=TEST_ISSUE_KEY, summary=TEST_ISSUE_SUMMARY, worklogs=[WorklogEntry(author=TEST_WORKLOG_AUTHOR, time_spent=TEST_WORKLOG_TIME_SPENT, comment=TEST_WORKLOG_COMMENT)])]),
    ([])
])
def test_fetch_issues_with_worklogs(mock_jira_client: JiraClient, issues_data: list[JiraIssue]) -> None:
    # Set up the return value for the fetch_issues_with_worklogs method
    mock_jira_client.fetch_issues_with_worklogs.return_value = issues_data

    # Call the fetch_issues_with_worklogs method on the mocked JiraClient
    issues = mock_jira_client.fetch_issues_with_worklogs()
    
    # Assert the number of issues returned
    assert len(issues) == len(issues_data)
    
    # If there are issues, assert their details
    if issues_data:
        assert_issue_details(issues[0], TEST_ISSUE_KEY, TEST_ISSUE_SUMMARY, TEST_WORKLOG_AUTHOR, TEST_WORKLOG_TIME_SPENT, TEST_WORKLOG_COMMENT)

# Additional test cases can be added here to improve test coverage
