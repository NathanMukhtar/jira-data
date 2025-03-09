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

# Test function to verify the fetch_issues_with_worklogs method
def test_fetch_issues_with_worklogs(mock_jira_client: JiraClient) -> None:
    # Call the fetch_issues_with_worklogs method on the mocked JiraClient
    issues = mock_jira_client.fetch_issues_with_worklogs()
    
    # Assert that one issue is returned
    assert len(issues) == 1
    # Assert that the key of the first issue is as expected
    assert issues[0].key == TEST_ISSUE_KEY
    # Assert that the summary of the first issue is as expected
    assert issues[0].summary == TEST_ISSUE_SUMMARY
    # Assert that one worklog entry is present in the first issue
    assert len(issues[0].worklogs) == 1
    # Assert that the author of the first worklog entry is as expected
    assert issues[0].worklogs[0].author == TEST_WORKLOG_AUTHOR
    # Assert that the time spent on the first worklog entry is as expected
    assert issues[0].worklogs[0].time_spent == TEST_WORKLOG_TIME_SPENT
    # Assert that the comment of the first worklog entry is as expected
    assert issues[0].worklogs[0].comment == TEST_WORKLOG_COMMENT

# Additional test cases can be added here to improve test coverage
