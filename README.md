# CockroachDB Codex Plugin

CockroachDB plugin for [OpenAI Codex CLI](https://developers.openai.com/codex/). Connect Codex directly to your CockroachDB clusters — explore schemas, write optimized SQL, debug queries, and manage distributed database clusters. Ships an MCP Toolbox backend for any cluster (self-hosted, local, or Cloud) plus the managed CockroachDB Cloud MCP, skills across multiple operational domains, and built-in safety hooks.

> Using **Claude Code** instead? See [cockroachdb/claude-plugin](https://github.com/cockroachdb/claude-plugin).

## What's inside

- **MCP backends:**
  - `cockroachdb-cloud` (HTTP) — managed CockroachDB Cloud MCP for Cloud clusters. Zero local install.
  - `cockroachdb-toolbox` (stdio) — self-hosted [MCP Toolbox](https://mcp-toolbox.dev/integrations/cockroachdb/source/) for any cluster (local dev, self-hosted, or Cloud). Codex spawns the Toolbox process.
- **Skills** sourced from [`cockroachlabs/cockroachdb-skills`](https://github.com/cockroachlabs/cockroachdb-skills) — covers query/schema design, observability, security, migrations (MOLT), and cluster lifecycle.
- **Safety hooks** (`hooks/hooks.json` + `scripts/`), which run once you trust them in `/hooks`:
  - `validate-sql.py` (PreToolUse) — blocks `DROP DATABASE`/`TRUNCATE`, warns on `SERIAL`/multi-DDL.
  - `check-sql-files.py` (PostToolUse) — lints SQL/Go/Java/Python/Ruby/JS/TS files for CockroachDB anti-patterns.

## Install

### Prerequisites

- [Codex CLI](https://developers.openai.com/codex/cli/install) installed.
- [MCP Toolbox](https://mcp-toolbox.dev/documentation/introduction/#install-toolbox) v1.0.0 or later on your `PATH`, for the `cockroachdb-toolbox` backend. Use `brew install mcp-toolbox` on macOS or Linux. On Windows, download `toolbox.exe` into a folder on your `PATH` as described in the [Toolbox install instructions](https://github.com/googleapis/mcp-toolbox#install-toolbox).
- A running CockroachDB cluster for the `cockroachdb-toolbox` backend, or run `plugins/cockroachdb/scripts/setup-cockroachdb.sh` to spin up a local single-node cluster. Toolbox connects when Codex starts it, so without a reachable cluster the backend fails to start. If you don't run a cluster, [turn the backend off](#turn-off-a-backend-you-dont-use).

### Add the marketplace and install

```bash
codex plugin marketplace add cockroachdb/codex-plugin
codex plugin add cockroachdb@cockroachdb-codex-plugin
```

The marketplace source accepts `owner/repo`, an HTTPS Git URL, an SSH Git URL, or a local path. After `codex plugin marketplace add`, the marketplace is registered as `cockroachdb-codex-plugin` (the `name` field from `.agents/plugins/marketplace.json`).

### Trust the safety hooks

Codex skips plugin hooks until you review and trust them. Run `/hooks` in a Codex session and trust the two CockroachDB hooks:

- The PreToolUse hook on `mcp__cockroachdb_toolbox__cockroachdb_execute_sql`, Codex's name for the Toolbox SQL tool.
- The PostToolUse hook on file edits (`apply_patch`).

Both run small Python scripts bundled with the plugin. If a plugin update changes a hook, Codex asks you to review it again.

### Configure environment variables

All of these are optional. Set them in the environment you start Codex from.

The `cockroachdb-cloud` backend works without configuration and can reach every cluster your CockroachDB Cloud role allows. To limit it to one cluster:

```bash
export COCKROACHDB_CLUSTER_ID=<your-cloud-cluster-id>
```

The `cockroachdb-toolbox` (stdio) backend reads the variables below, and Codex forwards only these names to Toolbox. An unset variable falls back to its default in the bundled `tools.yaml`:

| Variable               | Default     | Notes                                                                        |
|------------------------|-------------|------------------------------------------------------------------------------|
| `COCKROACHDB_HOST`     | `localhost` |                                                                              |
| `COCKROACHDB_PORT`     | `26257`     |                                                                              |
| `COCKROACHDB_USER`     | `root`      |                                                                              |
| `COCKROACHDB_PASSWORD` | (empty)     |                                                                              |
| `COCKROACHDB_DATABASE` | `defaultdb` |                                                                              |
| `COCKROACHDB_SSLMODE`  | `require`   | Use `disable` for a local `--insecure` cluster, `verify-full` for production |

For a local development cluster:

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
| `cockroachdb-cloud` | HTTP | Managed CockroachDB Cloud MCP. Set `COCKROACHDB_CLUSTER_ID` to limit it to one cluster. Zero local install. |
| `cockroachdb-toolbox` | stdio | Self-hosted Toolbox against any cluster (local dev, self-hosted, or Cloud). Codex spawns the process. Read-only: writes and schema changes need `enableWriteMode: true` in a Toolbox configuration of your own. |

### Turn off a backend you don't use

Codex starts both backends in every session. To turn one off, add this to `~/.codex/config.toml`:

```toml
[plugins."cockroachdb@cockroachdb-codex-plugin".mcp_servers.cockroachdb-toolbox]
enabled = false
```

Use `cockroachdb-cloud` in place of `cockroachdb-toolbox` to turn off the Cloud backend. Don't put `enabled = false` under a bare `[mcp_servers.cockroachdb-toolbox]` table instead: Codex rejects a server table without a `command` or `url`, and every `codex` command fails until you remove it.

### Alternative backends

**MCP Toolbox over HTTP.** To use a Toolbox server you run yourself, for example a shared deployment, start it with `toolbox --config tools.yaml`, which listens on `http://127.0.0.1:5000/mcp` by default, and register it:

```bash
codex mcp add cockroachdb-toolbox-http --url http://127.0.0.1:5000/mcp
```

**CockroachDB MCP Server (first-party, self-hosted).** [CockroachDB MCP Server](https://github.com/cockroachdb/cockroachdb-mcp-server) is Cockroach Labs' own MCP server for clusters you run yourself. By default it registers only read-only tools, such as `list_databases`, `list_tables`, `get_table_schema`, `select_query`, `explain_query`, `show_statement`, and `show_running_queries`. Setting `CRDB_MCP_ENABLE_WRITE_QUERIES=true` adds `create_database`, `create_table`, `insert_rows`, `update_rows`, and `delete_rows`, and the server refuses an `UPDATE` or `DELETE` without a `WHERE` clause.

Install it with `go install github.com/cockroachdb/cockroachdb-mcp-server@latest` (Go 1.26+). Linux and Windows binaries and a Docker image are listed on the [releases page](https://github.com/cockroachdb/cockroachdb-mcp-server/releases). There are no prebuilt macOS binaries, so on macOS use `go install` or Docker. For a local `--insecure` development cluster:

```bash
codex mcp add cockroachdb-mcp-server --env CRDB_DATABASE_URL="postgresql://root@localhost:26257/defaultdb?sslmode=disable" --env CRDB_MCP_ALLOW_INSECURE_DB=true -- cockroachdb-mcp-server
```

For certificate authentication (recommended), add it to `~/.codex/config.toml`:

```toml
[mcp_servers.cockroachdb-mcp-server]
command = "cockroachdb-mcp-server"

[mcp_servers.cockroachdb-mcp-server.env]
CRDB_HOST = "your-cluster-host"
CRDB_USERNAME = "ai_agent"
CRDB_SSL_MODE = "verify-full"
CRDB_SSL_CA_PATH = "/certs/ca.crt"
CRDB_SSL_CERTFILE = "/certs/client.ai_agent.crt"
CRDB_SSL_KEYFILE = "/certs/client.ai_agent.key"
```

Password authentication is off unless you set `CRDB_MCP_ALLOW_PASSWORD_AUTH=true`. The plugin's SQL safety hook applies to the bundled Toolbox backend; this server enforces its own guardrails. See the [server's README](https://github.com/cockroachdb/cockroachdb-mcp-server#configuration) for every setting.

## Troubleshooting

**`toolbox: command not found`** — install [MCP Toolbox](https://mcp-toolbox.dev/documentation/introduction/#install-toolbox) (Homebrew, binary download, or container image).

**Hooks didn't run**: run `/hooks` in a Codex session and trust the CockroachDB hooks. Codex skips plugin hooks that haven't been trusted, or that changed since you trusted them.

**Skills not appearing** — verify the installed plugin cache contains skills: `find ~/.codex/plugins/cache/cockroachdb-codex-plugin/cockroachdb/*/skills -name SKILL.md | wc -l`.

**Toolbox uses an unexpected config path** — check `codex mcp list` for a
manually registered `cockroachdb-toolbox` server. A user-level server with the
same name can shadow the plugin-provided server. The plugin itself uses its
installed, bundled `tools.yaml`; it does not require an absolute checkout or
versioned cache path.

**`SSL error: certificate verify failed` or `node is running secure mode, SSL connection required`**: your cluster runs in secure mode, so set `COCKROACHDB_SSLMODE` to `require` or `verify-full`. The bundled `tools.yaml` passes only `sslmode` to the driver, and Codex forwards only the variables listed under [Configure environment variables](#configure-environment-variables). If you need a CA file or client certificates, run Toolbox with your own copy of `tools.yaml` that adds `sslrootcert`, `sslcert`, and `sslkey` under `queryParams`, register it as your own MCP server, and turn off the plugin's `cockroachdb-toolbox` backend.

For a quick local dev cluster, start one in insecure mode: `cockroach start-single-node --insecure --listen-addr=localhost:26257 &` and use `COCKROACHDB_SSLMODE=disable`.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Skills are sourced from [`cockroachlabs/cockroachdb-skills`](https://github.com/cockroachlabs/cockroachdb-skills) — open skill PRs there, not in this repo.


## License

Apache-2.0. See [`LICENSE`](./LICENSE).
