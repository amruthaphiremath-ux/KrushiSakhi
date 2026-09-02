# KrishiSakhi — AI-Powered Price Prediction for Agriculture Products

A ready-to-run Flask + LSTM project implementing the 8 core algorithms of the
price prediction pipeline, now with a full multi-page site: a marketing
landing page, login/signup, and a protected dashboard for the prediction tool.

## Site map
- `/` — Landing page (hero, how it works, features)
- `/register` — Create an account
- `/login` — Log in
- `/dashboard` — The prediction tool (requires login)
- `/logout` — Log out

## About the login system
Accounts are stored in a simple `users.json` file created automatically the
first time someone registers, with passwords hashed via Werkzeug (a Flask
dependency, no extra install needed). This is intentionally simple for a
college project demo — note that on free hosting tiers (like Render's free
plan) the filesystem is ephemeral, so accounts can reset when the service
redeploys or restarts after sleeping. For a permanent production system,
swap `users.json` for a real database (SQLite or Postgres).

## Project Structure & Algorithm Map

| File | Algorithm |
|---|---|
| `utils/preprocessing.py` | **Algorithm 1** — Data Preprocessing & Cleaning |
| `utils/model_loader.py` | **Algorithm 2** — Model & Scaler Loading |
| `utils/sequence_prep.py` | **Algorithm 3** — Feature Extraction & Sequence Preparation |
| `train_model.py` | **Algorithm 4** — LSTM Model Training |
| `utils/predictor.py` | **Algorithm 5** — Rolling-Window Multi-Month Prediction (main logic) |
| `app.py` | **Algorithm 6** — Backend Prediction API (Flask) |
| `static/script.js` (renderTable) | **Algorithm 7** — Frontend Table Rendering |
| `static/script.js` (renderChart) | **Algorithm 8** — Graph/Chart Visualization |

## Included Sample Data
Synthetic monthly datasets (month, year, rainfall, price) run from January 2018
through August 2026 — i.e. right up to "today," so a 6-month forecast correctly
projects September 2026 through February 2027, not stale historical dates.
Six crops are included so the project runs out of the box:
- `data/rice.csv`
- `data/wheat.csv`
- `data/onion.csv`
- `data/tomato.csv`
- `data/corn.csv`
- `data/potato.csv`

Replace these with real Agmarknet/market data any time — same column format
(`month, year, rainfall, price`) is all that's required. If you add a new crop
CSV yourself, keep the data current the same way: make sure its last row is
recent, or the model will forecast from an outdated starting point.

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the LSTM model for each crop (Algorithm 4)
python train_model.py all
# or individually:
python train_model.py rice
python train_model.py wheat
python train_model.py onion
python train_model.py tomato
python train_model.py corn
python train_model.py potato

# 4. Run the web app
python app.py
```

Then open **http://localhost:5000** in your browser, pick a crop, enter
months-ahead, and click **Predict Price** to see the table (Algorithm 7) and
line chart (Algorithm 8) update.

## Notes
- Trained models are saved under `models/` as `<crop>_lstm.keras` plus
  `<crop>_x_scaler.pkl` / `<crop>_y_scaler.pkl` (Algorithm 2 loads these).
- To add a new crop, drop a CSV with the same 4 columns into `data/`, then run
  `python train_model.py <cropname>`.
- `months_ahead` is capped at 24 in `predictor.py` — adjust `predict_future_prices`
  if you need longer-range forecasts.
