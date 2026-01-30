# Discord Data Viz

Visualize your Discord messages as a semantic map. Messages with similar content cluster together using word2vec embeddings and t-SNE dimensionality reduction.

## Quick Start

### 1. Export your Discord channels

Use [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) to export channels as JSON:

```bash
# Get your Discord token from browser devtools (Network tab, filter by "api", check Authorization header)
DiscordChatExporter.Cli export -t YOUR_TOKEN -c CHANNEL_ID -f Json -o exports/

# Export multiple channels
DiscordChatExporter.Cli export -t YOUR_TOKEN -c CHANNEL_ID_1 -f Json -o exports/
DiscordChatExporter.Cli export -t YOUR_TOKEN -c CHANNEL_ID_2 -f Json -o exports/
```

### 2. Run the pipeline

**Docker (recommended):**
```bash
docker compose up
```

This runs the full pipeline and starts the server at http://localhost:8080

**Or run steps separately:**
```bash
# Just run pipeline (no server)
docker compose --profile pipeline up

# Just serve (after pipeline has run)
docker compose --profile server up

# Run in background (detached)
docker compose up -d

# Re-run just clustering (after tweaking parameters)
docker compose run --rm viz python pipeline/4_cluster.py
```

**Without Docker (Linux/Mac/WSL):**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline + server
./pipeline.sh

# Or run steps manually:
python pipeline/1_parse_exports.py
python pipeline/2_generate_embeddings.py
python pipeline/3_run_tsne.py
python pipeline/4_cluster.py
python serve.py
```

**Without Docker (Windows):**
```batch
:: Install dependencies
pip install -r requirements.txt

:: Run the full pipeline + server
pipeline.bat

:: Or run steps manually:
python pipeline\1_parse_exports.py
python pipeline\2_generate_embeddings.py
python pipeline\3_run_tsne.py
python pipeline\4_cluster.py
python serve.py
```

**Note:** The first run downloads a 1.6GB word2vec model to `~/gensim-data/`. HDBSCAN requires a C compiler - if `pip install` fails, use conda: `conda install -c conda-forge hdbscan`

The pipeline will:
1. Parse all JSON exports in `exports/`
2. Generate word2vec embeddings (~10 seconds per 100k messages)
3. Run t-SNE dimensionality reduction (~2-5 minutes for 100k messages)
4. Cluster messages using HDBSCAN
5. Start a local server and open the visualization

## Visualization Features

- **Pan**: Click and drag to move around
- **Zoom**: Scroll to zoom (unlimited)
- **Search**: Type in search box to filter messages
- **Hover**: Hover over dots to see message preview
- **Click**: Click a dot to open the message in Discord
- **Clusters**: Click cluster names to filter by topic
- **Cursor effect**: Lines connect cursor to nearby dots

## Project Structure

```
discord-data-viz/
  exports/                    # Drop DiscordChatExporter JSON files here
  output/                     # Generated files
    messages_raw.json         # Parsed messages from exports
    embeddings.npy            # 300-dim word2vec embeddings
    messages_with_coords.json # Messages with t-SNE x,y coordinates
    viz_data.json             # Final output with clusters
  frontend/
    index.html                # Visualization
  pipeline/
    1_parse_exports.py        # Parse DiscordChatExporter JSON
    2_generate_embeddings.py  # Generate word2vec embeddings
    3_run_tsne.py             # Reduce to 2D with t-SNE
    4_cluster.py              # HDBSCAN clustering + naming
  docker-compose.yml
  Dockerfile
  serve.py
```

## Performance Notes

- **Docker build**: First build takes ~2 minutes (compiles HDBSCAN with gcc)
- **First run**: Downloads 1.6GB word2vec model (cached in Docker volume)
- **Embeddings**: ~0.1ms per message (10k msg/sec)
- **t-SNE**: ~2-5 minutes for 100k messages (scales O(n^2))
- **Small datasets**: Works with as few as 100-500 messages (clustering auto-scales)
- **Browser**: Handles 100k+ points smoothly with off-screen culling

## Troubleshooting

### Out of Memory (t-SNE)

For very large datasets (>200k messages), edit `pipeline/3_run_tsne.py` to sample:
```python
import random
sample_indices = random.sample(range(len(embeddings)), 100000)
embeddings = embeddings[sample_indices]
messages = [messages[i] for i in sample_indices]
```

### "No JSON files found"

Make sure your export files are in the `exports/` directory and have `.json` extension.

### No clusters found / all messages "unclustered"

HDBSCAN is density-based clustering - it needs enough similar messages to form clusters. The algorithm auto-scales parameters based on dataset size (min 5% of messages per cluster).

For very small datasets (<200 messages), you may see few or no clusters. This is expected - try exporting more channels.

### HDBSCAN installation fails (non-Docker)

Docker handles this automatically. For local install, try conda:
```bash
conda install -c conda-forge hdbscan
```

## License

Public domain. Do whatever you want with it.
