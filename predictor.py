"""
ALGORITHM 5 — ROLLING-WINDOW MULTI-MONTH PREDICTION (MAIN LOGIC)
--------------------------------------------------------------------
START
1. Read crop name and number of months ahead from the user
2. Load dataset, trained model, and scalers
3. Build the initial input sequence from the most recent data
4. FOR each future month from 1 to N:
     a. Feed sequence into the LSTM model
     b. Predict next price (scaled form)
     c. Inverse-transform to actual price using Y-scaler
     d. Store predicted price against that future month
     e. Slide the window forward — feed this prediction back
        into the sequence for the next month's forecast
   END FOR
5. Return all predicted values as JSON
END
"""

import numpy as np

from utils.preprocessing import preprocess_crop
from utils.model_loader import load_crop_model_and_scalers
from utils.sequence_prep import scale_features, last_known_sequence, TIME_STEPS


def _next_month_year(month: int, year: int):
    if month == 12:
        return 1, year + 1
    return month + 1, year


def predict_future_prices(crop_name: str, months_ahead: int):
    """Runs the full rolling-window forecast and returns a list of
    {month, year, predicted_price} dicts — ready to be JSON-serialized."""

    if months_ahead < 1 or months_ahead > 24:
        raise ValueError("months_ahead must be between 1 and 24")

    # Step 2: load cleaned data, model, scalers
    df, X, _ = preprocess_crop(crop_name)
    model, x_scaler, y_scaler = load_crop_model_and_scalers(crop_name)

    # Step 3: build the starting sequence from the most recent TIME_STEPS rows
    X_scaled = scale_features(X, x_scaler)
    sequence = last_known_sequence(X_scaled, TIME_STEPS)

    last_month = int(df.iloc[-1]["month"])
    last_year = int(df.iloc[-1]["year"])
    avg_rainfall = float(df["rainfall"].tail(TIME_STEPS).mean())

    results = []
    cur_month, cur_year = last_month, last_year

    for _ in range(months_ahead):
        # 4a-4b: predict next scaled price
        scaled_pred = model.predict(sequence, verbose=0)[0][0]

        # 4c: inverse scale back to real price
        real_price = float(y_scaler.inverse_transform([[scaled_pred]])[0][0])

        # advance the calendar
        cur_month, cur_year = _next_month_year(cur_month, cur_year)

        # 4d: store this month's prediction
        results.append({
            "month": cur_month,
            "year": cur_year,
            "predicted_price": round(real_price, 2),
        })

        # 4e: roll the window forward — build the next feature row
        # (month, year, rainfall) scaled the same way as training data
        next_row_raw = np.array([[cur_month, cur_year, avg_rainfall]])
        next_row_scaled = x_scaler.transform(next_row_raw)
        sequence = np.append(sequence[:, 1:, :], next_row_scaled.reshape(1, 1, -1), axis=1)

    return results
