from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = SKILL_ROOT / "scripts" / "run_handoff_validation.py"
SPEC = importlib.util.spec_from_file_location("run_handoff_validation", WRAPPER)
assert SPEC and SPEC.loader
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)


class SecretMaskingPatternTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="secret-pattern-tests-"))
        self.source = self.temp_dir / "fixture.md"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mock_secret_families_are_detected(self) -> None:
        aws = "AKIA" + "1234567890ABCDEF"
        github = "gh" + "p_" + ("G" * 24)
        openai = "sk-" + ("O" * 24)
        bearer = "Bearer " + ("B" * 24)
        credential = "password" + " = " + ("P" * 16)
        private_key = (
            "-----BEGIN " + "RSA " + "PRIVATE KEY-----\n"
            + "mock-private-key-material\n"
            + "-----END " + "RSA " + "PRIVATE KEY-----"
        )
        self.source.write_text("\n".join([aws, github, openai, bearer, credential, private_key]), encoding="utf-8")

        findings = wrapper.scan_sensitive(self.temp_dir, set())
        labels = {label for _, _, label in findings}
        self.assertEqual(
            labels,
            {"AWS access key", "GitHub token", "OpenAI-style key", "bearer token", "credential assignment", "private key"},
        )

    def test_all_mock_secret_families_are_masked(self) -> None:
        corpus = "\n".join(
            [
                "AKIA" + "1234567890ABCDEF",
                "gh" + "p_" + ("G" * 24),
                "sk-" + ("O" * 24),
                "Bearer " + ("B" * 24),
                "password" + " = " + ("P" * 16),
                "-----BEGIN " + "RSA " + "PRIVATE KEY-----\nmock-private-key-material\n-----END " + "RSA " + "PRIVATE KEY-----",
            ]
        )
        self.source.write_text(corpus, encoding="utf-8")
        replacements = wrapper.mask_sensitive(self.temp_dir, set())
        masked = self.source.read_text(encoding="utf-8")

        self.assertEqual(replacements, 6)
        self.assertEqual(wrapper.scan_sensitive(self.temp_dir, set()), [])
        self.assertNotIn("1234567890ABCDEF", masked)
        self.assertNotIn("mock-private-key-material", masked)
        self.assertIn("REDACTED_AWS_ACCESS_KEY", masked)
        self.assertIn("REDACTED_PRIVATE_KEY", masked)


if __name__ == "__main__":
    unittest.main()
