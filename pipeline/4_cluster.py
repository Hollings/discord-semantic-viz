#!/usr/bin/env python3
"""
Step 4: Cluster messages using HDBSCAN and generate cluster names
Requires: hdbscan, numpy
"""

import json
import numpy as np
from collections import Counter
import re
from pathlib import Path

try:
    import hdbscan
except ImportError:
    print("HDBSCAN not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'hdbscan'])
    import hdbscan

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
INPUT_FILE = OUTPUT_DIR / 'messages_with_coords.json'
OUTPUT_FILE = OUTPUT_DIR / 'viz_data.json'

# Common words to exclude from cluster naming
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
    'them', 'my', 'your', 'his', 'its', 'our', 'their', 'what', 'which',
    'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
    'now', 'here', 'there', 'then', 'if', 'because', 'while', 'although',
    'though', 'after', 'before', 'since', 'until', 'unless', 'about', 'into',
    'through', 'during', 'above', 'below', 'between', 'under', 'again',
    'further', 'once', 'dont', "don't", 'like', 'get', 'got', 'going',
    'know', 'think', 'want', 'need', 'make', 'made', 'way', 'thing', 'things',
    'yeah', 'yes', 'no', 'okay', 'ok', 'oh', 'well', 'really', 'actually',
    'pretty', 'much', 'even', 'still', 'back', 'out', 'up', 'down', 'over',
    'any', 'being', 'something', 'anything', 'nothing', 'everything',
    'someone', 'anyone', 'everyone', 'one', 'two', 'first', 'time', 'good',
    'new', 'used', 'man', 'work', 'look', 'see', 'come', 'say', 'said',
    'people', 'take', 'give', 'find', 'long', 'little', 'big', 'great',
    'old', 'right', 'high', 'small', 'different', 'large', 'next', 'early',
    'young', 'important', 'few', 'public', 'bad', 'same', 'able', 'im', "i'm"
}

def get_cluster_name(messages, n_words=3):
    """Generate a name for a cluster based on most common words"""
    word_counts = Counter()

    for msg in messages:
        # Extract words, lowercase, filter short words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', msg['content'].lower())
        # Filter stop words and count
        words = [w for w in words if w not in STOP_WORDS]
        word_counts.update(words)

    # Get top words
    top_words = [word for word, _ in word_counts.most_common(n_words)]

    if not top_words:
        return "misc"

    return ' '.join(top_words)

def main():
    print("Loading messages with coordinates...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"Loaded {len(messages)} messages")

    # Extract coordinates for clustering
    coords = np.array([[msg['x'], msg['y']] for msg in messages])

    # Scale parameters based on dataset size
    # Goal: catch small clusters (10-20 messages) while keeping max around 1% of data
    n_messages = len(messages)

    # Target ~200 clusters for 15-20k message datasets
    min_cluster_size = 15

    # min_samples controls how conservative clustering is
    min_samples = 7

    print(f"Running HDBSCAN clustering (min_cluster_size={min_cluster_size}, min_samples={min_samples})...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_method='leaf',  # More granular clusters
        # No epsilon - don't merge nearby clusters
    )
    labels = clusterer.fit_predict(coords)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"Found {n_clusters} clusters, {n_noise} noise points ({n_noise * 100 // n_messages}% unclustered)")

    # Check for oversized clusters (>10% of data) and warn
    max_cluster_size = n_messages // 10
    for label in set(labels):
        if label == -1:
            continue
        count = list(labels).count(label)
        if count > max_cluster_size:
            print(f"  Warning: Cluster {label} has {count} messages ({count * 100 // n_messages}% of data)")

    # Group messages by cluster
    cluster_messages = {}
    for i, label in enumerate(labels):
        if label not in cluster_messages:
            cluster_messages[label] = []
        cluster_messages[label].append(messages[i])

    # Generate cluster names
    print("Generating cluster names...")
    cluster_names = {}
    for label, msgs in cluster_messages.items():
        if label == -1:
            cluster_names[label] = "unclustered"
        else:
            cluster_names[label] = get_cluster_name(msgs)
            print(f"  Cluster {label} ({len(msgs)} msgs): {cluster_names[label]}")

    # Add cluster info to messages
    for i, msg in enumerate(messages):
        label = int(labels[i])
        msg['cluster'] = label
        msg['cluster_name'] = cluster_names[label]

    # Save final output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f)

    print(f"\nSaved {len(messages)} messages with cluster data to {OUTPUT_FILE}")

    # Print cluster summary
    print("\nCluster summary:")
    for label in sorted(cluster_messages.keys()):
        if label != -1:
            count = len(cluster_messages[label])
            print(f"  {cluster_names[label]}: {count:,} messages")

if __name__ == '__main__':
    main()
