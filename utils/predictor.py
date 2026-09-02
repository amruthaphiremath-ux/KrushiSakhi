"""
Prediction utilities for KrishiSakhi.

Loads a trained LSTM model and its scalers, then predicts future
crop prices using the most recent historical sequence.
"""

import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model

from utils.preprocessing import preprocess_crop, FEATURE_COLUMNS
from utils.sequence_prep import TIME_STEPS, last_known_sequence


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")


def predict_future_prices(crop: str, months_ahead: int):
    """
    Predict crop prices for the requested number of months.

    Parameters
    ----------
    crop : str
        Crop name, e.g. "rice" or "wheat".

    months_ahead : int
        Number of future months to predict.

    Returns
    -------
    list
        List of dictionaries containing month number and predicted price.
    """

    crop = str(crop).strip().lower()

    if months_ahead <= 0:
        raise ValueError("months_ahead must be a positive number.")

    # ---------------------------------------------------------------
    # Locate trained model and scalers
    # ---------------------------------------------------------------
    model_path = os.path.join(
        MODELS_DIR,
        f"{crop}_lstm.keras"
    )

    x_scaler_path = os.path.join(
        MODELS_DIR,
        f"{crop}_x_scaler.pkl"
    )

    y_scaler_path = os.path.join(
        MODELS_DIR,
        f"{crop}_y_scaler.pkl"
    )

    # If the model/scalers don't exist, tell app.py that the model
    # has not been trained yet.
    if not all(
        os.path.exists(path)
        for path in [model_path, x_scaler_path, y_scaler_path]
    ):
        raise FileNotFoundError(
            f"Model not trained for '{crop}'. "
            f"Run: python train_model.py {crop}"
        )

    # ---------------------------------------------------------------
    # Load trained model and scalers
    # ---------------------------------------------------------------
    model = load_model(model_path)

    x_scaler = joblib.load(x_scaler_path)
    y_scaler = joblib.load(y_scaler_path)

    # ---------------------------------------------------------------
    # Load and preprocess historical crop data
    # ---------------------------------------------------------------
    df, X, y = preprocess_crop(crop)

    if len(X) < TIME_STEPS:
        raise ValueError(
            f"Not enough historical data for '{crop}'. "
            f"At least {TIME_STEPS} rows are required."
        )

    # ---------------------------------------------------------------
    # Scale features using the SAME scaler used during training
    # ---------------------------------------------------------------
    X_scaled = x_scaler.transform(X)

    # ---------------------------------------------------------------
    # Get the most recent 6-month sequence
    # ---------------------------------------------------------------
    sequence = last_known_sequence(
        X_scaled,
        TIME_STEPS
    )

    predictions = []

    # ---------------------------------------------------------------
    # Rolling prediction
    #
    # Important:
    # The model was trained with:
    #   month
    #   year
    #   rainfall
    #
    # For future months we do not know actual future rainfall.
    #
    # Therefore, for the prediction window we keep the latest known
    # rainfall value and advance month/year.
    # ---------------------------------------------------------------

    last_month = int(df["month"].iloc[-1])
    last_year = int(df["year"].iloc[-1])
    last_rainfall = float(df["rainfall"].iloc[-1])

    current_month = last_month
    current_year = last_year

    for step in range(1, months_ahead + 1):

        # -----------------------------------------------------------
        # Ask the LSTM for the next price
        # -----------------------------------------------------------
        predicted_scaled = model.predict(
            sequence,
            verbose=0
        )

        predicted_price = float(
            y_scaler.inverse_transform(
                np.array(predicted_scaled).reshape(-1, 1)
            )[0][0]
        )

        # Avoid tiny negative values caused by model error.
        predicted_price = max(0.0, predicted_price)

        # -----------------------------------------------------------
        # Advance calendar month
        # -----------------------------------------------------------
        current_month += 1

        if current_month > 12:
            current_month = 1
            current_year += 1

        # -----------------------------------------------------------
        # Save result
        # -----------------------------------------------------------
        predictions.append({
            "month": current_month,
            "year": current_year,
            "price": round(predicted_price, 2)
        })

        # -----------------------------------------------------------
        # Create the next input row.
        #
        # We use the predicted price only for the output. The model's
        # input features are month/year/rainfall, so the predicted
        # price itself is not inserted into X.
        # -----------------------------------------------------------
        next_features = np.array([[
            float(current_month),
            float(current_year),
            last_rainfall
        ]])

        next_features_scaled = x_scaler.transform(next_features)

        # -----------------------------------------------------------
        # Roll the sequence forward by one timestep.
        # -----------------------------------------------------------
        sequence = np.concatenate(
            [
                sequence[:, 1:, :],
                next_features_scaled.reshape(
                    1,
                    1,
                    len(FEATURE_COLUMNS)
                )
            ],
            axis=1
        )

    return predictions
