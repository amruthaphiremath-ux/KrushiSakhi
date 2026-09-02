"""
ALGORITHM 4 — LSTM MODEL TRAINING
------------------------------------
START
1. Feed prepared sequences into the LSTM network
2. Model learns temporal dependencies across months/years
3. Capture seasonal cycles and long-range trends
4. Evaluate using RMSE, MAE, and MAPE metrics
5. Save the trained model in .keras format for reuse
END

Run this once per crop before starting the Flask app:
    python train_model.py rice
    python train_model.py wheat
    python train_model.py onion
    python train_model.py all      (trains every crop found in /data)
"""

import os
import sys
import glob
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

from utils.preprocessing import preprocess_crop, TARGET_COLUMN
from utils.sequence_prep import create_sequences, TIME_STEPS

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(MODELS_DIR, exist_ok=True)


def build_lstm_model(input_shape):
    """Defines the LSTM architecture used by the system."""
    model = Sequential([
        LSTM(64, activation="tanh", return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32, activation="tanh"),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")
    return model


def train_for_crop(crop_name: str, epochs: int = 60, batch_size: int = 8):
    print(f"\n=== Training LSTM model for '{crop_name}' ===")

    # Step 1 (of Algorithm 1): clean data + split features/target
    df, X, y = preprocess_crop(crop_name)

    # Fit scalers on the whole series (Algorithm 3, step 2)
    x_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()
    X_scaled = x_scaler.fit_transform(X)
    y_scaled = y_scaler.fit_transform(y)

    # Build time-step sequences (Algorithm 3, step 3)
    X_seq, y_seq = create_sequences(X_scaled, y_scaled, TIME_STEPS)
    if len(X_seq) < 10:
        raise ValueError(f"Not enough data to train '{crop_name}' — need more history.")

    split = int(len(X_seq) * 0.85)
    X_train, X_test = X_seq[:split], X_seq[split:]
    y_train, y_test = y_seq[:split], y_seq[split:]

    # Step 1-2 of Algorithm 4: train the network
    model = build_lstm_model((X_seq.shape[1], X_seq.shape[2]))
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

    # Step 4 of Algorithm 4: evaluate
    preds = model.predict(X_test, verbose=0)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    print(f"  RMSE(scaled)={rmse:.4f}  MAE(scaled)={mae:.4f}")

    # Step 5 of Algorithm 4: save model + scalers
    model.save(os.path.join(MODELS_DIR, f"{crop_name}_lstm.keras"))
    joblib.dump(x_scaler, os.path.join(MODELS_DIR, f"{crop_name}_x_scaler.pkl"))
    joblib.dump(y_scaler, os.path.join(MODELS_DIR, f"{crop_name}_y_scaler.pkl"))
    print(f"  Saved model + scalers to {MODELS_DIR}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_model.py <crop_name|all>")
        sys.exit(1)

    target = sys.argv[1].lower()
    if target == "all":
        crops = [os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(DATA_DIR, "*.csv"))]
    else:
        crops = [target]

    for crop in crops:
        train_for_crop(crop)

    print("\nAll requested models trained successfully.")
