import os
import sys
from pathlib import Path

# PyInstaller --windowed builds have no console on Windows, so sys.stdout /
# sys.stderr are None. Any print() before this is patched crashes with
# "'NoneType' object has no attribute 'write'".
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

sys.path.insert(0, str(Path(__file__).parent))

from ui.app import App


if __name__ == "__main__":
    App().mainloop()
