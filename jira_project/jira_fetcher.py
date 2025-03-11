from atlassian import Jira
from loguru import logger
from pydantic import BaseModel
from typing import List, Optional
from jira_project.config import settings
from jira_project.data_quality import validate_issues, validate_worklogs

# Configure logger to write logs to a file with rotation and level settings
logger.add("jira_project/logs/jira_fetcher.log", rotation="1 MB", level="INFO")

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

class JiraClient:
    """Client to interact with Jira."""
    def __init__(self):
        """Initialize Jira client with settings from configuration."""
        self.jira = Jira(
            url=settings.jira_url,
            username=settings.jira_username,
            password=settings.jira_api_token.get_secret_value(),
        )

    def fetch_issues_with_worklogs(self) -> List[JiraIssue]:
        """
        Fetch issues from Jira along with their worklogs.

        Returns:
            List[JiraIssue]: List of Jira issues with worklogs.
        """
        logger.info("Fetching issues from Jira project: {}", settings.jira_project)
        start_at = 0
        all_issues = []

        # Loop to fetch issues in batches
        while True:
            issues = self._fetch_issues(start_at)
            if not issues:
                break

            # Process each issue and add to the list
            for issue in issues:
                try:
                    jira_issue = self._process_issue(issue)
                    all_issues.append(jira_issue)
                except Exception as e:
                    logger.error(f"Error processing issue {issue['key']}: {e}")

            # Increment the start index for the next batch
            start_at += settings.max_results

        # Validate the fetched issues and their worklogs
        validate_issues(all_issues)
        for issue in all_issues:
            validate_worklogs(issue.worklogs)

        logger.info(f"Total issues fetched: {len(all_issues)}")
        return all_issues

    def _fetch_issues(self, start_at: int) -> List[dict]:
        """
        Fetch a batch of issues from Jira.

        Args:
            start_at (int): The starting index for fetching issues.

        Returns:
            List[dict]: List of issues fetched from Jira.
        """
        try:
            jql_query = f'project="{settings.jira_project}" ORDER BY created DESC'
            issues_response = self.jira.jql(jql_query, start=start_at, limit=settings.max_results)
            return issues_response.get("issues", [])
        except Exception as e:
            logger.error(f"Error fetching issues: {e}")
            return []

    def _process_issue(self, issue: dict) -> JiraIssue:
        """
        Process a single issue to extract relevant information and worklogs.

        Args:
            issue (dict): The issue data from Jira.

        Returns:
            JiraIssue: The processed Jira issue.
        """
        issue_key = issue["key"]
        summary = issue["fields"]["summary"]

        logger.info(f"Fetching worklogs for issue: {issue_key}")
        worklogs = self._fetch_worklogs(issue_key)

        # Create worklog entries from the fetched worklogs
        worklog_entries = [
            WorklogEntry(
                author=w["author"]["displayName"],
                time_spent=w["timeSpent"],
                comment=w.get("comment"),
            )
            for w in worklogs.get("worklogs", [])
        ]

        return JiraIssue(key=issue_key, summary=summary, worklogs=worklog_entries)

    def _fetch_worklogs(self, issue_key: str) -> dict:
        """
        Fetch worklogs for a specific issue.

        Args:
            issue_key (str): The key of the issue.

        Returns:
            dict: The worklogs for the issue.
        """
        try:
            return self.jira.issue_get_worklog(issue_key)
        except Exception as e:
            logger.error(f"Error fetching worklogs for issue {issue_key}: {e}")
            return {}

if __name__ == "__main__":
    client = JiraClient()
    issues = client.fetch_issues_with_worklogs()
