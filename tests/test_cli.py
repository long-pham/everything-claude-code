"""Tests for everything_claude_code.cli — regression suite."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from everything_claude_code.cli import (
    _deep_merge,
    _find_package_root,
    _read_json,
    _set_filesystem_path,
    _write_json,
    cli,
)


# ---------------------------------------------------------------------------
# _deep_merge
# ---------------------------------------------------------------------------


class TestDeepMerge:
    def test_flat_merge(self) -> None:
        base = {"a": 1, "b": 2}
        overlay = {"b": 3, "c": 4}
        result = _deep_merge(base, overlay)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self) -> None:
        base = {"hooks": {"PreToolUse": [1], "Stop": [2]}}
        overlay = {"hooks": {"PreToolUse": [3], "New": [4]}}
        result = _deep_merge(base, overlay)
        # Lists are replaced, not appended (matches jq * behavior)
        assert result == {"hooks": {"PreToolUse": [3], "Stop": [2], "New": [4]}}

    def test_does_not_mutate_base(self) -> None:
        base = {"a": {"b": 1}}
        overlay = {"a": {"c": 2}}
        _deep_merge(base, overlay)
        assert base == {"a": {"b": 1}}

    def test_empty_overlay(self) -> None:
        base = {"a": 1}
        assert _deep_merge(base, {}) == {"a": 1}

    def test_empty_base(self) -> None:
        overlay = {"a": 1}
        assert _deep_merge({}, overlay) == {"a": 1}

    def test_overlay_replaces_non_dict_with_dict(self) -> None:
        base = {"a": "string"}
        overlay = {"a": {"nested": True}}
        assert _deep_merge(base, overlay) == {"a": {"nested": True}}


# ---------------------------------------------------------------------------
# _read_json / _write_json
# ---------------------------------------------------------------------------


class TestJsonIO:
    def test_read_missing_file(self, tmp_path: Path) -> None:
        assert _read_json(tmp_path / "nope.json") == {}

    def test_read_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.json"
        f.write_text("")
        assert _read_json(f) == {}

    def test_roundtrip(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        data = {"key": [1, 2, 3], "nested": {"a": True}}
        _write_json(f, data)
        assert _read_json(f) == data

    def test_write_creates_trailing_newline(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        _write_json(f, {"x": 1})
        assert f.read_text().endswith("\n")


# ---------------------------------------------------------------------------
# _set_filesystem_path
# ---------------------------------------------------------------------------


class TestSetFilesystemPath:
    def test_replaces_last_arg(self, tmp_path: Path) -> None:
        f = tmp_path / "claude.json"
        _write_json(f, {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@mcp/server-filesystem", "PLACEHOLDER"],
                }
            }
        })
        _set_filesystem_path(f, "/home/user/code")
        data = _read_json(f)
        assert data["mcpServers"]["filesystem"]["args"][-1] == "/home/user/code"

    def test_appends_if_args_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "claude.json"
        _write_json(f, {"mcpServers": {"filesystem": {"args": []}}})
        _set_filesystem_path(f, "/tmp")
        data = _read_json(f)
        assert data["mcpServers"]["filesystem"]["args"] == ["/tmp"]

    def test_creates_structure_if_missing(self, tmp_path: Path) -> None:
        f = tmp_path / "claude.json"
        _write_json(f, {})
        _set_filesystem_path(f, "/tmp")
        data = _read_json(f)
        assert data["mcpServers"]["filesystem"]["args"] == ["/tmp"]


# ---------------------------------------------------------------------------
# _find_package_root
# ---------------------------------------------------------------------------


class TestFindPackageRoot:
    def test_finds_repo_root(self) -> None:
        root = _find_package_root()
        assert (root / "hooks").is_dir()
        assert (root / "link_all.sh").is_file()


# ---------------------------------------------------------------------------
# Fixtures for link command integration tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """Create a minimal fake source repo structure."""
    src = tmp_path / "repo"
    src.mkdir()
    for d in ("agents", "commands", "contexts", "plugins", "rules", "skills"):
        (src / d).mkdir()
        (src / d / "test.md").write_text(f"# {d}")

    # hooks/hooks.json with a placeholder
    hooks_dir = src / "hooks"
    hooks_dir.mkdir()
    hooks_data = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": 'node "${CLAUDE_PLUGIN_ROOT}/scripts/test.js"',
                        }
                    ],
                }
            ]
        }
    }
    (hooks_dir / "hooks.json").write_text(json.dumps(hooks_data))

    # mcp-configs/mcp-servers.json
    mcp_dir = src / "mcp-configs"
    mcp_dir.mkdir()
    mcp_data = {
        "mcpServers": {
            "github": {
                "command": "npx",
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT_HERE"},
            },
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@mcp/server-filesystem", "YOUR_FILESYSTEM_PATH_HERE"],
            },
        }
    }
    (mcp_dir / "mcp-servers.json").write_text(json.dumps(mcp_data))

    return src


# ---------------------------------------------------------------------------
# link command — full integration
# ---------------------------------------------------------------------------


class TestLinkCommand:
    def test_creates_symlinks(self, fake_repo: Path, tmp_path: Path) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output

        for name in ("agents", "commands", "contexts", "plugins", "rules", "skills"):
            link = dest / name
            assert link.is_symlink()
            assert link.resolve() == (fake_repo / name).resolve()

    def test_replaces_existing_symlink(self, fake_repo: Path, tmp_path: Path) -> None:
        dest = tmp_path / "dest"
        dest.mkdir()
        # Pre-existing symlink pointing elsewhere
        old_target = tmp_path / "old_agents"
        old_target.mkdir()
        (dest / "agents").symlink_to(old_target)

        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        assert (dest / "agents").resolve() == (fake_repo / "agents").resolve()

    def test_backs_up_real_directory(self, fake_repo: Path, tmp_path: Path) -> None:
        dest = tmp_path / "dest"
        dest.mkdir()
        real_dir = dest / "agents"
        real_dir.mkdir()
        (real_dir / "existing.md").write_text("keep me")

        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        # Original should be a symlink now
        assert (dest / "agents").is_symlink()
        # Backup should exist
        bak = dest / "agents.bak"
        assert bak.is_dir()
        assert (bak / "existing.md").read_text() == "keep me"

    def test_resolves_plugin_root_placeholder(
        self, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        settings = json.loads((dest / "settings.json").read_text())
        cmd = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert "${CLAUDE_PLUGIN_ROOT}" not in cmd
        assert str(fake_repo) in cmd

    def test_merges_hooks_into_existing_settings(
        self, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        dest.mkdir()
        # Pre-existing settings with a custom key
        existing = {"customKey": "preserved", "hooks": {"Stop": [{"old": True}]}}
        (dest / "settings.json").write_text(json.dumps(existing))

        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        settings = json.loads((dest / "settings.json").read_text())
        assert settings["customKey"] == "preserved"
        assert "PreToolUse" in settings["hooks"]

    def test_merges_mcp_servers_preserving_existing(
        self, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        # Pre-existing claude.json with a custom server
        existing = {
            "topLevel": "kept",
            "mcpServers": {
                "custom": {"command": "my-server"},
            },
        }
        cj.write_text(json.dumps(existing))

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(cj.read_text())
        assert data["topLevel"] == "kept"
        assert "custom" in data["mcpServers"]
        assert "github" in data["mcpServers"]

    @patch("everything_claude_code.cli._gh_auth_token", return_value="ghp_test123")
    def test_auto_fills_github_token(
        self, _mock_gh: object, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(cj.read_text())
        token = data["mcpServers"]["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"]
        assert token == "ghp_test123"
        assert "YOUR_GITHUB_PAT_HERE" not in cj.read_text()

    def test_fs_path_flag(self, fake_repo: Path, tmp_path: Path) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        fs_dir = tmp_path / "mycode"
        fs_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--fs-path", str(fs_dir), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(cj.read_text())
        assert data["mcpServers"]["filesystem"]["args"][-1] == str(fs_dir)

    def test_preserves_existing_fs_path_from_backup(
        self, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        fs_dir = tmp_path / "existing_code"
        fs_dir.mkdir()

        # Pre-existing claude.json with valid filesystem path
        existing = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@mcp/server-filesystem", str(fs_dir)],
                }
            }
        }
        cj.write_text(json.dumps(existing))

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(cj.read_text())
        # Should restore the existing valid path, not the placeholder
        assert data["mcpServers"]["filesystem"]["args"][-1] == str(fs_dir)

    def test_no_prompt_skips_interactive(
        self, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        assert "Skipped filesystem path prompt" in result.output

    def test_creates_backup_of_settings(
        self, fake_repo: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "dest"
        dest.mkdir()
        orig = {"existing": True}
        (dest / "settings.json").write_text(json.dumps(orig))

        cj = tmp_path / "claude.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["link", "--src", str(fake_repo), "--dest", str(dest),
             "--claude-json", str(cj), "--no-prompt"],
        )
        assert result.exit_code == 0, result.output
        bak = dest / "settings.json.bak"
        assert bak.is_file()
        assert json.loads(bak.read_text()) == orig
