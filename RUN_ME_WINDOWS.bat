@echo off
echo ============================================
echo   KrishiSakhi - One-Click Setup and Run
echo ============================================
echo.

echo [1/4] Creating virtual environment (using Python 3.11)...
py -3.11 -m venv venv
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.11 was not found on this computer.
    echo Please install it from:
    echo   https://www.python.org/downloads/release/python-3119/
    echo Download "Windows installer (64-bit)", run it, and TICK
    echo "Add python.exe to PATH" on the first screen before installing.
    echo Then run this file again.
    pause
    exit /b
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing required packages (this can take 5-10 minutes the first time)...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed. See the red text above for details.
    echo If it mentions a specific package, copy that error and share it for help.
    pause
    exit /b
)

echo [4/4] Training the prediction models (rice, wheat, onion)...
if not exist "models\rice_lstm.keras" (
    python train_model.py all
) else (
    echo Models already trained - skipping.
)

echo.
echo ============================================
echo   Starting KrishiSakhi...
echo   Once it says "Running on http://...",
echo   open this in your browser:
echo.
echo        http://localhost:5000
echo.
echo   Press CTRL+C in this window to stop it.
echo ============================================
echo.
python app.py

pause
