import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PagesBuildTests(unittest.TestCase):
    def test_project_subpath_supports_place_and_language_navigation(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "pages"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_pages.py"), "--out", str(out),
                 "--base-url", "https://adventurewave-labs.github.io/quiet-places/"],
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                check=True, capture_output=True,
            )
            home = (out / "directory/index.html").read_text()
            self.assertIn('href="/quiet-places/directory/es/"', home)
            self.assertIn('href="/quiet-places/directory/assets/style.css"', home)
            self.assertTrue((out / "directory/es/index.html").is_file())
            place = (out / "directory/places/bacalar/index.html").read_text()
            self.assertIn('href="https://adventurewave-labs.github.io/quiet-places/directory/places/bacalar/"', place)
            self.assertTrue((out / "directory/guides/bacalar/index.html").is_file())
            self.assertTrue((out / "directory/match/index.html").is_file())
            self.assertFalse((out / "directory/.quiet-places-build").exists())
            self.assertTrue((out / "index.html").is_file())
            live = ROOT / "docs/directory"
            generated = out / "directory"
            expected = {path.relative_to(generated): path.read_bytes()
                        for path in generated.rglob("*") if path.is_file()}
            committed = {path.relative_to(live): path.read_bytes()
                         for path in live.rglob("*") if path.is_file()}
            self.assertEqual(committed, expected, "Regenerate docs/directory from the release build")
