# Changelog

## [0.1.0] (2026-05-26)

Initial release of the CockroachDB plugin for OpenAI Codex CLI. This plugin is a Codex-native port of the [cockroachdb/claude-plugin](https://github.com/cockroachdb/claude-plugin), adapted for the Codex plugin marketplace format.


### Features

* package CockroachDB skills, MCP server backends (Toolbox stdio, Toolbox HTTP/SSE, CockroachDB Cloud HTTP), SQL validation hooks, and local setup script as a Codex plugin
* sync skills from upstream [cockroachlabs/cockroachdb-skills](https://github.com/cockroachlabs/cockroachdb-skills) submodule via weekly CI workflow
* provide one-command local install via `codex plugin marketplace add` and `codex plugin install`
