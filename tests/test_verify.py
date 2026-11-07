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


class ParseCurl(unittest.TestCase):
    def test_clean_200_passes(self):
        code, final = verify.parse_curl(0, "200 https://a.com/\n")
        self.assertEqual(code, 200)
        self.assertEqual(final, "https://a.com/")

    def test_nonzero_exit_fails_even_with_200(self):
        """Regression: curl timing out after a 200 header line once counted as PASS."""
        code, detail = verify.parse_curl(28, "200 https://a.com/")
        self.assertIsNone(code)
        self.assertIn("200", detail)

    def test_000_no_connection_fails(self):
        code, detail = verify.parse_curl(6, "000 ")
        self.assertIsNone(code)

    def test_empty_stdout_nonzero_exit(self):
        code, detail = verify.parse_curl(1, "")
        self.assertIsNone(code)
        self.assertIn("curl exit 1", detail)


if __name__ == "__main__":
    unittest.main()
