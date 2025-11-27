# Azure Functions Assessment – LMS Submission Guide

This guide packages all five scenarios required for the LMS submission. It summarizes objectives, architecture, configuration, validation steps, and screenshot references so evaluators can verify each workload quickly.

## Table of Contents
1. [Submission Overview](#submission-overview)
2. [Environment Checklist](#environment-checklist)
3. [Scenario 1 – Product CRUD API](#scenario-1--product-crud-api)
4. [Scenario 2 – Queue-Based Image Resizer](#scenario-2--queue-based-image-resizer)
5. [Scenario 3 – Event Grid Auto Indexer](#scenario-3--event-grid-auto-indexer)
6. [Scenario 4 – Timer-Based SQL Cleanup](#scenario-4--timer-based-sql-cleanup)
7. [Scenario 5 – Durable Data Migration](#scenario-5--durable-data-migration)
8. [Validation Matrix](#validation-matrix)
9. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Submission Overview
- **Repo root:** `function_app_assessment/`
- **Solutions included:** CRUD API, Image Resizer, Auto Indexer, Cleanup Timer, Durable Migration.
- **Evidence assets:** `terminal_output.png`, `postman_request.png`, `Screenshot 2025-11-27 123824.png`, `migration_report.png`, `sql_db.png` stored in the respective scenario folders.
- **Deliverables:**
  - `README.md` (repository-level overview)
  - `Docs/LMS_Guide.md` (this file) for LMS upload.

---

## Environment Checklist
| Item | Notes |
| --- | --- |
| Python runtime | 3.10/3.11 (Functions v4) |
| Azure Functions Core Tools | v4 `func` CLI |
| Azurite emulator | Used by solutions needing Storage locally |
| Azure CLI (optional) | For provisioning + deployment |
| Virtual environment | Recommended per scenario to isolate dependencies |

Global command template:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r <solution>/requirements.txt
func start
```

---

## Scenario 1 – Product CRUD API
- **Folder:** `1st_question_CRUD/`
- **Objective:** Implement HTTP functions for creating, reading, updating, deleting products stored in Cosmos DB.
- **Key Functions:** `AddProduct`, `GetProduct`, `ListProducts`, `DelProduct`, `updateProduct`.
- **Configuration:**
  - `COSMOS_CONN_STRING`, `COSMOS_DB`, `COSMOS_CONTAINER` in `local.settings.json`.
- **Validation Steps:**
  1. Run `func start` inside the folder.
  2. Execute POST/GET/PUT/DELETE requests (samples in scenario README).
  3. Confirm data in Cosmos DB via Data Explorer.
  4. Capture outputs similar to `terminal_output.png`.
- **Screenshot Reference:** `1st_question_CRUD/terminal_output.png`.

---

## Scenario 2 – Queue-Based Image Resizer
- **Folder:** `2nd_question_resize_image/`
- **Objective:** HTTP upload → Blob Storage → Queue message → Queue-triggered resizing into another container.
- **Functions:** `img_upload` (HTTP trigger), `auto_resize_image` (queue trigger).
- **Configuration:** `AzureWebJobsStorage`, `BLOB_CONTAINER`, `RESIZED_CONTAINER`, `QUEUE_NAME`.
- **Validation Steps:**
  1. Start the Functions host.
  2. POST multipart image (see `postman_request.png`).
  3. Confirm queue trigger logs (`terminal_output.png`, `Screenshot 2025-11-27 123824.png`).
  4. Verify resized blobs at `resized/<size>/<filename>`.
- **Screenshot References:** `postman_request.png`, `Screenshot 2025-11-27 123824.png`, `terminal_output.png`.

---

## Scenario 3 – Event Grid Auto Indexer
- **Folder:** `3rd_question_auto_index/`
- **Objective:** Automatically index blobs dropped into the `documents` container by writing metadata to Cosmos DB.
- **Implementation:** `function_app.py` uses Event Grid trigger to read blob, extract title/word count, upsert into Cosmos.
- **Configuration:** `BLOB_ACCOUNT_CONN_STR`, `COSMOS_DB_CONN_STR`, `COSMOS_DB`, `COSMOS_CONTAINER`.
- **Validation Steps:**
  1. Ensure Event Grid subscription is wired to the Function endpoint.
  2. Upload sample text/markdown to the `documents` container.
  3. Inspect log output (see `terminal_output.png`).
  4. Verify Cosmos DB entries contain derived metadata.
- **Screenshot Reference:** `3rd_question_auto_index/terminal_output.png`.

---

## Scenario 4 – Timer-Based SQL Cleanup
- **Folder:** `6th_question_clean_up/`
- **Objective:** Archive old SQL `Orders` rows to Blob storage (NDJSON) and delete them from SQL on a schedule.
- **Function:** `time_cleanup` (timer trigger defined in `function.json`).
- **Configuration:** `SQL_CONN_STR`, `ARCHIVE_CONTAINER`, `BATCH_SIZE`, `DAYS_OLD`, optional `DISABLE_SQL`.
- **Validation Steps:**
  1. Create table via `scripts/orders_table.sql` and seed aged rows.
  2. Run `func start` and wait for trigger (or adjust CRON).
  3. Verify blob output path `orders/<yyyy>/<mm>/<dd>/orders-*.ndjson`.
  4. Ensure SQL row count decreases accordingly.
- **Screenshot Reference:** `6th_question_clean_up/terminal_output.png`.

---

## Scenario 5 – Durable Data Migration
- **Folder:** `9th_question_data_migration/`
- **Objective:** Durable Functions orchestration moves product data from Cosmos DB to Azure SQL using batched processing.
- **Components:** `Orchestrator`, `read_cosmos`, `write_to_sql`.
- **Configuration:** `COSMOS_DB_CONNECTION_STRING`, `COSMOS_DB_NAME`, `COSMOS_CONTAINER`, `SQL_CONN_STR`.
- **Validation Steps:**
  1. Start Azurite and ensure Cosmos/SQL are reachable.
  2. Run `func start`.
  3. Trigger the orchestrator (HTTP start endpoint) and monitor progress.
  4. Inspect `migration_report.png` and `sql_db.png` representations for expected results.
- **Screenshot References:** `migration_report.png`, `sql_db.png`, `terminal_output.png`.

---

## Validation Matrix
| Scenario | Local Run | Cloud Deploy | Screenshot | Data Proof |
| --- | --- | --- | --- | --- |
| CRUD API | `func start` + REST calls | `func azure functionapp publish` | `terminal_output.png` | Cosmos DB Data Explorer |
| Image Resizer | HTTP upload test | Function App w/ Storage | `postman_request.png`, `Screenshot 2025-11-27 123824.png` | Blob containers show resized assets |
| Auto Indexer | Event Grid simulation/deploy | Event Grid → Function wiring | `terminal_output.png` | Cosmos entries include title + wordCount |
| SQL Cleanup | Timer trigger run | Azure Function App w/ SQL | `terminal_output.png` | Blob NDJSON + reduced SQL rows |
| Data Migration | Durable orchestration run | Durable Functions in Azure | `migration_report.png`, `sql_db.png` | SQL tables populated + migration summary |

---

## FAQ & Troubleshooting
- **How to force timer execution locally?** Run `func host start --verbose` and wait, or temporarily change CRON to `*/1 * * * * *`.
- **Queue function not firing?** Ensure `QUEUE_NAME` matches both `function.json` and configuration; check Storage queue content via Azurite/Explorer.
- **Cosmos throttling (429s)?** Lower batch sizes or increase RU/s; add retry/backoff logic if needed.
- **Durable instance stuck?** Clear storage tables under `AzureWebJobsStorage` (`DurableFunctionsHub*`) or start with a new instance ID.
- **ODBC errors in cleanup function?** Install Microsoft ODBC Driver 18 for SQL Server and verify `Encrypt`/`TrustServerCertificate` parameters.

---

**Submission Tip:** Zip the entire `function_app_assessment` folder including this `Docs/LMS_Guide.md`, the root `README.md`, and all screenshot assets before uploading to the LMS. Provide a short note pointing reviewers to the guide for scenario-by-scenario validation.

