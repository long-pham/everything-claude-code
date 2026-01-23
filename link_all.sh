
#!/bin/bash

# Setup script to symlink everything-claude-code configs to ~/.claude

# Get the directory where this script is located
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude"

# Check source exists
if [[ ! -d "$SRC" ]]; then
    echo "Error: Source directory not found: $SRC"
    exit 1
fi

# Create ~/.claude if it doesn't exist
mkdir -p "$DEST"

# Directories to link
DIRS=(agents commands contexts plugins rules skills)

for dir in "${DIRS[@]}"; do
    src_path="$SRC/$dir"
    dest_path="$DEST/$dir"
    
    if [[ -d "$src_path" ]]; then
        # Remove existing (backup if it's a real directory, not a link)
        if [[ -L "$dest_path" ]]; then
            echo "Removing existing symlink: $dest_path"
            rm "$dest_path"
        elif [[ -d "$dest_path" ]]; then
            echo "Backing up existing directory: $dest_path -> ${dest_path}.bak"
            mv "$dest_path" "${dest_path}.bak"
        fi
        
        echo "Linking: $src_path -> $dest_path"
        ln -s "$src_path" "$dest_path"
    else
        echo "Warning: Source not found, skipping: $src_path"
    fi
done

# Check for jq (required for JSON merging)
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required for JSON merging. Install with: brew install jq"
    exit 1
fi

# Merge hooks.json into settings.json
HOOKS_SRC="$SRC/hooks/hooks.json"
SETTINGS_DEST="$DEST/settings.json"

if [[ -f "$HOOKS_SRC" ]]; then
    echo ""
    echo "=== Merging hooks into settings.json ==="

    # Always backup first before any jq operations
    if [[ -f "$SETTINGS_DEST" ]]; then
        cp "$SETTINGS_DEST" "${SETTINGS_DEST}.bak"
        echo "Backed up: $SETTINGS_DEST -> ${SETTINGS_DEST}.bak"

        # Deep merge hooks from source into destination using temp file
        if jq -s '.[0] * .[1]' "$SETTINGS_DEST.bak" "$HOOKS_SRC" > "${SETTINGS_DEST}.tmp"; then
            mv "${SETTINGS_DEST}.tmp" "$SETTINGS_DEST"
            echo "Merged hooks into: $SETTINGS_DEST"
        else
            echo "Error: jq merge failed, restoring from backup"
            cp "${SETTINGS_DEST}.bak" "$SETTINGS_DEST"
            rm -f "${SETTINGS_DEST}.tmp"
        fi
    else
        # No existing settings, just copy hooks.json
        cp "$HOOKS_SRC" "$SETTINGS_DEST"
        echo "Created: $SETTINGS_DEST"
    fi
fi

# Merge mcp-servers.json into ~/.claude.json
MCP_SRC="$SRC/mcp-configs/mcp-servers.json"
CLAUDE_JSON="$HOME/.claude.json"

if [[ -f "$MCP_SRC" ]]; then
    echo ""
    echo "=== Merging MCP servers into ~/.claude.json ==="

    # Always backup first before any jq operations
    if [[ -f "$CLAUDE_JSON" ]]; then
        cp "$CLAUDE_JSON" "${CLAUDE_JSON}.bak"
        echo "Backed up: $CLAUDE_JSON -> ${CLAUDE_JSON}.bak"

        # Deep merge mcpServers (preserve existing, add new) using temp file
        if jq -s '.[0] * {mcpServers: ((.[0].mcpServers // {}) * (.[1].mcpServers // {}))}' \
            "$CLAUDE_JSON.bak" "$MCP_SRC" > "${CLAUDE_JSON}.tmp"; then
            mv "${CLAUDE_JSON}.tmp" "$CLAUDE_JSON"
            echo "Merged MCP servers into: $CLAUDE_JSON"
        else
            echo "Error: jq merge failed, restoring from backup"
            cp "${CLAUDE_JSON}.bak" "$CLAUDE_JSON"
            rm -f "${CLAUDE_JSON}.tmp"
        fi
    else
        # No existing config, create with just mcpServers
        jq '{mcpServers: .mcpServers}' "$MCP_SRC" > "$CLAUDE_JSON"
        echo "Created: $CLAUDE_JSON"
    fi
    echo ""
    echo "NOTE: Replace YOUR_*_HERE placeholders in ~/.claude.json with actual values"

    # Auto-replace GitHub token if gh CLI is authenticated
    if command -v gh &> /dev/null; then
        GH_TOKEN=$(gh auth token 2>/dev/null)
        if [[ -n "$GH_TOKEN" ]]; then
            if grep -q "YOUR_GITHUB_PAT_HERE" "$CLAUDE_JSON"; then
                sed -i.tmp "s/YOUR_GITHUB_PAT_HERE/$GH_TOKEN/" "$CLAUDE_JSON"
                rm -f "${CLAUDE_JSON}.tmp"
                echo "Auto-filled GITHUB_PERSONAL_ACCESS_TOKEN from gh CLI"
            fi
        else
            echo "TIP: Run 'gh auth login' to auto-fill GitHub token"
        fi
    fi

    # Prompt for Firecrawl API key if placeholder exists
    if grep -q "YOUR_FIRECRAWL_KEY_HERE" "$CLAUDE_JSON"; then
        echo ""
        echo "=== Firecrawl API Key Setup ==="
        echo "Opening https://firecrawl.dev to get your API key..."
        open "https://www.firecrawl.dev/app/api-keys" 2>/dev/null || xdg-open "https://www.firecrawl.dev/app/api-keys" 2>/dev/null || true
        echo ""
        read -p "Paste your Firecrawl API key (or press Enter to skip): " FIRECRAWL_KEY
        if [[ -n "$FIRECRAWL_KEY" ]]; then
            sed -i.tmp "s/YOUR_FIRECRAWL_KEY_HERE/$FIRECRAWL_KEY/" "$CLAUDE_JSON"
            rm -f "${CLAUDE_JSON}.tmp"
            echo "Saved Firecrawl API key"
        else
            echo "Skipped - you can manually add it later to ~/.claude.json"
        fi
    fi
fi

echo ""
echo "Done! Linked directories:"
ls -la "$DEST" | grep "^l"

