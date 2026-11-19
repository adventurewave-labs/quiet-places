"""Relocation guide (PRD 05) templates and loaders.

National topic copy lives here; per-town overlays live in data/relocation.json.
Imports build lazily at call time to avoid a circular import.
"""

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELOCATION_FILE = ROOT / "data" / "relocation.json"

TOPICS = [
    {
        "key": "visa",
        "title_en": "Visa path",
        "title_es": "Ruta de visa",
        "body_en": "Mexico grants temporary residency at a consulate before you move: you present financial solvency, a job offer, or a family tie, receive the visa in your passport, then exchange it for a residency card at an Instituto Nacional de Migración office in Mexico. Permanent residency works the same way with higher thresholds. Figures and rules change, so read the current requirements before you apply.",
        "body_es": "México otorga la residencia temporal en un consulado antes de mudarte: presentas solvencia económica, una oferta de trabajo o un vínculo familiar, recibes la visa en tu pasaporte y luego la canjeas por una tarjeta de residencia en una oficina del Instituto Nacional de Migración en México. La residencia permanente sigue el mismo camino con umbrales más altos. Las cifras y reglas cambian, así que lee los requisitos vigentes antes de aplicar.",
        "sources": ["inm"],
    },
    {
        "key": "healthcare",
        "title_en": "Healthcare",
        "title_es": "Salud",
        "body_en": "Public coverage runs through IMSS, which residents join through employment or a voluntary scheme, and many long stayers pair it with private consultorios that cost a fraction of US prices. Bring prescriptions in their original boxes, get a checkup before the move, and decide your insurance mix while you are healthy rather than after.",
        "body_es": "La cobertura pública corre por el IMSS, al que los residentes entran por empleo o por un esquema voluntario, y quien se queda largo suele combinarla con consultorios privados que cuestan una fracción de los precios de Estados Unidos. Trae las recetas en su caja original, hazte un chequeo antes de mudarte y define tu mezcla de seguros mientras estás sano, no después.",
        "sources": ["imss"],
    },
    {
        "key": "banking",
        "title_en": "Banking",
        "title_es": "Banca",
        "body_en": "With a residency card, a CURP, and proof of address, national banks open accounts, and fintech apps open faster and are accepted nearly everywhere. SPEI transfers move money between accounts in seconds, and cash still runs markets and small shops. Expect the first account to take an in person visit, and keep documents from your visa path handy.",
        "body_es": "Con tarjeta de residencia, CURP y comprobante de domicilio, los bancos nacionales abren cuentas, y las apps fintech abren más rápido y se aceptan en casi todo. Las transferencias SPEI mueven dinero entre cuentas en segundos, y el efectivo sigue mandando en mercados y negocios pequeños. Espera que la primera cuenta tome una visita presencial y ten a mano los documentos de tu trámite de visa.",
        "sources": [],
    },
    {
        "key": "internet",
        "title_en": "Internet",
        "title_es": "Internet",
        "body_en": "The fixed market is led by Telmex, izzi, Totalplay, and Axtel, with AT&T and Telcel at the front of mobile, all under the watch of the Instituto Federal de Telecomunicaciones. Coverage is strong on main streets, thinner at town edges, and satellite fills remote casitas. The honest method is the same everywhere: test with your own devices at the exact address before you sign.",
        "body_es": "El mercado fijo lo encabezan Telmex, izzi, Totalplay y Axtel, con AT&T y Telcel al frente del móvil, todo bajo la vigilancia del Instituto Federal de Telecomunicaciones. La cobertura es fuerte en las calles principales, más delgada en las orillas, y el satélite llena las casitas remotas. El método honesto es el mismo en todos lados: prueba con tus propios equipos en la dirección exacta antes de firmar.",
        "sources": ["ift"],
    },
    {
        "key": "cost",
        "title_en": "Cost of a month",
        "title_es": "Costo de un mes",
        "body_en": "Real monthly figures are published only after a sweep measures them, so no town guide here invents a number. The honest frame: rents move with season and street, small town baskets run below Mexico City, INEGI publishes the national price statistics, and the variables that matter are housing, transport, and how often you eat out.",
        "body_es": "Las cifras mensuales reales se publican solo después de que un barrido las mida, así que ninguna guía de pueblo inventa un número. El marco honesto: las rentas se mueven con la temporada y la calle, las canastas de pueblo corren por debajo de la Ciudad de México, el INEGI publica las estadísticas nacionales de precios y las variables que importan son vivienda, transporte y cuánto comes fuera.",
        "sources": ["inegi"],
    },
]


def guard(strings):
    from build import FORBIDDEN_CHARS

    bad = []
    for label, text in strings:
        for ch in FORBIDDEN_CHARS:
            if ch in text:
                bad.append(f"{label}: contains {ch!r}")
    if bad:
        raise SystemExit("em or en dash in customer-facing copy:\n" + "\n".join(bad))


def load_relocation():
    import re

    raw = json.loads(RELOCATION_FILE.read_text(encoding="utf-8"))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw["meta"]["updated"]):
        raise SystemExit(f"relocation meta.updated {raw['meta']['updated']!r} is not an ISO date")
    slugs = set()
    for town in raw["towns"]:
        for field in ("slug", "place_slug"):
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", town[field]):
                raise SystemExit(f"relocation {field} {town[field]!r} is not filename safe")
        if town["slug"] in slugs:
            raise SystemExit(f"duplicate relocation slug {town['slug']!r}")
        slugs.add(town["slug"])
    for src in raw["sources"]:
        if not re.fullmatch(r"https?://\S+", src["url"], re.IGNORECASE):
            raise SystemExit(f"unsafe source url for {src['key']!r}: {src['url']!r}")
    strings = [("meta.updated", raw["meta"]["updated"])]
    for src in raw["sources"]:
        strings.append((f"source.{src['key']}", src["name_en"]))
        strings.append((f"source.{src['key']}", src["name_es"]))
    for town in raw["towns"]:
        for field, value in town.items():
            if isinstance(value, str):
                strings.append((f"{town['slug']}.{field}", value))
    guard(strings)
    return raw


def guide_page(town, lang, sources, updated):
    from build import BASE_URL, guide_path, guide_url, layout

    es = lang == "es"

    def t(en, es_):
        return es_ if es else en

    title = f"{town['name']} | {t('Relocation guide', 'Guía de mudanza')} | {t('Quiet Places', 'Quiet Places')}"
    lead = town["lead_es"] if es else town["lead_en"]
    method = sources["meta"]["method_es"] if es else sources["meta"]["method_en"]
    sections = []
    for topic in TOPICS:
        heading = topic["title_es"] if es else topic["title_en"]
        body = topic["body_es"] if es else topic["body_en"]
        note = town[f"{topic['key']}_note_es"] if es else town[f"{topic['key']}_note_en"]
        src_names = []
        for key in topic["sources"]:
            src = next(x for x in sources["sources"] if x["key"] == key)
            src_names.append(
                f'<a href="{escape(src["url"])}" rel="noopener">{escape(src["name_es"] if es else src["name_en"])}</a>'
            )
        src_line = ""
        if src_names:
            src_line = f'<p class="note">{t("Source: ", "Fuente: ")}{" · ".join(src_names)}</p>'
        sections.append(
            f"<section>\n<h2>{escape(heading)}</h2>\n<p>{escape(body)}</p>\n<p>{escape(note)}</p>\n{src_line}\n</section>"
        )
    sections_html = "\n".join(sections)
    place_href = f"/places/{town['place_slug']}" if not es else f"/es/lugares/{town['place_slug']}"
    name = escape(town["name"])
    next_step = t(
        f'Next step: the <a href="{escape(place_href)}">directory page for {name}</a> lists quiet places to stay, banded and verified, and contact happens on each place\'s own channel.',
        f'Siguiente paso: la <a href="{escape(place_href)}">página del directorio de {name}</a> lista lugares tranquilos donde quedarse, con banda y verificación, y el contacto sucede en el canal de cada lugar.',
    )
    content = f"""<nav class="crumb"><a href="{guide_path(None, lang)}">{t('Relocation guides', 'Guías de mudanza')}</a> / {escape(town['name'])}</nav>
<article>
  <h1>{escape(town['name'])}, {escape(town['state'])}</h1>
  <p class="answer">{escape(lead)}</p>
  <p class="note">{escape(method)}</p>
  {sections_html}
  <section class="cta">
    <h2>{t('Where to stay', 'Dónde quedarse')}</h2>
    <p>{next_step}</p>
  </section>
</article>"""
    return layout(
        lang,
        title,
        lead,
        guide_url(town["slug"], lang),
        {"en": guide_url(town["slug"], "en"), "es": guide_url(town["slug"], "es")},
        json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": f"{town['name']}: {t('relocation practicalities', 'prácticos de mudanza')}",
                "description": lead,
                "inLanguage": "es-MX" if es else "en",
                "url": guide_url(town["slug"], lang),
                "about": {
                    "@type": "TouristDestination",
                    "name": town["name"],
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": town["name"],
                        "addressRegion": town["state"],
                        "addressCountry": "MX",
                    },
                },
            },
            ensure_ascii=False,
        ),
        content,
        updated,
        guide_path(town["slug"], "es" if not es else "en"),
    )


def guides_index(towns, lang, sources, updated):
    from build import guide_path, guide_url, layout

    es = lang == "es"

    def t(en, es_):
        return es_ if es else en

    title = t(
        "Relocation guides: visas, healthcare, banking, internet, costs",
        "Guías de mudanza: visas, salud, banca, internet, costos",
    )
    desc = t(
        "Practical guides per town: the visa path, healthcare, banking, internet, and the real cost of a month, bilingual and refreshed every quarter.",
        "Guías prácticas por pueblo: la ruta de visa, la salud, la banca, el internet y el costo real de un mes, bilingües y renovadas cada trimestre.",
    )
    items = []
    for town in towns:
        href = guide_path(town["slug"], lang)
        lead = town["lead_es"] if es else town["lead_en"]
        items.append(
            f'    <li class="card">\n      <a href="{href}">\n        <span class="name">{escape(town["name"])}</span>\n        <span class="where">{escape(town["state"])}, México</span>\n        <span class="tagline">{escape(lead)}</span>\n      </a>\n    </li>'
        )
    method = sources["meta"]["method_es"] if es else sources["meta"]["method_en"]
    content = f"""<section class="hero">
  <h1>{t('Relocation guides', 'Guías de mudanza')}</h1>
  <p class="answer">{escape(desc)}</p>
  <p class="intro">{escape(method)}</p>
</section>
<section>
  <ul class="grid">
{chr(10).join(items)}
  </ul>
</section>"""
    return layout(
        lang,
        title,
        desc,
        guide_url(None, lang),
        {"en": guide_url(None, "en"), "es": guide_url(None, "es")},
        json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "url": guide_url(None, lang),
                "inLanguage": "es-MX" if es else "en",
                "description": desc,
            },
            ensure_ascii=False,
        ),
        content,
        updated,
        guide_path(None, "es" if not es else "en"),
    )
