import sys
import traceback
from pathlib import Path

# Startup-Fehler dürfen nie lautlos verschwinden: Traceback immer in ein Logfile
# schreiben — unabhängig davon, ob die App mit oder ohne Konsole gebaut wurde.
_LOG_PATH = Path.home() / "ShortFlow_log.txt"

if sys.stdout is None or sys.stderr is None:
    log_file = open(_LOG_PATH, "a", buffering=1, encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file

sys.path.insert(0, str(Path(__file__).parent))


def _report_startup_error(exc: BaseException) -> None:
    """Traceback ins Logfile schreiben und — auf Windows — im Klartext anzeigen."""
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        _LOG_PATH.write_text(tb, encoding="utf-8")
    except Exception:
        pass
    traceback.print_exc()
    if sys.platform == "win32":
        try:
            import ctypes

            msg = f"ShortFlow konnte nicht starten:\n\n{tb[-1500:]}\n\nLog: {_LOG_PATH}"
            ctypes.windll.user32.MessageBoxW(None, msg, "ShortFlow – Startfehler", 0x10)
        except Exception:
            pass


try:
    from ui.app import App

    if __name__ == "__main__":
        App().mainloop()
except Exception as exc:
    _report_startup_error(exc)
    raise
