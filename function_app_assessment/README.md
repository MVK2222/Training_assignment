# Azure Functions Mini-Solutions Suite

This repository bundles five Azure Functions workloads that mirror common interview/assessment prompts: CRUD APIs backed by Cosmos DB, queue-driven image resizing, Event Grid indexing, timer-based SQL cleanup, and a Durable Functions data migration pipeline. Use this README as the single landing page to understand each scenario, prerequisites, and how to validate them locally or in Azure.

## Repository Map

| Folder | Scenario | Trigger(s) | Primary Services | Key Artifacts |
| --- | --- | --- | --- | --- |
| `1st_question_CRUD/` | Product CRUD API | HTTP | Azure Functions, Cosmos DB | `AddProduct`, `DelProduct`, `ListProducts`, `GetProduct`, `updateProduct`, `cosmos_client.py`, `terminal_output.png` |
| `2nd_question_resize_image/` | Upload → Queue → Resize | HTTP + Queue | Blob Storage, Queue Storage | `img_upload`, `auto_resize_image`, `postman_request.png`, `Screenshot 2025-11-27 123824.png`, `terminal_output.png` |
| `3rd_question_auto_index/` | Blob auto-indexing | Event Grid | Blob Storage, Cosmos DB | `function_app.py`, `README_EventGrid.md`, `terminal_output.png` |
| `6th_question_clean_up/` | SQL archival cleanup | Timer | SQL Database, Blob Storage | `time_cleanup`, `scripts/orders_table.sql`, `terminal_output.png` |
| `9th_question_data_migration/` | Cosmos → SQL migration | Durable orchestration | Cosmos DB, SQL Database | `Orchestrator`, `read_cosmos`, `write_to_sql`, `migration_report.png`, `sql_db.png`, `terminal_output.png` |

---

## Global Prerequisites
- Python 3.10 or 3.11 (match the Functions v4 runtime).
- Azure Functions Core Tools (`func`) for local runs and deployment.
- Azure CLI (optional) for provisioning but recommended.
- Storage Emulator / Azurite when running locally (`AzuriteConfig` folders provided in relevant solutions).
- Each sub-solution includes its own `requirements.txt`; install within a virtual environment to avoid conflicts.

> **Tip:** Many settings use `UseDevelopmentStorage=true` or sample connection strings. Replace them with secure secrets before deploying.

### Local Environment Bootstrapping
```powershell
cd function_app_assessment
python -m venv .venv
.\.venv\Scripts\activate
# Install dependencies per project
pip install -r 1st_question_CRUD/requirements.txt
pip install -r 2nd_question_resize_image/requirements.txt
# ...repeat per folder when working on it
```

---

## 1️⃣ Product CRUD API (`1st_question_CRUD/`)
- **Purpose:** REST-style endpoints (`/api/AddProduct`, `/api/ListProducts`, etc.) backed by Azure Cosmos DB.
- **Highlights:** Shared `cosmos_client.py`, partition key `/id`, screenshots in `terminal_output.png`.
- **Config:** `local.settings.json` requires `COSMOS_CONN_STRING`, `COSMOS_DB`, `COSMOS_CONTAINER`.
- **Test Flow:**
  1. `func start` from this folder.
  2. Use Postman/curl for POST/PUT/GET/DELETE calls (see README for examples).
  3. Inspect Cosmos container to confirm document changes.
- **Detailed guide:** [1st_question_CRUD/README.md](1st_question_CRUD/README.md)

---

## 2️⃣ Queue-Based Image Resizer (`2nd_question_resize_image/`)
- **Purpose:** `img_upload` HTTP trigger uploads to Blob Storage and enqueues resize jobs; `auto_resize_image` queue trigger produces thumbnails (default 320px & 1024px) in a separate container.
- **Config keys:** `BLOB_CONTAINER`, `RESIZED_CONTAINER`, `QUEUE_NAME`, and `AzureWebJobsStorage` connection string.
- **Validation:**
  1. Run `func start`.
  2. `POST` multipart image via Postman (screenshot in `postman_request.png`).
  3. Watch queue trigger logs (`terminal_output.png`, `Screenshot 2025-11-27 123824.png`).
  4. Verify both original and resized blobs exist in Storage Explorer.
- **Detailed guide:** [2nd_question_resize_image/README.md](2nd_question_resize_image/README.md)

---

## 3️⃣ Event Grid Auto Indexer (`3rd_question_auto_index/`)
- **Purpose:** Event Grid trigger listens for `BlobCreated` events in a `documents` container, enriches metadata (title, word count) and upserts into Cosmos DB.
- **Key file:** `function_app.py` encapsulates the handler plus storage/cosmos clients.
- **Setup:** Provide `BLOB_ACCOUNT_CONN_STR`, `COSMOS_DB_CONN_STR`, `COSMOS_DB`, and `COSMOS_CONTAINER` in `local.settings.json`.
- **Testing:**
  - Configure a local Event Grid simulator or deploy to Azure and connect Storage -> Event Grid -> Function.
  - Upload sample Markdown/HTML/TXT, confirm logs match `terminal_output.png` and Cosmos documents reflect derived metrics.
- **Detailed guide:** [3rd_question_auto_index/README_EventGrid.md](3rd_question_auto_index/README_EventGrid.md)

---

## 4️⃣ Timer-Based SQL Cleanup (`6th_question_clean_up/`)
- **Purpose:** Timer trigger archives old `Orders` rows to Blob (NDJSON) then purges them from SQL.
- **Settings:** `SQL_CONN_STR`, `ARCHIVE_CONTAINER`, `BATCH_SIZE`, `DAYS_OLD`, optional `DISABLE_SQL` flag for dry runs.
- **Artifacts:** SQL schema in `scripts/orders_table.sql`, runtime logs screenshot `terminal_output.png`.
- **Testing:**
  - Seed `Orders` table with aged data.
  - Start function host and wait for timer (or adjust CRON for quick test).
  - Validate blob output path `orders/<yyyy>/<mm>/<dd>/...` and reduced row count in SQL.
- **Detailed guide:** [6th_question_clean_up/README.md](6th_question_clean_up/README.md)

---

## 5️⃣ Durable Data Migration (`9th_question_data_migration/`)
- **Purpose:** Cosmos DB products → Azure SQL using Durable Functions orchestrator with batch paging, continuation tokens, and SQL bulk writes.
- **Function trio:**
  - `Orchestrator` coordinates batches & reporting.
  - `read_cosmos` fetches items per page.
  - `write_to_sql` flattens data and upserts into `Products`/`ProductTags` tables.
- **Assets:** `migration_report.png`, `sql_db.png`, `sample_product_data.json` for seeding.
- **Runbook:**
  1. Ensure Durable Functions extension installed (refer to `requirements.txt`).
  2. Start Azurite + local SQL (or remote resources).
  3. `func start` and trigger the orchestrator via HTTP or CLI.
  4. Review returned migration report plus screenshots for baseline expectations.
- **Detailed guide:** [9th_question_data_migration/README.md](9th_question_data_migration/README.md)

---

