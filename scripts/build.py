#!/usr/bin/env python3
"""quiet-places site generator.

Reads data/places.json and emits the static bilingual directory into site/.
Python stdlib only, per the estate's html-sites pattern. Edit data, never
output, then rebuild: python3 scripts/build.py
"""

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "places.json"
DEFAULT_OUT = ROOT / "site"

BASE_URL = "https://quiet-places.vercel.app"  # update when the directory lands on its own domain
ESTATE_CONTACT = "https://www.adventureonthewave.com/#services"
SITE_NAME = "Quiet Places"
SITE_NAME_ES = "Quiet Places"

HERO_EN = (
    "Quiet Places is a bilingual directory of places to log off in Mexico: calm towns, "
    "artist residencies, wellness hubs, and retreat houses. Every entry links to the "
    "place's own site, carries a price band and languages spoken, and is verified from "
    "public sources before it ships. Contact happens on the place's own channel, not through us."
)
HERO_ES = (
    "Quiet Places es un directorio bilingüe de lugares para desconectarse en México: "
    "pueblos tranquilos, residencias artísticas, espacios de bienestar y casas de retiro. "
    "Cada entrada enlaza al sitio propio del lugar, indica banda de precio e idiomas, y "
    "se verifica con fuentes públicas antes de publicarse. El contacto sucede en el canal "
    "del propio lugar, no a través de nosotros."
)

INTRO_EN = (
    "People retreating from public feeds still need to find each other, and they ask an "
    "assistant or search, they do not scroll a hashtag. This directory is built to be the "
    "structured answer: one canonical page per place, structured data on every page, and "
    "an index written for both humans and AI assistants."
)
INTRO_ES = (
    "Las personas que se retiran de los feeds públicos siguen necesitando encontrarse, y "
    "preguntan a un asistente o buscan, no revisan un hashtag. Este directorio está "
    "construido para ser la respuesta estructurada: una página canónica por lugar, datos "
    "estructurados en cada página y un índice escrito para personas y asistentes de IA."
)

METHODOLOGY_EN = [
    ("Who gets in", "Hubs, residencies, and towns verifiable from public sources. Free inclusion, one canonical page each. No feeds, no reviews, no rankings."),
    ("Verification states", "web: entered and linked from the place's own public web presence, not yet confirmed on the ground. sweep: confirmed in person by a Market Watch sweep pass."),
    ("Price bands", "Per person per night equivalent for stays, per day for programs. Band 1 under MX$1,000. Band 2 MX$1,000 to 3,000. Band 3 MX$3,000 to 7,000. Band 4 above MX$7,000. Indicative at entry, confirmed by the sweep pass."),
    ("Contact", "Contact happens on the place's own channel, linked from its page. We do not intermediate, take bookings, or host reviews."),
]
METHODOLOGY_ES = [
    ("Quién entra", "Hubs, residencias y pueblos verificables con fuentes públicas. Inclusión gratuita, una página canónica por lugar. Sin feeds, sin reseñas, sin rankings."),
    ("Estados de verificación", "web: ingresado y enlazado desde la presencia pública del propio lugar, aún sin confirmar en campo. sweep: confirmado en persona por una pasada de barrido Market Watch."),
    ("Bandas de precio", "Equivalente por persona por noche en estancias, por día en programas. Banda 1 menos de MX$1,000. Banda 2 MX$1,000 a 3,000. Banda 3 MX$3,000 a 7,000. Banda 4 más de MX$7,000. Indicativas al ingreso, confirmadas por el barrido."),
    ("Contacto", "El contacto sucede en el canal del propio lugar, enlazado desde su página. No intermediamos, no reservamos, no alojamos reseñas."),
]

FOCUSES = {
    "art": ("Art residencies", "Residencias artísticas"),
    "retreat": ("Retreat houses", "Casas de retiro"),
    "wellness": ("Wellness hubs", "Espacios de bienestar"),
    "craft": ("Craft villages", "Pueblos artesanales"),
    "town": ("Calm towns", "Pueblos tranquilos"),
}

JSONLD_TYPE = {
    "art": "EducationalOrganization",
    "retreat": "LodgingBusiness",
    "wellness": "DaySpa",
    "craft": "TouristDestination",
    "town": "TouristDestination",
}

LANG_NAMES = {"es": "Spanish", "en": "English"}
LANG_NAMES_ES = {"es": "español", "en": "inglés"}

BAND_RANGE = {
    1: ("under MX$1,000", "menos de MX$1,000"),
    2: ("MX$1,000 to 3,000", "MX$1,000 a 3,000"),
    3: ("MX$3,000 to 7,000", "MX$3,000 a 7,000"),
    4: ("above MX$7,000", "más de MX$7,000"),
}

PRICE_UNIT = {
    "night": {
        "en": "per person per night",
        "es": "por persona por noche",
    },
    "day": {
        "en": "per person per day for programs and treatments",
        "es": "por persona por día en programas y tratamientos",
    },
}

STATUS_LABEL = {
    "web": ("Verified from public web sources", "Verificado con fuentes públicas en la web"),
    "sweep": ("Confirmed on the ground by a sweep pass", "Confirmado en campo por una pasada de barrido"),
}

FORBIDDEN_CHARS = ("\u2014", "\u2013")  # em dash, en dash: banned in customer-facing copy


def guard(strings):
    """Fail the build if a banned character reaches customer-facing copy."""
    bad = []
    for label, text in strings:
        for ch in FORBIDDEN_CHARS:
            if ch in text:
                bad.append(f"{label}: contains {ch!r}")
    if bad:
        raise SystemExit("em or en dash in customer-facing copy:\n" + "\n".join(bad))


def load_data():
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    strings = []
    for p in raw["places"]:
        strings += [
            (f"{p['slug']}.name", p["name"]),
            (f"{p['slug']}.town", p["town"]),
            (f"{p['slug']}.state", p["state"]),
            (f"{p['slug']}.tagline_en", p["tagline_en"]),
            (f"{p['slug']}.tagline_es", p["tagline_es"]),
            (f"{p['slug']}.desc_en", p["desc_en"]),
            (f"{p['slug']}.desc_es", p["desc_es"]),
        ]
    guard(strings)
    return raw


def page_url(slug, lang, kind="place"):
    if kind == "place":
        return f"{BASE_URL}/places/{slug}.html" if lang == "en" else f"{BASE_URL}/es/lugares/{slug}.html"
    if kind == "home":
        return f"{BASE_URL}/index.html" if lang == "en" else f"{BASE_URL}/es/index.html"
    if kind == "match":
        return f"{BASE_URL}/match/index.html" if lang == "en" else f"{BASE_URL}/es/vinculacion/index.html"
    raise ValueError(kind)


def page_path(slug, lang, kind="place"):
    """Root-relative form of page_url, for links that must stay inside
    whatever host renders the page (preview deploys, custom domains)."""
    return page_url(slug, lang, kind).removeprefix(BASE_URL)


def lang_attrs(langs, es=False):
    names = LANG_NAMES_ES if es else LANG_NAMES
    return ", ".join(names[l] for l in langs)


def band_text(p, es=False):
    rng = BAND_RANGE[p["band"]]
    unit = PRICE_UNIT[p.get("price_unit", "night")]
    return f"{rng[1] if es else rng[0]} ({unit['es'] if es else unit['en']})"


def place_jsonld(p, lang):
    data = {
        "@context": "https://schema.org",
        "@type": JSONLD_TYPE[p["focus"]],
        "name": p["name"],
        "description": p["desc_es"] if lang == "es" else p["desc_en"],
        "url": page_url(p["slug"], lang),
        "sameAs": [p["url"]],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": p["town"],
            "addressRegion": p["state"],
            "addressCountry": "MX",
        },
        "availableLanguage": [LANG_NAMES[l] for l in p["langs"]],
    }
    if p["focus"] in ("retreat", "wellness"):
        data["priceRange"] = "$" * p["band"]
    return json.dumps(data, ensure_ascii=False)


def layout(lang, title, desc, canonical, hreflang_for, body_jsonld, content, updated):
    """Shared page shell. hreflang_for: dict of lang -> url for this page's alternates."""
    es = lang == "es"
    home = "/index.html" if not es else "/es/index.html"
    match = "/match/index.html" if not es else "/es/vinculacion/index.html"
    other = "en" if es else "es"
    other_url = hreflang_for[other]
    nav_label = "Español" if not es else "English"
    t = lambda s_en, s_es: s_es if es else s_en  # noqa: E731
    alt_links = "\n".join(
        f'  <link rel="alternate" hreflang="{code}" href="{escape(url)}">'
        for code, url in hreflang_for.items()
    )
    status_note = t(
        f"Directory updated {updated}. Free inclusion, one canonical page per place.",
        f"Directorio actualizado el {updated}. Inclusión gratuita, una página canónica por lugar.",
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{escape(canonical)}">
{alt_links}
<link rel="alternate" type="application/rss+xml" title="llms" href="{BASE_URL}/llms.txt">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
{body_jsonld}
</script>
</head>
<body>
<header class="top">
  <a class="brand" href="{home}">{SITE_NAME if not es else SITE_NAME_ES}</a>
  <nav>
    <a href="{home}#directory">{t('Directory', 'Directorio')}</a>
    <a href="{home}#methodology">{t('Methodology', 'Metodología')}</a>
    <a href="{match}">{t('Residency match', 'Vinculación de residencias')}</a>
    <a class="lang" href="{other_url}" hreflang="{other}">{nav_label}</a>
  </nav>
</header>
<main>
{content}
</main>
<footer>
  <p>{status_note}</p>
  <p>{t('A project of the log off economy portfolio.', 'Un proyecto del portafolio log off economy.')} <a href="{ESTATE_CONTACT}" rel="noopener">{t('Contact the estate', 'Contactar al estate')}</a></p>
</footer>
</body>
</html>
"""


def place_card(p, lang):
    es = lang == "es"
    href = f"/places/{p['slug']}.html" if not es else f"/es/lugares/{p['slug']}.html"
    focus_label = FOCUSES[p["focus"]][1] if es else FOCUSES[p["focus"]][0]
    tagline = p["tagline_es"] if es else p["tagline_en"]
    band_label = "Banda" if es else "Band"
    return f"""    <li class="card">
      <a href="{href}">
        <span class="focus">{escape(focus_label)}</span>
        <span class="name">{escape(p['name'])}</span>
        <span class="where">{escape(p['town'])}, {escape(p['state'])}</span>
        <span class="tagline">{escape(tagline)}</span>
        <span class="meta">{band_label} {'$' * p['band']} · {escape(lang_attrs(p['langs'], es))}</span>
      </a>
    </li>"""


def home_page(places, lang, updated):
    es = lang == "es"
    t = lambda s_en, s_es: s_es if es else s_en  # noqa: E731
    title = t(
        "Quiet Places: calm towns, residencies, and retreats in Mexico",
        "Quiet Places: pueblos tranquilos, residencias y retiros en México",
    )
    website_jsonld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": page_url(None, lang, "home"),
            "inLanguage": "es-MX" if es else "en",
            "description": HERO_ES if es else HERO_EN,
        },
        ensure_ascii=False,
    )
    sections = []
    for focus, (label_en, label_es) in FOCUSES.items():
        group = [p for p in places if p["focus"] == focus]
        if not group:
            continue
        cards = "\n".join(place_card(p, lang) for p in group)
        sections.append(
            f'<section id="{focus}">\n<h2>{escape(label_es if es else label_en)}</h2>\n<ul class="grid">\n{cards}\n</ul>\n</section>'
        )
    method_items = "\n".join(
        f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in (METHODOLOGY_ES if es else METHODOLOGY_EN)
    )
    content = f"""<section class="hero">
  <h1>{t('Where do you go to log off?', '¿A dónde vas para desconectarte?')}</h1>
  <p class="answer">{escape(HERO_ES if es else HERO_EN)}</p>
  <p class="intro">{escape(INTRO_ES if es else INTRO_EN)}</p>
</section>
<section id="directory">
  <h2>{t('The directory', 'El directorio')}</h2>
  {"".join(sections)}
</section>
<section id="match-teaser">
  <h2>{t('Residency match', 'Vinculación de residencias')}</h2>
  <p>{t('Hubs need artists and practitioners in residence. Practitioners need a place to land. We hand match both sides. ', 'Los hubs necesitan artistas y practicantes en residencia. Los practicantes necesitan donde aterrizar. Vinculamos a ambas partes a mano. ')}<a href="{'/match/index.html' if not es else '/es/vinculacion/index.html'}">{t('How it works', 'Cómo funciona')}</a></p>
</section>
<section id="methodology">
  <h2>{t('Methodology', 'Metodología')}</h2>
  <dl>
  {method_items}
  </dl>
</section>"""
    return layout(
        lang,
        title,
        (HERO_ES if es else HERO_EN)[:155],
        page_url(None, lang, "home"),
        {"en": page_path(None, "en", "home"), "es": page_path(None, "es", "home")},
        website_jsonld,
        content,
        updated,
    )


def place_page(p, lang, updated):
    es = lang == "es"
    t = lambda s_en, s_es: s_es if es else s_en  # noqa: E731
    title = f"{p['name']} | {t('Quiet Places', 'Quiet Places')}"
    desc = p["desc_es"] if es else p["desc_en"]
    home_href = "../index.html" if not es else "../index.html"
    if es:
        home_href = "../index.html"
    focus_label = FOCUSES[p["focus"]][1] if es else FOCUSES[p["focus"]][0]
    status_label = STATUS_LABEL[p["status"]][1] if es else STATUS_LABEL[p["status"]][0]
    rows = [
        (t("Focus", "Enfoque"), focus_label),
        (t("Location", "Ubicación"), f"{p['town']}, {p['state']}, México"),
        (t("Languages", "Idiomas"), lang_attrs(p["langs"], es)),
        (t("Price band", "Banda de precio"), band_text(p, es)),
        (t("Verification", "Verificación"), f"{status_label} ({t('checked', 'verificado')} {p['checked']})"),
    ]
    table = "\n".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in rows)
    contact_label = t("Contact the place directly on its own channel:", "Contacta al lugar directo en su propio canal:")
    content = f"""<nav class="crumb"><a href="{home_href}">{t('Quiet Places', 'Quiet Places')}</a> / {escape(focus_label)}</nav>
<article>
  <h1>{escape(p['name'])}</h1>
  <p class="answer">{escape(desc)}</p>
  <table class="facts">
  {table}
  </table>
  <p class="contact">{contact_label} <a href="{escape(p['url'])}" rel="noopener">{escape(p['url'])}</a></p>
  <p class="note">{t('Free listing. No booking, no feed, no reviews. Inclusion is free and one page per place is canonical.', 'Publicación gratuita. Sin reservas, sin feed, sin reseñas. La inclusión es gratuita y una página por lugar es la canónica.')}</p>
</article>"""
    return layout(
        lang,
        title,
        (p["tagline_es"] if es else p["tagline_en"]),
        page_url(p["slug"], lang),
        {"en": page_path(p["slug"], "en"), "es": page_path(p["slug"], "es")},
        place_jsonld(p, lang),
        content,
        updated,
    )


def match_page(lang, updated):
    es = lang == "es"
    t = lambda s_en, s_es: s_es if es else s_en  # noqa: E731
    title = t("Residency match | Quiet Places", "Vinculación de residencias | Quiet Places")
    desc_en = (
        "Two sided placement for artist and wellness residencies in Mexico: hubs post needs, "
        "practitioners apply, we hand match both sides within two weeks. Flat placement fee per match."
    )
    desc_es = (
        "Vinculación de residencias artísticas y de bienestar en México: los hubs publican "
        "necesidades, los practicantes aplican y vinculamos a ambas partes a mano en dos semanas. "
        "Tarifa plana por vinculación."
    )
    if es:
        steps = [
            ("Aplicas", "Envías tu perfil: práctica, fechas, lo que buscas y lo que ofreces. Los hubs publican su necesidad: espacio, semanas, estipendio o cuota, y lo que el hub recibe."),
            ("Revisamos", "Revisamos ambas partes a mano. No hay algoritmo: leemos, llamamos por WhatsApp y confirmamos encaje de fechas y espacio."),
            ("Vinculamos", "Presentamos a ambas partes, acordamos semanas, espacio y estipendio o cuota. La tarifa plana de vinculación la paga el hub, o se parte."),
            ("Sucede", "La residencia sucede. Ambas partes nos reportan al cerrar y la página pública de residencias pasadas lo registra."),
        ]
        practitioner = ["Nombre y práctica: qué haces y desde cuándo", "Fechas y duración que buscas", "Qué ofreces: taller, clases, sesiones, obra", "Qué necesitas: espacio, silencio, comunidad, estipendio", "Canal de contacto, normalmente WhatsApp"]
        hub = ["Nombre del hub y ubicación", "El espacio: estudio, habitación, taller, terreno", "Semanas y fechas disponibles", "Estipendio, cuota o intercambio que propones", "Lo que el hub recibe: programación, pulso, obra"]
    else:
        steps = [
            ("You apply", "You send your profile: practice, dates, what you are looking for, and what you offer. Hubs post their need: space, weeks, stipend or fee, and what the hub gets."),
            ("We review", "We review both sides by hand. No algorithm: we read, we call over WhatsApp, and we confirm the fit on dates and space."),
            ("We match", "We introduce both sides and agree weeks, space, and stipend or fee. The flat placement fee is paid by the hub, or split."),
            ("It happens", "The residency happens. Both sides report back at the end, and the public page of past residencies records it."),
        ]
        practitioner = ["Name and practice: what you do and since when", "Dates and length you are looking for", "What you offer: workshop, classes, sessions, work", "What you need: space, silence, community, stipend", "A contact channel, usually WhatsApp"]
        hub = ["Hub name and location", "The space: studio, room, workshop, land", "Weeks and dates available", "Stipend, fee, or exchange you propose", "What the hub gets: programming, pulse, work"]
    steps_html = "\n".join(f"<li><strong>{escape(k)}</strong> {escape(v)}</li>" for k, v in steps)
    practitioner_html = "\n".join(f"<li>{escape(x)}</li>" for x in practitioner)
    hub_html = "\n".join(f"<li>{escape(x)}</li>" for x in hub)
    content = f"""<section class="hero">
  <h1>{t('Residency match', 'Vinculación de residencias')}</h1>
  <p class="answer">{escape(desc_es if es else desc_en)}</p>
  <p class="intro">{t(
      'Every hub the quiet trend creates needs programming and pulse. Every practitioner needs affordable space and an audience. The match is high trust and local, which is exactly what a feed cannot do and a curator can. Matching is done by hand while volume is low.',
      'Cada hub que crea la tendencia silenciosa necesita programación y pulso. Cada practicante necesita espacio accesible y una audiencia. La vinculación es de alta confianza y local, justo lo que un feed no puede hacer y un curador sí. Por ahora vinculamos a mano.')}</p>
</section>
<section>
  <h2>{t('How it works', 'Cómo funciona')}</h2>
  <ol class="steps">
  {steps_html}
  </ol>
</section>
<section>
  <h2>{t('Apply as a practitioner', 'Aplica como practicante')}</h2>
  <ul class="checklist">
  {practitioner_html}
  </ul>
</section>
<section>
  <h2>{t('Post a need as a hub', 'Publica una necesidad como hub')}</h2>
  <ul class="checklist">
  {hub_html}
  </ul>
</section>
<section class="cta">
  <h2>{t('Send your application', 'Envía tu aplicación')}</h2>
  <p>{t(
      'Intake is handled personally over WhatsApp and email while volume stays low. Write to us through the estate contact line and say which side you are on.',
      'El intake se maneja en persona por WhatsApp y correo mientras el volumen sea bajo. Escríbenos por la línea de contacto del estate y dinos de qué lado vienes.')}</p>
  <p><a class="button" href="{ESTATE_CONTACT}" rel="noopener">{t('Contact us', 'Contáctanos')}</a></p>
</section>"""
    return layout(
        lang,
        title,
        (desc_es if es else desc_en),
        page_url(None, lang, "match"),
        {"en": page_path(None, "en", "match"), "es": page_path(None, "es", "match")},
        json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "url": page_url(None, lang, "match"),
                "inLanguage": "es-MX" if es else "en",
                "description": desc_es if es else desc_en,
            },
            ensure_ascii=False,
        ),
        content,
        updated,
    )


STYLE = """:root { --ink: #26251f; --paper: #faf7f0; --moss: #4a5d43; --sand: #e8e0d0; --line: #d8d0c0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: var(--ink); background: var(--paper); line-height: 1.6; }
header.top { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; align-items: baseline; padding: 1.2rem 1.5rem; border-bottom: 1px solid var(--line); }
.brand { font-weight: 700; font-size: 1.15rem; color: var(--moss); text-decoration: none; letter-spacing: 0.02em; }
nav a { margin-left: 1.2rem; color: var(--ink); text-decoration: none; }
nav a.lang { color: var(--moss); font-weight: 600; }
main { max-width: 62rem; margin: 0 auto; padding: 1rem 1.5rem 3rem; }
.hero h1 { font-size: 2rem; line-height: 1.2; margin: 1.5rem 0 0.75rem; }
.answer { font-size: 1.08rem; border-left: 3px solid var(--moss); padding-left: 1rem; }
.intro { color: #55524a; }
section { margin: 2.2rem 0; }
h2 { font-size: 1.35rem; margin: 0 0 0.9rem; }
ul.grid { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr)); gap: 1rem; }
.card a { display: flex; flex-direction: column; gap: 0.25rem; height: 100%; padding: 1rem; border: 1px solid var(--line); border-radius: 0.6rem; background: #fff; text-decoration: none; color: inherit; }
.card a:hover { border-color: var(--moss); }
.card .focus { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--moss); }
.card .name { font-weight: 700; font-size: 1.05rem; }
.card .where { color: #6b675d; font-size: 0.9rem; }
.card .tagline { font-size: 0.92rem; }
.card .meta { color: #86816f; font-size: 0.8rem; margin-top: auto; }
table.facts { border-collapse: collapse; margin: 1.2rem 0; }
table.facts th { text-align: left; padding: 0.4rem 1rem 0.4rem 0; color: #6b675d; font-weight: 600; white-space: nowrap; vertical-align: top; }
table.facts td { padding: 0.4rem 0; }
dl dt { font-weight: 700; margin-top: 0.8rem; }
dl dd { margin: 0.15rem 0 0 0; }
ol.steps li, ul.checklist li { margin: 0.5rem 0; }
.crumb { color: #6b675d; font-size: 0.9rem; margin-top: 1.2rem; }
.crumb a { color: var(--moss); text-decoration: none; }
.contact a { color: var(--moss); overflow-wrap: anywhere; }
.note { color: #86816f; font-size: 0.88rem; }
.cta { border: 1px solid var(--line); border-radius: 0.6rem; padding: 1rem 1.4rem; background: var(--sand); }
.button { display: inline-block; padding: 0.55rem 1.2rem; background: var(--moss); color: #fff; border-radius: 0.4rem; text-decoration: none; font-weight: 600; }
footer { border-top: 1px solid var(--line); padding: 1.2rem 1.5rem 2rem; color: #86816f; font-size: 0.88rem; }
footer p { max-width: 62rem; margin: 0.3rem auto; }
@media (max-width: 40rem) { nav a { margin-left: 0.8rem; } .hero h1 { font-size: 1.5rem; } }
"""


def llms_txt(places, updated, full=False):
    lines = [
        "# Quiet Places",
        "",
        f"> Bilingual directory of places to log off in Mexico: calm towns, artist residencies, wellness hubs, and retreat houses. One canonical page per place, verified from public sources, updated {updated}. Contact happens on the place's own channel.",
        "",
        "Every place below has an English and a Spanish page with structured data. Price bands are per person per night equivalents for stays, per day for programs. Free inclusion, no feeds, no reviews.",
        "",
        "## Places, English",
    ]
    for p in places:
        line = f"- [{p['name']}]({page_url(p['slug'], 'en')}): {p['tagline_en']}"
        if full:
            line += f" {p['desc_en']}"
        lines.append(line)
    lines += ["", "## Lugares, español"]
    for p in places:
        line = f"- [{p['name']}]({page_url(p['slug'], 'es')}): {p['tagline_es']}"
        if full:
            line += f" {p['desc_es']}"
        lines.append(line)
    lines += [
        "",
        "## Residency match",
        f"- [Residency match]({page_url(None, 'en', 'match')}): two sided placement, hubs and practitioners, hand matched.",
        f"- [Vinculación de residencias]({page_url(None, 'es', 'match')}): vinculación artesanal entre hubs y practicantes.",
        "",
        "## Method",
        f"- [Methodology]({page_url(None, 'en', 'home')}#methodology): verification states, price bands, inclusion rules.",
    ]
    return "\n".join(lines) + "\n"


def sitemap(places):
    urls = [("en", "home", None), ("es", "home", None), ("en", "match", None), ("es", "match", None)]
    urls += [("en", "place", p["slug"]) for p in places] + [("es", "place", p["slug"]) for p in places]
    items = []
    for lang, kind, slug in urls:
        url = page_url(slug, lang, kind) if kind != "place" else page_url(slug, lang)
        alts = ""
        if kind in ("home", "match"):
            other = page_url(slug, "es" if lang == "en" else "en", kind)
        else:
            other = page_url(slug, "es" if lang == "en" else "en")
        for code, href in (("en", url if lang == "en" else other), ("es", url if lang == "es" else other)):
            alts += f'    <xhtml:link rel="alternate" hreflang="{code}" href="{escape(href, quote=True)}"/>\n'
        items.append(
            f"  <url>\n    <loc>{escape(url, quote=True)}</loc>\n{alts}  </url>"
        )
    body = "\n".join(items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{body}\n</urlset>\n"
    )


def build_into(outdir: Path):
    raw = load_data()
    places = raw["places"]
    updated = raw["meta"]["updated"]
    slugs = [p["slug"] for p in places]
    if len(slugs) != len(set(slugs)):
        raise SystemExit("duplicate slugs in data/places.json")
    for p in places:
        if p["focus"] not in FOCUSES:
            raise SystemExit(f"unknown focus {p['focus']!r} on {p['slug']}")
        if p["status"] not in STATUS_LABEL:
            raise SystemExit(f"unknown status {p['status']!r} on {p['slug']}")
        if p["band"] not in BAND_RANGE:
            raise SystemExit(f"unknown band {p['band']!r} on {p['slug']}")
        if p.get("price_unit", "night") not in PRICE_UNIT:
            raise SystemExit(f"unknown price_unit {p['price_unit']!r} on {p['slug']}")

    out = Path(outdir)
    (out / "places").mkdir(parents=True, exist_ok=True)
    (out / "es" / "lugares").mkdir(parents=True, exist_ok=True)
    (out / "match").mkdir(parents=True, exist_ok=True)
    (out / "es" / "vinculacion").mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(parents=True, exist_ok=True)

    (out / "index.html").write_text(home_page(places, "en", updated), encoding="utf-8")
    (out / "es" / "index.html").write_text(home_page(places, "es", updated), encoding="utf-8")
    for p in places:
        (out / "places" / f"{p['slug']}.html").write_text(place_page(p, "en", updated), encoding="utf-8")
        (out / "es" / "lugares" / f"{p['slug']}.html").write_text(place_page(p, "es", updated), encoding="utf-8")
    (out / "match" / "index.html").write_text(match_page("en", updated), encoding="utf-8")
    (out / "es" / "vinculacion" / "index.html").write_text(match_page("es", updated), encoding="utf-8")
    (out / "assets" / "style.css").write_text(STYLE, encoding="utf-8")
    (out / "llms.txt").write_text(llms_txt(places, updated), encoding="utf-8")
    (out / "llms-full.txt").write_text(llms_txt(places, updated, full=True), encoding="utf-8")
    (out / "sitemap.xml").write_text(sitemap(places), encoding="utf-8")
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    return places


def main():
    places = build_into(DEFAULT_OUT)
    print(f"built {len(places)} place pages x2 languages into {DEFAULT_OUT}")


if __name__ == "__main__":
    main()
