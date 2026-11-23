# Quiet Places

![Quiet Places. A field guide to logging off in Mexico.](docs/assets/quiet-places-banner.svg)

Quiet Places is a bilingual directory of calm towns, artist residencies, wellness hubs, and retreat houses in Mexico. The first release includes **25 place profiles, five relocation guides, and residency program pages** in English and Spanish.

[Landing page](https://adventurewave-labs.github.io/quiet-places/) · [En español](https://adventurewave-labs.github.io/quiet-places/es/) · [Download v0.1.0](https://github.com/adventurewave-labs/quiet-places/releases/tag/v0.1.0)

## Use the directory

Each profile links to a verifiable source and the place’s own contact channels. The relocation guides cover visas, healthcare, banking, internet, and monthly costs for five towns. The residency pages explain the program for artists, practitioners, and hosts.

- [Current directory website](https://quiet-places.vercel.app/)
- [Versioned site archive](https://github.com/adventurewave-labs/quiet-places/releases/download/v0.1.0/quiet-places-v0.1.0-site.tar.gz)
- [Release notes](CHANGELOG.md) and [download checksums](https://github.com/adventurewave-labs/quiet-places/releases/download/v0.1.0/SHA256SUMS)
- [Infographic SVG](docs/assets/quiet-places-infographic.svg) and [infographic PNG](docs/assets/quiet-places-infographic.png)

## Build and preview from source

Use Python 3.12, which is also the version used by CI. The build uses the Python standard library.

```bash
git clone https://github.com/adventurewave-labs/quiet-places.git
cd quiet-places
python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open [the English directory](http://127.0.0.1:8000/) or [the Spanish directory](http://127.0.0.1:8000/es/). The build writes the HTML, sitemap, and `llms.txt` files to `site/`.

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

Keep entries verifiable, publish corresponding English and Spanish pages, and direct visitors to the places’ own channels. The project has no reviews or rankings.

## Deployment and release

GitHub Pages hosts the release landing. [The Vercel workflow](.github/workflows/deploy.yml) deploys the directory when the generated site changes on `main` and the project credentials are configured. [The Turbo Rig release policy](.turbo-rig/release.json) records the license, visibility, repository metadata, and publishing paths.

## Product scope

- [Quiet-places directory](prds/03-quiet-places-directory.md)
- [Relocation guides](prds/05-relocation-guides.md)
- [Residency match](prds/09-residency-match.md)
- [Log-off economy portfolio index](prds/00-INDEX.md)

## License

[MIT](LICENSE)
