#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== ShortFlow macOS Build ==="
echo "Python: $(python3 --version)"
echo "PyInstaller: $(pyinstaller --version)"
echo ""

# Altes Build-Verzeichnis aufräumen
rm -rf dist/ShortFlow.app build/ ShortFlow.spec

echo "--- Starte Build ---"
pyinstaller \
  --windowed \
  --name "ShortFlow" \
  --icon "icon.icns" \
  --collect-all customtkinter \
  --hidden-import fal_client \
  --hidden-import fal_client.client \
  --hidden-import pandas \
  --hidden-import pandas._libs.tslibs.np_datetime \
  --hidden-import pandas._libs.tslibs.nattype \
  --hidden-import pandas._libs.skiplist \
  --hidden-import openpyxl \
  --hidden-import PIL \
  --hidden-import PIL.Image \
  --hidden-import PIL.ImageDraw \
  --hidden-import PIL.PngImagePlugin \
  --hidden-import httpx \
  --hidden-import anyio \
  --hidden-import anyio._backends._asyncio \
  --osx-bundle-identifier "com.shortflow.app" \
  main.py

echo ""
echo "--- Ad-hoc Signatur ---"
codesign --force --deep --sign - "$PROJECT_DIR/dist/ShortFlow.app"

echo ""
echo "=== Build fertig ==="
echo "App: $PROJECT_DIR/dist/ShortFlow.app"
echo ""
echo "Testen:"
echo "  open dist/ShortFlow.app"
echo "  # Bei Gatekeeper-Block: Rechtsklick → Öffnen"
