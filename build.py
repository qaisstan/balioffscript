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

# ---- Where the site is published -------------------------------------------
#
# To move the site onto the custom domain, change this ONE line to
# DOMAIN = "balioffscript.com" and run `python3 build.py`. Everything below
# follows from it: the link prefix, canonical URLs, the sitemap, and the CNAME
# file GitHub needs.
#
# Only set this once the domain is bought AND its DNS points at GitHub Pages.
# A CNAME file naming a domain that doesn't resolve takes the site offline.
DOMAIN = "balioffscript.com"

# BASE is the path the site is served from, no trailing slash. A custom domain
# serves from the root; without one this is a GitHub project page living under
# /balioffscript/ (the account's user site is taken by an unrelated project).
BASE = "" if DOMAIN else "/balioffscript"
SITE_URL = f"https://{DOMAIN}" if DOMAIN else f"https://qaisstan.github.io{BASE}"

INSTAGRAM = "https://www.instagram.com/balioffscript/"

# ---- Analytics --------------------------------------------------------------
#
# GA4_ID: paste the Measurement ID from Google Analytics (looks like
#   "G-XXXXXXXXXX"). Leave empty and no tracking script is emitted at all.
# GSC_VERIFY: the token from Google Search Console's "HTML tag" verification
#   method — the content="..." value only, not the whole tag. Search Console is
#   the one that shows which search terms people found you with.
GA4_ID = "G-9LMCFLT4XX"
GSC_VERIFY = ""

AUTHOR = "Kai"
AUTHOR_ROLE = "Bali property adviser"
# Drop the file in assets/ under this name. If it isn't there, the portrait is
# simply skipped rather than rendering a broken image on all 27 pages.
AUTHOR_PHOTO = "kai.jpg"
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

# Category landing pages were thin — a heading and a list of cards. They are
# also the pages best placed to rank for the broad terms ("bali property tax",
# "bali visa"), so each one gets a real introduction and an SEO title.
CATEGORY_SEO = {
    "ownership": (
        "Can foreigners own property in Bali?",
        "Foreigners cannot hold Hak Milik — Indonesian freehold — under any structure, "
        "including through a company or a spouse. Three lawful routes exist instead: a "
        "leasehold contract, Hak Pakai registered in your own name if you hold residency, "
        "or HGB held through a PT PMA for commercial use. Everything else being marketed "
        "to foreign buyers is a nominee arrangement, which has been void since 1960 and "
        "criminal in Bali since February 2026. These pages explain what each route gives "
        "you, what the certificate actually says, and the clauses that decide whether a "
        "lease is worth what you paid."),
    "visas": (
        "Indonesian visas and stay permits, explained",
        "The system was restructured in 2025 — 133 indices reduced to 110, and "
        "employer-sponsored work visas cut from 31 to 6 — so most visa advice written "
        "before then is wrong. The rule underneath it has not changed: you choose a permit "
        "by what you will actually do in Indonesia, not by how long you want to stay. "
        "These pages cover the investor and remote-worker routes, Second Home, family "
        "permits, permanent residence, and the pre-investment visa built for property "
        "due diligence."),
    "company": (
        "PT PMA setup, capital and licensing in Bali",
        "A PT PMA is the vehicle foreigners use to hold HGB and run a business in "
        "Indonesia. Forming one is the easy part. The load is the capital requirement, the "
        "business classification that decides what you may lawfully do, and the annual "
        "reporting that continues whether or not the company trades. Bali also closed "
        "several accommodation classifications to new foreign-owned companies in July "
        "2026, which changed what a villa PT PMA can legally be used for."),
    "tax": (
        "Bali property tax: what buyers actually pay",
        "Transaction tax, rental income tax, and the residency rule that decides which "
        "country taxes you. The buyer's transfer tax runs around 5% on a titled transfer "
        "and nothing on a leasehold, which is a larger difference than most buyers "
        "realise. Rental income attracts its own treatment, and the 10% regional "
        "accommodation tax is collected from guests and remitted by the operator — it is "
        "not income. Spend more than 183 days here and you are an Indonesian tax resident "
        "regardless of your visa."),
    "building": (
        "Bali zoning, PBG permits and what you can build",
        "Zone colour tells you whether you may build. KDB and KLB tell you how much — and "
        "a green-zone plot with a 10% footprint cap can be entirely legal and still "
        "useless as a rental business. PBG is the building approval and SLF confirms the "
        "finished building is fit for use; neither is a formality, and timelines run from "
        "3 to 6 months in Denpasar to 10 to 12 months in Badung for an existing "
        "unpermitted structure. Setbacks come off before any of it."),
    "rental": (
        "Bali villa rental yields and licensing",
        "Advertised yields are gross. After platform commission, the 10% regional tax, "
        "management fees, staffing, refurbishment and income tax, an advertised 12% "
        "commonly lands between 4% and 6% — and on a leasehold, amortising the premium "
        "over the years remaining can take it below zero. Licensing is the separate "
        "question underneath: whether nightly rental is permitted on that plot at all, "
        "and which business classification the operator holds."),
    "areas": (
        "Where to buy in Bali, area by area",
        "Canggu has the liquidity and the strictest enforcement. The Bukit has the highest "
        "nightly rates and the setback rules that produced the 2025 Bingin demolitions. "
        "Sanur has the fastest permits on the island. Ubud has small buildable ratios and "
        "sacred-site buffers. Tabanan has the clearest appreciation story and the hardest "
        "route to a commercial accommodation licence. These pages cover what each area "
        "costs and the specific constraint that breaks deals there."),
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

def title_tag(t):
    """Google truncates around 60 characters. Append the site name only when
    it still fits — the question itself carries the keywords, the brand does
    not, so the brand is what gets dropped."""
    if SITE_NAME in t:
        return t
    full = f"{t} — {SITE_NAME}"
    return full if len(full) <= 60 else t


def robots_meta(path):
    """Utility pages have nothing to rank for. Keeping them out of the index
    stops them being counted as thin content against the site."""
    return '\n<meta name="robots" content="noindex,follow">' if path in ("/search/",) else ""


def head(title, desc, path):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_tag(title)}</title>
<meta name="description" content="{desc}">{robots_meta(path)}
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{title}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/{AUTHOR_PHOTO}">
<meta name="twitter:card" content="summary">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITE_NAME}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Public+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/style.css">
<link rel="icon" href="{BASE}/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="{BASE}/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{BASE}/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{BASE}/favicon-16x16.png">
<link rel="apple-touch-icon" href="{BASE}/apple-touch-icon.png">
<link rel="manifest" href="{BASE}/site.webmanifest">
<meta name="theme-color" content="#9e2b20">
<script>window.SITE_BASE={json.dumps(BASE)}</script>
{analytics()}</head>
<body>"""


def analytics():
    """Emitted only when the IDs above are filled in."""
    out = ""
    if GSC_VERIFY:
        out += f'<meta name="google-site-verification" content="{GSC_VERIFY}">\n'
    if GA4_ID:
        out += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>\n'
                "<script>window.dataLayer=window.dataLayer||[];"
                "function gtag(){{dataLayer.push(arguments);}}"
                "gtag('js',new Date());"
                f"gtag('config','{GA4_ID}');</script>\n").replace("{{", "{").replace("}}", "}")
    return out


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
<nav class="nav"><div class="nav-inner">{links}<a class="nav-calc" href="{BASE}/calculator/">Calculator</a><a class="nav-search" href="{BASE}/search/">Search</a></div></nav>
</div>
</header>"""


def footer(extra=""):
    return f"""<footer class="foot">
<div class="wrap foot-inner">
<div>
<p class="foot-mark">Bali Off Script</p>
<p class="foot-note">{TAGLINE}</p>
</div>
<div class="foot-links">
<a class="ig-link" href="{INSTAGRAM}" rel="me">{ig_logo("ig ig-sm")}<span>@balioffscript</span></a>
<a href="{BASE}/calculator/">ROI calculator</a>
<a href="{BASE}/check/">What I'd check first</a>
<a href="{BASE}/checklist/">Due diligence checklist</a>
<a href="{BASE}/disclaimer/">Disclaimer</a>
</div>
</div>
<div class="wrap foot-legal">
<p>General information, not legal or tax advice. Indonesian regulations change often and are applied inconsistently between regencies. Verify anything here with a licensed Indonesian notary, lawyer or tax consultant before you act on it.</p>
</div>
<script src="{BASE}/search.js" defer></script>{extra}
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


def ig_logo(cls="ig"):
    """Instagram glyph, inline so it needs no network request and inherits
    the surrounding ink colour."""
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">'
        '<path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41-.56-.22-.96-.48-1.38-.9-.42-.42-.68-.82-.9-1.38-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.31-1.46.72-2.13 1.38C1.35 2.68.94 3.35.63 4.14.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.31.79.72 1.46 1.38 2.13.67.67 1.34 1.07 2.13 1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56.79-.31 1.46-.72 2.13-1.38.67-.67 1.07-1.34 1.38-2.13.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91-.31-.79-.72-1.46-1.38-2.13C21.32 1.35 20.65.94 19.86.63c-.76-.3-1.64-.5-2.91-.56C15.67.01 15.26 0 12 0z"/>'
        '<path d="M12 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84zM12 16a4 4 0 1 1 4-4 4 4 0 0 1-4 4z"/>'
        '<circle cx="18.41" cy="5.59" r="1.44"/>'
        "</svg>"
    )


def portrait(cls="cta-photo"):
    """Rendered only when the photo is actually present, so a missing file
    degrades to a text-only block instead of a broken image on every page."""
    if not os.path.exists(os.path.join(ASSETS, AUTHOR_PHOTO)):
        return ""
    return (f'<img class="{cls}" src="{BASE}/{AUTHOR_PHOTO}" width="96" height="96" '
            f'loading="lazy" alt="{AUTHOR}, {AUTHOR_ROLE}">')


def cta(kicker="Got a specific situation?",
        body="Every deal in Bali has a detail that breaks the general rule. Send me the details and I'll tell you what I'd check first.",
        btn="Ask on Instagram"):
    return f"""<section class="cta">
<div class="cta-id">
{portrait()}
<div class="cta-said">
<p class="cta-k">{kicker}</p>
<p class="cta-b">{body}</p>
<p class="cta-by">{AUTHOR} — {AUTHOR_ROLE}</p>
</div>
</div>
<a class="btn" href="{INSTAGRAM}" rel="me">{ig_logo()}<span>{btn}</span></a>
</section>"""


# ---------------------------------------------------------------- pages

def article(m, siblings):
    cat_name = CATEGORIES[m["category"]][0]
    path = f'/{m["category"]}/{m["slug"]}/'
    related = "".join(
        f'<li><a href="{BASE}/{s["category"]}/{s["slug"]}/">{s["question"]}</a></li>'
        for s in siblings if s["slug"] != m["slug"]
    )
    # Two graphs: the FAQ entity Google uses for rich results, and an Article
    # with author and dates, which is what answer engines look for when
    # deciding whether a page is attributable and current.
    schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "FAQPage",
                "mainEntity": [{
                    "@type": "Question",
                    "name": m["question"],
                    "acceptedAnswer": {"@type": "Answer", "text": m["summary"]},
                }],
            },
            {
                "@type": "Article",
                "headline": m["question"],
                "description": m["summary"],
                "datePublished": m.get("verified", str(date.today())),
                "dateModified": m.get("verified", str(date.today())),
                "inLanguage": "en",
                "author": {"@type": "Person", "name": AUTHOR, "jobTitle": AUTHOR_ROLE,
                           "url": INSTAGRAM},
                "publisher": {"@type": "Organization", "name": SITE_NAME,
                              "url": SITE_URL},
                "mainEntityOfPage": {"@type": "WebPage", "@id": SITE_URL + path},
                "articleSection": cat_name,
                "citation": m.get("regulation", ""),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
                    {"@type": "ListItem", "position": 2, "name": cat_name,
                     "item": f'{SITE_URL}/{m["category"]}/'},
                    {"@type": "ListItem", "position": 3, "name": m["question"]},
                ],
            },
        ],
    })
    return f"""{head(m["question"], m["summary"], path)}
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
    seo_title, intro = CATEGORY_SEO[key]
    # Meta description has to fit Google's ~158 char cut; the intro is the
    # on-page copy that gives the landing page something to rank with.
    meta = (blurb if len(blurb) <= 158 else blurb[:155].rsplit(" ", 1)[0] + "…")
    cat_schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "name": seo_title, "description": meta,
             "url": f"{SITE_URL}/{key}/", "inLanguage": "en",
             "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
             "hasPart": [{"@type": "Article", "headline": q["question"],
                          "url": f'{SITE_URL}/{key}/{q["slug"]}/'} for q in pages]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": name}]},
        ],
    })
    return f"""{head(seo_title, meta, f"/{key}/")}
<script type="application/ld+json">{cat_schema}</script>
{nav(key)}
<main class="wrap section">
<p class="eyebrow">Section</p>
<h1>{seo_title}</h1>
<p class="standfirst">{blurb}</p>
<div class="prose section-intro"><p>{intro}</p></div>
<h2 class="sec-h">Every answer in this section</h2>
<ul class="cards">{items}</ul>
</main>
{footer()}"""


CHECK_ITEMS = [
    ("The plot", [
        "Exact location — regency and village, not 'Canggu area'",
        "Certificate type and number: Hak Milik, HGB, Hak Pakai, or a lease",
        "Whose name is on the certificate, and their authority to transact",
        "Land area, and the cadastral drawing against what you walked",
    ]),
    ("The zoning", [
        "RDTR designation for this parcel, from the regency, not the agent",
        "KDB and KLB figures — what you can actually build, not just whether you can",
        "Setbacks: beach, river, cliff, temple",
        "Whether LP2B or subak protections apply",
    ]),
    ("The building", [
        "PBG for every structure standing on the plot",
        "SLF issued, not 'being processed'",
        "If off-plan: what has actually been approved, with application numbers",
    ]),
    ("The business", [
        "The rental model — nightly, monthly, or genuine long-term residential",
        "Which KBLI classification the operator intends to use",
        "Whether that classification is open for new registration today",
        "Whether the NIB covers this location or only a company domicile",
    ]),
    ("The agreement", [
        "If leasehold: term remaining, and whether extension is priced or merely promised",
        "Whether transfer and sublease rights are explicit",
        "Whether the extension clause binds the owner's heirs and successors",
        "Who pays which taxes, in writing",
    ]),
]


def check_page():
    desc = ("The information I need to tell you whether a Bali property works — and the "
            "list of things that decide it, in the order they decide it.")
    blocks = "".join(
        f"""<section class="chk">
<h2>{title}</h2>
<ul class="chk-list">{''.join(f'<li>{i}</li>' for i in items)}</ul>
</section>"""
        for title, items in CHECK_ITEMS
    )
    return f"""{head("What I'd check first before you buy", desc, "/check/")}
{nav()}
<main class="wrap article">
<p class="eyebrow">Before you commit</p>
<h1>What I'd check first</h1>
<p class="standfirst">{desc}</p>

<div class="prose">
<p>Most Bali deals do not fail on price. They fail because one link in a chain does not match the others, and nobody checked the chain in order.</p>
<p>The order is: <strong>land → owner → agreement → zoning → permitted use → business classification → PBG → SLF → operating licence</strong>. A break anywhere invalidates everything downstream. A beautiful plot with clean title is worthless for a rental business if the classification is closed, and a perfect licence is worthless if the building has no PBG.</p>
<p>Below is what I go through. If you send me these, I can tell you where the problem is. If a seller becomes evasive about any single line, you have already learned something.</p>
</div>

{blocks}

<div class="prose">
<h2>What the answers usually reveal</h2>
<p>In practice the break is nearly always in the same three places: the zoning does not permit the intended use, the business classification is unavailable, or the lease extension was promised verbally and never written into the deed.</p>
<p>None of those are visible in a photograph of a villa.</p>
</div>

{cta("Send me the file.",
     "Location, title type, zoning, and any permits you've been shown. I'll tell you which link in the chain breaks, and what it would take to fix it. No charge, and I'm not selling you the property.",
     "Send it on Instagram")}
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
    site_schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL,
             "description": TAGLINE, "inLanguage": "en",
             "potentialAction": {"@type": "SearchAction",
                                 "target": SITE_URL + "/search/?q={search_term_string}",
                                 "query-input": "required name=search_term_string"}},
            {"@type": "Person", "name": AUTHOR, "jobTitle": AUTHOR_ROLE,
             "url": SITE_URL, "sameAs": [INSTAGRAM],
             "image": f"{SITE_URL}/{AUTHOR_PHOTO}",
             "knowsAbout": ["Indonesian property law", "Bali real estate",
                            "PT PMA", "Indonesian visas", "Land zoning"]},
        ],
    })
    return f"""{head(SITE_NAME + " — " + TAGLINE, TAGLINE, "/")}
<script type="application/ld+json">{site_schema}</script>
{nav()}
<main>
<section class="hero wrap">
<h1 class="hero-h">You cannot own land in Bali.<br><span>Three legal routes say otherwise.</span></h1>
<p class="hero-sub">Leasehold, Hak Pakai, or HGB through a PT PMA. Everything else being sold to you is a nominee arrangement — void since 1960, and a criminal offence in Bali since February 2026.</p>
<form class="hero-search" action="{BASE}/search/">
<input type="search" name="q" placeholder="Search: nominee, E33G, BPHTB, Pererenan…" aria-label="Search">
<button type="submit">Search</button>
</form>
<a class="hero-jump" href="#tool">Work out the real return <b>→</b></a>
</section>
<section class="wrap tool-wrap" id="tool">
<div class="tool-head">
<p class="proof-k">Start here</p>
<h2 class="tool-h">Put the deal through this before you believe the yield.</h2>
<p class="tool-b">Advertised Bali yields are gross — before platform commission, the 10% PB1, management, staff, refurbishment and tax. On a lease there is one more deduction nobody shows you: the premium, amortised over the years you actually get. Change any figure and every number and chart below updates.</p>
</div>
{calc_widget()}
</section>

<section class="wrap warn-wrap">
<div class="warn-block">
<span class="warn-flag">Read this before you sign anything</span>
<h2>If the structure puts the land in an Indonesian person's name for you, it is void.</h2>
<p>Nominee arrangements have been void since 1960 under UU 5/1960 Art. 26(2). Since Perda Bali 4/2026 they are also a criminal matter, and facilitating one is prohibited in its own right. Regional authorities can suspend operations and close premises directly.</p>
<p>It is still the most commonly sold structure in Bali. <a href="{BASE}/ownership/nominee-structure-bali/">Here is exactly what happens when it unwinds.</a></p>
</div>
</section>

<section class="wrap ledger-wrap">
<div class="ledger">{counts}</div>
</section>
<section class="wrap">
<h2 class="sec-h">Start here</h2>
<ul class="cards">{recent}</ul>
</section>

<section class="wrap who-wrap">
<div class="who">
{portrait("who-photo")}
<div>
<h2 class="who-h">I'm {AUTHOR}.</h2>
<p class="who-b">I advise on property in Bali, and I'm on the ground here. This site exists because the honest answers to these questions are not what gets published — the market runs on optimism, and buyers find out afterwards. Everything here carries the regulation it comes from and the date I last checked it.</p>
<p class="who-b">If you're looking at something specific, send it to me. I'll tell you what I'd check first.</p>
<a class="ig-link who-ig" href="{INSTAGRAM}" rel="me">{ig_logo("ig")}<span>@balioffscript</span></a>
</div>
</div>
</section>

<section class="wrap">{cta()}</section>
</main>
{footer(f'<script src="{BASE}/calc.js" defer></script>')}"""


def field(fid, label, val, info="", step="1", cls=""):
    """Every input carries an explanation behind an info toggle — the reader is
    usually meeting these terms for the first time."""
    btn = (f'<button type="button" class="info" aria-expanded="false" '
           f'aria-label="What is {label}?">i</button>') if info else ""
    hint = f'<span class="f-h" hidden>{info}</span>' if info else ""
    return f"""<label class="f {cls}">
<span class="f-l">{label}{btn}</span>
<input type="number" id="{fid}" value="{val}" step="{step}" inputmode="decimal">
{hint}
</label>"""


def choice(name, label, opts, info=""):
    """Segmented control. Radios stay real radios for keyboard and screen
    readers; the styling sits on the label."""
    btn = (f'<button type="button" class="info" aria-expanded="false" '
           f'aria-label="What is {label}?">i</button>') if info else ""
    hint = f'<span class="f-h" hidden>{info}</span>' if info else ""
    radios = "".join(
        f'<label class="seg"><input type="radio" name="{name}" value="{v}"'
        f'{" checked" if i == 0 else ""}><span>{lbl}</span></label>'
        for i, (v, lbl) in enumerate(opts)
    )
    return f"""<div class="f f-choice">
<span class="f-l">{label}{btn}</span>
<div class="segs">{radios}</div>
{hint}
</div>"""


def out(oid, label, note=""):
    return f"""<div class="calc-row" id="row_{oid.replace('o_', '')}">
<span class="calc-k">{label}{f'<em>{note}</em>' if note else ''}</span>
<span class="calc-v" id="{oid}">—</span>
</div>"""


CALC_DESC = ("Work out what a Bali villa or apartment really returns after platform fees, "
             "PB1, management and tax — including the lease amortisation nobody shows you.")
# Longer version for the page itself, where there is no character limit.
CALC_INTRO = ("Model what a Bali property actually returns: occupancy, platform commission, "
              "PB1, management and running costs — and, on a time-limited right, the "
              "amortisation nobody puts in the projection. Works for leasehold, HGB or "
              "freehold, and for nightly or long-term letting.")


def calc_widget():
    """The interactive model. Shared by the home page and the tool page, so the
    markup and the field IDs calc.js depends on stay in one place."""
    return f"""<div class="calc-wrap">
<form id="calc" class="calc-form" onsubmit="return false">

<fieldset class="fs">
<legend>What you are buying</legend>
{choice("tenure", "What you are buying", [("lease", "Leasehold"), ("hgb", "HGB / Hak Pakai"), ("freehold", "Freehold-equivalent")],
        "Leasehold is a contract for a fixed number of years — at the end it returns nothing unless the agreement contains an enforceable extension. HGB and Hak Pakai are registered rights, time-limited but renewable, commonly 30 years plus a 20-year extension and a 30-year renewal, each step subject to approval. Freehold-equivalent means the value does not run down — Hak Milik is not available to foreigners, so this mainly models an Indonesian-held title or a comparison case.")}
{choice("asset", "Property type", [("villa", "Villa"), ("apartment", "Apartment"), ("guesthouse", "Guesthouse")],
        "This only sets sensible starting numbers for rate, occupancy and running costs. Change any field and your value is kept.")}
{choice("revmode", "How it earns", [("nightly", "Nightly rental"), ("monthly", "Long-term rental")],
        "Nightly means short-term accommodation, which is a licensed business activity and attracts OTA commission and PB1. Long-term means a genuine residential tenancy — different legal activity, far lower costs, and it does not need an accommodation licence.")}
{field("years", "Years remaining on the right", "25",
       "The number of years you actually get. This drives the amortisation — it is the single most important input on the page and the one most often glossed over in a sales pitch.", "1", "term-only")}
{field("residual", "Value left at the end (%)", "0",
       "What the asset is still worth to you when the term expires, as a percentage of what you put in. A plain lease is 0 — it reverts to the landowner. HGB defaults to 60% on the assumption renewal succeeds but costs money and carries risk. Set it to 0 to see the worst case.", "5", "term-only")}
</fieldset>

<fieldset class="fs">
<legend>Capital in</legend>
{field("price", "Purchase price or lease premium (USD)", "300000",
       "The headline number — what you hand over for the property or the lease.", "1000")}
{field("build", "Build or renovation (USD)", "0",
       "Construction or refurbishment. Leave at zero if you are buying something finished.", "1000")}
{field("ffe", "Furniture, pool, setup (USD)", "35000",
       "Furniture, fittings and equipment. Routinely underestimated — a villa fit-out to rentable standard is rarely trivial.", "1000")}
{field("tx", "Transaction costs (%)", "7",
       "BPHTB (buyer's transfer tax, around 5% on a titled transfer), notary and PPAT fees, legal due diligence and agent commission. Budget an extra margin for contingencies.", "0.5")}
</fieldset>

<fieldset class="fs">
<legend>Revenue</legend>
{field("adr", "Average nightly rate (USD)", "180",
       "Your average achieved rate across the whole year — not your high-season headline rate.", "5", "nightly-only")}
{field("occ", "Occupancy (%)", "65",
       "Nights sold as a percentage of nights available, across a full year. Bali low season is real; sustained figures above 75% are unusual.", "1", "nightly-only")}
{field("rent", "Monthly rent (USD)", "2200",
       "What a long-term tenant pays each month.", "50", "monthly-only")}
{field("vacancy", "Vacancy (%)", "8",
       "Share of the year with no tenant, including gaps between tenancies.", "1", "monthly-only")}
{field("growth", "Annual revenue growth (%)", "3",
       "How much you expect rate or rent to rise each year. Applied to the projection charts, not to the first-year figures.", "0.5")}
</fieldset>

<fieldset class="fs">
<legend>Costs</legend>
{field("ota", "OTA commission (%)", "16",
       "What Airbnb, Booking.com and the other platforms take off the top. Typically 15–20% once you account for the mix.", "1", "nightly-only")}
{field("pb1", "PB1 regional tax (%)", "10",
       "The regional tax on accommodation revenue, collected from the guest and remitted by the operator. It is not optional and it is not income to you.", "1")}
{field("mgmt", "Management fee (%)", "20",
       "What a management company charges, usually on net room revenue after platform commission. Verify the base — a fee on gross is a materially different number.", "1")}
{field("opex", "Staff, utilities, upkeep (USD / month)", "1200",
       "Villa staff, power, water, pool and garden, internet, supplies, repairs. Staffing is the big line and it does not scale down in low season.", "50")}
{field("capex", "Refurbishment reserve (%)", "5",
       "Money set aside for the refit a rental property needs every few years. Almost never shown in a yield projection, which is why projections look better than reality.", "1")}
{field("tax_rate", "Income tax (%)", "22",
       "Tax on profit. 22% is the standard Indonesian corporate rate for a PT PMA. Personal rates and small-business regimes differ — use your actual figure.", "1")}
</fieldset>
</form>

<aside class="calc-out">
<h2 class="calc-h">Result</h2>
{out("o_invested", "Total capital in")}
<div class="calc-sep">First trading year</div>
{out("o_gross", "Gross revenue")}
{out("o_netrev", "After platform + PB1")}
{out("o_noi", "Net operating income")}
{out("o_tax", "Income tax")}
{out("o_net", "Net profit")}
<div class="calc-sep">Return</div>
{out("o_grossyield", "Gross yield", "what gets advertised")}
{out("o_netyield", "Net yield", "what you keep")}
{out("o_amort", "Amortisation", "value lost per year")}
{out("o_real", "Real return", "after amortisation")}
{out("o_payback", "Capital returned in")}
{out("o_break", "Break-even")}
{out("o_endpos", "Position at end of term")}
<div class="calc-warn" id="o_warn"></div>
</aside>
</div>

<section class="charts">
<figure class="chart">
<figcaption><h2>Do you get your money back?</h2>
<p>Cumulative position across the term — you start at minus your capital, and the line is where you stand each year. Anything below zero at the end is a loss, whatever the yield said.</p></figcaption>
<div id="chart_cum"></div>
</figure>

<figure class="chart">
<figcaption><h2>Where a year of revenue goes</h2>
<p>The advertised yield is the whole bar. What reaches you is the last segment.</p></figcaption>
<div id="chart_split"></div>
</figure>

<figure class="chart" id="chart_value_wrap">
<figcaption><h2>What the right itself is worth</h2>
<p>A time-limited right depreciates towards its residual as the clock runs down. This is the cost nobody puts in the projection, and on a lease it ends at zero.</p></figcaption>
<div id="chart_value"></div>
</figure>
</section>"""


def calculator():
    return f"""{head("Bali property ROI calculator", CALC_DESC, "/calculator/")}
{nav()}
<main class="wrap calc-page">
<p class="eyebrow">Tool</p>
<h1>What does this property actually return?</h1>
<p class="standfirst">{CALC_INTRO}</p>
{calc_widget()}

<div class="prose calc-notes">
<h2>How this differs from the yield you were quoted</h2>
<p>Most Bali villa yields are quoted gross: annual revenue divided by purchase price. That figure ignores OTA commission, the 10% PB1 regional accommodation tax, management fees, staffing, refurbishment and income tax. Once those are applied, an advertised 12% commonly lands between 4% and 6%.</p>
<p>On a leasehold there is a further deduction that is almost never shown. A 25-year lease is a wasting asset: you are buying 25 years of use, after which the land and everything built on it revert to the owner unless the lease contains an enforceable, priced extension clause. Amortising the premium over the remaining term is the only way to compare a leasehold against a freehold purchase honestly.</p>
<p>The defaults above are deliberately middle-of-road, not optimistic. Change them to your actual numbers. If a seller's projection cannot survive being typed into this page, that is the answer.</p>
<h2>What this does not model</h2>
<p>Capital appreciation, currency movement, financing costs, and the risk that the property cannot legally be operated as short-term accommodation at all. That last one is not a rounding error — <a href="{BASE}/company/pt-pma-kbli-closure-bali/">Bali closed the villa and homestay business classifications to new foreign-owned companies in July 2026</a>, and zoning determines whether nightly rental is permitted on the plot before any of these numbers matter.</p>
</div>
{cta("Send me the seller's projection.",
     "If you have a yield sheet from an agent or developer, send it to me with the location and the title type. I'll tell you which assumptions break first — the occupancy, the lease term, the licence, or the zoning. No charge, and no pitch.",
     "Send it on Instagram")}
</main>
{footer(f'<script src="{BASE}/calc.js" defer></script>')}"""


def search_page():
    return f"""{head("Search", "Search every answer on the site.", "/search/")}
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
    return f"""{head(title, title, f"/{slug}/")}
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
    write("/calculator/", calculator())
    write("/check/", check_page())
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

    urls = ["/", "/calculator/", "/check/", "/search/", "/checklist/", "/disclaimer/"] + [f"/{k}/" for k in CATEGORIES] + \
           [f'/{p["category"]}/{p["slug"]}/' for p in pages]
    sm = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    # Answer engines are a real referral source now. A wildcard allow already
    # permits them, but several read named rules, so they are listed by name.
    ai_agents = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
                 "anthropic-ai", "Claude-Web", "PerplexityBot", "Google-Extended",
                 "Applebot-Extended", "CCBot", "Bingbot", "Amazonbot"]
    robots = "User-agent: *\nAllow: /\n\n"
    for a in ai_agents:
        robots += f"User-agent: {a}\nAllow: /\n\n"
    robots += f"Sitemap: {SITE_URL}/sitemap.xml\n"
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(robots)

    # Web app manifest, so the favicon set is used on home screens too.
    open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps({
        "name": SITE_NAME, "short_name": "Off Script",
        "icons": [{"src": f"{BASE}/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": f"{BASE}/icon-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#9e2b20", "background_color": "#faf8f4", "display": "standalone",
        "start_url": f"{BASE}/",
    }))
    # Stops GitHub running Jekyll over the output. Without it the build breaks.
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

    # GitHub reads docs/CNAME as "serve this site at this domain". This script
    # wipes docs/ on every run, so the file GitHub writes when you set a custom
    # domain in Settings > Pages would be destroyed by the next build. Writing
    # it from DOMAIN keeps it surviving rebuilds. No DOMAIN, no file — pointing
    # Pages at a domain that doesn't resolve takes the site offline.
    if DOMAIN:
        open(os.path.join(OUT, "CNAME"), "w").write(DOMAIN + "\n")

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
