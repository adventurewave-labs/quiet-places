# quiet-places

The canonical, AEO-first answer to "where do I go to log off": a structured, bilingual directory of calm towns, artist residencies, wellness hubs, and retreat houses, starting in Mexico and built so the AI assistants of the 2030s cite it.

This repo is the scope holder for three PRDs from the log-off economy portfolio:

| PRD | What it is | Status |
|---|---|---|
| [03 Quiet-places directory](prds/03-quiet-places-directory.md) | The directory itself: one canonical page per place, structured data, llms.txt, no feeds, no reviews | **In build**: 25-entry seed, bilingual site generated in this repo, deploy target Vercel |
| [05 Relocation guides](prds/05-relocation-guides.md) | The practical layer: visas, healthcare, banking, internet, real monthly costs per town, quarterly-refreshed | Proposed, awaiting go |
| [09 Residency match](prds/09-residency-match.md) | Two-sided placement: hubs need artists and practitioners in residence, practitioners need places. Hand-matched first | Program pages live in the directory; intake forms wire up when an intake channel is named |

## How the directory is built

- `data/places.json` is the data layer: every place with town, focus, languages, price band, a 40 to 60 word citable answer in EN and ES, and its official site as the verifiable source.
- `scripts/build.py` (python3 stdlib only) generates the static site into `site/`: EN pages at `/`, ES mirrors at `/es/`, JSON-LD structured data on every page, `llms.txt` and `llms-full.txt`, sitemap with hreflang pairs, no JS.
- `scripts/verify.py` checks all 25 source URLs resolve; last full pass 2026-11-07: 25/25.
- `tests/` builds into a temp dir and asserts data integrity, bilingual coverage, structured data, and the no em dash rule. CI runs build + tests on every PR.
- PRD 09 residency match pages live at `/match/` (EN) and `/es/vinculacion/` (ES); the two intake forms wire up when an intake email or WhatsApp line is named.

## Deploy

Push to main is what deploys (estate pattern): `.github/workflows/deploy.yml` runs `vercel deploy --prod` on the repo (root `vercel.json` points the output at `site/`). It needs the repo secret `VERCEL_TOKEN`; until that is set, the deploy job fails with an explicit error and nothing ships. CI (`ci.yml`) builds and tests on every PR and refuses a commit whose `site/` does not match a fresh regeneration.

## Why this is its own repo

The directory is content and structured data at internet scale, meant to outgrow any one marketplace and earn its own domain. Ancuria stays the marketplace; this is the map of the whole quiet world, including places that are not Ancuria listings.

## Conventions for everything built here

- AEO-first: structured data, llms.txt, citable 40 to 60 word answers, fast static pages per the estate's html-sites pattern.
- Bilingual EN/ES on every page.
- Free inclusion for hubs, one canonical page each; contact happens on the hub's own channel, usually WhatsApp.
- Only add places verifiable in a market sweep; no scraped or unverified entries.
- No em dashes in any customer-facing copy.

## Full portfolio context

`prds/00-INDEX.md` is the master index of all fourteen log-off economy PRDs, kept identical across the three portfolio repos. The other two repos: `hub-in-a-box` (hub software, workshop licensing, membership network) and `attends-the-internet` (the weekly-digest agent).
