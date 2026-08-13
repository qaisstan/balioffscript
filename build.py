#!/usr/bin/env python3
"""
Bali Off Script — static site builder.

Usage:  python3 build.py

Reads every .md file in content/, writes plain HTML into docs/.
No dependencies. No database. Push docs/ to GitHub Pages.

To add a page: copy any file in content/, change the frontmatter and body,
run this script again, commit.
"""

import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "assets")

SITE_NAME = "Bali Off Script"

# BASE is the path the site is served from, with no trailing slash.
#
#   ""                 site lives at a domain root  (custom domain)
#   "/balioffscript"   site lives at github.io/<repo>/  (GitHub project page)
#
# Every internal link is built from BASE, so moving the site is a two-line
# change here followed by `python3 build.py`. When baliofscript.com is bought
# and pointed at GitHub Pages, set BASE = "" and SITE_URL to the new domain.
BASE = "/balioffscript"
SITE_URL = "https://qaisstan.github.io" + BASE

INSTAGRAM = "https://instagram.com/baliofscript"
TAGLINE = "Straight answers on buying, building and living in Bali."

CATEGORIES = {
    "ownership": ("Ownership", "What foreigners can actually own, and how the three legal routes really work."),
    "visas": ("Visas", "Every stay permit that matters, with the real requirements and costs."),
    "company": ("Companies", "PT PMA setup, capital rules, licensing and the annual compliance load."),
    "tax": ("Tax", "Transaction taxes, rental income tax, NPWP and what actually gets enforced."),
    "building": ("Building & Zoning", "Zone colours, permits, the moratorium, and what it costs to build."),
    "rental": ("Rental & ROI", "Licensing, management fees, and yields that survive contact with reality."),
    "areas": ("Areas", "Land prices, demand and constraints, area by area."),
}

RISK_LABELS = {
    "critical": "Critical risk",
    "high": "High risk",
    "medium": "Worth checking",
    "info": "Reference",
}


# ---------------------------------------------------------------- parsing

def parse(path):
    raw = open(path, encoding="utf-8").read()
    if not raw.startswith("---"):
        raise ValueError(f"{path}: missing frontmatter")
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["body"] = body.strip()
    return meta


def md(text):
    """Minimal markdown. Enough for this site, deliberately small."""
    html, lines = [], text.split("\n")
    in_ul = in_table = False

    def close():
        nonlocal in_ul, in_table
        if in_ul:
            html.append("</ul>")
            in_ul = False
        if in_table:
            html.append("</tbody></table></div>")
            in_table = False

    def inline(s):
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
        return s

    for line in lines:
        s = line.strip()
        if not s:
            close()
            continue
        if s.startswith("| "):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if not in_table:
                close()
                html.append('<div class="table-wrap"><table><thead><tr>')
                html.append("".join(f"<th>{inline(c)}</th>" for c in cells))
                html.append("</tr></thead><tbody>")
                in_table = True
                continue
            html.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if s.startswith("- "):
            if not in_ul:
                close()
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{inline(s[2:])}</li>")
            continue
        if s.startswith("> "):
            close()
            html.append(f'<p class="callout">{inline(s[2:])}</p>')
            continue
        if s.startswith("### "):
            close()
            html.append(f"<h3>{inline(s[4:])}</h3>")
            continue
        if s.startswith("## "):
            close()
            html.append(f"<h2>{inline(s[3:])}</h2>")
            continue
        close()
        html.append(f"<p>{inline(s)}</p>")
    close()
    return "\n".join(html)


# ---------------------------------------------------------------- chrome

def head(title, desc, path):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITE_NAME}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Public+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/style.css">
<script>window.SITE_BASE={json.dumps(BASE)}</script>
</head>
<body>"""


def nav(active=""):
    on = ' class="on"'
    links = "".join(
        f'<a href="{BASE}/{k}/"{on if k == active else ""}>{v[0]}</a>'
        for k, v in CATEGORIES.items()
    )
    return f"""<header class="masthead">
<div class="wrap masthead-inner">
<a class="wordmark" href="{BASE}/"><span>Bali</span> Off Script</a>
<button class="menu-btn" aria-label="Menu" aria-expanded="false">Menu</button>
<nav class="nav">{links}<a class="nav-search" href="{BASE}/search/">Search</a></nav>
</div>
</header>"""


def footer():
    return f"""<footer class="foot">
<div class="wrap foot-inner">
<div>
<p class="foot-mark">Bali Off Script</p>
<p class="foot-note">{TAGLINE}</p>
</div>
<div class="foot-links">
<a href="{INSTAGRAM}">Instagram</a>
<a href="{BASE}/checklist/">Due diligence checklist</a>
<a href="{BASE}/disclaimer/">Disclaimer</a>
</div>
</div>
<div class="wrap foot-legal">
<p>General information, not legal or tax advice. Indonesian regulations change often and are applied inconsistently between regencies. Verify anything here with a licensed Indonesian notary, lawyer or tax consultant before you act on it.</p>
</div>
<script src="{BASE}/search.js" defer></script>
</footer>
</body>
</html>"""


def stamp(m):
    """The endorsement block — the signature element. Modelled on the
    validation panel stamped on the back of an Indonesian land certificate."""
    risk = m.get("risk", "info")
    rows = []
    if m.get("regulation"):
        rows.append(("Legal basis", f'<code>{m["regulation"]}</code>'))
    if m.get("applies"):
        rows.append(("Applies to", m["applies"]))
    rows.append(("Verified", m.get("verified", str(date.today()))))
    body = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    return f"""<aside class="stamp stamp-{risk}">
<span class="stamp-flag">{RISK_LABELS.get(risk, "Reference")}</span>
<dl>{body}</dl>
</aside>"""


def reel(url):
    if not url:
        return ""
    return f"""<section class="reel">
<h2 class="reel-h">Watch this one</h2>
<blockquote class="instagram-media" data-instgrm-permalink="{url}" data-instgrm-version="14"></blockquote>
<script async src="//www.instagram.com/embed.js"></script>
</section>"""


def cta():
    return f"""<section class="cta">
<p class="cta-k">Got a specific situation?</p>
<p class="cta-b">Every deal in Bali has a detail that breaks the general rule. Send me the details and I'll tell you what I'd check first.</p>
<a class="btn" href="{INSTAGRAM}">Ask on Instagram</a>
</section>"""


# ---------------------------------------------------------------- pages

def article(m, siblings):
    cat_name = CATEGORIES[m["category"]][0]
    path = f'/{m["category"]}/{m["slug"]}/'
    related = "".join(
        f'<li><a href="{BASE}/{s["category"]}/{s["slug"]}/">{s["question"]}</a></li>'
        for s in siblings if s["slug"] != m["slug"]
    )
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": m["question"],
            "acceptedAnswer": {"@type": "Answer", "text": m["summary"]},
        }],
    })
    return f"""{head(m["question"] + " — " + SITE_NAME, m["summary"], path)}
<script type="application/ld+json">{schema}</script>
{nav(m["category"])}
<main class="wrap article">
<p class="eyebrow"><a href="{BASE}/{m['category']}/">{cat_name}</a></p>
<h1>{m["question"]}</h1>
<p class="standfirst">{m["summary"]}</p>
{stamp(m)}
<div class="prose">{md(m["body"])}</div>
{reel(m.get("reel", ""))}
{cta()}
<section class="related">
<h2>Related</h2>
<ul>{related}</ul>
</section>
</main>
{footer()}"""


def category(key, pages):
    name, blurb = CATEGORIES[key]
    items = "".join(
        f"""<li class="card">
<a href="{BASE}/{key}/{p['slug']}/">
<h3>{p["question"]}</h3>
<p>{p["summary"]}</p>
</a></li>"""
        for p in pages
    )
    return f"""{head(name + " — " + SITE_NAME, blurb, f"/{key}/")}
{nav(key)}
<main class="wrap section">
<p class="eyebrow">Section</p>
<h1>{name}</h1>
<p class="standfirst">{blurb}</p>
<ul class="cards">{items}</ul>
</main>
{footer()}"""


def home(pages):
    counts = "".join(
        f"""<a class="ledger-row" href="{BASE}/{k}/">
<span class="ledger-name">{v[0]}</span>
<span class="ledger-rule"></span>
<span class="ledger-n">{len([p for p in pages if p["category"] == k])}</span>
</a>"""
        for k, v in CATEGORIES.items()
    )
    recent = "".join(
        f"""<li class="card"><a href="{BASE}/{p['category']}/{p['slug']}/">
<h3>{p["question"]}</h3><p>{p["summary"]}</p></a></li>"""
        for p in pages[:6]
    )
    return f"""{head(SITE_NAME + " — " + TAGLINE, TAGLINE, "/")}
{nav()}
<main>
<section class="hero wrap">
<h1 class="hero-h">You cannot own land in Bali.<br><span>Three legal routes say otherwise.</span></h1>
<p class="hero-sub">Leasehold, Hak Pakai, or HGB through a PT PMA. Everything else being sold to you is a nominee arrangement — void since 1960, and a criminal offence in Bali since February 2026.</p>
<form class="hero-search" action="{BASE}/search/">
<input type="search" name="q" placeholder="Search: nominee, E33G, BPHTB, Pererenan…" aria-label="Search">
<button type="submit">Search</button>
</form>
</section>
<section class="wrap ledger-wrap">
<div class="ledger">{counts}</div>
</section>
<section class="wrap">
<h2 class="sec-h">Start here</h2>
<ul class="cards">{recent}</ul>
</section>
<section class="wrap">{cta()}</section>
</main>
{footer()}"""


def search_page():
    return f"""{head("Search — " + SITE_NAME, "Search every answer on the site.", "/search/")}
{nav()}
<main class="wrap section">
<p class="eyebrow">Search</p>
<h1>Find an answer</h1>
<form class="page-search" onsubmit="return false">
<input type="search" id="q" placeholder="Try: leasehold extension, PT PMA capital, Uluwatu" aria-label="Search" autofocus>
</form>
<p class="hits" id="hits"></p>
<ul class="cards" id="results"></ul>
</main>
{footer()}"""


def simple(slug, title, body):
    return f"""{head(title + " — " + SITE_NAME, title, f"/{slug}/")}
{nav()}
<main class="wrap article">
<h1>{title}</h1>
<div class="prose">{md(body)}</div>
</main>
{footer()}"""


# ---------------------------------------------------------------- run

def write(path, html):
    full = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    pages = sorted(
        (parse(os.path.join(CONTENT, f)) for f in os.listdir(CONTENT) if f.endswith(".md")),
        key=lambda p: p.get("order", "99"),
    )

    for p in pages:
        sib = [s for s in pages if s["category"] == p["category"]][:5]
        write(f'/{p["category"]}/{p["slug"]}/', article(p, sib))

    for k in CATEGORIES:
        cat_pages = [p for p in pages if p["category"] == k]
        write(f"/{k}/", category(k, cat_pages))

    write("/", home(pages))
    write("/search/", search_page())
    write("/disclaimer/", simple("disclaimer", "Disclaimer", DISCLAIMER))
    write("/checklist/", simple("checklist", "Due diligence checklist", CHECKLIST))

    index = [{
        "t": p["question"],
        "s": p["summary"],
        "u": f'{BASE}/{p["category"]}/{p["slug"]}/',
        "c": CATEGORIES[p["category"]][0],
        "b": re.sub(r"[#*`|>\-]", " ", p["body"])[:2000],
    } for p in pages]
    open(os.path.join(OUT, "search-index.json"), "w", encoding="utf-8").write(json.dumps(index))

    urls = ["/", "/search/", "/checklist/", "/disclaimer/"] + [f"/{k}/" for k in CATEGORIES] + \
           [f'/{p["category"]}/{p["slug"]}/' for p in pages]
    sm = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    # Stops GitHub running Jekyll over the output. Without it the build breaks.
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

    # No CNAME file is written. GitHub reads CNAME as "serve this site at this
    # domain", so writing one for a domain that isn't registered and pointed at
    # Pages takes the site offline. Once baliofscript.com is bought and its DNS
    # points here, set the domain in Settings > Pages and GitHub commits its own
    # CNAME file — then set BASE = "" above and rebuild.

    for f in os.listdir(ASSETS):
        shutil.copy(os.path.join(ASSETS, f), os.path.join(OUT, f))

    print(f"Built {len(pages)} answers + {len(CATEGORIES)} sections into docs/")


DISCLAIMER = """
Bali Off Script publishes general information about Indonesian property, immigration and tax rules. It is not legal advice, tax advice, or financial advice, and reading it does not create an adviser relationship.

Indonesian regulations change frequently and are applied inconsistently between regencies and between individual government offices. A rule that held last quarter in Badung may be administered differently this quarter in Tabanan. Figures on this site — minimum property values, capital thresholds, tax rates, visa income requirements — are the ones in force on the date stamped on each page, and they move.

Before you sign anything, transfer any money, or rely on any structure described here, verify it with a licensed Indonesian notary or PPAT, an Indonesian lawyer, and a registered tax consultant. Engage your own, not the seller's.

Every page carries a verification date. If a page is more than six months old, treat the numbers as a starting point for your own checking rather than a current fact.
"""

CHECKLIST = """
Print this. Take it to viewings. If a seller or agent gets defensive about any line on it, that is the answer.

## Before you pay a deposit

- Original certificate sighted — SHM, SHGB or SHP, not a photocopy, not a photo
- Certificate verified at the local BPN office by your own notary
- Land physically walked with GPS against the cadastral drawing
- Zoning confirmed on GISTARU or at the regency planning office — not from the agent
- Zoning permits your intended use (pink for commercial rental; yellow and green do not)
- No hak tanggungan (mortgage or lien) registered against the title
- No dispute, no overlapping certificate, no sertifikat ganda
- Seller identity confirmed against KTP and family card
- Spouse consent obtained where land is joint marital property
- All heirs identified and consenting where the land came through inheritance
- PBB (annual land tax) receipts current, no arrears

## Before you sign

- Access road confirmed as legal right of way, in writing, with width recorded
- Setbacks checked — beach, river, cliff, and any temple or sacred-site buffer
- PBG (building permit) exists for every structure on the plot
- SLF (fitness certificate) issued
- If leasehold: extension clause is unconditional, priced or formula-based, and binds the owner's heirs and successors
- If leasehold: transfer and sublease rights are explicit
- If buying a company: full corporate, tax and licensing due diligence, and confirmation the LKPM reports are filed
- Your own notary or PPAT engaged — not the one the seller brought

## Before you complete

- Funds moving by bank transfer only, never cash
- BPHTB and seller's PPh calculated and provably paid before the deed
- Deed executed in front of a PPAT, not a private agreement
- Registration at BPN confirmed, and you hold the receipt
- Every promise made verbally by the agent is written into the deed, or it does not exist

> If you are being told to move fast, that is the pressure working. Nothing legitimate in Indonesian land transfer requires you to skip a step.
"""


if __name__ == "__main__":
    main()
