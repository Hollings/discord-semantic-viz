#!/usr/bin/env python3
"""
Step 1: Parse DiscordChatExporter JSON files
Reads all JSON exports from exports/ directory and extracts messages
"""

import json
import re
import os
from glob import glob
from pathlib import Path

EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'
MIN_LENGTH = 20

def parse_export_file(filepath):
    """Parse a single DiscordChatExporter JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    guild = data.get('guild', {})
    channel = data.get('channel', {})
    raw_messages = data.get('messages', [])

    messages = []
    for msg in raw_messages:
        # Skip non-default messages (joins, pins, etc.)
        if msg.get('type') != 'Default':
            continue

        content = msg.get('content', '')

        # Skip short messages
        if len(content) < MIN_LENGTH:
            continue

        # Skip bot messages
        author = msg.get('author', {})
        if author.get('isBot', False):
            continue

        # Strip bot command prefixes
        content = re.sub(r'^[!#$@%^&*]+\s*', '', content)

        # Use nickname if available, else name
        author_name = author.get('nickname') or author.get('name', 'Unknown')

        messages.append({
            'id': msg.get('id'),
            'channel': channel.get('id'),
            'channel_name': channel.get('name', 'unknown'),
            'guild_id': guild.get('id'),
            'guild_name': guild.get('name', 'Unknown Server'),
            'author': author_name,
            'content': content,
            'timestamp': msg.get('timestamp')
        })

    return messages, {
        'guild_id': guild.get('id'),
        'guild_name': guild.get('name'),
        'channel_id': channel.get('id'),
        'channel_name': channel.get('name'),
        'category': channel.get('category')
    }

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all JSON files in exports directory
    export_files = list(EXPORTS_DIR.glob('*.json'))

    if not export_files:
        print(f"No JSON files found in {EXPORTS_DIR}")
        print("Please export your Discord channels using DiscordChatExporter:")
        print("  DiscordChatExporter.Cli export -t TOKEN -c CHANNEL_ID -f Json -o exports/")
        return

    print(f"Found {len(export_files)} export file(s)")

    all_messages = []
    channels = {}
    seen_ids = set()
    guild_info = {}

    for filepath in export_files:
        print(f"  Parsing {filepath.name}...")
        try:
            messages, channel_meta = parse_export_file(filepath)

            # Store guild info (use first one found)
            if not guild_info and channel_meta.get('guild_id'):
                guild_info = {
                    'id': channel_meta['guild_id'],
                    'name': channel_meta['guild_name']
                }

            # Deduplicate by message ID
            new_messages = []
            for msg in messages:
                if msg['id'] not in seen_ids:
                    seen_ids.add(msg['id'])
                    new_messages.append(msg)

            all_messages.extend(new_messages)

            # Track channel metadata
            channel_id = channel_meta['channel_id']
            if channel_id not in channels:
                channels[channel_id] = {
                    'name': channel_meta['channel_name'],
                    'category': channel_meta['category'],
                    'count': 0
                }
            channels[channel_id]['count'] += len(new_messages)

            print(f"    {len(new_messages)} messages extracted")

        except Exception as e:
            print(f"    Error parsing {filepath.name}: {e}")

    print(f"\nTotal: {len(all_messages)} unique messages")

    # Print channel distribution
    print("\nChannel distribution:")
    for channel_id, info in sorted(channels.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"  {info['name']}: {info['count']:,} messages")

    # Save messages
    output_file = OUTPUT_DIR / 'messages_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, indent=2)
    print(f"\nSaved {len(all_messages)} messages to {output_file}")

    # Save channel metadata
    channels_file = OUTPUT_DIR / 'channels.json'
    with open(channels_file, 'w', encoding='utf-8') as f:
        json.dump(channels, f, indent=2)
    print(f"Saved channel metadata to {channels_file}")

    # Save guild info for frontend
    guild_file = OUTPUT_DIR / 'guild.json'
    with open(guild_file, 'w', encoding='utf-8') as f:
        json.dump(guild_info, f, indent=2)
    print(f"Saved guild info to {guild_file}")

if __name__ == '__main__':
    main()
