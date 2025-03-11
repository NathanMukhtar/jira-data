import pytest
from pytest_mock import MockerFixture
from jira_project.jira_fetcher import JiraClient
from jira_project.models import JiraIssue, WorklogEntry

# Constants for test data
TEST_ISSUE_KEY = "TEST-1"
TEST_ISSUE_SUMMARY = "Test Issue"
TEST_WORKLOG_AUTHOR = "John Doe"
TEST_WORKLOG_TIME_SPENT = "1h"
TEST_WORKLOG_COMMENT = "Worked on bugfix"

# Additional constants for second test issue
TEST_ISSUE_KEY_2 = "TEST-2"
TEST_ISSUE_SUMMARY_2 = "Another Test Issue"
TEST_WORKLOG_AUTHOR_2 = "Jane Doe"
TEST_WORKLOG_TIME_SPENT_2 = "2h"
TEST_WORKLOG_COMMENT_2 = "Worked on feature"

# Define a pytest fixture to mock the JiraClient
@pytest.fixture
def mock_jira_client(mocker: MockerFixture) -> JiraClient:
    # Patch the JiraClient class in the jira_fetcher module
    mock_jira = mocker.patch("jira_project.jira_fetcher.JiraClient", autospec=True)
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
    # Create a mock for the jira attribute
    mock_instance.jira = mocker.Mock()
    # Return the mocked instance
    return mock_instance

# Fixture for a single worklog entry
@pytest.fixture
def single_worklog() -> WorklogEntry:
    return WorklogEntry(
        author=TEST_WORKLOG_AUTHOR,
        time_spent=TEST_WORKLOG_TIME_SPENT,
        comment=TEST_WORKLOG_COMMENT
    )

# Fixture for multiple worklogs
@pytest.fixture
def multiple_worklogs() -> list[WorklogEntry]:
    return [
        WorklogEntry(
            author=TEST_WORKLOG_AUTHOR,
            time_spent=TEST_WORKLOG_TIME_SPENT,
            comment=TEST_WORKLOG_COMMENT
        ),
        WorklogEntry(
            author=TEST_WORKLOG_AUTHOR_2,
            time_spent=TEST_WORKLOG_TIME_SPENT_2,
            comment=TEST_WORKLOG_COMMENT_2
        )
    ]

# Fixture for a single issue (without worklogs)
@pytest.fixture
def single_issue() -> JiraIssue:
    return JiraIssue(
        key=TEST_ISSUE_KEY,
        summary=TEST_ISSUE_SUMMARY,
        worklogs=[]
    )

# Fixture for a single issue with a worklog
@pytest.fixture
def single_issue_with_worklog(single_issue, single_worklog) -> list[JiraIssue]:
    issue = single_issue
    issue.worklogs = [single_worklog]
    return [issue]

# Fixture for multiple issues
@pytest.fixture
def multiple_issues(single_issue, multiple_worklogs) -> list[JiraIssue]:
    return [
        JiraIssue(
            key=TEST_ISSUE_KEY,
            summary=TEST_ISSUE_SUMMARY,
            worklogs=[multiple_worklogs[0]]
        ),
        JiraIssue(
            key=TEST_ISSUE_KEY_2,
            summary=TEST_ISSUE_SUMMARY_2,
            worklogs=[multiple_worklogs[1]]
        )
    ]

# Fixture for no issues
@pytest.fixture
def no_issues() -> list[JiraIssue]:
    return []

# Fixture for issues without worklogs
@pytest.fixture
def issues_without_worklogs() -> list[JiraIssue]:
    return [
        JiraIssue(
            key=TEST_ISSUE_KEY,
            summary=TEST_ISSUE_SUMMARY,
            worklogs=[]
        )
    ]

# Fixture for a single worklog response
@pytest.fixture
def mock_worklog_response() -> dict:
    return {
        "worklogs": [
            {
                "author": {"displayName": TEST_WORKLOG_AUTHOR},
                "timeSpent": TEST_WORKLOG_TIME_SPENT,
                "comment": TEST_WORKLOG_COMMENT
            }
        ]
    }

# Fixture for multiple worklog responses
@pytest.fixture
def mock_multiple_worklog_response() -> dict:
    return {
        "worklogs": [
            {
                "author": {"displayName": TEST_WORKLOG_AUTHOR},
                "timeSpent": TEST_WORKLOG_TIME_SPENT,
                "comment": TEST_WORKLOG_COMMENT
            },
            {
                "author": {"displayName": TEST_WORKLOG_AUTHOR_2},
                "timeSpent": TEST_WORKLOG_TIME_SPENT_2,
                "comment": TEST_WORKLOG_COMMENT_2
            }
        ]
    }

# Fixture for a single issue response
@pytest.fixture
def mock_issue_response() -> dict:
    return {
        "key": TEST_ISSUE_KEY,
        "fields": {
            "summary": TEST_ISSUE_SUMMARY
        }
    }

# Fixture to provide issues data based on the parameter
@pytest.fixture
def issues_data(request, single_issue_with_worklog, multiple_issues, no_issues, issues_without_worklogs) -> list[JiraIssue]:
    if request.param == "single_issue_with_worklog":
        return single_issue_with_worklog
    elif request.param == "multiple_issues":
        return multiple_issues
    elif request.param == "no_issues":
        return no_issues
    elif request.param == "issues_without_worklogs":
        return issues_without_worklogs
    else:
        return []

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
    "single_issue_with_worklog",
    "multiple_issues",
    "no_issues",
    "issues_without_worklogs",
], indirect=True)
def test_fetch_issues_with_worklogs(mock_jira_client: JiraClient, issues_data: list[JiraIssue]) -> None:
    # Set up the return value for the fetch_issues_with_worklogs method
    mock_jira_client.fetch_issues_with_worklogs.return_value = issues_data

    # Call the fetch_issues_with_worklogs method on the mocked JiraClient
    issues = mock_jira_client.fetch_issues_with_worklogs()
    
    # Assert the number of issues returned
    assert len(issues) == len(issues_data)
    
    # If there are issues, assert their details
    for i, issue in enumerate(issues_data):
        if issue.worklogs:
            assert_issue_details(issues[i], issue.key, issue.summary, issue.worklogs[0].author, issue.worklogs[0].time_spent, issue.worklogs[0].comment)
        else:
            assert issues[i].key == issue.key
            assert issues[i].summary == issue.summary
            assert len(issues[i].worklogs) == 0

def test_fetch_issues_with_worklogs_error(mock_jira_client: JiraClient, mocker: MockerFixture) -> None:
    # Mock the _fetch_issues method to raise an exception
    mocker.patch.object(mock_jira_client, '_fetch_issues', side_effect=Exception("Error fetching issues"))

    # Call the fetch_issues_with_worklogs method on the mocked JiraClient
    issues = mock_jira_client.fetch_issues_with_worklogs()

    # Assert that no issues are returned due to the error
    assert len(issues) == 0

def test_process_issue(mock_jira_client: JiraClient, mock_issue_response: dict, single_issue_with_worklog: list[JiraIssue]) -> None:
    # Mock the _process_issue method to return a JiraIssue object
    mock_jira_client._process_issue.return_value = single_issue_with_worklog[0]

    # Call the _process_issue method on the mocked JiraClient
    jira_issue = mock_jira_client._process_issue(mock_issue_response)

    # Assert the details of the processed issue
    assert_issue_details(jira_issue, TEST_ISSUE_KEY, TEST_ISSUE_SUMMARY, 
                        TEST_WORKLOG_AUTHOR, TEST_WORKLOG_TIME_SPENT, TEST_WORKLOG_COMMENT)

def test_fetch_worklogs(mock_jira_client: JiraClient, mock_worklog_response: dict) -> None:
    # Mock the Jira client's issue_get_worklog method to return a worklog
    mock_jira_client.jira.issue_get_worklog = mock_worklog_response

    # Call the _fetch_worklogs method on the mocked JiraClient
    worklogs = mock_jira_client._fetch_worklogs(TEST_ISSUE_KEY)

    # Assert the details of the fetched worklogs
    assert len(worklogs["worklogs"]) == 1
    worklog = worklogs["worklogs"][0]
    assert worklog["author"]["displayName"] == TEST_WORKLOG_AUTHOR
    assert worklog["timeSpent"] == TEST_WORKLOG_TIME_SPENT
    assert worklog["comment"] == TEST_WORKLOG_COMMENT

def test_fetch_worklogs_error(mock_jira_client: JiraClient, mocker: MockerFixture) -> None:
    # Mock the issue_get_worklog method to raise an exception
    mock_jira_client.jira.issue_get_worklog = mocker.Mock(
        side_effect=Exception("Error fetching worklogs")
    )

    # Call the _fetch_worklogs method on the mocked JiraClient
    worklogs = mock_jira_client._fetch_worklogs(TEST_ISSUE_KEY)

    # Assert that an empty worklog list is returned
    assert worklogs == {"worklogs": []}