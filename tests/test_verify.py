"""Unit tests for verify.py's redirect classification."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import verify  # noqa: E402


class Classify(unittest.TestCase):
    def test_same_url_passes(self):
        self.assertEqual(verify.classify("https://a.com/x", "https://a.com/x"), "PASS")

    def test_www_alias_passes(self):
        self.assertEqual(verify.classify("https://www.a.com", "https://a.com/"), "PASS")

    def test_path_change_same_host_passes(self):
        self.assertEqual(verify.classify("https://a.com/x", "https://a.com/y/"), "PASS")

    def test_cross_host_fails(self):
        self.assertEqual(verify.classify("https://a.com", "https://parked.example.com"), "FAIL")

    def test_www_lookalike_fails(self):
        self.assertEqual(verify.classify("https://a.com", "https://a-com.other.com"), "FAIL")

    def test_empty_final_fails(self):
        self.assertEqual(verify.classify("https://a.com", ""), "FAIL")

    def test_case_insensitive_host(self):
        self.assertEqual(verify.classify("https://A.com", "https://a.com/"), "PASS")


if __name__ == "__main__":
    unittest.main()
