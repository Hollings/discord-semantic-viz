# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Discord Data Viz is a semantic visualization tool that maps Discord messages in 2D space where semantically similar messages cluster together. It uses word2vec embeddings for semantic similarity and t-SNE for dimensionality reduction.

## Commands

**Run full pipeline + server (Docker):**
```bash
docker compose up
```

**Run individual pipeline steps:**
```bash
docker compose run --rm viz python pipeline/1_parse_exports.py
docker compose run --rm viz python pipeline/2_generate_embeddings.py
docker compose run --rm viz python pipeline/3_run_tsne.py
docker compose run --rm viz python pipeline/4_cluster.py
```

**Server only (after pipeline has run):**
```bash
docker compose --profile server up
```

**Rebuild after code changes:**
```bash
docker compose build --no-cache viz
```

**Local development (without Docker):**
```bash
pip install -r requirements.txt
python pipeline/1_parse_exports.py
python pipeline/2_generate_embeddings.py
python pipeline/3_run_tsne.py
python pipeline/4_cluster.py
python serve.py
```

## Architecture

### Pipeline Flow

```
exports/*.json → 1_parse_exports.py → messages_raw.json
                                           ↓
                     2_generate_embeddings.py → embeddings.npy + messages_with_embeddings.json
                                           ↓
                         3_run_tsne.py → messages_with_coords.json
                                           ↓
                         4_cluster.py → viz_data.json
                                           ↓
                         serve.py → frontend/index.html (browser)
```

### Data Format

Each pipeline step reads from the previous step's output in `output/`:

- **messages_raw.json**: Parsed messages with `id`, `channel`, `author`, `content`, `timestamp`, `guild_id`
- **embeddings.npy**: NumPy array of 300-dim word2vec embeddings
- **messages_with_coords.json**: Adds `x`, `y` coordinates from t-SNE
- **viz_data.json**: Adds `cluster` (int) and `cluster_name` (string) from HDBSCAN

### Input Format

Expects DiscordChatExporter JSON format in `exports/`. Key fields used:
- `guild.id`, `guild.name`
- `channel.id`, `channel.name`
- `messages[].id`, `messages[].type`, `messages[].content`, `messages[].timestamp`
- `messages[].author.name`, `messages[].author.nickname`, `messages[].author.isBot`

### Docker Services

- **viz** (default): Runs full pipeline then serves on port 8080
- **pipeline**: Runs pipeline only (no server)
- **server**: Serves only (reads existing output/)

The `gensim_data` volume caches the 1.6GB word2vec model between runs.

## Key Implementation Details

- Clustering parameters auto-scale based on dataset size: `min_cluster_size = max(5, min(50, n_messages // 20))`
- Cluster names are generated from top 3 most common non-stopwords
- Messages shorter than 20 chars and bot messages are filtered out
- Bot command prefixes (`!`, `$`, etc.) are stripped from content
