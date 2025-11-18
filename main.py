import pandas as pd
import pickle
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
load_dotenv()
 
CONN_STRING = os.getenv("COSMOS_CONN_STRING")
DB_NAME = os.getenv("DB_NAME")
COLL_NAME = os.getenv("COLLECTION")
PREPROCESSED_COLL_NAME = os.getenv("CLEANED_COLLECTION")

# Load the trained model
with open("price_model.pkl", "rb") as f:
    price_model = pickle.load(f)
 
app = FastAPI()
client = AsyncIOMotorClient(CONN_STRING, tls=True, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]
collection = db[COLL_NAME]
preprocessed_collection = db[PREPROCESSED_COLL_NAME]
 
def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc
 
@app.get("/")
async def root():
    return {"message": "Cosmos App running"}
 
# Insert
@app.post("/products")
async def create_product(product:list [dict]):
    #result = await collection.insert_one(product)
    result = await collection.insert_many(product)
    return {"inserted_ids:": [str(id) for id in result.inserted_ids]}
 
# Read
@app.get("/products")
async def read_product():
    logger.info("GET /products - read all products")
    cursor = await collection.find().to_list(100)
    docs = [fix_id(p) for p in cursor]
    logger.info("GET /products - returned_count=%d", len(docs))
    return docs
 
# Read a product
@app.get("/products/{id}")
async def get_product(id: str):
    logger.info("GET /products/%s - fetching product", id)
    product = await collection.find_one({"_id": ObjectId(id)})
    if not product:
        logger.warning("GET /products/%s - product not found", id)
        raise HTTPException(404, "Product not Found")
    result = fix_id(product)
    logger.info("GET /products/%s - found product", id)
    return result
 
#PREPROCESSED DATA
@app.put("/preprocessed_data")
async def update_missing_prices():
    logger.info("Fetching products from preprocessed collection...")

    # Fetch all preprocessed products
    products = await collection.find().to_list(1000)

    if not products:
        logger.warning("No documents found in collection.")
        return {"message": "No documents found in collection."}

    logger.info(f"RAW PRODUCTS FROM DB: {products}")

    # Convert to DataFrame
    df = pd.DataFrame(products)
    logger.info(f"RAW DATAFRAME:\n{df}")

    # Filter rows where price is missing
    df_missing = df[df["price"].isnull()]
    logger.info(f"MISSING PRICE ROWS:\n{df_missing}")

    if df_missing.empty:
        logger.info("No missing prices found in DB.")
        return {"message": "No missing prices found in preprocessed data."}

    # Convert _id to str for easier processing
    df_missing["_id"] = df_missing["_id"].astype(str)

    # Prepare features for ML prediction
    X_missing = df_missing.drop(columns=["price", "_id"])
    logger.info(f"FEATURES SENT TO MODEL (X_missing):\n{X_missing}")

    # Predict prices
    df_missing["predicted_price"] = price_model.predict(X_missing)
    logger.info(f"PREDICTED PRICES:\n{df_missing[['name','predicted_price']]}")

    # Update each document in MongoDB
    updated_docs = []
    for _id, predicted in zip(df_missing["_id"], df_missing["predicted_price"]):
        await preprocessed_collection.update_one(
            {"_id": ObjectId(_id)},
            {"$set": {"price": float(predicted)}}
        )
        updated_docs.append({"_id": _id, "predicted_price": float(predicted)})

    #logger.info(f"UPDATED DOCUMENTS:\n{updated_docs}")

    return {
        "message": "Missing prices predicted and updated successfully.",
        "count": len(df_missing),
        "updated_items": updated_docs
    }


# Update
@app.put("/products/{id}")
async def update_item(id: str, data: dict):
    logger.info("PUT /products/%s - update called with data=%s", id, data)
    result = await collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )
    if result.modified_count == 0:
        logger.warning("PUT /products/%s - no documents modified", id)
        raise HTTPException(404, "Product not Found")
    logger.info("PUT /products/%s - modified_count=%d", id, result.modified_count)
    return {"message": "Updated"}
 
# Delete
@app.delete("/products/{id}")
async def delete_product(id: str):
    logger.info("DELETE /products/%s - delete called", id)
    result = await collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        logger.warning("DELETE /products/%s - product not found", id)
        raise HTTPException(404, "Product not Found")
    logger.info("DELETE /products/%s - deleted_count=%d", id, result.deleted_count)
    return {"message": "Deleted Successfully"}