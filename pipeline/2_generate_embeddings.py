#!/usr/bin/env python3
"""
Step 2: Generate word2vec embeddings for all messages
Requires: gensim, numpy

Downloads the word2vec-google-news-300 model (1.6GB) on first run.
"""

import json
import numpy as np
import gensim.downloader as api
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
INPUT_FILE = OUTPUT_DIR / 'messages_raw.json'
OUTPUT_EMBEDDINGS = OUTPUT_DIR / 'embeddings.npy'
OUTPUT_MESSAGES = OUTPUT_DIR / 'messages_with_embeddings.json'

def get_message_embedding(text, model):
    """Generate embedding by averaging word vectors"""
    words = text.lower().split()
    vecs = [model[word] for word in words if word in model]
    if not vecs:
        return None
    return np.mean(vecs, axis=0)

def main():
    print("Loading word2vec model (this will download 1.6GB on first run)...")
    model = api.load('word2vec-google-news-300')

    # Load messages
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"Processing {len(messages)} messages...")
    embeddings = []
    valid_messages = []

    start = time.time()
    for i, msg in enumerate(messages):
        emb = get_message_embedding(msg['content'], model)
        if emb is not None:
            embeddings.append(emb)
            valid_messages.append(msg)

        if (i+1) % 10000 == 0:
            elapsed = time.time() - start
            rate = (i+1) / elapsed
            remaining = (len(messages) - i - 1) / rate
            print(f"  {i+1}/{len(messages)} processed... ({rate:.0f}/sec, ~{remaining:.0f}s remaining)")

    total_time = time.time() - start
    print(f"\nGenerated {len(embeddings)} embeddings in {total_time:.2f}s ({len(embeddings)/total_time:.0f} msg/sec)")

    # Save embeddings
    print("Saving embeddings...")
    np.save(OUTPUT_EMBEDDINGS, np.array(embeddings))

    with open(OUTPUT_MESSAGES, 'w', encoding='utf-8') as f:
        json.dump(valid_messages, f, indent=2)

    print(f"Saved {len(valid_messages)} messages with embeddings")
    print(f"Embeddings shape: {np.array(embeddings).shape}")

if __name__ == '__main__':
    main()
