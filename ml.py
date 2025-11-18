import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
import pickle
import logging

logging.basicConfig(level=logging.INFO)

# Load dataset
df = pd.read_json("sample_products.json")
logging.info("Dataset loaded successfully.")

# Split dataset into training and missing-data sets
df_train = df[df["price"].notnull()]
df_missing = df[df["price"].isnull()]
logging.info(f"Training set size: {len(df_train)}")
logging.info(f"Missing data set size: {len(df_missing)}")
# Features and target
X = df_train.drop("price", axis=1)
y = df_train["price"]

# Columns to transform
categorical_cols = ["name", "category"]
numeric_cols = ["inStock"]

# Preprocessing pipeline
preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", "passthrough", numeric_cols)
    ]
)


# Final model pipeline
model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("regressor", DecisionTreeRegressor())
])

# Train the model
model.fit(X, y)

# Predict missing prices
X_missing = df_missing.drop("price", axis=1)
predicted_prices = model.predict(X_missing)

# Fill missing values
df.loc[df["price"].isnull(), "price"] = predicted_prices

#with open("price_model.pkl", "wb") as f:
#    pickle.dump(model, f)
# Save output
df.to_json("products_filled.json", orient="records", indent=4)

print("Missing prices filled successfully!")
