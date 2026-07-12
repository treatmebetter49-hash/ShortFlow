import os
import sys
import traceback
from pathlib import Path

# PyInstaller --windowed builds have no console on Windows, so sys.stdout /
# sys.stderr are None. Any print() before this is patched crashes with
# "'NoneType' object has no attribute 'write'". Route both to a log file
# instead of devnull so startup/runtime errors are still diagnosable.
_LOG_PATH = Path.home() / "ShortFlow-debug.log"
if sys.stdout is None or sys.stderr is None:
    _log_file = open(_LOG_PATH, "a", encoding="utf-8", buffering=1)
    if sys.stdout is None:
        sys.stdout = _log_file
    if sys.stderr is None:
        sys.stderr = _log_file

sys.path.insert(0, str(Path(__file__).parent))


def _log_uncaught(exc_type, exc_value, exc_tb):
    with open(_LOG_PATH, "a", encoding="utf-8") as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)


sys.excepthook = _log_uncaught

try:
    from ui.app import App
except Exception:
    with open(_LOG_PATH, "a", encoding="utf-8") as f:
        traceback.print_exc(file=f)
    raise


if __name__ == "__main__":
    try:
        app = App()
        app.report_callback_exception = lambda *exc_info: _log_uncaught(*exc_info)
        app.mainloop()
    except Exception:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise
