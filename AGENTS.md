# quiet-places repo instructions

Imports and defers to `~/rig/AGENTS.md` (the constitution). This file only adds what is specific to this repo.

## What this repo is

The scope holder for log-off PRDs 03 (quiet-places directory), 05 (relocation guides), and 09 (residency match). The directory is AEO-first: structured data, llms.txt, citable 40 to 60 word answers, fast static pages, bilingual EN and ES on everything customer facing.

## Layout

- `data/places.json` — the data layer for the directory. The only place entries are edited.
- `data/relocation.json` — per-town overlays for PRD 05 guides; national topic copy lives in `scripts/guides.py`.
- `scripts/build.py` — generates everything under `site/` from the data. Stdlib only.
- `scripts/guides.py` — PRD 05 relocation guide templates (five evergreen topics, EN and ES).
- `scripts/verify.py` — checks every entry's source URL resolves. Run before promoting statuses.
- `site/` — generated output, committed so PR diffs show the exact pages that ship.
- `prds/` — the PRDs. Do not edit them in feature branches without mp.

## Conventions

- No em dashes or en dashes in anything customer facing. The build fails on them.
- Every place entry carries a real source URL: the place's own site where one exists, otherwise a stable public source. No scraped or unverified entries.
- Contact happens on the place's own channel. The directory never intermediates, never hosts reviews.
- Site copy is bilingual EN and ES, including llms.txt and sitemap coverage.
- Edit data, never output, then rebuild and commit both.

## Gate checks

- python3 scripts/build.py
- python3 -m unittest discover -s tests
