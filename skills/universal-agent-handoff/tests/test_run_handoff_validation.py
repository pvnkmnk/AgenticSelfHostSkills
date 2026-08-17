from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_handoff_zip.py"
WRAPPER = SKILL_ROOT / "scripts" / "run_handoff_validation.py"
SPEC = importlib.util.spec_from_file_location("validate_handoff_zip", VALIDATOR)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class WrapperSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="handoff-wrapper-tests-"))
        self.repository = self.temp_dir / "handoff-repository"
        for relative in validator.REQUIRED_FILES:
            target = self.repository / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"fixture: {relative}\n", encoding="utf-8")
        validator_target = self.repository / "06-skills/universal-agent-handoff/scripts/validate_handoff_zip.py"
        shutil.copy2(VALIDATOR, validator_target)

    def run_wrapper(self, output: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python", str(WRAPPER), "--repository", str(self.repository), "--output", str(output), "--skip-tests", *extra],
            text=True,
            capture_output=True,
        )

    def test_sensitive_data_blocks_zip_generation(self) -> None:
        marker = "api" + "_key = " + "abcdefghijklmnop\n"
        (self.repository / "02-status" / "current-status.md").write_text(marker, encoding="utf-8")
        output = self.temp_dir / "blocked.zip"
        result = self.run_wrapper(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        self.assertIn("SENSITIVE DATA DETECTED", result.stderr)

    def test_masking_packages_copy_without_modifying_source(self) -> None:
        marker = "api" + "_key = " + "abcdefghijklmnop\n"
        source_file = self.repository / "02-status" / "current-status.md"
        source_file.write_text(marker, encoding="utf-8")
        output = self.temp_dir / "masked.zip"
        result = self.run_wrapper(output, "--mask-sensitive")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(source_file.read_text(encoding="utf-8"), marker)
        with zipfile.ZipFile(output) as archive:
            contents = archive.read("handoff-repository/02-status/current-status.md").decode("utf-8")
        self.assertNotIn("abcdefghijklmnop", contents)
        self.assertIn("REDACTED_CREDENTIAL_ASSIGNMENT", contents)


if __name__ == "__main__":
    unittest.main()
