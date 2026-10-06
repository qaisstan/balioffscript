"""Topic guides: one free PDF per buyer topic, built from the site's own answers.

The Buyer's Kit (kit.py) stays the general lead magnet. A reader on a building page is offered
the build guide, on an ownership page the ownership guide, and so on: the same form, the same
lead flow, a guide that matches what they are reading. Every guide is the questions of its
topic, each with its short answer and a link to the full page, so nothing in it is new or
unchecked. English only for now; other languages keep the Buyer's Kit.

    python3 build.py                                   # writes the guide pages and landing pages
    python3 tools/make_pdfs.py http://localhost:8792   # prints the PDFs (kit + guides)
"""

import json
import os

import kit as K

GUIDES = {
    "build": dict(cats=["building"], title="The Bali Villa Build Guide",
                  sub="Zoning, permits, build costs and running costs: every question answered straight.",
                  pitch="Every building question on this site in one PDF: zone colours, PBG and SLF permits, what a villa really costs to build, and what it costs to run afterwards.",
                  points=["Zoning and the colour map, explained", "Permits: PBG, SLF and who signs what", "Real build and pool costs", "Water, septic and power before you buy land"],
                  path="/guides/villa-build/", land_title="Building a villa in Bali: free guide (PDF)",
                  land_desc="Free PDF: zoning, permits, build costs and running costs for a villa in Bali, every question answered."),
    "own": dict(cats=["ownership", "company"], title="Owning Property in Bali as a Foreigner",
                sub="Leasehold, Hak Pakai, PT PMA and the nominee trap, answered without the sales talk.",
                pitch="What a foreigner can actually own in Bali and the three legal routes, side by side. Leasehold, Hak Pakai, PT PMA, the nominee trap, and the clauses that protect you.",
                points=["Leasehold vs freehold vs Hak Pakai", "PT PMA: when it makes sense, and what it costs", "Why nominee deals fail", "Extensions, inheritance and resale"],
                path="/guides/ownership/", land_title="Can foreigners own property in Bali? Free guide (PDF)",
                land_desc="Free PDF: leasehold, Hak Pakai, PT PMA and nominee risk for foreigners buying property in Bali."),
    "rent": dict(cats=["rental", "tax"], title="The Bali Rental Income Guide",
                 sub="Licences, tax and the yields that survive real costs.",
                 pitch="What a Bali villa really earns: the licences you need to rent it out, the tax on rental income, management fees, occupancy, and the yield that is left at the end.",
                 points=["Licences you need to rent legally", "Tax on rental income, explained", "Management fees and occupancy", "Net yield, not the brochure number"],
                 path="/guides/rental-income/", land_title="Bali villa rental income and tax: free guide (PDF)",
                 land_desc="Free PDF: rental licences, tax, management fees and real net yields for a villa in Bali."),
    "areas": dict(cats=["areas"], title="Where to Buy in Bali: Area by Area",
                  sub="Land prices, demand and the catch in every area.",
                  pitch="Every area worth buying in, from Canggu to Uluwatu to the quiet coast: land prices, who rents there, what is changing, and the catch nobody mentions.",
                  points=["Land prices by area", "Where rental demand really is", "What is changing in each area", "The catch in every area"],
                  path="/guides/where-to-buy/", land_title="Where to buy property in Bali: free area guide (PDF)",
                  land_desc="Free PDF: land prices, rental demand and the catch in every Bali area worth buying in."),
    "move": dict(cats=["living", "visas"], title="Moving to Bali: Visas, Living and Buying",
                 sub="The visas, the real cost of living, and what to settle before you buy.",
                 pitch="Everything to settle before you move: which visa fits, what life here really costs, schools, health, and when buying makes more sense than renting.",
                 points=["Which visa fits your plan", "What living here really costs", "Schools, health and daily life", "Rent first or buy?"],
                 path="/guides/moving-to-bali/", land_title="Moving to Bali: free visa and living guide (PDF)",
                 land_desc="Free PDF: visas, cost of living and what to settle before buying property in Bali."),
}
BY_CAT = {c: k for k, g in GUIDES.items() for c in g["cats"]}


def for_category(cat):
    return BY_CAT.get(cat)


def pdf_url(B, key):
    return f"{B.BASE}/kit/{K.TOKEN}/bali-{key}-guide.pdf"


def doc_path(key):
    return f"/kit/{K.TOKEN}/guide-{key}/"


def ui(key):
    """The Buyer's Kit wording with this guide's title, pitch and points."""
    g = GUIDES[key]
    u = dict(K.UI["en"])
    u.update(title=g["title"], pitch=g["pitch"], points=g["points"], dl="Download the guide (PDF)",
             btn="Send me the guide", land_title=g["land_title"], land_desc=g["land_desc"],
             land_h=g["title"], land_p=g["sub"])
    return u


def doc_page(B, key, pages):
    """The guide itself as a printable page: every question of its topics, its short answer, a link."""
    g = GUIDES[key]
    sections = []
    for cat in g["cats"]:
        ps = sorted([p for p in pages if p["category"] == cat], key=lambda p: (str(p.get("order", "99")), p["question"]))
        if not ps:
            continue
        items = "".join(
            f'<div class="gd-q"><h3>{p["question"]}</h3><p>{p["summary"]}</p>'
            f'<p class="gd-l"><a href="{B.SITE_URL}/{cat}/{p["slug"]}/">Full answer: balioffscript.com/{cat}/{p["slug"]}/</a></p></div>'
            for p in ps)
        sections.append(f'<h2>{B.CATEGORIES[cat][0]}</h2><p class="gd-intro">{B.CATEGORIES[cat][1]}</p>{items}')
    from urllib.parse import quote
    wa = f"https://wa.me/{B.LEAD_WHATSAPP}?text=" + quote(f"Hi Kai, I read {g['title']}. Can you help me with a property in Bali?")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{g["title"]} | {B.SITE_NAME}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Public+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{B.BASE}/style.css">
<style>
.gd-q{{break-inside:avoid;padding:0.6rem 0 0.9rem;border-bottom:1px solid var(--rule)}}
.gd-q h3{{font-size:1.05rem;margin:0 0 0.35rem}}
.gd-q p{{margin:0 0 0.3rem}}
.gd-l{{font-size:0.8rem}} .gd-l a{{color:var(--slate)}}
.gd-intro{{color:var(--slate);margin-bottom:0.6rem}}
.kitdoc h2{{break-before:page}}
.gd-how{{background:var(--paper-2);border-radius:10px;padding:1rem 1.2rem;margin:1rem 0 1.5rem}}
</style>
</head>
<body class="kitdoc">
<section class="kd-cover" style="background-image:linear-gradient(180deg,rgba(22,25,29,0) 0%,rgba(22,25,29,.1) 40%,rgba(22,25,29,.88) 78%),url({K.img_url(B, 'cover', 1000, 1414)})">
<p class="kd-brand">Bali Off Script</p>
<h1 class="kd-title">{g["title"]}</h1>
<p class="kd-sub">{g["sub"]}</p>
<p class="kd-by">By Kai, Strategic Investment Adviser<br>balioffscript.com</p>
</section>
<main class="kd-body prose">
<div class="gd-how"><p><b>How to use this guide.</b> Every question buyers ask me about this topic, each with the short answer. The link under each one opens the full answer with the sources. Rules change: check the date on the page, and verify anything before you sign with your own notary, lawyer and tax consultant.</p></div>
{"".join(sections)}
<h2>Want a second pair of eyes?</h2>
<p>I look at deals before people sign: the documents, the zoning, the lease and the numbers. Message me with what you are looking at.</p>
<p class="kd-cta"><a href="{wa}">WhatsApp Kai</a> · <a href="{B.SITE_URL}/">balioffscript.com</a></p>
</main>
</body>
</html>"""


def landing(B, key, head_fn, nav_html, footer_html, box_html):
    g, u = GUIDES[key], ui(key)
    schema = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": u["land_title"],
                         "description": u["land_desc"], "url": B.SITE_URL + g["path"], "inLanguage": "en",
                         "isPartOf": {"@type": "WebSite", "name": B.SITE_NAME, "url": B.SITE_URL}})
    pts = "".join(f"<li>{p}</li>" for p in g["points"])
    return f"""{head_fn(u["land_title"], u["land_desc"], g["path"])}
<script type="application/ld+json">{schema}</script>
{nav_html}
<main class="wrap article kit-land">
<p class="eyebrow">Free PDF</p>
<h1>{g["title"]}</h1>
<p class="standfirst">{g["sub"]}</p>
<div class="prose"><ul>{pts}</ul></div>
{box_html}
</main>
{footer_html}"""


def index_page(B, head_fn, nav_html, footer_html):
    cards = "".join(
        f'<a class="gd-card" href="{B.BASE}{g["path"]}"><b>{g["title"]}</b><span>{g["sub"]}</span></a>'
        for g in GUIDES.values())
    kit_card = (f'<a class="gd-card" href="{B.BASE}{K.LANDING["en"]}"><b>{K.UI["en"]["title"]}</b>'
                f'<span>The checklist, 20 questions, 12 lease clauses and 15 red flags before you sign.</span></a>')
    return f"""{head_fn("Free Bali property guides (PDF)", "Free PDF guides for buying property in Bali: ownership, building, rental income, areas and moving here.", "/guides/")}
{nav_html}
<main class="wrap article">
<p class="eyebrow">Free PDFs</p>
<h1>Free guides for buying in Bali</h1>
<p class="standfirst">Pick the one that matches where you are. Each is every question buyers ask me on that topic, answered straight.</p>
<div class="gd-grid">{kit_card}{cards}</div>
</main>
{footer_html}"""
