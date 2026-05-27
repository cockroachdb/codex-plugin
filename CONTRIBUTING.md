# Contributing to CockroachDB Plugin for Codex

Thank you for your interest in contributing! This guide covers the plugin itself — hooks, MCP configuration, and tooling. For contributing **skills**, see the [cockroachdb-skills CONTRIBUTING.md](https://github.com/cockroachlabs/cockroachdb-skills/blob/main/CONTRIBUTING.md) instead; skills are maintained upstream and synced here automatically.

## Getting Started

### Prerequisites

- [Codex CLI](https://developers.openai.com/codex/cli/install) installed
- [MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox) v1.0.0+ (`brew install mcp-toolbox`)
- Python 3 (for hook scripts — no external dependencies)
- A running CockroachDB instance (local or cloud)

### Setup

```bash
git clone --recurse-submodules https://github.com/cockroachdb/codex-plugin.git
cd codex-plugin
```

Set your connection environment variables:

```bash
export COCKROACHDB_HOST=localhost
export COCKROACHDB_PORT=26257
export COCKROACHDB_USER=root
export COCKROACHDB_PASSWORD=
export COCKROACHDB_DATABASE=defaultdb
export COCKROACHDB_SSLMODE=disable
```

Test the plugin locally:

```bash
codex plugin marketplace add "$(pwd)"
codex plugin add cockroachdb@cockroachdb-codex-plugin
```

Validate that the marketplace install layout is correct:

```bash
REPO_URL="file://$(pwd)" ./scripts/validate-marketplace-install.sh HEAD
```

## Project Structure

```
.agents/plugins/
  marketplace.json         # Codex marketplace catalog entry
plugins/cockroachdb/       # Plugin payload (the directory Codex installs)
  .codex-plugin/
    plugin.json            # Plugin manifest (version managed by Release Please)
  .mcp.json                # MCP server definitions (stdio, HTTP, Cloud)
  tools.yaml               # MCP Toolbox source and tool definitions
  hooks.json               # Hook triggers and matchers (Codex auto-discovers at plugin root)
  scripts/
    validate-sql.py        # PreToolUse: blocks dangerous SQL patterns
    check-sql-files.py     # PostToolUse: lints files for anti-patterns
    setup-cockroachdb.sh   # Local 3-node cluster + Toolbox bootstrap
  assets/
    logo.svg               # Brand mark
  skills/                  # Synced from cockroachdb-skills submodule (do not edit directly)
scripts/                   # Repo-level tooling (not shipped with the plugin)
  sync-skills.sh           # Refresh plugins/cockroachdb/skills/ from submodule
  validate-marketplace-install.sh
submodules/
  cockroachdb-skills/      # Upstream skills submodule
```

## What You Can Contribute

| Area | Examples |
|------|----------|
| **Hooks** | New safety checks, additional SQL anti-pattern detection |
| **MCP config** | New backend integrations, connection improvements |
| **Tools** | New tool definitions in `tools.yaml` |
| **Bug fixes** | Path handling, env var defaults, config issues |
| **Documentation** | README improvements, inline comments |

### What belongs elsewhere

- **New skills** → [cockroachdb-skills](https://github.com/cockroachlabs/cockroachdb-skills) repo
- **Toolbox bugs** → [MCP Toolbox](https://github.com/googleapis/mcp-toolbox) repo
- **Codex CLI bugs** → [openai/codex](https://github.com/openai/codex) repo

## Development Workflow

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b fix/describe-your-change
   ```

2. **Make your changes** — match the existing code style and conventions.

3. **Test locally** — install the plugin from the local path: `codex plugin marketplace add "$(pwd)" && codex plugin add cockroachdb@cockroachdb-codex-plugin`. Verify your change works.

4. **Test hook scripts** (if modified):
   ```bash
   # validate-sql.py — expects JSON on stdin
   echo '{"tool_input":{"sql":"SELECT 1"}}' | python3 plugins/cockroachdb/scripts/validate-sql.py

   # check-sql-files.py — expects JSON on stdin
   echo '{"tool_input":{"file_path":"test.sql"}}' | python3 plugins/cockroachdb/scripts/check-sql-files.py
   ```

5. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "fix: quote PLUGIN_ROOT for paths with spaces"
   git commit -m "feat: add new hook to validate index definitions"
   git commit -m "docs: clarify Cloud MCP setup in README"
   ```

6. **Open a Pull Request** against `main`.

## Commit Conventions

This repo uses [Release Please](https://github.com/googleapis/release-please) for automated versioning and changelogs. Your commit prefix determines what happens:

| Prefix | Effect | Example |
|--------|--------|---------|
| `fix:` | Patch release (0.1.x) | `fix: handle empty SQL in validate hook` |
| `feat:` | Minor release (0.x.0) | `feat: add index validation hook` |
| `docs:` | No release | `docs: update README with new backend` |
| `chore:` | No release | `chore: update submodule reference` |

**Important:**
- Never bump the version in `plugin.json` or `.release-please-manifest.json` manually — Release Please owns these files.
- Use `fix:` or `feat:` only for changes that should appear in the changelog and trigger a release.

## Guidelines

### Hooks

- Hook scripts must be Python 3 with **no external dependencies** (stdlib only).
- Read JSON from stdin, write JSON to stdout.
- Exit code 0 = allow/continue; exit code 2 = block the tool call.
- Place `hooks.json` at the plugin root (`plugins/cockroachdb/hooks.json`). Codex discovers it by convention.
- Use paths relative to the plugin root in hook commands — Codex runs hook commands with the plugin directory as the working directory:
  ```json
  "command": "python3 ./scripts/your-script.py"
  ```

### MCP Configuration

- `.mcp.json` defines MCP server backends.
- Use `${ENV_VAR}` syntax for environment variable references.
- The `tools.yaml` file uses Toolbox v1.1.0 map-based format with `${VAR:default}` syntax for defaults.

### Skills

Skills are synced from the upstream [cockroachdb-skills](https://github.com/cockroachlabs/cockroachdb-skills) submodule into `plugins/cockroachdb/skills/` by a [weekly CI workflow](.github/workflows/update-skills.yml). Do not edit files in `plugins/cockroachdb/skills/` directly — changes will be overwritten. Contribute new skills to the upstream repo instead.

## Reporting Issues

- Use [GitHub Issues](https://github.com/cockroachdb/codex-plugin/issues) for bugs and feature requests.
- Include your plugin version (`plugin.json` → `version`), Codex version, and OS.
- For connection issues, include the MCP backend you're using (Toolbox, Cloud MCP, or ccloud).

## License

By contributing, you agree that your contributions will be licensed under the [Apache-2.0 License](LICENSE).
