"""Deterministic checks for the quiet-places build.

Run: python3 -m unittest discover -s tests -v
Builds into a temp dir and asserts data integrity, output completeness,
bilingual coverage, structured data, and the em dash ban on customer copy.
"""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

REQUIRED_FIELDS = [
    "slug", "name", "focus", "town", "state", "langs", "band",
    "url", "status", "checked", "tagline_en", "tagline_es", "desc_en", "desc_es",
]


def words(text):
    return len(re.findall(r"\S+", text))


class BuildHarness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "site"
        self.places = build.build_into(self.out)
        self.data = json.loads(build.DATA_FILE.read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def page(self, slug, lang):
        if lang == "en":
            return self.out / "places" / f"{slug}.html"
        return self.out / "es" / "lugares" / f"{slug}.html"


class DataIntegrity(BuildHarness):
    def test_at_least_25_entries(self):
        self.assertGreaterEqual(len(self.places), 25)

    def test_unique_slugs(self):
        slugs = [p["slug"] for p in self.places]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_required_fields_present(self):
        for p in self.places:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, p, f"{p['slug']} missing {field}")

    def test_field_domains(self):
        for p in self.places:
            self.assertIn(p["focus"], build.FOCUSES, p["slug"])
            self.assertIn(p["status"], build.STATUS_LABEL, p["slug"])
            self.assertIn(p["band"], build.BAND_RANGE, p["slug"])
            self.assertIn(p.get("price_unit", "night"), build.PRICE_UNIT, p["slug"])
            self.assertTrue(p["url"].startswith("https://"), p["slug"])
            self.assertTrue(p["langs"], p["slug"])

    def test_card_links_resolve_to_files(self):
        """Regression: ES home cards once linked to /lugares/ instead of /es/lugares/."""
        for lang, index_rel in (("en", "index.html"), ("es", "es/index.html")):
            html = (self.out / index_rel).read_text(encoding="utf-8")
            page_dir = (self.out / index_rel).parent
            hrefs = re.findall(r'<a href="(/places/[^"]+\.html|/es/lugares/[^"]+\.html)">', html)
            self.assertGreaterEqual(len(hrefs), len(self.places), f"{lang} home card count")
            for href in hrefs:
                self.assertTrue((self.out / href.lstrip("/")).exists(), f"{lang} home -> {href}")

    def test_description_word_counts(self):
        for p in self.places:
            for lang in ("en", "es"):
                n = words(p[f"desc_{lang}"])
                self.assertTrue(
                    40 <= n <= 60, f"{p['slug']}.desc_{lang} has {n} words, want 40 to 60"
                )

    def test_taglines_short(self):
        for p in self.places:
            for lang in ("en", "es"):
                self.assertLessEqual(words(p[f"tagline_{lang}"]), 14, p["slug"])


class OutputCompleteness(BuildHarness):
    def test_all_place_pages_exist(self):
        for p in self.places:
            for lang in ("en", "es"):
                self.assertTrue(self.page(p["slug"], lang).exists(), f"{p['slug']} {lang}")

    def test_index_and_infra_files(self):
        for rel in ("index.html", "es/index.html", "match/index.html",
                    "es/vinculacion/index.html", "llms.txt", "llms-full.txt",
                    "sitemap.xml", "robots.txt", "assets/style.css"):
            self.assertTrue((self.out / rel).exists(), rel)

    def test_sitemap_covers_every_page(self):
        xml = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(xml.count("<loc>"), (len(self.places) + 2) * 2)

    def test_llms_txt_format(self):
        text = (self.out / "llms.txt").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# "))
        self.assertIn("\n> ", text)
        for p in self.places:
            self.assertIn(build.page_url(p["slug"], "en"), text)
            self.assertIn(build.page_url(p["slug"], "es"), text)


class PageQuality(BuildHarness):
    def test_place_page_basics(self):
        for p in self.places:
            for lang in ("en", "es"):
                html = self.page(p["slug"], lang).read_text(encoding="utf-8")
                self.assertIn(f'<html lang="{lang}">', html)
                self.assertIn(f">{p['name']}<", html)
                self.assertIn('rel="canonical"', html)
                self.assertIn('hreflang="en"', html)
                self.assertIn('hreflang="es"', html)
                self.assertIn(p["url"], html)  # official site linked
                self.assertIn("application/ld+json", html)

    def test_jsonld_parses_on_every_page(self):
        for p in self.places:
            for lang in ("en", "es"):
                html = self.page(p["slug"], lang).read_text(encoding="utf-8")
                block = html.split('<script type="application/ld+json">')[1].split("</script>")[0]
                data = json.loads(block)
                self.assertEqual(data["address"]["addressCountry"], "MX")
                self.assertIn(data["@type"], set(build.JSONLD_TYPE.values()))

    def test_home_links_every_place(self):
        for lang in ("en", "es"):
            html = (self.out / ("index.html" if lang == "en" else "es/index.html")).read_text(encoding="utf-8")
            for p in self.places:
                self.assertIn(f"{p['slug']}.html", html, f"{p['slug']} missing on {lang} home")

    def test_no_em_or_en_dash_in_output_html(self):
        for path in list(self.out.rglob("*.html")) + list(self.out.rglob("*.txt")):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", str(path) + text)
            self.assertNotIn("\u2013", text)

    def test_band_wording_matches_price_unit(self):
        """Regression: a day spa once rendered 'per person per night'."""
        day = next(p for p in self.places if p.get("price_unit") == "day")
        night = next(p for p in self.places if p.get("price_unit", "night") == "night")
        for lang in ("en", "es"):
            day_html = self.page(day["slug"], lang).read_text(encoding="utf-8")
            night_html = self.page(night["slug"], lang).read_text(encoding="utf-8")
            self.assertIn(build.PRICE_UNIT["day"][lang], day_html)
            self.assertIn(build.PRICE_UNIT["night"][lang], night_html)
            self.assertNotIn(build.PRICE_UNIT["night"][lang], day_html)

    def test_contact_line_renders_only_with_channel(self):
        """Regression: encyclopedia source links were once labeled as contact channels."""
        for p in self.places:
            for lang in ("en", "es"):
                html = self.page(p["slug"], lang).read_text(encoding="utf-8")
                has_line = 'class="contact"' in html
                self.assertEqual(
                    has_line, bool(p.get("contact")), f"{p['slug']} {lang} contact line mismatch"
                )
                self.assertIn(p["url"], html)  # source always visible in facts table
                self.assertIn(f'<a href="{p["url"]}"', html)  # source is clickable, not plain text

    def test_removed_entries_leave_no_stale_pages(self):
        """Regression: rebuilding over an existing output once kept deleted listings."""
        import copy
        import tempfile

        slim = copy.deepcopy(self.data)
        removed = slim["places"].pop()
        with tempfile.TemporaryDirectory() as td:
            slim_file = Path(td) / "slim.json"
            slim_file.write_text(json.dumps(slim), encoding="utf-8")
            original = build.DATA_FILE
            build.DATA_FILE = slim_file
            try:
                build.build_into(self.out)  # rebuild over the full output
            finally:
                build.DATA_FILE = original
            self.assertFalse(
                (self.out / "places" / f"{removed['slug']}.html").exists(),
                "removed entry still in output",
            )
            self.assertFalse(
                (self.out / "es" / "lugares" / f"{removed['slug']}.html").exists(),
                "removed entry still in ES output",
            )
            self.assertEqual(len(list((self.out / "places").glob("*.html"))), len(slim["places"]))

    def test_rebuild_refuses_foreign_directory(self):
        """Regression: a nonempty dir with an index.html once passed ownership check."""
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            foreign = Path(td) / "other-site"
            (foreign / "assets").mkdir(parents=True)
            (foreign / "assets" / "keep.css").write_text("body{}", encoding="utf-8")
            (foreign / "index.html").write_text("<html>not ours</html>", encoding="utf-8")
            with self.assertRaises(SystemExit):
                build.build_into(foreign)
            self.assertTrue((foreign / "index.html").exists(), "foreign index deleted")
            self.assertTrue((foreign / "assets" / "keep.css").exists(), "foreign assets deleted")

    def test_jsonld_never_breaks_out_of_script_tag(self):
        """Regression: a hostile description could close the JSON-LD script tag."""
        import copy
        import tempfile

        hostile = copy.deepcopy(self.data)
        hostile["places"][0]["desc_en"] = 'Fine place </script><script>alert(1)</script> really'
        with tempfile.TemporaryDirectory() as td:
            hostile_file = Path(td) / "hostile.json"
            hostile_file.write_text(json.dumps(hostile), encoding="utf-8")
            original = build.DATA_FILE
            build.DATA_FILE = hostile_file
            try:
                build.build_into(self.out)
            finally:
                build.DATA_FILE = original
            html = (self.out / "places" / f"{hostile['places'][0]['slug']}.html").read_text(encoding="utf-8")
            self.assertEqual(html.count("</script>"), 1, "script tag escaped into output")
            self.assertEqual(html.count("<script"), 1, "second script tag injected")
            self.assertIn("\\u003c/script\\u003e", html)  # hostile payload neutralized inside JSON

    def test_hero_is_citable_length(self):
        for text in (build.HERO_EN, build.HERO_ES):
            n = words(text)
            self.assertTrue(40 <= n <= 60, f"hero has {n} words")


if __name__ == "__main__":
    unittest.main()
