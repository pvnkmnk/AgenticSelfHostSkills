from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_handoff_zip.py"
SPEC = importlib.util.spec_from_file_location("validate_handoff_zip", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class HandoffZipValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="handoff-validator-tests-"))
        self.repository = self.temp_dir / "handoff-repository"
        for relative in validator.REQUIRED_FILES:
            target = self.repository / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"fixture: {relative}\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def make_zip(self, name: str = "handoff.zip") -> Path:
        archive_path = self.temp_dir / name
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in self.repository.rglob("*"):
                if path.is_file():
                    archive.write(path, Path("handoff-repository") / path.relative_to(self.repository))
        return archive_path

    def test_valid_directory_and_zip_pass(self) -> None:
        self.assertEqual(validator.validate_directory(self.repository), [])
        self.assertEqual(validator.validate_zip(self.make_zip()), [])

    def test_missing_required_document_fails(self) -> None:
        (self.repository / "MANIFEST.md").unlink()
        errors = validator.validate_directory(self.repository)
        self.assertTrue(any("MANIFEST.md" in error for error in errors))

    def test_multiple_top_level_directories_fail(self) -> None:
        archive_path = self.make_zip()
        with zipfile.ZipFile(archive_path, "a") as archive:
            archive.writestr("second-root/extra.txt", "unexpected root")
        errors = validator.validate_zip(archive_path)
        self.assertTrue(any("exactly one top-level directory" in error for error in errors))

    def test_path_traversal_member_fails(self) -> None:
        archive_path = self.make_zip()
        with zipfile.ZipFile(archive_path, "a") as archive:
            archive.writestr("handoff-repository/../outside.txt", "unsafe")
        errors = validator.validate_zip(archive_path)
        self.assertTrue(any("path traversal" in error for error in errors))

    def test_secret_like_content_fails(self) -> None:
        (self.repository / "02-status" / "current-status.md").write_text(
            "api" + "_key = " + "abcdefghijklmnop\n", encoding="utf-8"
        )
        errors = validator.validate_directory(self.repository)
        self.assertTrue(any("secret-like" in error for error in errors))

    def test_corrupt_zip_fails_cleanly(self) -> None:
        archive_path = self.temp_dir / "corrupt.zip"
        archive_path.write_bytes(b"not a zip archive")
        errors = validator.validate_zip(archive_path)
        self.assertTrue(any("valid ZIP" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
