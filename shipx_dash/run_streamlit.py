# run_streamlit.py
import os, sys, webbrowser, socket

def _free_port():
    s = socket.socket(); s.bind(('', 0)); p = s.getsockname()[1]; s.close(); return p

def main():
    from streamlit.web.cli import main as st_main  # <- imported INSIDE main
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(base, "app.py")
    port = _free_port()
    try: webbrowser.open(f"http://localhost:{port}")
    except Exception: pass
    sys.argv = ["streamlit", "run", app_path,
                f"--server.port={port}", "--server.headless=true",
                "--browser.gatherUsageStats=false", "--client.toolbarMode=minimal"]
    raise SystemExit(st_main())

if __name__ == "__main__":
    main()
