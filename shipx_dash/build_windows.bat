
@echo off
setlocal
python -m pip install --upgrade pip pyinstaller
pyinstaller --noconfirm --clean --windowed ^
  --name "ShipX-RE1-Dashboard" ^
  --add-data "app.py;." ^
  --add-data "shipx_dash;shipx_dash" ^
  --add-data "veres_re1_to_excel.py;." ^
  run_streamlit.py
echo.
echo Build complete! Find the EXE under dist\ShipX-RE1-Dashboard.exe
pause
