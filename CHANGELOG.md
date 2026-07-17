# Changelog

## [0.1.1](https://github.com/cockroachdb/codex-plugin/compare/v0.1.0...v0.1.1) (2026-07-17)


### Features

* add .mcp.json with 3 backends (toolbox stdio/http, cloud) ([f4fd0da](https://github.com/cockroachdb/codex-plugin/commit/f4fd0da712966e45a755072af495de2958dabf8e))
* add CockroachDB logo asset ([0e0e7c1](https://github.com/cockroachdb/codex-plugin/commit/0e0e7c1096bcdc3770eba0e7d3c5a3593129df65))
* add Codex plugin manifest ([cd0e497](https://github.com/cockroachdb/codex-plugin/commit/cd0e4973067e6dbac4c4fc0bde4aa85909a765cf))
* add Codex-adapted marketplace install validator ([9ae040f](https://github.com/cockroachdb/codex-plugin/commit/9ae040f14a9184fe218087c5306c4789b19e15f9))
* add Codex-native marketplace.json ([35d9b40](https://github.com/cockroachdb/codex-plugin/commit/35d9b4093e7b9aa0c049e5bb1b9f1ab883515779))
* add hooks.json with PreToolUse SQL validator and PostToolUse linter ([16cf5ac](https://github.com/cockroachdb/codex-plugin/commit/16cf5ac5697ff7992b1ae22edbca79317ee9c7d5))
* add MCP Toolbox source config (tools.yaml) ([2eea41b](https://github.com/cockroachdb/codex-plugin/commit/2eea41b7aeb427ef21bc0a8d233eb7e13f70b154))
* add safety hook scripts (validate-sql, check-sql-files) ([9660f5f](https://github.com/cockroachdb/codex-plugin/commit/9660f5fe6996e2e204bfa6f77bee566b7b60dba4))
* add setup-cockroachdb.sh (Toolbox + local cluster bootstrap) ([4286728](https://github.com/cockroachdb/codex-plugin/commit/42867285197e44b773725d1d0698184b72e6aa70))
* add sync-skills.sh and vendor initial skills snapshot ([445d304](https://github.com/cockroachdb/codex-plugin/commit/445d304d419c6e5fdcc978b8d28f85a88f2c6d6e))


### Bug Fixes

* align hook layout with Codex conventions ([c3faa69](https://github.com/cockroachdb/codex-plugin/commit/c3faa69bdd623e99b987e4c00b3c700faa8b71ec))
* emit both hook output formats and drop the skills symlink ([a32fd91](https://github.com/cockroachdb/codex-plugin/commit/a32fd91408faab69630d799443808c4ef0c90f2c))
* set application_name to cockroachdb-codex-plugin ([e5cd764](https://github.com/cockroachdb/codex-plugin/commit/e5cd7645eb8e1122fa4fe3eb3a705d6f31b50804))

## [0.1.0] (2026-05-26)

Initial release of the CockroachDB plugin for OpenAI Codex CLI. This plugin is a Codex-native port of the [cockroachdb/claude-plugin](https://github.com/cockroachdb/claude-plugin), adapted for the Codex plugin marketplace format.


### Features

* package CockroachDB skills, MCP server backends (Toolbox stdio, Toolbox HTTP/SSE, CockroachDB Cloud HTTP), SQL validation hooks, and local setup script as a Codex plugin
* sync skills from upstream [cockroachlabs/cockroachdb-skills](https://github.com/cockroachlabs/cockroachdb-skills) submodule via weekly CI workflow
* provide one-command local install via `codex plugin marketplace add` and `codex plugin install`
