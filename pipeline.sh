#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Discord Data Viz Pipeline ==="
echo ""

# Check for exports
if [ ! -d "exports" ] || [ -z "$(ls -A exports/*.json 2>/dev/null)" ]; then
    echo "No JSON files found in exports/"
    echo ""
    echo "Please export your Discord channels using DiscordChatExporter:"
    echo "  DiscordChatExporter.Cli export -t TOKEN -c CHANNEL_ID -f Json -o exports/"
    echo ""
    exit 1
fi

echo "Step 1: Parsing exports..."
python3 pipeline/1_parse_exports.py
echo ""

echo "Step 2: Generating embeddings (downloads 1.6GB model on first run)..."
python3 pipeline/2_generate_embeddings.py
echo ""

echo "Step 3: Running t-SNE dimensionality reduction..."
python3 pipeline/3_run_tsne.py
echo ""

echo "Step 4: Clustering messages..."
python3 pipeline/4_cluster.py
echo ""

echo "=== Pipeline complete! ==="
echo ""
echo "Starting server..."
python3 serve.py
