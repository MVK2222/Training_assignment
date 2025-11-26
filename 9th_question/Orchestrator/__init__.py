import logging
import azure.durable_functions as df
import time

# Durable Function Orchestrator for Cosmos → SQL migration
# Coordinates batch reading, writing, and migration reporting

def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrates the migration of product data from Cosmos DB to Azure SQL.
    - Reads batches from Cosmos DB using continuation tokens.
    - Writes each batch to SQL, flattening tags and upserting products.
    - Tracks migration progress, failures, and timing.
    - Produces a detailed migration report at completion.
    - Handles errors and can resume migration if interrupted.
    """
    # Get current state or initialize defaults
    input_data = context.get_input() or {}

    current_token = input_data.get("continuation_token", None)  # Cosmos continuation token
    total_migrated = input_data.get("total_migrated", 0)        # Total migrated so far
    start_time = input_data.get("start_time", None)              # Migration start time
    if not start_time:
        start_time = time.time()
    failures = input_data.get("failures", 0)                    # Total failures
    batch_reports = input_data.get("batch_reports", [])          # Per-batch report list

    # Read a batch from Cosmos DB
    read_result = yield context.call_activity("read_cosmos", {
        "continuation_token": current_token
    })
    items = read_result["items"]
    next_token = read_result["next_token"]
    batch_count = read_result["count"]

    # Write batch to SQL and collect report
    batch_report = None
    if batch_count > 0:
        try:
            batch_report = yield context.call_activity("write_to_sql", items)
            total_migrated += batch_count
        except Exception as e:
            # Log and count failures
            failures += batch_count
            batch_report = {"status": "Failed", "error": str(e), "batch_count": batch_count}
    batch_reports.append(batch_report)

    # If more data, continue with next token; else, finish and report
    if next_token:
        logging.info(f"Batch done. Migrated: {total_migrated}. Continuing...")
        context.continue_as_new({
            "continuation_token": next_token,
            "total_migrated": total_migrated,
            "start_time": start_time,
            "failures": failures,
            "batch_reports": batch_reports
        })
    else:
        # Migration complete: calculate duration and return report
        end_time = time.time()
        duration = end_time - start_time
        return {
            "status": "Completed",
            "total_records": total_migrated,
            "failures": failures,
            "duration_seconds": duration,
            "batch_reports": batch_reports
        }

# Register orchestrator
main = df.Orchestrator.create(orchestrator_function)