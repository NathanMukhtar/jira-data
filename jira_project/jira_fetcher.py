from atlassian import Jira
from loguru import logger
from pydantic import BaseModel
from typing import List
from jira_project.config import settings
from jira_project.data_quality import validate_issues, validate_worklogs

logger.add("jira_project\logs\jira_fetcher.log", rotation="1 MB", level="INFO")

class WorklogEntry(BaseModel):
    author: str
    time_spent: str
    comment: str | None

class JiraIssue(BaseModel):
    key: str
    summary: str
    worklogs: List[WorklogEntry] = []

class JiraClient:
    def __init__(self):
        self.jira = Jira(
            url=settings.jira_url,
            username=settings.jira_username,
            password=settings.jira_api_token.get_secret_value(),
        )

    def fetch_issues_with_worklogs(self):
        logger.info("Fetching issues from Jira project: {}", settings.jira_project)
        start_at = 0
        all_issues = []

        while True:
            jql_query = f'project="{settings.jira_project}" ORDER BY created DESC'
            issues_response = self.jira.jql(jql_query, start=start_at, limit=settings.max_results)
            issues = issues_response.get("issues", [])

            if not issues:
                break  

            for issue in issues:
                issue_key = issue["key"]
                summary = issue["fields"]["summary"]

                logger.info(f"Fetching worklogs for issue: {issue_key}")
                worklogs = self.jira.get_issue_worklogs(issue_key)

                worklog_entries = [
                    WorklogEntry(
                        author=w["author"]["displayName"],
                        time_spent=w["timeSpent"],
                        comment=w.get("comment"),
                    )
                    for w in worklogs.get("worklogs", [])
                ]

                validated_issue = JiraIssue(key=issue_key, summary=summary, worklogs=worklog_entries)
                all_issues.append(validated_issue)

            start_at += settings.max_results

        validate_issues(all_issues)
        for issue in all_issues:
            validate_worklogs(issue.worklogs)

        logger.info(f"Total issues fetched: {len(all_issues)}")
        return all_issues

if __name__ == "__main__":
    client = JiraClient()
    issues = client.fetch_issues_with_worklogs()
