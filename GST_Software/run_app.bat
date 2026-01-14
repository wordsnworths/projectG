@echo off
echo ==========================================
echo      GST REPORT ARCHITECT - LAUNCHER
echo ==========================================
echo.
echo [1/2] Checking and installing requirements...
pip install -r requirements.txt
echo.
echo [2/2] Launching Application...
streamlit run gst_app.py
pause