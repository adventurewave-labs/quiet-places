# Quiet Places

![Quiet Places. A field guide to logging off in Mexico.](docs/assets/quiet-places-banner.svg)

Quiet Places is a bilingual directory of calm towns, artist residencies, wellness hubs, and retreat houses in Mexico. The directory includes **25 place profiles, five relocation guides, and residency program pages** in English and Spanish.

[Landing page](https://adventurewave-labs.github.io/quiet-places/) · [En español](https://adventurewave-labs.github.io/quiet-places/es/) · [Download v0.1.1](https://github.com/adventurewave-labs/quiet-places/releases/tag/v0.1.1)

## Use the directory

Each profile links to a verifiable source and the place’s own contact channels. The relocation guides cover visas, healthcare, banking, and internet for five towns, plus monthly costs where figures are available. The residency pages explain the program for artists, practitioners, and hosts.

- [Browse the live directory](https://adventurewave-labs.github.io/quiet-places/directory/)
- [Versioned site archive](https://github.com/adventurewave-labs/quiet-places/releases/download/v0.1.1/quiet-places-v0.1.1-site.tar.gz)
- [Release notes](CHANGELOG.md) and [download checksums](https://github.com/adventurewave-labs/quiet-places/releases/download/v0.1.1/SHA256SUMS)
- [Infographic SVG](docs/assets/quiet-places-infographic.svg) and [infographic PNG](docs/assets/quiet-places-infographic.png)

## Build and preview from source

Use Python 3.12, which is also the version used by CI. The build uses the Python standard library.

```bash
git clone https://github.com/adventurewave-labs/quiet-places.git
cd quiet-places
preview="$(mktemp -d)"
python3 scripts/build_pages.py --out "$preview/site" --base-url http://127.0.0.1:8000
python3 -m http.server 8000 --bind 127.0.0.1 --directory "$preview/site"
```

Open [the English directory](http://127.0.0.1:8000/directory/) or [the Spanish directory](http://127.0.0.1:8000/directory/es/). Run `python3 scripts/build.py` when updating the committed Vercel output under `site/`.

## Test and contribute

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify.py
```

The second command checks each place’s source URL over the network. Edit the source data or templates, then rebuild and commit the generated pages. CI checks that the committed `site/` matches a clean build.

| Path | Purpose |
| --- | --- |
| [data/places.json](data/places.json) | Bilingual places, source links, and contact details |
| [data/relocation.json](data/relocation.json) | Town-specific guide data |
| [scripts/build.py](scripts/build.py) and [scripts/guides.py](scripts/guides.py) | Static site generator and guide templates |
| [site/](site/) | Generated directory with structured data and bilingual navigation |
| [docs/](docs/) | Release landing source and artwork |
| [prds/](prds/) | Product scope and implementation notes |

Keep entries verifiable, publish corresponding English and Spanish pages, and direct visitors to the places’ own channels. Keep visitor-facing copy free of em dashes and en dashes.

## Deployment and release

GitHub Pages hosts the release landing and the live directory. The Pages build generates `sitemap.xml` and `llms.txt` for the landing and the directory. The crawler policy lives at the shared host’s root. Rebuild the Pages copy with `scripts/build_pages.py` from the same source used for `site/`. [The Turbo Rig release policy](.turbo-rig/release.json) records the license, publishing paths, and live acceptance checks.

[The Vercel workflow](.github/workflows/deploy.yml) supports deployments from `main` and uses Vercel CLI 65.12.1. It needs the GitHub Actions secrets `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID`. The workflow passes the token as an environment variable and reports any missing secret.

## Product scope

- [Quiet-places directory](prds/03-quiet-places-directory.md)
- [Relocation guides](prds/05-relocation-guides.md)
- [Residency match](prds/09-residency-match.md)
- [Log-off economy portfolio index](prds/00-INDEX.md)

## License

[MIT](LICENSE)
