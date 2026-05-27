# CockroachDB Codex Plugin

Official CockroachDB plugin for [OpenAI Codex CLI](https://developers.openai.com/codex/). Connect Codex directly to your CockroachDB clusters — explore schemas, write optimized SQL, debug queries, and manage distributed database clusters.

> Using **Claude Code** instead? See [cockroachdb/claude-plugin](https://github.com/cockroachdb/claude-plugin).

## What's inside

- **3 MCP backends:**
  - `cockroachdb-toolbox` (stdio, default) — self-hosted [MCP Toolbox](https://mcp-toolbox.dev/integrations/cockroachdb/source/) for any cluster (self-hosted, local dev, or Cloud).
  - `cockroachdb-toolbox-http` (SSE) — remote/multi-user Toolbox over HTTP.
  - `cockroachdb-cloud` (HTTP) — managed CockroachDB Cloud MCP for Cloud clusters.
- **Skills** sourced from [`cockroachlabs/cockroachdb-skills`](https://github.com/cockroachlabs/cockroachdb-skills) — covers query/schema design, observability, security, migrations (MOLT), and cluster lifecycle.
- **Safety hooks:**
  - `validate-sql.py` (PreToolUse) — blocks `DROP DATABASE`/`TRUNCATE`, warns on `SERIAL`/multi-DDL.
  - `check-sql-files.py` (PostToolUse) — lints SQL/Go/Java/Python/Ruby/JS/TS files for CockroachDB anti-patterns.

## Install

### Prerequisites

- [Codex CLI](https://developers.openai.com/codex/cli/install) installed.
- [MCP Toolbox](https://mcp-toolbox.dev/install/) installed (for the default backend): `brew install googleapis/tap/mcp-toolbox`.
- Access to a CockroachDB cluster, or run `plugins/cockroachdb/scripts/setup-cockroachdb.sh` to spin up a local single-node cluster.

### Add the marketplace and install

```bash
codex plugin marketplace add cockroachdb/codex-plugin
codex plugin add cockroachdb@cockroachdb-codex-plugin
```

The marketplace source accepts `owner/repo`, an HTTPS Git URL, an SSH Git URL, or a local path. After `codex plugin marketplace add`, the marketplace is registered as `cockroachdb-codex-plugin` (the `name` field from `.agents/plugins/marketplace.json`).

### Trust the safety hooks

Codex does not auto-trust plugin-bundled hooks. On first run, Codex will prompt you to review and approve:

- The PreToolUse hook on `mcp__cockroachdb-toolbox__cockroachdb-execute-sql`.
- The PostToolUse hook on `Write|Edit|MultiEdit`.

Both run small Python scripts in `plugins/cockroachdb/scripts/` — review and approve to enable the safety checks.

### Configure environment variables

For the `cockroachdb-toolbox` (stdio) backend:

```bash
export COCKROACHDB_HOST=localhost
export COCKROACHDB_PORT=26257
export COCKROACHDB_USER=root
export COCKROACHDB_PASSWORD=
export COCKROACHDB_DATABASE=defaultdb
export COCKROACHDB_SSLMODE=disable   # local dev only; use 'require' or 'verify-full' otherwise
```

For the `cockroachdb-cloud` backend:

```bash
export COCKROACHDB_CLUSTER_ID=<your-cloud-cluster-id>
```

## Usage

Once installed, Codex auto-discovers the MCP tools. Try:

- "List schemas in the connected CockroachDB database."
- "Show me the tables in the public schema with their column types."
- "Run `SELECT COUNT(*) FROM rides` and explain the query plan."

The plugin's skills will be auto-loaded by Codex based on task context.

## Backends

| Backend | Transport | Use case |
|---|---|---|
| `cockroachdb-toolbox` | stdio | Default. Works against any cluster. Read-only by default; enable writes via `tools.yaml`. |
| `cockroachdb-toolbox-http` | HTTP/SSE | Remote/multi-user Toolbox deployments. Run `toolbox --config tools.yaml` separately. |
| `cockroachdb-cloud` | HTTP | Managed CockroachDB Cloud MCP. Requires `COCKROACHDB_CLUSTER_ID`. |

Enable/disable per-backend via Codex's MCP toggle UI.

## Troubleshooting

**`toolbox: command not found`** — install MCP Toolbox: `brew install googleapis/tap/mcp-toolbox`.

**Hooks didn't run** — check Codex's hook trust review screen (`codex plugin trust cockroachdb`).

**Skills not appearing** — verify the installed plugin cache contains skills: `find ~/.codex/plugins/cache/cockroachdb-codex-plugin/cockroachdb/*/skills -name SKILL.md | wc -l` (expect 33).

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Skills are sourced from [`cockroachlabs/cockroachdb-skills`](https://github.com/cockroachlabs/cockroachdb-skills) — open skill PRs there, not in this repo.

## License

Apache-2.0. See [`LICENSE`](./LICENSE).
