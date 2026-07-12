import sys
import traceback
from pathlib import Path

if sys.stdout is None or sys.stderr is None:
    log_path = Path.home() / "ShortFlow_log.txt"
    log_file = open(log_path, "a", buffering=1, encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ui.app import App

    if __name__ == "__main__":
        App().mainloop()
except Exception:
    traceback.print_exc()
    raise
