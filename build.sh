#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== ShortFlow macOS Build ==="
echo "Python: $(python3 --version)"
echo "PyInstaller: $(python3 -m PyInstaller --version)"
echo ""

# Altes Build-Verzeichnis aufräumen
rm -rf dist/ build/ ShortFlow.spec

echo "--- Starte Build ---"
python3 -m PyInstaller \
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
  --add-data "shortflow_theme.json:." \
  --osx-bundle-identifier "com.shortflow.app" \
  main.py

echo ""
echo "--- Ad-hoc Signatur ---"
codesign --force --deep --sign - "$PROJECT_DIR/dist/ShortFlow.app"

echo ""
echo "--- DMG bauen ---"
DMG_PATH="$PROJECT_DIR/dist/ShortFlow.dmg"
DMG_STAGING="$PROJECT_DIR/dist/dmg-staging"
rm -f "$DMG_PATH"
rm -rf "$DMG_STAGING"
# Staging-Ordner mit App + Programme-Alias, damit der Nutzer die App per
# Drag & Drop in den Programme-Ordner ziehen kann (statt aus der DMG zu starten).
mkdir -p "$DMG_STAGING"
cp -R "$PROJECT_DIR/dist/ShortFlow.app" "$DMG_STAGING/"
ln -s /Applications "$DMG_STAGING/Applications"
hdiutil create -volname "ShortFlow" -srcfolder "$DMG_STAGING" -ov -format UDZO "$DMG_PATH"
rm -rf "$DMG_STAGING"

echo ""
echo "=== Build fertig ==="
echo "App: $PROJECT_DIR/dist/ShortFlow.app"
echo "DMG: $DMG_PATH"
echo ""
echo "Testen:"
echo "  open dist/ShortFlow.app"
echo "  # Bei Gatekeeper-Block: Rechtsklick → Öffnen"
