#!/usr/bin/env python3
"""
Step 3: Run t-SNE dimensionality reduction
Requires: scikit-learn, numpy
"""

import json
import numpy as np
from sklearn.manifold import TSNE
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
INPUT_EMBEDDINGS = OUTPUT_DIR / 'embeddings.npy'
INPUT_MESSAGES = OUTPUT_DIR / 'messages_with_embeddings.json'
OUTPUT_FILE = OUTPUT_DIR / 'messages_with_coords.json'

def main():
    print("Loading embeddings...")
    embeddings = np.load(INPUT_EMBEDDINGS)
    print(f"Loaded {embeddings.shape[0]} embeddings with {embeddings.shape[1]} dimensions")

    with open(INPUT_MESSAGES, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print("Running t-SNE dimensionality reduction...")
    print("  This will take 2-5 minutes for 100k messages...")
    start = time.time()

    tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
    coords_2d = tsne.fit_transform(embeddings)

    elapsed = time.time() - start
    print(f"t-SNE completed in {elapsed:.2f}s")

    # Add coordinates to messages
    for i, msg in enumerate(messages):
        msg['x'] = float(coords_2d[i, 0])
        msg['y'] = float(coords_2d[i, 1])

    # Save processed data
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2)

    print(f"Saved {len(messages)} messages with 2D coordinates")
    print(f"X range: [{coords_2d[:, 0].min():.2f}, {coords_2d[:, 0].max():.2f}]")
    print(f"Y range: [{coords_2d[:, 1].min():.2f}, {coords_2d[:, 1].max():.2f}]")

if __name__ == '__main__':
    main()
