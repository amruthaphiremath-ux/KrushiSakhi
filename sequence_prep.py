"""
ALGORITHM 3 — FEATURE EXTRACTION & SEQUENCE PREPARATION
-----------------------------------------------------------
START
1. Select relevant columns: month, year, rainfall, price/WPI
2. Scale all features using the fitted feature scaler
3. Group scaled values into fixed-length time-step windows
4. Prepare the "last known sequence" as the LSTM's starting input
END
"""

import numpy as np

TIME_STEPS = 6  # number of past months the LSTM looks at for one prediction


def scale_features(X, x_scaler):
    """Step 2: Scale raw feature matrix using a pre-fitted scaler."""
    return x_scaler.transform(X)


def create_sequences(X_scaled, y_scaled, time_steps=TIME_STEPS):
    """Step 3: Convert a scaled feature/target series into (samples, time_steps, features)."""
    X_seq, y_seq = [], []
    for i in range(len(X_scaled) - time_steps):
        X_seq.append(X_scaled[i:i + time_steps])
        y_seq.append(y_scaled[i + time_steps])
    return np.array(X_seq), np.array(y_seq)


def last_known_sequence(X_scaled, time_steps=TIME_STEPS):
    """Step 4: Build the most recent window to seed rolling-window prediction."""
    if len(X_scaled) < time_steps:
        raise ValueError("Not enough historical rows to build a prediction sequence.")
    return X_scaled[-time_steps:].reshape(1, time_steps, X_scaled.shape[1])
