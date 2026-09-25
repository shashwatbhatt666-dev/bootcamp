"""
Background Browser Launcher for Smart Classroom AI Suite.
Waits for the FastAPI backend to start and respond with HTTP 200,
then automatically opens the web browser to the application URL.
"""

import sys
import time
import urllib.request
import webbrowser

def wait_and_open(url: str, timeout_seconds: int = 40):
    start_time = time.time()
    ping_url = url.rstrip("/") + "/"

    print(f"[Launcher] Waiting for server to respond at {url} ...", flush=True)

    while time.time() - start_time < timeout_seconds:
        try:
            req = urllib.request.Request(
                ping_url,
                headers={"User-Agent": "SmartClassroomLauncher/1.0"}
            )
            with urllib.request.urlopen(req, timeout=1.0) as response:
                if response.getcode() == 200:
                    time.sleep(0.3)
                    print(f"[Launcher] Server ready! Opening browser to {url}", flush=True)
                    webbrowser.open(url)
                    return True
        except Exception:
            time.sleep(0.6)

    # Fallback open if timeout reached
    webbrowser.open(url)
    return False

if __name__ == "__main__":
    target_url = "http://127.0.0.1:8000"
    for arg in sys.argv[1:]:
        if arg.startswith("http://") or arg.startswith("https://"):
            target_url = arg
            break
    wait_and_open(target_url)
