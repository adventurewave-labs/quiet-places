"""Parity between committed site/ and a fresh regeneration.

Regression: CI once compared with `git diff`, which ignores untracked files,
so a commit missing a generated page could pass while the deployed commit
served a 404. This test rebuilds into a temp dir and compares the whole tree.
"""

import filecmp
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

COMMITTED = ROOT / "site"


class Parity(unittest.TestCase):
    def test_committed_site_equals_regeneration(self):
        with tempfile.TemporaryDirectory() as td:
            fresh = Path(td) / "site"
            build.build_into(fresh)
            committed_files = {p.relative_to(COMMITTED) for p in COMMITTED.rglob("*") if p.is_file()}
            fresh_files = {p.relative_to(fresh) for p in fresh.rglob("*") if p.is_file()}
            self.assertEqual(
                committed_files, fresh_files,
                f"committed site/ is out of sync: only committed={sorted(committed_files - fresh_files)[:5]}, "
                f"only regenerated={sorted(fresh_files - committed_files)[:5]}",
            )
            for rel in fresh_files:
                self.assertTrue(
                    filecmp.cmp(COMMITTED / rel, fresh / rel, shallow=False),
                    f"content differs for {rel}: rebuild and commit site/",
                )


if __name__ == "__main__":
    unittest.main()
