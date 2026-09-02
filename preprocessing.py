"""
ALGORITHM 1 — DATA PREPROCESSING & CLEANING
--------------------------------------------
START
1. Read the crop-specific CSV file
2. Remove rows with missing/null values
3. Reset index to preserve chronological order
4. Extract input features: Month, Year, Rainfall
5. Extract target variable: Crop Price
6. Store features and target separately for scaling
END
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

FEATURE_COLUMNS = ["month", "year", "rainfall"]
TARGET_COLUMN = "price"


def load_crop_csv(crop_name: str) -> pd.DataFrame:
    """Step 1: Read the crop-specific CSV file from the data directory."""
    path = os.path.join(DATA_DIR, f"{crop_name.lower()}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found for crop: {crop_name}")
    return pd.read_csv(path)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Steps 2-3: Remove missing rows and reset index."""
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df


def extract_features_and_target(df: pd.DataFrame):
    """Steps 4-6: Split into feature matrix X and target vector y."""
    X = df[FEATURE_COLUMNS].values.astype(float)
    y = df[[TARGET_COLUMN]].values.astype(float)
    return X, y


def preprocess_crop(crop_name: str):
    """Convenience wrapper running the full Algorithm 1 pipeline."""
    df = load_crop_csv(crop_name)
    df = clean_dataset(df)
    X, y = extract_features_and_target(df)
    return df, X, y
