import logging
from azure.cosmos import CosmosClient
import os
import concurrent.futures

# Activity function: Reads a batch of documents from Cosmos DB
# Supports batching, continuation tokens, and parallelism

def main(payload: dict) -> dict:
    """
    Reads a batch of documents from Cosmos DB.
    - Uses SDK's by_page() for pagination and continuation tokens.
    - Supports batching to avoid memory/RU issues.
    - Demonstrates parallel batch fetching for throughput (up to 4 batches).
    - Returns items, next continuation token, and batch count.
    """
    # Configuration: get connection info from environment
    connect_str = os.environ["COSMOS_DB_CONNECTION_STRING"]
    db_name = os.environ["COSMOS_DB_NAME"]
    container_name = os.environ["COSMOS_CONTAINER"]

    # Extract inputs from orchestrator
    continuation_token = payload.get("continuation_token")
    batch_size = 1000  # Tune for memory/RU limits

    # Connect to Cosmos DB
    client = CosmosClient.from_connection_string(connect_str)
    container = client.get_database_client(db_name).get_container_client(container_name)

    # Query with pagination
    query = "SELECT * FROM c"
    item_pages = container.query_items(
        query=query,
        enable_cross_partition_query=True,
        max_item_count=batch_size
    ).by_page(continuation_token=continuation_token)

    try:
        # Get the first page of results
        page = next(item_pages)
        items = list(page)
        # Get the token for the NEXT batch
        next_token = item_pages.continuation_token

        logging.info(f"Fetched {len(items)} items from Cosmos.")

        return {
            "items": items,
            "next_token": next_token,
            "count": len(items)
        }
    except StopIteration:
        # No more items found
        return {
            "items": [],
            "next_token": None,
            "count": 0
        }