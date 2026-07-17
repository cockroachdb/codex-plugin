# Agent instructions for codex-plugin

Guidance for AI coding assistants (and new contributors) working in this repo. It complements [CONTRIBUTING.md](./CONTRIBUTING.md).

## What this repo is

The CockroachDB plugin for OpenAI Codex. The repo doubles as a Codex plugin marketplace: `.agents/plugins/marketplace.json` at the root lists the plugin, and the payload lives in `plugins/cockroachdb/` with its manifest at `plugins/cockroachdb/.codex-plugin/plugin.json`.

Install flow users follow:

```bash
codex plugin marketplace add cockroachdb/codex-plugin
codex plugin add cockroachdb@cockroachdb-codex-plugin
```

(The Codex CLI subcommand is `add`, not `install`.)

## Rules that prevent breakage

- **Never edit `plugins/cockroachdb/skills/` by hand.** Skills are synced from the [cockroachdb-skills](https://github.com/cockroachlabs/cockroachdb-skills) submodule by `scripts/sync-skills.sh`. The sync uses `rsync -aL` on purpose: upstream uses symlinks for shared reference files, and symlinks break on Windows clones (`core.symlinks=false` checks them out as text files). Keep the `-L`.
- **Skills keep the upstream domain-grouped layout** (unlike the copilot plugin, which flattens). Cross-skill relative links resolve on disk here, so no link rewriting is needed. If you change the layout, re-verify every `../` link still resolves.
- **Hook commands use paths relative to the plugin payload** (`python3 ./scripts/...`), matching Codex conventions. The hook scripts emit both output contracts (top-level `permissionDecision`/`additionalContext` plus `hookSpecificOutput`/`systemMessage`) and are shared verbatim with the copilot plugin; if you change one, change both. Note that Codex runtime support for plugin hooks has version-dependent gaps; the scripts must always fail open (exit 0) so a runtime that does run them can never get stuck.
- **Hook scripts are Python 3 stdlib only**, read JSON on stdin, write JSON on stdout.
- **Never bump versions by hand.** Release Please owns `version` in `plugins/cockroachdb/.codex-plugin/plugin.json`, `.release-please-manifest.json`, and `CHANGELOG.md`. Conventional commits: `fix:`/`feat:` cut a release, `chore:`/`docs:` do not.
- **No counts in descriptions.** Counts go stale; name the things instead.

## Testing

Smoke-test hook scripts from the payload directory, the way `hooks.json` invokes them:

```bash
cd plugins/cockroachdb
echo '{"tool_input":{"sql":"DROP DATABASE x"}}' | python3 ./scripts/validate-sql.py
```

To verify the full install path, add this repo as a marketplace with the Codex CLI (commands above) and confirm the cached payload contains the manifest, `.mcp.json`, `hooks.json`, and the skills tree.

## Writing style

Commit messages and PR bodies in a plain human voice: conventional-commit prefixes, no AI attribution trailers, plain punctuation.
