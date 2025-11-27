# Event Grid → Azure Function → Cosmos DB Pipeline

This guide explains how to index every new blob that lands in the `documents` container by wiring Azure Event Grid to an Azure Function that enriches and stores metadata in Cosmos DB.

## Solution Overview
1. Storage emits `BlobCreated` events for items dropped into the `documents` container.
2. Event Grid subscription forwards those events to the `DocumentIndexer` Azure Function (Event Grid trigger binding).
3. The Function retrieves blob properties plus content, derives title and word count when the file is textual, and prepares the Cosmos document payload.
4. Cosmos DB stores the enriched record, enabling downstream search or analytics without repeatedly scanning blobs.
5. Logs and Application Insights capture the ingestion trail; Cosmos queries surface the largest documents for quick inspection.

### Architecture Diagram
```
Blob Storage (documents container)
        │ BlobCreated Event
        ▼
 Event Grid Topic / System Topic
        │
        ▼
 Azure Function (Event Grid trigger)
        │  ├─ Reads blob metadata + stream
        │  ├─ Extracts title + wordCount
        │  └─ Upserts record into Cosmos DB
        ▼
 Cosmos DB (Documents container)
```

---

## Repository Layout (Suggested)
```
EventGridIndexer/
├─ host.json
├─ local.settings.json
├─ requirements.txt
├─ README_EventGrid.md          # this file
├─ DocumentIndexer/
│  ├─ __init__.py               # Event Grid function entry point
│  └─ function.json             # trigger binding metadata
└─ scripts/
   └─ cosmos_seed.sql           # optional helper queries
```

---

## Prerequisites
- Python 3.11+ (Functions runtime v4).
- Azure CLI or Azure PowerShell for provisioning.
- Azure Functions Core Tools v4 (`func`).
- An Azure Storage account with a `documents` container.
- An Azure Cosmos DB account (SQL API) with a database `ContentDb` and container `Documents` (partition key `/tenantId` or `/container`).
- Appropriate drivers and SDKs listed in `requirements.txt`.

### Dependencies (`requirements.txt`)
```
azure-functions
azure-storage-blob
azure-cosmos
```
Install locally:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

---

## Configuration (`local.settings.json`)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsSecretStorageType": "files",
    "BLOB_ACCOUNT_CONN_STR": "DefaultEndpointsProtocol=https;AccountName=<storage>;AccountKey=<key>;EndpointSuffix=core.windows.net",
    "COSMOS_DB_CONN_STR": "AccountEndpoint=https://<cosmos-account>.documents.azure.com:443/;AccountKey=<key>;",
    "COSMOS_DB": "ContentDb",
    "COSMOS_CONTAINER": "Documents"
  }
}

```

---

## Provisioning Overview
- Create an Azure resource group, Storage account (with `documents` container), Cosmos DB SQL account/database/container, and a Function App running Python 3.11.
- Grant the Function permission to read blobs (connection string or role assignment) and write to Cosmos (key or managed identity role).
- Add an Event Grid subscription referencing the Storage account as the source and the Function URL as the endpoint, filtering on `/blobServices/default/containers/documents/` so only relevant blobs trigger executions.

---

## Function Logic Summary
- Receive the Event Grid payload and extract the blob URL plus metadata.
- Use the Storage SDK to read blob properties and stream the content when the MIME type indicates text.
- Determine the title (first Markdown/HTML H1 or first line) and compute a word count via whitespace tokenization.
- Assemble the Cosmos document with identifiers, metadata, title, and word count, then perform an upsert so repeated events simply overwrite the existing record.
- Log each major step, including blob identity, derived title, and word-count, to simplify troubleshooting.

---

## Testing & Validation Flow
1. Run the Function locally with Azurite or development storage to confirm the trigger wiring and logging story.
2. Upload representative files (plain text, Markdown, HTML) into the `documents` container and ensure the logs show extracted titles and word counts.
3. Inspect Cosmos DB to verify one record per blob and confirm the values align with expectations.
4. Describe a Cosmos query that orders documents by `wordCount` descending and returns the top results; use Data Explorer to execute it during validation.

### Sample Function Log
```
[2025-11-27T10:14:22Z] Blob sample.md detected (text/markdown, 1.2 KB)
[2025-11-27T10:14:22Z] Extracted title="Sample Title" wordCount=9
[2025-11-27T10:14:23Z] Upserted Cosmos item id=sample.md
```

### Cosmos Query: Largest Documents
```sql
SELECT TOP 10 c.id, c.wordCount, c.url
FROM c
WHERE IS_DEFINED(c.wordCount)
ORDER BY c.wordCount DESC
```



## Terminal Snapshot
![Event Grid Function logs](terminal_output.png)
