import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "cockroachdb"
MCP_MANIFEST = PLUGIN_ROOT / ".mcp.json"
HOOKS_FILE = PLUGIN_ROOT / "hooks" / "hooks.json"
# Top-level keys Codex accepts in PreToolUse/PostToolUse hook output; it rejects
# any other key and then ignores the whole output.
CODEX_OUTPUT_KEYS = {"continue", "stopReason", "suppressOutput", "systemMessage", "decision", "reason", "hookSpecificOutput"}


class PluginMcpPackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.servers = json.loads(MCP_MANIFEST.read_text(encoding="utf-8"))["mcpServers"]

    def test_stdio_toolbox_resolves_bundled_config_from_plugin_root(self) -> None:
        server = self.servers["cockroachdb-toolbox"]

        self.assertEqual(server["cwd"], ".")
        config_flag = server["args"].index("--config")
        config_path = server["args"][config_flag + 1]
        relative_config = Path(config_path)

        self.assertEqual(config_path, "./tools.yaml")
        self.assertFalse(relative_config.is_absolute())
        self.assertNotIn("..", relative_config.parts)

        with tempfile.TemporaryDirectory() as install_parent:
            installed_root = Path(install_parent) / "cockroachdb"
            shutil.copytree(PLUGIN_ROOT, installed_root)
            installed_manifest = json.loads(
                (installed_root / ".mcp.json").read_text(encoding="utf-8")
            )
            installed_server = installed_manifest["mcpServers"]["cockroachdb-toolbox"]
            installed_config_flag = installed_server["args"].index("--config")
            installed_config = installed_server["args"][installed_config_flag + 1]
            resolved_config = (
                installed_root / installed_server["cwd"] / installed_config
            ).resolve()

            self.assertEqual(resolved_config, (installed_root / "tools.yaml").resolve())
            self.assertTrue(resolved_config.is_file())

    def test_stdio_toolbox_forwards_connection_environment(self) -> None:
        server = self.servers["cockroachdb-toolbox"]

        self.assertNotIn("env", server)
        self.assertEqual(
            server["env_vars"],
            [
                "COCKROACHDB_HOST",
                "COCKROACHDB_PORT",
                "COCKROACHDB_USER",
                "COCKROACHDB_PASSWORD",
                "COCKROACHDB_DATABASE",
                "COCKROACHDB_SSLMODE",
            ],
        )

    def test_cloud_mcp_sources_cluster_header_from_environment(self) -> None:
        server = self.servers["cockroachdb-cloud"]

        self.assertNotIn("headers", server)
        self.assertEqual(
            server["env_http_headers"],
            {"mcp-cluster-id": "COCKROACHDB_CLUSTER_ID"},
        )

    def test_remote_servers_use_https(self) -> None:
        for name, server in self.servers.items():
            if "url" in server:
                with self.subTest(server=name):
                    self.assertTrue(server["url"].startswith("https://"), server["url"])


def codex_tool_name(server: str, tool: str) -> str:
    """Codex replaces every character outside [A-Za-z0-9_] in MCP names."""
    sanitize = lambda name: re.sub(r"[^A-Za-z0-9_]", "_", name)
    return f"mcp__{sanitize(server)}__{sanitize(tool)}"


class PluginHooksPackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hooks = json.loads(HOOKS_FILE.read_text(encoding="utf-8"))["hooks"]

    def run_script(self, command: str, payload: dict) -> str:
        script = re.search(r'"\$\{PLUGIN_ROOT\}/(scripts/[^"]+)"', command).group(1)
        args = [sys.executable, str(PLUGIN_ROOT / script)] + (["--codex"] if "--codex" in command else [])
        result = subprocess.run(args, input=json.dumps(payload), capture_output=True, text=True, check=True)
        return result.stdout

    def test_hooks_live_where_codex_discovers_them(self) -> None:
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertTrue(HOOKS_FILE.is_file())
        self.assertFalse((PLUGIN_ROOT / "hooks.json").exists())
        self.assertNotIn("hooks", manifest)

    def test_sql_hook_matches_the_codex_name_of_the_toolbox_tool(self) -> None:
        self.assertIn("cockroachdb-toolbox", json.loads(MCP_MANIFEST.read_text(encoding="utf-8"))["mcpServers"])
        self.assertIn("cockroachdb-execute-sql:", (PLUGIN_ROOT / "tools.yaml").read_text(encoding="utf-8"))
        matcher = self.hooks["PreToolUse"][0]["matcher"]
        self.assertEqual(matcher, codex_tool_name("cockroachdb-toolbox", "cockroachdb-execute-sql"))

    def test_lint_hook_matches_apply_patch(self) -> None:
        self.assertIn("apply_patch", self.hooks["PostToolUse"][0]["matcher"].split("|"))

    def test_hook_commands_use_the_plugin_root_and_fail_open(self) -> None:
        for event in ("PreToolUse", "PostToolUse"):
            with self.subTest(event=event):
                command = self.hooks[event][0]["hooks"][0]["command"]
                self.assertIn('"${PLUGIN_ROOT}/scripts/', command)
                self.assertIn(" --codex", command)
                self.assertTrue(command.endswith("; exit 0"), command)
                script = re.search(r'"\$\{PLUGIN_ROOT\}/(scripts/[^"]+)"', command).group(1)
                self.assertTrue((PLUGIN_ROOT / script).is_file(), script)

    def test_sql_hook_denies_in_the_codex_output_shape(self) -> None:
        command = self.hooks["PreToolUse"][0]["hooks"][0]["command"]
        out = json.loads(self.run_script(command, {"hook_event_name": "PreToolUse", "tool_input": {"sql": "DROP DATABASE x"}}))
        self.assertEqual(set(out), {"hookSpecificOutput"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")

        warning = json.loads(self.run_script(command, {"tool_input": {"sql": "CREATE TABLE t (id SERIAL PRIMARY KEY)"}}))
        self.assertLessEqual(set(warning), CODEX_OUTPUT_KEYS)
        self.assertIn("additionalContext", warning["hookSpecificOutput"])

        self.assertEqual(self.run_script(command, {"tool_input": {"sql": "SELECT 1"}}), "")

    def test_lint_hook_reads_apply_patch_paths(self) -> None:
        command = self.hooks["PostToolUse"][0]["hooks"][0]["command"]
        with tempfile.TemporaryDirectory() as cwd:
            Path(cwd, "schema.sql").write_text("CREATE TABLE t (id SERIAL PRIMARY KEY);\n", encoding="utf-8")
            patch = "*** Begin Patch\n*** Add File: schema.sql\n+CREATE TABLE t (id SERIAL PRIMARY KEY);\n*** End Patch\n"
            out = json.loads(self.run_script(command, {"cwd": cwd, "tool_name": "apply_patch", "tool_input": {"command": patch}}))
        self.assertLessEqual(set(out), CODEX_OUTPUT_KEYS)
        self.assertIn("CockroachDB lint", out["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
