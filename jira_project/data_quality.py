import pandas as pd
import great_expectations as gx
from loguru import logger

def validate_issues(issues):
    """
    Validates Jira issue data using Great Expectations.
    """
    logger.info("Validating Jira issues and worklogs data...")

    # Convert issues to a Pandas DataFrame
    df = pd.DataFrame({
        "key": [issue.key for issue in issues],
        "summary": [issue.summary for issue in issues],
        "worklog_count": [len(issue.worklogs) for issue in issues],
    })

    # Retrieve your Data Context
    context = gx.get_context()

    # Define the Data Source name and add it to the Data Context
    data_source_name = "issues_data_source"
    data_source = context.data_sources.add_pandas(name=data_source_name)

    # Define the Data Asset name and add it to the Data Source
    data_asset_name = "issues_dataframe_data_asset"
    data_asset = data_source.add_dataframe_asset(name=data_asset_name)

    # Define the Batch Definition name and add it to the Data Asset
    batch_definition_name = "issues_batch_definition"
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

    # Define expectations
    expectations = [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="key"),
        gx.expectations.ExpectColumnValuesToMatchRegex(column="key", regex=r"^[A-Z]+-\d+$"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="summary"),
        gx.expectations.ExpectColumnValuesToBeBetween(column="worklog_count", min_value=0)
    ]

    # Get the dataframe as a Batch
    batch = batch_definition.get_batch(batch_parameters=batch_parameters)

    # Validate data
    results = [batch.validate(expectation) for expectation in expectations]
    success = all(result["success"] for result in results)

    if success:
        logger.info("✅ Jira issues data validation passed.")
    else:
        logger.error("❌ Jira issues data validation failed. Details: {}", results)
        raise ValueError("Jira issues data validation failed.")

def validate_worklogs(worklogs):
    """
    Validates Jira worklog data using Great Expectations.
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

    # Retrieve your Data Context
    context = gx.get_context()

    # Define the Data Source name and add it to the Data Context
    data_source_name = "worklogs_data_source"
    data_source = context.data_sources.add_pandas(name=data_source_name)

    # Define the Data Asset name and add it to the Data Source
    data_asset_name = "worklogs_dataframe_data_asset"
    data_asset = data_source.add_dataframe_asset(name=data_asset_name)

    # Define the Batch Definition name and add it to the Data Asset
    batch_definition_name = "worklogs_batch_definition"
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

    # Define expectations
    expectations = [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="author"),
        gx.expectations.ExpectColumnValuesToBeOfType(column="author", type_="str"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="time_spent"),
        gx.expectations.ExpectColumnValuesToBeOfType(column="time_spent", type_="str")
    ]

    # Get the dataframe as a Batch
    batch = batch_definition.get_batch(batch_parameters=batch_parameters)

    # Validate data
    results = [batch.validate(expectation) for expectation in expectations]
    success = all(result["success"] for result in results)

    if success:
        logger.info("✅ Jira worklogs data validation passed.")
    else:
        logger.error("❌ Jira worklogs data validation failed. Details: {}", results)
        raise ValueError("Jira worklogs data validation failed.")