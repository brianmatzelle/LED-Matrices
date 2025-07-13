#!/bin/bash

SOURCE_DIR="$HOME/projects/active/led-matrices/mets/embedded"
TARGET_DIR="/Volumes/CIRCUITPY"

# Function to sync a single file
sync_file() {
    local file="$1"
    local rel_path="${file#$SOURCE_DIR/}"
    local target_file="$TARGET_DIR/$rel_path"
    
    # Skip hidden files and temp files
    if [[ $(basename "$file") == .* ]] || [[ $(basename "$file") == *.tmp ]]; then
        return
    elif [[ $(basename "$file") == "sync_to_circuitpy.sh" ]]; then
        return
    fi
    
    # Create target directory if needed
    mkdir -p "$(dirname "$target_file")"
    
    # Copy file
    if cp "$file" "$target_file"; then
        echo "Synced: $rel_path"
    else
        echo "Error syncing: $rel_path"
    fi
}

# Initial sync
echo "Performing initial sync..."
find "$SOURCE_DIR" -type f ! -name ".*" ! -name "*.tmp" | while read -r file; do
    sync_file "$file"
done

echo "Watching $SOURCE_DIR for changes..."
echo "Press Ctrl+C to stop"

# Watch for changes
fswatch -r "$SOURCE_DIR" | while read -r file; do
    if [[ -f "$file" ]]; then
        sync_file "$file"
    fi
done