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


ROOT = Path(__file__).resolve().parent.parent
ROOT_LINK = re.compile(r"""(\b(?:href|src)=["'])(/(?!/))""")


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
        prepared.rename(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--base-url", required=True, help="The standalone landing URL")
    args = parser.parse_args()
    build_pages(args.out.resolve(), args.base_url)


if __name__ == "__main__":
    main()
