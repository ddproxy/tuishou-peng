"""Tests for the release version helper."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "set-release-version.py"
_spec = importlib.util.spec_from_file_location("set_release_version", SCRIPT)
release = importlib.util.module_from_spec(_spec)
sys.modules["set_release_version"] = release
_spec.loader.exec_module(release)

MANIFEST = """[package]
name = "tuishou-peng"
version = "0.1.0"

[dependencies]
serde = "1.0.0"
"""


class SetReleaseVersionTest(unittest.TestCase):
    def manifest(self, version: str = "0.1.0") -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "Cargo.toml"
        path.write_text(MANIFEST.replace('version = "0.1.0"', f'version = "{version}"'))
        return path

    def test_stable_tag_mismatch_refused(self) -> None:
        path = self.manifest()
        with self.assertRaises(release.ReleaseVersionError):
            release.set_release_version("v0.2.0", path)
        self.assertEqual(release.read_package_version(path), "0.1.0")
        self.assertEqual(MANIFEST, path.read_text())

    def test_stable_tag_match_is_noop(self) -> None:
        path = self.manifest()
        self.assertEqual(release.set_release_version("v0.1.0", path), "0.1.0")
        self.assertEqual(MANIFEST, path.read_text())

    def test_dev_rewrite_correct(self) -> None:
        path = self.manifest()
        version = release.set_release_version("v0.1.1-dev.4.gabc1234", path)
        self.assertEqual(version, "0.1.1-dev.4.gabc1234")
        self.assertEqual(release.read_package_version(path), version)
        self.assertIn(f'version = "{version}"', path.read_text())
        self.assertIn('serde = "1.0.0"', path.read_text())

    def test_dev_tag_wrong_base_refused(self) -> None:
        path = self.manifest()
        with self.assertRaises(release.ReleaseVersionError):
            release.set_release_version("v0.2.1-dev.1.gabc1234", path)
        self.assertEqual(release.read_package_version(path), "0.1.0")

    def test_dev_tag_generation(self) -> None:
        self.assertEqual(release.dev_tag("0.1.0", 7, "abc1234"), "v0.1.1-dev.7.gabc1234")

    def test_ordering_after_base_before_next(self) -> None:
        base_version = "0.1.0"
        next_version = release.next_patch_version(base_version)
        dev_version = release.release_version(
            release.dev_tag(base_version, 4, "abc1234"), base_version
        )
        base = release.version_key(base_version)
        dev = release.version_key(dev_version)
        next_stable = release.version_key(next_version)
        self.assertLess(base, dev)
        self.assertLess(dev, next_stable)
        earlier = release.version_key(
            release.release_version(release.dev_tag(base_version, 3, "abc1234"), base_version)
        )
        later = release.version_key(
            release.release_version(release.dev_tag(base_version, 5, "abc1234"), base_version)
        )
        self.assertLess(earlier, dev)
        self.assertLess(dev, later)
        self.assertLess(later, next_stable)

    def test_cli_refuses_mismatch_and_rewrites_dev(self) -> None:
        script = Path(__file__).resolve().parent / "set-release-version.py"
        path = self.manifest()
        mismatch = subprocess.run(
            [sys.executable, str(script), "v0.9.9", "--manifest", str(path)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertEqual(release.read_package_version(path), "0.1.0")

        rewritten = subprocess.run(
            [
                sys.executable,
                str(script),
                "v0.1.1-dev.2.gabc1234",
                "--manifest",
                str(path),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(rewritten.returncode, 0, rewritten.stderr)
        self.assertEqual(release.read_package_version(path), "0.1.1-dev.2.gabc1234")


if __name__ == "__main__":
    unittest.main()
