from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "generate_command_reference.py"


class GeneratorTest(unittest.TestCase):
    def test_generates_valid_bash_reference_from_sanitized_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands.txt"
            source.write_text("git\nls\nll\n", encoding="utf-8")
            prefix = root / "out" / "commands"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--shell", "bash", "--input", str(source), "--out-prefix", str(prefix)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(prefix.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(payload["meta"]["shell"], "bash")
            self.assertEqual(payload["meta"]["total_unique_commands"], 3)
            self.assertEqual([item["name"] for item in payload["commands"]], ["git", "ll", "ls"])
            self.assertTrue(prefix.with_suffix(".md").exists())
            self.assertTrue(prefix.with_suffix(".yaml").exists())


if __name__ == "__main__":
    unittest.main()
