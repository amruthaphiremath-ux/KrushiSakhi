"""
ALGORITHM 2 — MODEL & SCALER LOADING
--------------------------------------
START
1. Receive selected crop name
2. Load trained LSTM model file (.keras) for that crop
3. Load the feature scaler (X-scaler)
4. Load the target price scaler (Y-scaler)
5. Return model + scalers for prediction use
END
"""

import os
import joblib
from tensorflow.keras.models import load_model

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


def load_crop_model_and_scalers(crop_name: str):
    crop_name = crop_name.lower()
    model_path = os.path.join(MODELS_DIR, f"{crop_name}_lstm.keras")
    x_scaler_path = os.path.join(MODELS_DIR, f"{crop_name}_x_scaler.pkl")
    y_scaler_path = os.path.join(MODELS_DIR, f"{crop_name}_y_scaler.pkl")

    for p in (model_path, x_scaler_path, y_scaler_path):
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"Model artifact missing: {p}. Run train_model.py for '{crop_name}' first."
            )

    model = load_model(model_path)
    x_scaler = joblib.load(x_scaler_path)
    y_scaler = joblib.load(y_scaler_path)
    return model, x_scaler, y_scaler
