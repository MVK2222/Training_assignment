# Cosmos DB to Azure SQL Data Migration (Durable Function)

## Overview
This project provides an Azure Durable Function solution for migrating product data from a Cosmos DB container to an Azure SQL database. It supports large-scale migrations with batching, continuation token handling, and parallelism, and produces a detailed migration report.

---

## Features
- **Batch Reading:** Reads documents from Cosmos DB in batches to avoid memory issues and respect RU limits.
- **Continuation Token:** Uses Cosmos DB continuation tokens for reliable pagination.
- **Parallelism:** Demonstrates parallel batch fetching for improved throughput.
- **Bulk SQL Insert:** Inserts/updates products and tags in bulk using SQL MERGE and fast_executemany.
- **Tag Flattening:** Handles nested `tags` arrays by flattening them into a child table (`ProductTags`).
- **Migration Report:** Tracks total migrated, failures, time taken, and per-batch results.
- **Error Handling:** Reports and logs failures per batch.

---

## Folder Structure
```
9th_question/
├── Orchestrator/         # Durable orchestrator function
│   ├── __init__.py
│   └── function.json
├── read_cosmos/          # Reads batches from Cosmos DB
│   ├── __init__.py
│   └── function.json
├── write_to_sql/         # Writes batches to Azure SQL
│   ├── __init__.py
│   └── function.json
├── sample_product_data.json
├── migration_report.png  # Example migration report output
├── sql_db.png            # Example SQL table screenshot
├── requirements.txt      # Python dependencies
├── local.settings.json   # Local configuration
└── ...
```

---

## Images
### Migration Report Example
![Migration Report](migration_report.png)

### SQL Table Example
![SQL Table](sql_db.png)

---

## How It Works
1. **Orchestrator** starts the migration, tracks progress, and loops through batches using continuation tokens.
2. **read_cosmos** reads a batch of documents from Cosmos DB, returning items and the next continuation token.
3. **write_to_sql** flattens product and tag data, then bulk upserts into SQL tables.
4. The orchestrator repeats until all documents are migrated, then returns a detailed migration report.

---

## Setup Instructions
### Prerequisites
- Python 3.8+
- Azure Functions Core Tools
- Azure Cosmos DB account (or Emulator)
- Azure SQL Database
- Azurite (for local Cosmos DB/Storage emulation)
- Required Python packages (see `requirements.txt`)

### Azurite Setup (Local Emulator)
Azurite is a local emulator for Azure Storage. To install and run Azurite:
```powershell
npm install -g azurite
azurite --location ./AzuriteConfig --debug ./AzuriteConfig/debug.log
```
- Update `local.settings.json` to use `UseDevelopmentStorage=true` for local development.

### Configuration
Edit `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_DB_CONNECTION_STRING": "<your-cosmos-connection-string>",
    "COSMOS_DB_NAME": "<your-db-name>",
    "COSMOS_CONTAINER": "<your-container-name>",
    "SQL_CONN_STR": "<your-sql-connection-string>"
  }
}
```

### SQL Table Schema
Create these tables in your Azure SQL database:
```sql
CREATE TABLE Products (
    ProductId NVARCHAR(100) PRIMARY KEY,
    Name NVARCHAR(255),
    Price FLOAT,
    Category NVARCHAR(100)
);

CREATE TABLE ProductTags (
    ProductId NVARCHAR(100),
    Tag NVARCHAR(100),
    FOREIGN KEY (ProductId) REFERENCES Products(ProductId)
);
```

### Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Example requirements.txt
```
azure-functions
azure-cosmos
pyodbc
```

---

## Run Locally
```powershell
func start
```

---

## Usage
- The migration is triggered by starting the orchestrator function.
- Progress and results are logged and returned as a migration report.
- See `migration_report.png` for a sample output.

---

## Migration Report
The report includes:
- Total records migrated
- Number of failures
- Time taken (seconds)
- Per-batch results (success/failure, counts, errors)

---

## Error Handling
- All exceptions are logged.
- Failed batches are reported in the migration report.

---

## Advanced Details
### Batching and Parallelism
- Batches are read from Cosmos DB using the SDK's `by_page()` iterator.
- Parallelism is demonstrated using Python's `ThreadPoolExecutor` (see `read_cosmos/__init__.py`).
- Continuation tokens ensure reliable pagination and memory safety.

### Bulk SQL Insert
- Products and tags are upserted in bulk using SQL MERGE and `fast_executemany` for performance.
- Tags are flattened and inserted into the `ProductTags` table.

### Durable Function Orchestration
- The orchestrator coordinates reading, writing, and reporting.
- Migration can be resumed if interrupted (using continuation tokens).

### Customization
- Adjust batch size in `read_cosmos/__init__.py` for performance tuning.
- Enhance error handling or add retry logic as needed.
- Modify SQL schema or mapping logic for additional fields.

---

## License
MIT
