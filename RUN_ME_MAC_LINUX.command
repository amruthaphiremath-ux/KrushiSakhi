#!/bin/bash
echo "============================================"
echo "  KrishiSakhi - One-Click Setup and Run"
echo "============================================"
echo

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Python 3 was not found."
    echo "Please install it from https://www.python.org/downloads/"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing required packages (this can take 5-10 minutes the first time)..."
pip install -r requirements.txt

echo "[4/4] Training the prediction models (rice, wheat, onion)..."
if [ ! -f "models/rice_lstm.keras" ]; then
    python train_model.py all
else
    echo "Models already trained - skipping."
fi

echo
echo "============================================"
echo "  Starting KrishiSakhi..."
echo "  Once it says 'Running on http://...',"
echo "  open this in your browser:"
echo
echo "       http://localhost:5000"
echo
echo "  Press CTRL+C in this window to stop it."
echo "============================================"
echo
python app.py
