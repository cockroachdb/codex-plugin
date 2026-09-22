import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "cockroachdb"
MCP_MANIFEST = PLUGIN_ROOT / ".mcp.json"


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

    def test_http_toolbox_remains_an_independent_client_connection(self) -> None:
        server = self.servers["cockroachdb-toolbox-http"]

        self.assertEqual(server["type"], "http")
        self.assertEqual(server["url"], "http://127.0.0.1:5000/mcp")
        self.assertNotIn("command", server)


if __name__ == "__main__":
    unittest.main()
