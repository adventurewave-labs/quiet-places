import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree


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
            namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            root = ElementTree.parse(out / "sitemap.xml")
            urls = [node.text for node in root.iter(namespace + "loc")]
            base = "https://adventurewave-labs.github.io/quiet-places/"
            self.assertIn(base, urls)
            self.assertIn(base + "es/", urls)
            self.assertIn(base + "directory/places/bacalar/", urls)
            self.assertEqual(len(urls), len(set(urls)))
            self.assertIn(base + "directory/llms.txt", (out / "llms.txt").read_text(encoding="utf-8"))
            for name in ("sitemap.xml", "llms.txt"):
                self.assertEqual((out / name).read_bytes(), (ROOT / "docs" / name).read_bytes())
            live = ROOT / "docs/directory"
            generated = out / "directory"
            expected = {path.relative_to(generated): path.read_bytes()
                        for path in generated.rglob("*") if path.is_file()}
            committed = {path.relative_to(live): path.read_bytes()
                         for path in live.rglob("*") if path.is_file()}
            self.assertEqual(committed, expected, "Regenerate docs/directory from the release build")
