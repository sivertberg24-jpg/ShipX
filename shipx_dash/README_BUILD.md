
# Packaging & Sharing

## One‑click desktop (PyInstaller)

### Windows
```
python -m pip install --upgrade pip pyinstaller
build_windows.bat
```
Result: `dist/ShipX-RE1-Dashboard.exe` (double‑click).

### macOS
```
python3 -m pip install --upgrade pip pyinstaller
bash build_macos.sh
```
Result: `dist/ShipX-RE1-Dashboard.app` (double‑click). You may need to allow the app in *System Settings → Privacy & Security*.

### Linux
```
python3 -m pip install --upgrade pip pyinstaller
bash build_linux.sh
```
Result: `dist/shipx-re1-dashboard`.

## Docker (internal server)
```
docker build -t shipx-re1-dashboard .
docker run --rm -p 8501:8501 -v /data:/data shipx-re1-dashboard
```
Open http://localhost:8501

## Streamlit Cloud / Hugging Face
These hosts can't access a user's local filesystem. For public sharing, add a "zip folder upload" path or host the data remotely.
