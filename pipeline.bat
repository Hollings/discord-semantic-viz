@echo off
cd /d "%~dp0"

echo === Discord Data Viz Pipeline ===
echo.

REM Check for exports
if not exist "exports\*.json" (
    echo No JSON files found in exports\
    echo.
    echo Please export your Discord channels using DiscordChatExporter:
    echo   DiscordChatExporter.Cli export -t TOKEN -c CHANNEL_ID -f Json -o exports\
    echo.
    exit /b 1
)

echo Step 1: Parsing exports...
python pipeline\1_parse_exports.py
if errorlevel 1 exit /b 1
echo.

echo Step 2: Generating embeddings (downloads 1.6GB model on first run)...
python pipeline\2_generate_embeddings.py
if errorlevel 1 exit /b 1
echo.

echo Step 3: Running t-SNE dimensionality reduction...
python pipeline\3_run_tsne.py
if errorlevel 1 exit /b 1
echo.

echo Step 4: Clustering messages...
python pipeline\4_cluster.py
if errorlevel 1 exit /b 1
echo.

echo === Pipeline complete! ===
echo.
echo Starting server...
python serve.py
