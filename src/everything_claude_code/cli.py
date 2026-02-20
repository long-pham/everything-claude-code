"""CLI for everything-claude-code — replaces link_all.sh."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import click

LINK_DIRS = ("agents", "commands", "contexts", "plugins", "rules", "skills")

GH_TOKEN_PLACEHOLDER = "YOUR_GITHUB_PAT_HERE"
FS_PATH_PLACEHOLDER = "YOUR_FILESYSTEM_PATH_HERE"


def _find_package_root() -> Path:
    """Find the root of the everything-claude-code package data."""
    # Walk up from this file to find hooks/ directory (marks repo root)
    candidate = Path(__file__).resolve().parent.parent.parent
    if (candidate / "hooks").is_dir():
        return candidate
    msg = (
        f"Cannot auto-detect source directory (tried {candidate}). "
        "Pass --src explicitly."
    )
    raise click.ClickException(msg)


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay into base, returning a new dict."""
    merged = {**base}
    for key, value in overlay.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_json(path: Path) -> dict:
    """Read a JSON file, returning empty dict if missing or invalid."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    return json.loads(text)


def _write_json(path: Path, data: dict) -> None:
    """Write dict as pretty-printed JSON."""
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _backup(path: Path) -> Path | None:
    """Create a .bak copy of a file if it exists. Returns backup path."""
    if not path.is_file():
        return None
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    click.echo(f"  Backed up: {path} -> {bak}")
    return bak


def _gh_auth_token() -> str | None:
    """Get GitHub token from gh CLI, or None."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=False,
        )
        token = result.stdout.strip()
        return token if token else None
    except FileNotFoundError:
        return None


def _link_directories(src: Path, dest: Path) -> None:
    """Symlink config directories into ~/.claude/."""
    click.echo("=== Linking directories ===")
    for name in LINK_DIRS:
        src_path = src / name
        dest_path = dest / name
        if not src_path.is_dir():
            click.echo(f"  Warning: Source not found, skipping: {src_path}")
            continue

        if dest_path.is_symlink():
            click.echo(f"  Removing existing symlink: {dest_path}")
            dest_path.unlink()
        elif dest_path.is_dir():
            bak = dest_path.with_suffix(".bak")
            click.echo(f"  Backing up existing directory: {dest_path} -> {bak}")
            if bak.exists():
                shutil.rmtree(bak)
            dest_path.rename(bak)

        click.echo(f"  Linking: {src_path} -> {dest_path}")
        dest_path.symlink_to(src_path)


def _merge_hooks(src: Path, dest: Path) -> None:
    """Merge hooks.json into ~/.claude/settings.json."""
    hooks_src = src / "hooks" / "hooks.json"
    if not hooks_src.is_file():
        click.echo("  Skipping hooks merge — hooks/hooks.json not found")
        return

    click.echo("\n=== Merging hooks into settings.json ===")
    settings_path = dest / "settings.json"

    # Read hooks and resolve ${CLAUDE_PLUGIN_ROOT}
    hooks_text = hooks_src.read_text(encoding="utf-8")
    hooks_text = hooks_text.replace("${CLAUDE_PLUGIN_ROOT}", str(src))
    hooks_data = json.loads(hooks_text)

    # Read existing settings
    _backup(settings_path)
    existing = _read_json(settings_path)

    # Deep merge hooks into existing settings
    merged = _deep_merge(existing, hooks_data)
    _write_json(settings_path, merged)
    click.echo(f"  Merged hooks into: {settings_path}")


def _merge_mcp_servers(
    src: Path,
    claude_json_path: Path,
    *,
    fs_path: str | None,
    no_prompt: bool,
) -> None:
    """Merge mcp-servers.json into ~/.claude.json."""
    mcp_src = src / "mcp-configs" / "mcp-servers.json"
    if not mcp_src.is_file():
        click.echo("  Skipping MCP merge — mcp-configs/mcp-servers.json not found")
        return

    click.echo("\n=== Merging MCP servers into ~/.claude.json ===")
    mcp_data = _read_json(mcp_src)

    # Backup and read existing
    bak_path = _backup(claude_json_path)
    existing = _read_json(claude_json_path)

    # Deep merge mcpServers only (preserve other top-level keys)
    existing_servers = existing.get("mcpServers", {})
    new_servers = mcp_data.get("mcpServers", {})
    merged_servers = _deep_merge(existing_servers, new_servers)
    merged = {**existing, "mcpServers": merged_servers}

    _write_json(claude_json_path, merged)
    click.echo(f"  Merged MCP servers into: {claude_json_path}")

    click.echo(
        "\n  NOTE: Replace YOUR_*_HERE placeholders in "
        f"{claude_json_path} with actual values"
    )

    # Auto-fill GitHub token
    _auto_fill_gh_token(claude_json_path)

    # Handle filesystem path
    _handle_filesystem_path(
        claude_json_path,
        bak_path,
        fs_path=fs_path,
        no_prompt=no_prompt,
    )


def _auto_fill_gh_token(claude_json_path: Path) -> None:
    """Replace GitHub token placeholder with value from gh CLI."""
    raw_text = claude_json_path.read_text(encoding="utf-8")

    if GH_TOKEN_PLACEHOLDER not in raw_text:
        return

    token = _gh_auth_token()
    if token:
        updated = raw_text.replace(GH_TOKEN_PLACEHOLDER, token)
        claude_json_path.write_text(updated, encoding="utf-8")
        click.echo("  Auto-filled GITHUB_PERSONAL_ACCESS_TOKEN from gh CLI")
    else:
        click.echo("  TIP: Run 'gh auth login' to auto-fill GitHub token")


def _handle_filesystem_path(
    claude_json_path: Path,
    bak_path: Path | None,
    *,
    fs_path: str | None,
    no_prompt: bool,
) -> None:
    """Set filesystem MCP path — from flag, backup, or prompt."""
    # Check existing path from backup (merge may have overwritten it)
    existing_fs_path: str | None = None
    if bak_path and bak_path.is_file():
        bak_data = _read_json(bak_path)
        args = (
            bak_data.get("mcpServers", {}).get("filesystem", {}).get("args", [])
        )
        if args:
            existing_fs_path = args[-1]

    # If CLI flag provided, use it
    if fs_path:
        resolved = Path(fs_path).expanduser().resolve()
        if resolved.is_dir():
            _set_filesystem_path(claude_json_path, str(resolved))
            click.echo(f"  Set filesystem path to: {resolved}")
        else:
            click.echo(f"  Warning: Directory not found: {resolved} (skipping)")
        return

    # If backup had a valid existing path, restore it
    if (
        existing_fs_path
        and existing_fs_path != FS_PATH_PLACEHOLDER
        and Path(existing_fs_path).is_dir()
    ):
        _set_filesystem_path(claude_json_path, existing_fs_path)
        click.echo(f"  Filesystem MCP already configured: {existing_fs_path}")
        return

    # Warn about stale path
    if (
        existing_fs_path
        and existing_fs_path != FS_PATH_PLACEHOLDER
        and not Path(existing_fs_path).is_dir()
    ):
        click.echo(
            f"  Warning: Previously configured path no longer exists: "
            f"{existing_fs_path}"
        )

    # Non-interactive: skip prompt
    if no_prompt:
        click.echo("  Skipped filesystem path prompt (--no-prompt)")
        return

    # Interactive prompt
    click.echo("\n=== Filesystem MCP Setup ===")
    user_path = click.prompt(
        "Enter the directory path for filesystem MCP (or press Enter to skip)",
        default="",
        show_default=False,
    )
    if user_path:
        resolved = Path(user_path).expanduser().resolve()
        if resolved.is_dir():
            _set_filesystem_path(claude_json_path, str(resolved))
            click.echo(f"  Set filesystem path to: {resolved}")
        else:
            click.echo(f"  Warning: Directory not found: {resolved} (skipping)")
    else:
        click.echo("  Skipped — you can manually set it later in ~/.claude.json")


def _set_filesystem_path(claude_json_path: Path, path_value: str) -> None:
    """Update the filesystem MCP server's last arg in claude.json."""
    data = _read_json(claude_json_path)
    fs_config = data.get("mcpServers", {}).get("filesystem", {})
    args = fs_config.get("args", [])
    if args:
        args[-1] = path_value
    else:
        args.append(path_value)
    data.setdefault("mcpServers", {}).setdefault("filesystem", {})["args"] = args
    _write_json(claude_json_path, data)


@click.group()
def cli() -> None:
    """Everything Claude Code — battle-tested configs for Claude Code."""


@cli.command()
@click.option(
    "--src",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Source config directory (auto-detected if omitted).",
)
@click.option(
    "--dest",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path.home() / ".claude",
    show_default=True,
    help="Destination directory for symlinks.",
)
@click.option(
    "--claude-json",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path.home() / ".claude.json",
    show_default=True,
    help="Path to claude.json config.",
)
@click.option(
    "--fs-path",
    type=str,
    default=None,
    help="Filesystem MCP path (skips prompt).",
)
@click.option(
    "--no-prompt",
    is_flag=True,
    default=False,
    help="Non-interactive mode, skip all prompts.",
)
def link(
    src: Path | None,
    dest: Path,
    claude_json: Path,
    fs_path: str | None,
    no_prompt: bool,
) -> None:
    """Link configs into ~/.claude and merge hooks/MCP servers."""
    if src is None:
        src = _find_package_root()

    click.echo(f"Source: {src}")
    click.echo(f"Destination: {dest}")

    # Ensure dest exists
    dest.mkdir(parents=True, exist_ok=True)

    # 1. Symlink directories
    _link_directories(src, dest)

    # 2. Merge hooks
    _merge_hooks(src, dest)

    # 3. Merge MCP servers
    _merge_mcp_servers(src, claude_json, fs_path=fs_path, no_prompt=no_prompt)

    # 4. Show linked directories
    click.echo("\nDone! Linked directories:")
    for item in sorted(dest.iterdir()):
        if item.is_symlink():
            click.echo(f"  {item.name} -> {item.resolve()}")


if __name__ == "__main__":
    cli()
