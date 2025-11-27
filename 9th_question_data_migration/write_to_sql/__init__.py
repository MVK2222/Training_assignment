import logging
import pyodbc
import os

# Activity function: Writes a batch of products and tags to Azure SQL
# Flattens tags, uses bulk upsert, and handles errors


def main(items: list) -> dict:
    """
    Writes a batch of product documents to Azure SQL.
    - Flattens product and tag data for relational storage.
    - Uses bulk upsert (MERGE) for products and bulk insert for tags.
    - Handles errors and returns batch migration stats.
    """
    if not items:
        return {"status": "No items to process.", "inserted": 0, "updated": 0, "tags_inserted": 0}

    # Transform data: flatten products and tags
    product_rows = []
    tag_rows = []
    for doc in items:
        # Extract product fields safely
        p_id = str(doc.get('id'))
        p_name = doc.get('name', 'Unknown')
        try:
            p_price = float(doc.get('price', 0))
        except (TypeError, ValueError):
            p_price = 0.0
        p_cat = doc.get('category', 'Uncategorized')
        product_rows.append((p_id, p_name, p_price, p_cat))
        # Flatten tags array
        tags = doc.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                tag_rows.append((p_id, str(tag)))

    # Bulk upsert into SQL (MERGE for products, bulk insert for tags)
    conn_str = os.environ["SQL_CONN_STR"]
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.fast_executemany = True
            inserted = 0
            updated = 0
            tags_inserted = 0
            if product_rows:
                # Check which product ids already exist
                product_ids = [r[0] for r in product_rows]
                in_placeholders = ",".join(["?"] * len(product_ids))
                select_existing_sql = f"SELECT ProductId FROM Products WHERE ProductId IN ({in_placeholders})"
                cursor.execute(select_existing_sql, product_ids)
                existing_rows = cursor.fetchall()
                existing_ids = {r[0] for r in existing_rows} if existing_rows else set()
                inserted = len(product_ids) - len(existing_ids)
                updated = len(existing_ids)
                # Build parameter placeholders for VALUES
                row_placeholders = ", ".join(["(?, ?, ?, ?)"] * len(product_rows))
                params = [val for row in product_rows for val in row]
                # Perform MERGE (upsert)
                merge_sql = f"""
MERGE INTO Products AS target
USING (VALUES {row_placeholders}) AS source (ProductId, Name, Price, Category)
ON target.ProductId = source.ProductId
WHEN MATCHED THEN
    UPDATE SET Name = source.Name, Price = source.Price, Category = source.Category
WHEN NOT MATCHED THEN
    INSERT (ProductId, Name, Price, Category)
    VALUES (source.ProductId, source.Name, source.Price, source.Category);
"""
                cursor.execute(merge_sql, params)
            # Handle tags: delete old, insert new in bulk
            if tag_rows:
                product_ids = list({r[0] for r in product_rows})
                in_placeholders = ",".join(["?"] * len(product_ids))
                delete_sql = f"DELETE FROM ProductTags WHERE ProductId IN ({in_placeholders})"
                cursor.execute(delete_sql, product_ids)
                insert_tag_sql = "INSERT INTO ProductTags (ProductId, Tag) VALUES (?, ?)"
                cursor.executemany(insert_tag_sql, tag_rows)
                tags_inserted = len(tag_rows)
            conn.commit()
        return {
            "status": "Success",
            "inserted": inserted,
            "updated": updated,
            "tags_inserted": tags_inserted,
            "batch_count": len(product_rows)
        }

    except Exception as e:
        logging.error(f"SQL Write/Upsert Failed: {e}")
        # Re-raise to let Durable Functions know this activity failed
        raise e