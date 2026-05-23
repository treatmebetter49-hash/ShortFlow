@echo off
echo === ShortFlow Windows Build ===
echo.

:: Python pruefen
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden.
    echo Bitte Python 3.11 von https://python.org installieren.
    echo Wichtig: "Add Python to PATH" beim Installieren anhaeken!
    pause
    exit /b 1
)

echo Python gefunden:
python --version
echo.

:: Abhaengigkeiten installieren
echo --- Installiere Abhaengigkeiten ---
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo FEHLER beim Installieren der Abhaengigkeiten.
    pause
    exit /b 1
)

echo.
echo --- Starte Build ---
pyinstaller ShortFlow-windows.spec --clean
if errorlevel 1 (
    echo FEHLER beim Build.
    pause
    exit /b 1
)

echo.
echo === Build fertig! ===
echo Die Datei liegt in: dist\ShortFlow\ShortFlow.exe
echo.
pause
