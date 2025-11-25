# Azure Functions Product API

This project is an Azure Functions-based REST API for managing products using Azure Cosmos DB. It includes endpoints to add, update, delete, list, and retrieve products.

## Project Structure

```
function_app_assessment/
├── AddProduct/
│   └── init.py
├── DelProduct/
│   └── init.py
├── GetProduct/
│   └── init.py
├── ListProducts/
│   └── init.py
├── updateProduct/
│   └── init.py
├── cosmos_client.py
├── requirements.txt
├── local.settings.json
├── host.json
└── README.md
```

## Prerequisites
- Python 3.8+
- [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- Azure Cosmos DB account (or Emulator)

## Setup Instructions

### 1. Clone the Repository
```
git clone <your-repo-url>
cd function_app_assessment
```

### 2. Install Python Dependencies
```
pip install -r requirements.txt
```

### 3. Configure local.settings.json

Create or edit `local.settings.json` in the project root. Example:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_CONN_STRING": "<your-cosmos-connection-string>",
    "COSMOS_DB": "ProductsDB",
    "COSMOS_CONTAINER": "products"
  }
}
```
- Replace `<your-cosmos-connection-string>` with your Azure Cosmos DB connection string.
- Ensure `COSMOS_DB` and `COSMOS_CONTAINER` match your Cosmos DB database and container names.

### 4. Run Locally

Start the Azure Functions host:
```
func start
```

The API will be available at `http://localhost:7071/api/`

### 5. Test Endpoints

Use tools like [Postman](https://www.postman.com/) or PowerShell's `Invoke-RestMethod` to interact with the API.

#### Example: Update Product
```
PUT http://localhost:7071/api/products/{id}
Content-Type: application/json

{
  "name": "New Product Name",
  "price": 99.99
}
```

#### Example: Add Product
```
POST http://localhost:7071/api/AddProduct
Content-Type: application/json

{
  "id": "123",
  "name": "Sample Product",
  "price": 49.99
}
```

## Dependencies

All required Python packages are listed in `requirements.txt`. This file ensures your environment has the correct libraries for Azure Functions and Cosmos DB integration.

**To install dependencies:**
```powershell
pip install -r requirements.txt
```

Main packages:
- `azure-functions`: Azure Functions Python runtime
- `azure-cosmos`: Cosmos DB Python SDK

## Sample Local Run Output

Below is a screenshot (`terminal_output.png`) showing the Azure Functions host running locally and sample output from function execution:

![Local Run Output](terminal_output.png)

This demonstrates successful startup and function invocation. If you see similar output, your setup is correct.

## Function Endpoints
| Function        | Route                   | Method |
|-----------------|------------------------|--------|
| AddProduct      | /api/AddProduct         | POST   |
| updateProduct   | /api/products/{id}      | PUT    |
| DelProduct      | /api/DelProduct/{id}    | DELETE |
| GetProduct      | /api/GetProduct/{id}    | GET    |
| ListProducts    | /api/ListProducts       | GET    |

## Notes
- Ensure your Cosmos DB account allows access from your local machine.
- For production, secure your connection strings and secrets.
- The code expects the partition key to be `/id`.
