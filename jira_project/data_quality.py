import pandas as pd
import great_expectations as gx
from loguru import logger
from typing import List
from jira_project.jira_fetcher import JiraIssue, WorklogEntry

def validate_issues(issues: List[JiraIssue]) -> None:
    """
    Validates Jira issue data using Great Expectations.

    Args:
        issues (List[JiraIssue]): List of Jira issues to validate.
    """
    logger.info("Validating Jira issues and worklogs data...")

    # Convert issues to a Pandas DataFrame
    df = pd.DataFrame({
        "key": [issue.key for issue in issues],
        "summary": [issue.summary for issue in issues],
        "worklog_count": [len(issue.worklogs) for issue in issues],
    })

    # Validate the DataFrame
    validate_dataframe(df, "issues_data_source", "issues_dataframe_data_asset", "issues_batch_definition", [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="key"),
        gx.expectations.ExpectColumnValuesToMatchRegex(column="key", regex=r"^[A-Z]+-\d+$"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="summary"),
        gx.expectations.ExpectColumnValuesToBeBetween(column="worklog_count", min_value=0)
    ])

def validate_worklogs(worklogs: List[WorklogEntry]) -> None:
    """
    Validates Jira worklog data using Great Expectations.

    Args:
        worklogs (List[WorklogEntry]): List of Jira worklogs to validate.
    """
    if not worklogs:
        logger.warning("No worklogs found, skipping validation.")
        return

    # Convert worklogs to a Pandas DataFrame
    df = pd.DataFrame({
        "author": [worklog.author for worklog in worklogs],
        "time_spent": [worklog.time_spent for worklog in worklogs],
        "comment": [worklog.comment if worklog.comment else "" for worklog in worklogs],
    })

    # Validate the DataFrame
    validate_dataframe(df, "worklogs_data_source", "worklogs_dataframe_data_asset", "worklogs_batch_definition", [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="author"),
        gx.expectations.ExpectColumnValuesToBeOfType(column="author", type_="str"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="time_spent"),
        gx.expectations.ExpectColumnValuesToBeOfType(column="time_spent", type_="str")
    ])

def validate_dataframe(df: pd.DataFrame, data_source_name: str, data_asset_name: str, batch_definition_name: str, expectations: List[gx.expectations.Expectation]) -> None:
    """
    Validates a Pandas DataFrame using Great Expectations.

    Args:
        df (pd.DataFrame): The DataFrame to validate.
        data_source_name (str): The name of the data source.
        data_asset_name (str): The name of the data asset.
        batch_definition_name (str): The name of the batch definition.
        expectations (List[gx.expectations.Expectation]): List of expectations to validate.
    """
    try:
        # Retrieve your Data Context
        context = gx.get_context()

        # Define the Data Source name and add it to the Data Context
        data_source = context.data_sources.add_pandas(name=data_source_name)

        # Define the Data Asset name and add it to the Data Source
        data_asset = data_source.add_dataframe_asset(name=data_asset_name)

        # Define the Batch Definition name and add it to the Data Asset
        batch_definition = data_asset.add_batch_definition_whole_dataframe(batch_definition_name)

        # Create a batch parameter dictionary
        batch_parameters = {"dataframe": df}

        # Retrieve the Batch Definition
        batch_definition = (
            context.data_sources
            .get(data_source_name)
            .get_asset(data_asset_name)
            .get_batch_definition(batch_definition_name)
        )

        # Get the dataframe as a Batch
        batch = batch_definition.get_batch(batch_parameters=batch_parameters)

        # Validate data
        results = [batch.validate(expectation) for expectation in expectations]
        success = all(result["success"] for result in results)

        if success:
            logger.info("✅ Data validation passed.")
        else:
            logger.error("❌ Data validation failed. Details: {}", results)
            raise ValueError("Data validation failed.")
    except Exception as e:
        logger.error(f"Error during data validation: {e}")
        raise