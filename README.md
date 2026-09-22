# CockroachDB Codex Plugin

CockroachDB plugin for [OpenAI Codex CLI](https://developers.openai.com/codex/). Connect Codex directly to your CockroachDB clusters — explore schemas, write optimized SQL, debug queries, and manage distributed database clusters. Ships an MCP Toolbox backend for any cluster (self-hosted, local, or Cloud) plus the managed CockroachDB Cloud MCP, skills across multiple operational domains, and built-in safety hooks.

> Using **Claude Code** instead? See [cockroachdb/claude-plugin](https://github.com/cockroachdb/claude-plugin).

## What's inside

- **3 MCP backends:**
  - `cockroachdb-cloud` (HTTP) — managed CockroachDB Cloud MCP for Cloud clusters. Zero local install.
  - `cockroachdb-toolbox` (stdio) — self-hosted [MCP Toolbox](https://mcp-toolbox.dev/integrations/cockroachdb/source/) for any cluster (local dev, self-hosted, or Cloud). Codex spawns the Toolbox process.
  - `cockroachdb-toolbox-http` (SSE) — remote/multi-user Toolbox over HTTP.
- **Skills** sourced from [`cockroachlabs/cockroachdb-skills`](https://github.com/cockroachlabs/cockroachdb-skills) — covers query/schema design, observability, security, migrations (MOLT), and cluster lifecycle.
- **Safety hooks** (ship as `hooks.json` + `scripts/`; activation depends on the Codex runtime version):
  - `validate-sql.py` (PreToolUse) — blocks `DROP DATABASE`/`TRUNCATE`, warns on `SERIAL`/multi-DDL.
  - `check-sql-files.py` (PostToolUse) — lints SQL/Go/Java/Python/Ruby/JS/TS files for CockroachDB anti-patterns.

## Install

### Prerequisites

- [Codex CLI](https://developers.openai.com/codex/cli/install) installed.
- [MCP Toolbox](https://mcp-toolbox.dev/documentation/introduction/#install-toolbox) installed (only needed for the Toolbox backends; supports Homebrew, binary download, or container).
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

For the `cockroachdb-cloud` backend:

```bash
export COCKROACHDB_CLUSTER_ID=<your-cloud-cluster-id>
```

For the `cockroachdb-toolbox` (stdio) backend:

```bash
export COCKROACHDB_HOST=localhost
export COCKROACHDB_PORT=26257
export COCKROACHDB_USER=root
export COCKROACHDB_PASSWORD=
export COCKROACHDB_DATABASE=defaultdb
export COCKROACHDB_SSLMODE=disable   # local dev only; use 'require' or 'verify-full' otherwise
```

Codex starts this backend from the installed plugin root, loads the bundled
`./tools.yaml`, and forwards these variables to Toolbox. No manual MCP
registration or path into the plugin cache is needed.

## Usage

Once installed, Codex auto-discovers the MCP tools. Try:

- "List schemas in the connected CockroachDB database."
- "Show me the tables in the public schema with their column types."
- "Run `SELECT COUNT(*) FROM rides` and explain the query plan."

The plugin's skills will be auto-loaded by Codex based on task context.

## Backends

| Backend | Transport | Use case |
|---|---|---|
| `cockroachdb-cloud` | HTTP | Managed CockroachDB Cloud MCP. Requires `COCKROACHDB_CLUSTER_ID`. Zero local install. |
| `cockroachdb-toolbox` | stdio | Self-hosted Toolbox against any cluster (local dev, self-hosted, or Cloud). Codex spawns the process. Read-only by default; enable writes via `tools.yaml`. |
| `cockroachdb-toolbox-http` | HTTP/SSE | Remote/multi-user Toolbox deployments. Client-only; start Toolbox separately. |

Enable/disable per-backend via Codex's MCP toggle UI.

The `cockroachdb-toolbox-http` entry only connects to
`http://127.0.0.1:5000/mcp`; it does not start a server. Before enabling it,
start Toolbox independently from a directory containing your Toolbox config:

```bash
toolbox --config tools.yaml
```

## Troubleshooting

**`toolbox: command not found`** — install [MCP Toolbox](https://mcp-toolbox.dev/documentation/introduction/#install-toolbox) (Homebrew, binary download, or container image).

**Hooks didn't run** — check Codex's hook trust review screen (`codex plugin trust cockroachdb`).

**Skills not appearing** — verify the installed plugin cache contains skills: `find ~/.codex/plugins/cache/cockroachdb-codex-plugin/cockroachdb/*/skills -name SKILL.md | wc -l`.

**Toolbox uses an unexpected config path** — check `codex mcp list` for a
manually registered `cockroachdb-toolbox` server. A user-level server with the
same name can shadow the plugin-provided server. The plugin itself uses its
installed, bundled `tools.yaml`; it does not require an absolute checkout or
versioned cache path.

**`SSL error: certificate verify failed` or `node is running secure mode, SSL connection required`** — your cluster runs in secure mode. Set:

```bash
export COCKROACHDB_SSLMODE=verify-full   # or 'require' for less strict
export COCKROACHDB_SSLROOTCERT=/path/to/ca.crt
export COCKROACHDB_SSLCERT=/path/to/client.<user>.crt
export COCKROACHDB_SSLKEY=/path/to/client.<user>.key
```

Then extend `tools.yaml` `queryParams:` block with `sslrootcert: ${COCKROACHDB_SSLROOTCERT}`, `sslcert: ${COCKROACHDB_SSLCERT}`, `sslkey: ${COCKROACHDB_SSLKEY}`.

For a quick local dev cluster, start one in insecure mode: `cockroach start-single-node --insecure --listen-addr=localhost:26257 &` and use `COCKROACHDB_SSLMODE=disable`.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Skills are sourced from [`cockroachlabs/cockroachdb-skills`](https://github.com/cockroachlabs/cockroachdb-skills) — open skill PRs there, not in this repo.


## License

Apache-2.0. See [`LICENSE`](./LICENSE).
