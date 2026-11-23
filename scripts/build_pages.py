#!/usr/bin/env python3
"""Build the landing and directory for a GitHub Pages project path."""

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
ROOT_LINK = re.compile(r"""(\b(?:href|src)=["'])(/(?!/))""")


def write_discovery(output, origin):
    base = origin.rstrip("/") + "/"
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    ElementTree.register_namespace("", sitemap_ns)
    ElementTree.register_namespace("xhtml", xhtml_ns)
    sitemap = ElementTree.parse(output / "directory" / "sitemap.xml")
    root = sitemap.getroot()
    landing_pages = {"en": base, "es": base + "es/"}
    for url in landing_pages.values():
        entry = ElementTree.SubElement(root, f"{{{sitemap_ns}}}url")
        ElementTree.SubElement(entry, f"{{{sitemap_ns}}}loc").text = url
        for language, alternate in landing_pages.items():
            ElementTree.SubElement(entry, f"{{{xhtml_ns}}}link", {
                "rel": "alternate", "hreflang": language, "href": alternate,
            })
    ElementTree.indent(sitemap, space="  ")
    (output / "sitemap.xml").write_text(
        ElementTree.tostring(root, encoding="unicode", xml_declaration=True) + "\n",
        encoding="utf-8",
    )

    links = {
        "About Quiet Places": base,
        "Presentación en español": base + "es/",
        "English directory": base + "directory/",
        "Directorio en español": base + "directory/es/",
        "Relocation guides": base + "directory/guides/",
        "Residency program": base + "directory/match/",
        "Directory sources and context": base + "directory/llms.txt",
        "Full directory context": base + "directory/llms-full.txt",
    }
    lines = [
        "# Quiet Places", "",
        "> Bilingual directory of calm towns, artist residencies, wellness hubs, and retreats in Mexico.",
        "", "Place profiles link to public sources and each place's own contact channels.",
        "", "## Pages and reference files", "",
    ]
    lines.extend(f"- [{label}]({url})" for label, url in links.items())
    (output / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_pages(output, origin):
    url = urlsplit(origin)
    if (url.scheme not in ("http", "https") or not url.netloc or url.query or url.fragment
            or not re.fullmatch(r"[A-Za-z0-9/_.-]*", url.path)):
        raise ValueError("Expected an HTTP site base URL without a query or fragment")
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    directory_url = origin.rstrip("/") + "/directory"
    prefix = urlsplit(directory_url).path
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        work = Path(scratch)
        raw = work / "site"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/build.py"), "--out", str(raw),
             "--base-url", directory_url, "--directory-urls"],
            check=True,
        )
        prepared = work / "pages"
        shutil.copytree(ROOT / "docs", prepared, ignore=shutil.ignore_patterns("directory"))
        for entry in sorted(raw.rglob("*")):
            if not entry.is_file() or entry.name == ".quiet-places-build":
                continue
            part = entry.relative_to(raw)
            if part.suffix == ".html" and part.name != "index.html":
                part = part.with_suffix("") / "index.html"
            target = prepared / "directory" / part
            target.parent.mkdir(parents=True, exist_ok=True)
            if part.suffix == ".html":
                content = ROOT_LINK.sub(lambda match: match[1] + prefix + "/", entry.read_text(encoding="utf-8"))
                target.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n", encoding="utf-8")
            else:
                shutil.copyfile(entry, target)
        write_discovery(prepared, origin)
        prepared.rename(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--base-url", required=True, help="The standalone landing URL")
    args = parser.parse_args()
    build_pages(args.out.resolve(), args.base_url)


if __name__ == "__main__":
    main()
