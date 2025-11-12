
#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --upgrade pip pyinstaller
pyinstaller --noconfirm --clean \
  --name "shipx-re1-dashboard" \
  --add-data "app.py:." \
  --add-data "shipx_dash:shipx_dash" \
  --add-data "veres_re1_to_excel.py:." \
  run_streamlit.py
echo "Binary in dist/shipx-re1-dashboard"
