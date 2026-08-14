#!/usr/bin/env python3
"""
Bali Off Script, static site builder.

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
    "living": ("Living Here", "Whether Bali works as a place to live, and where the market goes next."),
}

# Category landing pages were thin — a heading and a list of cards. They are
# also the pages best placed to rank for the broad terms ("bali property tax",
# "bali visa"), so each one gets a real introduction and an SEO title.
CATEGORY_SEO = {
    "ownership": (
        "Can foreigners own property in Bali?",
        "Foreigners cannot hold Hak Milik, Indonesian freehold, under any structure, "
        "including through a company or a spouse. Three lawful routes exist instead: a "
        "leasehold contract, Hak Pakai registered in your own name if you hold residency, "
        "or HGB held through a PT PMA for commercial use. Everything else being marketed "
        "to foreign buyers is a nominee arrangement, which has been void since 1960 and "
        "criminal in Bali since February 2026. These pages explain what each route gives "
        "you, what the certificate actually says, and the clauses that decide whether a "
        "lease is worth what you paid."),
    "visas": (
        "Indonesian visas and stay permits, explained",
        "The system was restructured in 2025: 133 indices reduced to 110, and "
        "employer-sponsored work visas cut from 31 to 6, so most visa advice written "
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
        "accommodation tax is collected from guests and remitted by the operator, it is "
        "not income. Spend more than 183 days here and you are an Indonesian tax resident "
        "regardless of your visa."),
    "building": (
        "Bali zoning, PBG permits and what you can build",
        "Zone colour tells you whether you may build. KDB and KLB tell you how much, and "
        "a green-zone plot with a 10% footprint cap can be entirely legal and still "
        "useless as a rental business. PBG is the building approval and SLF confirms the "
        "finished building is fit for use; neither is a formality, and timelines run from "
        "3 to 6 months in Denpasar to 10 to 12 months in Badung for an existing "
        "unpermitted structure. Setbacks come off before any of it."),
    "rental": (
        "Bali villa rental yields and licensing",
        "Advertised yields are gross. After platform commission, the 10% regional tax, "
        "management fees, staffing, refurbishment and income tax, an advertised 12% "
        "commonly lands between 4% and 6%, and on a leasehold, amortising the premium "
        "over the years remaining can take it below zero. Licensing is the separate "
        "question underneath: whether nightly rental is permitted on that plot at all, "
        "and which business classification the operator holds."),
    "living": (
        "Living in Bali: the honest version",
        "Bali is a genuinely good place to live for some people and a slow disappointment "
        "for others, and the difference is rarely what the brochures discuss. These pages "
        "cover what actually changes when you move here, the infrastructure and policy "
        "shifts pulling capital in, and where the market is heading next as Bali prices "
        "itself out of reach for some buyers. Written the same way as the rest of the "
        "site: specific, dated, and unwilling to sell you a version of the island that "
        "does not exist."),
    "areas": (
        "Where to buy in Bali, area by area",
        "Canggu has the liquidity and the strictest enforcement. The Bukit has the highest "
        "nightly rates and the setback rules that produced the 2025 Bingin demolitions. "
        "Sanur has the fastest permits on the island. Ubud has small buildable ratios and "
        "sacred-site buffers. Tabanan has the clearest appreciation story and the hardest "
        "route to a commercial accommodation licence. These pages cover what each area "
        "costs and the specific constraint that breaks deals there."),
}


# Top-level navigation. Sections are grouped so the bar stays at five items
# however many pages get added underneath — each dropdown lists its own
# articles, so growth goes downward rather than sideways.
NAV_GROUPS = [
    ("Owning",    ["ownership", "building"]),
    ("Moving",    ["visas", "living"]),
    ("Business",  ["company", "tax"]),
    ("Investing", ["rental", "areas"]),
]

# Populated in main() so nav() can list each section's pages.
ALL_PAGES = []

CATEGORY_DIAGRAM = {
    "ownership": "terms",
    "building": "zoning",
    "visas": "visas",
    "company": "pma",
    "rental": None,      # the calculator is the visual here
    "tax": None,
    "areas": None,       # the land explorer is the visual here
    "living": None,
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
        if s.startswith("[[diagram:") and s.endswith("]]"):
            close()
            key = s[10:-2].strip()
            if key in DIAGRAMS:
                html.append(DIAGRAMS[key]())
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



# ---------------------------------------------------------------- diagrams
#
# Inline SVG, no libraries and no image files. Drop one into any page body
# with a line containing only:  [[diagram:zoning]]
# Colours come from the stylesheet so they follow the section accent.

def _svg(vb, inner, cap=""):
    figcap = f'<figcaption class="dg-cap">{cap}</figcaption>' if cap else ""
    return (f'<figure class="dg"><svg viewBox="{vb}" class="dg-svg" role="img" '
            f'preserveAspectRatio="xMidYMid meet">{inner}</svg>{figcap}</figure>')


def dg_zoning():
    """Zone colour is where every Bali conversation starts and where most of
    them stop. The colours here are the actual planning colours."""
    cols = [
        ("Pink", "#d98b9a", "Tourism", ["Accommodation is the", "intended use", "Still confirm the exact", "permitted activity"]),
        ("Yellow", "#dcc98a", "Residential", ["Living, not operating", "Some conditional uses", "Not a green light for", "nightly rental"]),
        ("Green", "#93b08f", "Agricultural", ["Development heavily", "restricted", "LP2B may prohibit", "conversion entirely"]),
    ]
    out, x = "", 0
    for name, hexc, sub, lines in cols:
        out += f'<rect x="{x}" y="0" width="196" height="74" fill="{hexc}"/>'
        out += f'<text x="{x+16}" y="34" class="dg-t-lg">{name}</text>'
        out += f'<text x="{x+16}" y="55" class="dg-t-sm-d">{sub}</text>'
        out += f'<rect x="{x}" y="74" width="196" height="118" class="dg-panel"/>'
        for i, ln in enumerate(lines):
            out += f'<text x="{x+16}" y="{100+i*20}" class="dg-t">{ln}</text>'
        out += f'<line x1="{x}" y1="0" x2="{x}" y2="192" class="dg-div"/>'
        x += 200
    return _svg("0 0 596 192", out,
                "Zone colour is the start of the question, not the answer. The parcel's RDTR entry decides.")


def dg_kdb():
    """The number that turns a legal plot into an unusable one."""
    o = ""
    # Green zone plot: 500 m2, KDB 10%
    o += '<text x="0" y="14" class="dg-t-lab">GREEN ZONE &middot; 500 m&sup2; &middot; KDB 10%</text>'
    o += '<rect x="0" y="26" width="180" height="180" class="dg-plot"/>'
    o += '<rect x="60" y="86" width="57" height="57" class="dg-fill"/>'
    o += '<text x="88" y="119" class="dg-t-c">50 m&sup2;</text>'
    o += '<text x="0" y="226" class="dg-t-sm">A bungalow. Not a rental business.</text>'
    # Pink zone plot: 2000 m2, KDB 60%
    o += '<text x="260" y="14" class="dg-t-lab">PINK ZONE &middot; 2,000 m&sup2; &middot; KDB 60%</text>'
    o += '<rect x="260" y="26" width="180" height="180" class="dg-plot"/>'
    o += '<rect x="278" y="44" width="139" height="139" class="dg-fill-2"/>'
    o += '<text x="348" y="119" class="dg-t-c">1,200 m&sup2;</text>'
    o += '<text x="260" y="226" class="dg-t-sm">Same rules. Entirely different project.</text>'
    return _svg("0 0 460 240", o,
                "KDB caps the footprint as a share of the plot. Zoning says whether you may build; KDB says how much.")


def dg_terms():
    """Every right except freehold runs out. Drawn to scale against 100 years."""
    rows = [
        ("Hak Milik", [("Permanent", 100, "dg-b-perm")], "Closed to foreigners"),
        ("HGB / Hak Pakai", [("30", 30, "dg-b-1"), ("+20", 20, "dg-b-2"), ("+30", 30, "dg-b-3")], "Each step needs approval"),
        ("HGU", [("35", 35, "dg-b-1"), ("+25", 25, "dg-b-2"), ("+35", 35, "dg-b-3")], "Minimum 5 hectares"),
        ("Lease", [("20-30 typical", 27, "dg-b-1"), ("+ extension", 25, "dg-b-2")], "Only if the clause is enforceable"),
    ]
    o, y = "", 0
    SCALE = 4.4
    for label, segs, note in rows:
        o += f'<text x="0" y="{y+15}" class="dg-t-lab">{label.upper()}</text>'
        x = 0
        for txt, yrs, cls in segs:
            w = yrs * SCALE
            o += f'<rect x="{132+x}" y="{y+2}" width="{w-2}" height="20" class="{cls}"/>'
            if w > 34:
                o += f'<text x="{132+x+w/2}" y="{y+16}" class="dg-t-c-rev">{txt}</text>'
            x += w
        if label != "Hak Milik":
            o += f'<line x1="{132+x}" y1="{y-2}" x2="{132+x}" y2="{y+26}" class="dg-stop"/>'
        o += f'<text x="0" y="{y+33}" class="dg-t-note">{note}</text>'
        y += 52
    o += f'<line x1="132" y1="{y-8}" x2="{132+100*SCALE}" y2="{y-8}" class="dg-axis"/>'
    for t in (0, 25, 50, 75, 100):
        o += f'<text x="{132+t*SCALE}" y="{y+8}" class="dg-t-c-sm">{t}</text>'
    o += f'<text x="{132+100*SCALE+16}" y="{y+8}" class="dg-t-sm">years</text>'
    return _svg(f"0 0 620 {y+20}", o,
                "The vertical marks are reversion. At that point the land and everything on it returns to the owner or the State.")


def dg_pbg():
    """Permit time by regency, the months nobody budgets for."""
    rows = [("Denpasar", 3, 5), ("Gianyar", 4, 5), ("Tabanan", 4, 5), ("Badung", 5, 6), ("Klungkung", 5, 6)]
    o, y = "", 0
    SC = 62
    for name, lo, hi in rows:
        o += f'<text x="0" y="{y+15}" class="dg-t-lab">{name.upper()}</text>'
        o += f'<rect x="108" y="{y+3}" width="{lo*SC}" height="18" class="dg-b-1"/>'
        o += f'<rect x="{108+lo*SC}" y="{y+3}" width="{(hi-lo)*SC}" height="18" class="dg-b-2"/>'
        o += f'<text x="{108+hi*SC+10}" y="{y+17}" class="dg-t-sm">{lo}&ndash;{hi} months</text>'
        y += 30
    o += f'<line x1="108" y1="{y+2}" x2="{108+6*SC}" y2="{y+2}" class="dg-axis"/>'
    for m in range(0, 7):
        o += f'<text x="{108+m*SC}" y="{y+18}" class="dg-t-c-sm">{m}</text>'
    return _svg(f"0 0 560 {y+28}", o,
                "PBG from empty land. Add 8&ndash;12 months where an existing building has to be legalised instead.")


def dg_chain():
    """One broken link invalidates everything downstream."""
    steps = ["Land", "Owner", "Agreement", "Zoning", "Permitted use", "Classification", "PBG", "SLF", "Licence"]
    o, x = "", 0
    W, GAP = 58, 8
    for i, st in enumerate(steps):
        broken = st == "Classification"
        cls = "dg-node-bad" if broken else "dg-node"
        o += f'<rect x="{x}" y="14" width="{W}" height="38" class="{cls}"/>'
        words = st.split(" ")
        if len(words) == 1:
            o += f'<text x="{x+W/2}" y="{37}" class="dg-t-c-xs">{st}</text>'
        else:
            o += f'<text x="{x+W/2}" y="{31}" class="dg-t-c-xs">{words[0]}</text>'
            o += f'<text x="{x+W/2}" y="{43}" class="dg-t-c-xs">{words[1]}</text>'
        if i < len(steps) - 1:
            o += f'<line x1="{x+W}" y1="33" x2="{x+W+GAP}" y2="33" class="dg-axis"/>'
        if broken:
            o += f'<text x="{x+W/2}" y="8" class="dg-t-c-xs dg-warn">closed</text>'
            o += f'<line x1="{x+W+2}" y1="20" x2="{x+W+6}" y2="46" class="dg-break"/>'
        x += W + GAP
    o += f'<text x="0" y="72" class="dg-t-sm">A break anywhere invalidates every step to its right.</text>'
    return _svg(f"0 0 {x} 80", o,
                "The order due diligence actually runs in. Most failed deals break at zoning or classification.")



def dg_visas():
    """The rule the whole immigration system runs on: activity first."""
    rows = [
        ("Work for an Indonesian employer", "E23 family", "RPTKA required"),
        ("Invest / run a company", "E28 family", "Board role + shareholding"),
        ("Remote work, foreign employer", "E33G", "Income-tested"),
        ("Live on savings", "E33 Second Home", "Deposit or property"),
        ("Join Indonesian family", "E31 family", "Documented relationship"),
        ("Indonesian ancestry", "E32 / GCI", "Can reach indefinite ITAP"),
        ("Just evaluating a purchase", "C12 / D12", "Visitor, not residence"),
    ]
    o = '<text x="0" y="12" class="dg-t-lab">WHAT WILL YOU ACTUALLY DO?</text>'
    o += '<text x="286" y="12" class="dg-t-lab">ROUTE</text>'
    o += '<text x="418" y="12" class="dg-t-lab">GATE</text>'
    y = 24
    for act, route, gate in rows:
        o += f'<rect x="0" y="{y}" width="560" height="26" class="dg-panel"/>'
        o += f'<text x="10" y="{y+17}" class="dg-t">{act}</text>'
        o += f'<text x="286" y="{y+17}" class="dg-t-mono">{route}</text>'
        o += f'<text x="418" y="{y+17}" class="dg-t-sm">{gate}</text>'
        y += 30
    o += f'<text x="0" y="{y+16}" class="dg-t-sm">Length of stay follows from the activity. It is never the starting question.</text>'
    return _svg(f"0 0 560 {y+26}", o,
                "Choosing a permit by how long you want to stay is how people end up on a status that does not cover what they are doing.")


def dg_pma():
    """Six to ten weeks to a trading licence, if nothing stalls."""
    steps = [("Structure &amp; KBLI", 1.5), ("Deed &rarr; NPWP", 3), ("NIB", 1.5),
             ("Capital", 2.5), ("KKPR", 3), ("PBG &rarr; SLF", 13)]
    o, x = "", 0
    SC = 20
    for i, (label, wk) in enumerate(steps):
        w = wk * SC
        cls = "dg-b-1" if i < 4 else "dg-b-2"
        o += f'<rect x="{x}" y="20" width="{w-3}" height="26" class="{cls}"/>'
        o += f'<text x="{x}" y="14" class="dg-t-lab">{label}</text>'
        o += f'<text x="{x+4}" y="37" class="dg-t-c-rev" text-anchor="start">{wk:g}w</text>'
        x += w
    o += f'<line x1="0" y1="56" x2="{x}" y2="56" class="dg-axis"/>'
    o += '<text x="0" y="72" class="dg-t-sm">Trading NIB with a real domicile: 6&ndash;10 weeks. Building runs long after that.</text>'
    return _svg(f"0 0 {x+10} 82", o,
                "Any of these can double. Capital that does not reconcile, a virtual office, or an undigitised RDTR zone are the usual causes.")


DIAGRAMS = {
    "zoning": dg_zoning, "kdb": dg_kdb, "terms": dg_terms,
    "pbg": dg_pbg, "chain": dg_chain,
    "visas": dg_visas, "pma": dg_pma,
}


# ---------------------------------------------------------------- chrome

def title_tag(t):
    """Google truncates around 60 characters. Append the site name only when
    it still fits. The question itself carries the keywords, the brand does
    not, so the brand is what gets dropped."""
    if SITE_NAME in t:
        return t
    full = f"{t} | {SITE_NAME}"
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
    """Dropdowns list sections, not every article. Questions live on the
    section page, a menu that grows with the content stops being a menu."""
    def row(key):
        name, blurb = CATEGORIES[key]
        n = len([q for q in ALL_PAGES if q["category"] == key])
        return (f'<a class="nd-row" href="{BASE}/{key}/">'
                f'<span class="nd-row-h">{name}<em>{n}</em></span>'
                f'<span class="nd-row-b">{blurb}</span></a>')

    groups = ""
    for label, keys in NAV_GROUPS:
        on = " on" if active in keys else ""
        groups += (
            f'<div class="nav-g">'
            f'<button class="nav-t{on}" type="button" aria-expanded="false">{label}</button>'
            f'<div class="nav-drop"><div class="nd-in">{"".join(row(k) for k in keys)}</div></div>'
            f"</div>"
        )

    tools = [
        ("Return calculator", "/calculator/", "What a property really returns after every cost"),
        ("Area map", "/areas/#map", "What governs each area, regency by regency"),
        ("What I&rsquo;d check first", "/check/", "The intake list for a live deal"),
        ("Due diligence checklist", "/checklist/", "Print it and take it to viewings"),
        ("About", "/about/", "Who writes this, and why"),
    ]
    trows = "".join(
        f'<a class="nd-row" href="{BASE}{href}"><span class="nd-row-h">{t}</span>'
        f'<span class="nd-row-b">{d}</span></a>' for t, href, d in tools
    )
    groups += (f'<div class="nav-g">'
               f'<button class="nav-t" type="button" aria-expanded="false">Tools</button>'
               f'<div class="nav-drop"><div class="nd-in">{trows}</div></div></div>')

    return f"""<header class="masthead">
<div class="wrap masthead-inner">
<a class="wordmark" href="{BASE}/"><span>Bali</span> Off Script</a>
<button class="menu-btn" aria-label="Menu" aria-expanded="false">Menu</button>
<nav class="nav"><div class="nav-inner">{groups}<a class="nav-search" href="{BASE}/search/">Search</a></div></nav>
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
<a href="{BASE}/about/">About</a>
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
<p class="cta-by">{AUTHOR}, {AUTHOR_ROLE}</p>
</div>
</div>
<a class="btn" href="{INSTAGRAM}" rel="me">{ig_logo()}<span>{btn}</span></a>
</section>"""


# ---------------------------------------------------------------- pages


def read_time(body):
    """Rough minutes at 210 wpm. Setting the expectation up front measurably
    reduces people bouncing off a long page."""
    words = len(re.sub(r"[^\w\s]", " ", body).split())
    return max(1, round(words / 210))


def next_up(m, pages):
    """One strong recommendation beats a list of five. Next in the same
    section by order, wrapping round at the end."""
    sect = [p for p in pages if p["category"] == m["category"]]
    if len(sect) < 2:
        sect = pages
    i = next((n for n, p in enumerate(sect) if p["slug"] == m["slug"]), 0)
    return sect[(i + 1) % len(sect)]


def onward(m, pages):
    nxt = next_up(m, pages)
    cat = CATEGORIES[nxt["category"]][0]
    others = [p for p in pages
              if p["category"] == m["category"]
              and p["slug"] not in (m["slug"], nxt["slug"])][:5]
    more = "".join(
        f'<li><a href="{BASE}/{p["category"]}/{p["slug"]}/">{p["question"]}</a></li>'
        for p in others
    )
    more_block = (f'<div class="on-more"><p class="on-more-h">More in '
                  f'{CATEGORIES[m["category"]][0]}</p><ul>{more}</ul></div>') if more else ""
    return f"""<section class="onward">
<a class="on-next" href="{BASE}/{nxt["category"]}/{nxt["slug"]}/">
<span class="on-k">Read this next &middot; {cat}</span>
<span class="on-h">{nxt["question"]}</span>
<span class="on-b">{nxt["summary"]}</span>
</a>
{more_block}
</section>"""


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
<p class="eyebrow"><a href="{BASE}/{m['category']}/">{cat_name}</a><span class="rt">{read_time(m["body"])} min read</span></p>
<h1>{m["question"]}</h1>
<p class="standfirst">{m["summary"]}</p>
<div class="prose">{md(m["body"])}</div>
{map_widget(focus=m["slug"], compact=True) if m["category"] == "areas" and any(a["slug"] == m["slug"] for a in MAP_AREAS) else ""}
{reel(m.get("reel", ""))}
{cta()}
{onward(m, ALL_PAGES)}
</main>
{footer(f'<script src="{BASE}/map.js" defer></script>') if m["category"] == "areas" else footer()}"""


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
<div class="prose section-intro"><p>{intro}</p>
{DIAGRAMS[CATEGORY_DIAGRAM[key]]() if CATEGORY_DIAGRAM.get(key) else ""}</div>
{map_widget() if key == "areas" else ""}
<h2 class="sec-h">Every answer in this section</h2>
<ul class="cards">{items}</ul>
</main>
{footer(f'<script src="{BASE}/map.js" defer></script>') if key == "areas" else footer()}"""


CHECK_ITEMS = [
    ("The plot", [
        "Exact location, regency and village, not 'Canggu area'",
        "Certificate type and number: Hak Milik, HGB, Hak Pakai, or a lease",
        "Whose name is on the certificate, and their authority to transact",
        "Land area, and the cadastral drawing against what you walked",
    ]),
    ("The zoning", [
        "RDTR designation for this parcel, from the regency, not the agent",
        "KDB and KLB figures. What you can actually build, not just whether you can",
        "Setbacks: beach, river, cliff, temple",
        "Whether LP2B or subak protections apply",
    ]),
    ("The building", [
        "PBG for every structure standing on the plot",
        "SLF issued, not 'being processed'",
        "If off-plan: what has actually been approved, with application numbers",
    ]),
    ("The business", [
        "The rental model, nightly, monthly, or genuine long-term residential",
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


def about_page():
    """The entity page. Search engines and answer engines both need one place
    that states plainly who publishes this and what they do, otherwise a
    'who is X' question has nothing to resolve against."""
    desc = ("Bali Off Script is written by Kai, a property adviser based in Bali. "
            "Straight answers on buying, building and living here, with the regulation "
            "cited and checked against the current rules.")
    schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "AboutPage", "url": f"{SITE_URL}/about/", "name": f"About {SITE_NAME}",
             "description": desc, "inLanguage": "en"},
            {"@type": "Person", "@id": f"{SITE_URL}/#kai", "name": AUTHOR,
             "jobTitle": AUTHOR_ROLE, "url": f"{SITE_URL}/about/",
             "image": f"{SITE_URL}/{AUTHOR_PHOTO}", "sameAs": [INSTAGRAM],
             "worksFor": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
             "homeLocation": {"@type": "Place", "name": "Bali, Indonesia"},
             "knowsAbout": ["Indonesian property law", "Bali real estate", "Leasehold",
                            "Hak Pakai", "HGB", "PT PMA", "Indonesian visas",
                            "Zoning and RDTR", "PBG and SLF permits"]},
            {"@type": "Organization", "@id": f"{SITE_URL}/#org", "name": SITE_NAME,
             "url": SITE_URL, "logo": f"{SITE_URL}/icon-512.png",
             "description": TAGLINE, "sameAs": [INSTAGRAM],
             "founder": {"@id": f"{SITE_URL}/#kai"},
             "areaServed": {"@type": "Place", "name": "Bali, Indonesia"}},
        ],
    })
    return f"""{head(f"About {SITE_NAME}, who writes this", desc, "/about/")}
<script type="application/ld+json">{schema}</script>
{nav()}
<main class="wrap article">
<p class="eyebrow">About</p>
<h1>Who writes this</h1>
<p class="standfirst">{desc}</p>

<div class="who who-about">
{portrait("who-photo")}
<div>
<h2 class="who-h">{AUTHOR}</h2>
<p class="who-b">{AUTHOR_ROLE}, based in Bali. I advise foreign buyers on property here. What can actually be owned, what can legally be built and rented, and which structures fall apart when someone looks at them properly.</p>
<a class="ig-link who-ig" href="{INSTAGRAM}" rel="me">{ig_logo("ig")}<span>@balioffscript</span></a>
</div>
</div>

<div class="prose">
<h2>What I do</h2>
<p>I advise foreign buyers and investors on property across Bali and the surrounding islands, Nusa Penida, Lombok, the Gilis, and further east where clients are looking. The work covers the whole arc of a project, not one slice of it:</p>
<ul>
<li><strong>Land and property acquisition</strong>. What can actually be held, under which right, and what the certificate really says</li>
<li><strong>Due diligence</strong>. Title, zoning, permits, and the licensing position underneath the sale</li>
<li><strong>Development and construction projects</strong>. What is buildable on a plot once KDB, KLB and setbacks are applied, and what the permit sequence actually costs in time</li>
<li><strong>Structuring</strong>, leasehold, Hak Pakai or a company-held right, and which one fits the intended use rather than the one that closes fastest</li>
<li><strong>Investment analysis</strong>. What a project returns after the costs that get left out of the projection</li>
</ul>
<p>Different islands are not interchangeable. Spatial rules, permit timelines and enforcement all vary by regency and province, and an assumption carried from Canggu to Lombok is a common and expensive mistake.</p>

<h2>Why this site exists</h2>
<p>Most Bali property information is published by people selling Bali property. That is not a conspiracy, it is an incentive, and it means the honest answers to the hardest questions tend not to get written down.</p>
<p>Foreigners cannot own freehold land in Indonesia. Nominee arrangements, still the most commonly sold structure on the island, have been void since 1960 and criminal in Bali since February 2026. Advertised rental yields are gross figures that ignore platform commission, regional tax, management, staffing and, on a lease, the fact that the asset expires. None of that is secret. It is simply inconvenient to the sale.</p>
<p>This site publishes it anyway.</p>

<h2>How to judge whether I am any use</h2>
<p>Not by testimonials, which anyone can write. By whether the reasoning holds up when you check it:</p>
<ul>
<li>Regulations are named by number in the text where one exists, so you can look it up rather than take my word for it</li>
<li>Pages are rewritten when the rules change, not left to rot</li>
<li>Where rules are ambiguous, recently changed, or applied differently between regencies, the page says so instead of picking the convenient reading</li>
<li>Where a figure is commonly cited but subject to revision, it is presented that way rather than as settled fact</li>
<li>Nothing here is framed as a workaround for foreign ownership restrictions</li>
</ul>
<p>The <a href="{BASE}/calculator/">return calculator</a> is the clearest example. It is built to show what a property actually returns after every cost, including the lease amortisation that turns an advertised 12% into something very different. An adviser trying to sell you a villa would not publish that tool.</p>

<h2>How I work</h2>
<p>Send me a deal and I will tell you which link in the chain breaks first, the zoning, the licence, the lease term, or the numbers. The <a href="{BASE}/check/">intake list is here</a>. A first look costs you nothing.</p>
<p>The most useful thing I can tell someone is often &ldquo;not this one&rdquo;. A deal that cannot survive being checked properly is not a deal worth doing, whoever is selling it.</p>

<h2>What this is not</h2>
<p>It is not legal advice, tax advice, or financial advice, and reading it does not create an adviser relationship. Indonesian regulations change often and are administered inconsistently between regencies and between individual offices. Before you sign anything or transfer any money, verify it with your own licensed Indonesian notary or PPAT, your own lawyer, and your own registered tax consultant, not the seller's. The <a href="{BASE}/disclaimer/">full disclaimer is here</a>.</p>
<p>I work in Bali property, which is how I know what goes wrong. That also means I am not a neutral party, so check what I tell you against your own notary, lawyer and tax consultant, exactly as you would with anyone else in this market.</p>
</div>

{cta("Got a specific situation?",
     "Send me the details. Location, title type, zoning, and whatever permits you've been shown. I'll tell you what I'd check first.",
     "Ask on Instagram")}
</main>
{footer()}"""


def check_page():
    desc = ("The information I need to tell you whether a Bali property works, and the "
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

{DIAGRAMS["chain"]()}

{blocks}

<div class="prose">
<h2>What the answers usually reveal</h2>
<p>In practice the break is nearly always in the same three places: the zoning does not permit the intended use, the business classification is unavailable, or the lease extension was promised verbally and never written into the deed.</p>
<p>None of those are visible in a photograph of a villa.</p>
</div>

{cta("Send me the file.",
     "Location, title type, zoning, and any permits you've been shown. I'll tell you which link in the chain breaks, and what it would take to fix it. ",
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
    return f"""{head(SITE_NAME + " | " + TAGLINE, TAGLINE, "/")}
<script type="application/ld+json">{site_schema}</script>
{nav()}
<main>
<section class="hero-split">
<div class="hero-copy">
<h1 class="hero-h">Send me the deal<br><span>before you sign it.</span></h1>
<p class="hero-sub">What a certificate actually gives you. What you can legally build and rent on the land. What a deal returns once every real cost is counted.</p>
<p class="hero-note">Eyes on the ground in Bali. Message me before you sign anything.</p>
<div class="hero-acts">
<a class="lnk lnk-solid" href="#tool">Work out the real return</a>
<a class="lnk" href="{BASE}/check/">Ask me about a deal</a>
</div>
<form class="hero-search" action="{BASE}/search/">
<input type="search" name="q" placeholder="nominee, E33G, BPHTB, Pererenan…" aria-label="Search">
<button type="submit">Search</button>
</form>
</div>
<div class="hero-fig">
<img src="{BASE}/kai-hero.jpg" width="726" height="969" alt="{AUTHOR}, {AUTHOR_ROLE}" fetchpriority="high">
<figcaption class="hero-cap"><span>{AUTHOR}</span>Property adviser</figcaption>
</div>
</section>
<section class="wrap tool-wrap" id="tool">
<div class="tool-head">
<p class="proof-k">Start here</p>
<h2 class="tool-h">Put the deal through this before you believe the yield.</h2>
<p class="tool-b">Advertised Bali yields are gross, before platform commission, the 10% PB1, management, staff, refurbishment and tax. On a lease there is one more deduction nobody shows you: the premium, amortised over the years you actually get. Change any figure and every number and chart below updates.</p>
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

<section class="wrap">
<h2 class="sec-h">Start here</h2>
<ul class="cards">{recent}</ul>
</section>

<section class="wrap who-wrap">
<div class="who">
{portrait("who-photo")}
<div>
<h2 class="who-h">I'm {AUTHOR}.</h2>
<p class="who-b">I advise on property in Bali, and I'm on the ground here. This site exists because the honest answers to these questions are not what gets published. The market runs on optimism, and buyers find out afterwards. Everything here carries the regulation it comes from and the date I last checked it.</p>
<p class="who-b">If you're looking at something specific, send it to me. I'll tell you what I'd check first.</p>
<a class="ig-link who-ig" href="{INSTAGRAM}" rel="me">{ig_logo("ig")}<span>@balioffscript</span></a>
</div>
</div>
</section>

<section class="wrap">{cta()}</section>
</main>
{footer(f'<script src="{BASE}/calc.js" defer></script>')}"""


def field(fid, label, val, info="", step="1", cls=""):
    """Every input carries an explanation behind an info toggle, the reader is
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
<span class="calc-v" id="{oid}">&middot;</span>
</div>"""


CALC_DESC = ("Work out what a Bali villa or apartment really returns after platform fees, "
             "PB1, management and tax. Including the lease amortisation nobody shows you.")
# Longer version for the page itself, where there is no character limit.
CALC_INTRO = ("Model what a Bali property actually returns: occupancy, platform commission, "
              "PB1, management and running costs, and, on a time-limited right, the "
              "amortisation nobody puts in the projection. Works for leasehold, HGB or "
              "freehold, and for nightly or long-term letting.")




def section_grid(pages, limit=4):
    """A visual index of the whole site. Replaces the counts ledger, which
    told a reader how many answers existed without showing them any."""
    cells = ""
    for k, (name, blurb) in CATEGORIES.items():
        items = [p for p in pages if p["category"] == k]
        links = "".join(
            f'<a class="sg-q" href="{BASE}/{k}/{q["slug"]}/">{q["question"]}</a>'
            for q in items[:limit]
        )
        more = (f'<a class="sg-more" href="{BASE}/{k}/">All {len(items)} in {name} &rarr;</a>'
                if len(items) > limit else
                f'<a class="sg-more" href="{BASE}/{k}/">Open {name} &rarr;</a>')
        cells += f"""<div class="sg-cell">
<a class="sg-h" href="{BASE}/{k}/">{name}<em>{len(items)}</em></a>
<p class="sg-b">{blurb}</p>
<div class="sg-qs">{links}</div>
{more}
</div>"""
    return f'<div class="sg">{cells}</div>'


def all_page(pages):
    """Every answer on one page. Useful for a reader who wants to browse, and
    a strong internal-linking hub for search engines."""
    desc = ("Every answer on Bali Off Script in one place, ownership, visas, "
            "companies, tax, building, rental returns, areas and living here.")
    blocks = ""
    for k, (name, blurb) in CATEGORIES.items():
        items = [p for p in pages if p["category"] == k]
        rows = "".join(
            f'<li><a href="{BASE}/{k}/{q["slug"]}/"><span>{q["question"]}</span>'
            f'<em>{q["summary"]}</em></a></li>' for q in items
        )
        blocks += f"""<section class="ax">
<h2 class="ax-h"><a href="{BASE}/{k}/">{name}</a><span>{len(items)}</span></h2>
<p class="ax-b">{blurb}</p>
<ul class="ax-list">{rows}</ul>
</section>"""
    return f"""{head("Every answer, in one place", desc, "/all/")}
{nav()}
<main class="wrap article">
<p class="eyebrow">Index</p>
<h1>Every answer, in one place</h1>
<p class="standfirst">{len(pages)} answers across eight sections, written from the regulations rather than from the sales pitch.</p>
<div class="ax-tools">
<a class="lnk lnk-solid" href="{BASE}/calculator/">Return calculator</a>
<a class="lnk" href="{BASE}/check/">Ask me about a deal</a>
<a class="lnk" href="{BASE}/areas/#map">Area map</a>
</div>
{blocks}
</main>
{footer()}"""


# Areas plotted on a schematic Bali. Not a survey map — the coastline is
# stylised — but the relative positions, regencies and constraints are real.
MAP_AREAS = [
    dict(id="tabanan", n="Tabanan &amp; Tanah Lot", x=288, y=284, r="Tabanan",
         price="30–50% below Canggu", pbg="4–5 months",
         watch="LP2B and coastal setback. Hardest place to licence a rental",
         slug="tabanan-west-coast-property", url="/areas/tabanan-west-coast-property/"),
    dict(id="pererenan", n="Pererenan &amp; Cemagi", x=299, y=296, r="Badung",
         price="USD 55–75k / are", pbg="5–6 months",
         watch="More green zone than Canggu, check LP2B and KDB before the view",
         slug="pererenan-cemagi-property", url="/areas/pererenan-cemagi-property/"),
    dict(id="canggu", n="Canggu &amp; Berawa", x=310, y=295, r="Badung",
         price="~USD 82.5k / are", pbg="5–6 months",
         watch="Tightest short-term rental enforcement on the island",
         slug="canggu-berawa-property", url="/areas/canggu-berawa-property/"),
    dict(id="seminyak", n="Seminyak &amp; Umalas", x=322, y=314, r="Badung",
         price="Near the ceiling", pbg="5–6 months",
         watch="Mature market, stable cashflow, modest appreciation",
         slug="where-to-buy-bali", url="/areas/where-to-buy-bali/"),
    dict(id="uluwatu", n="Uluwatu &amp; the Bukit", x=287, y=372, r="Badung",
         price="USD 25–60k / are", pbg="5–6 months",
         watch="Cliff and beach setbacks. Bingin was demolished in 2025",
         slug="uluwatu-bukit-property", url="/areas/uluwatu-bukit-property/"),
    dict(id="sanur", n="Sanur", x=361, y=312, r="Denpasar",
         price="Best value, established", pbg="3–5 months",
         watch="Fastest permits in Bali. Lower rates than the west coast",
         slug="sanur-denpasar-property", url="/areas/sanur-denpasar-property/"),
    dict(id="ubud", n="Ubud &amp; Tegallalang", x=361, y=236, r="Gianyar",
         price="Good land value", pbg="4–5 months",
         watch="Temple buffers and very small buildable ratios",
         slug="ubud-gianyar-property", url="/areas/ubud-gianyar-property/"),
    dict(id="penida", n="Nusa Penida", x=479, y=329, r="Klungkung",
         price="Frontier pricing", pbg="5–6 months",
         watch="Water supply is the binding constraint, not the permit",
         slug="nusa-penida-property", url="/areas/nusa-penida-property/"),
    dict(id="lombok", n="Lombok", x=804, y=296, r="West Nusa Tenggara",
         price="Materially cheaper", pbg="Varies by regency",
         watch="Different province. Bali's 2026 closure and nominee Perda do not apply",
         slug="lombok-property-foreigners", url="/areas/lombok-property-foreigners/"),
    dict(id="gili", n="Gili Islands", x=685, y=171, r="West Nusa Tenggara",
         price="Thin, seasonal market", pbg="Varies by regency",
         watch="Tiny land supply, boat-dependent construction, fragile water",
         slug="lombok-property-foreigners", url="/areas/lombok-property-foreigners/"),
]


def map_widget(focus=None, compact=False):
    """Hover or tap an area to see what actually governs it there."""
    pins = "".join(
        f'<g class="mp-pin" data-id="{a["id"]}" tabindex="0" role="button" '
        f'aria-label="{a["n"]}">'
        f'<circle class="mp-hit" cx="{a["x"]}" cy="{a["y"]}" r="26"/>'
        f'<circle class="mp-dot" cx="{a["x"]}" cy="{a["y"]}" r="7"/>'
        f'<circle class="mp-ring" cx="{a["x"]}" cy="{a["y"]}" r="13"/>'
        f'<text class="mp-lab" x="{a["x"]}" y="{a["y"] - 20}">{a["n"]}</text>'
        f"</g>"
        for a in MAP_AREAS
    )
    data = json.dumps({a["id"]: {k: a[k] for k in ("n", "r", "price", "pbg", "watch", "url")}
                       for a in MAP_AREAS})
    return f"""<section class="mp{' mp-compact' if compact else ''}" id="map" data-focus="{focus or ''}">
<div class="mp-top">
<h2 class="mp-h">{"Where this sits" if compact else "Where things actually differ"}</h2>
<p class="mp-sub">{"Every regency runs its own spatial rules and its own permit queue. Hover any area for what governs it there." if compact else "Every regency runs its own spatial rules and its own permit queue. Hover an area &mdash; or tap on a phone &mdash; for what governs it there."}</p>
</div>
<div class="mp-stage">
<svg viewBox="0 0 1000 470" class="mp-svg" role="img" aria-label="Schematic map of Bali showing investment areas">
<path class="mp-land" d="M932.2 138.3 L946.8 144.3 L962.6 156.0 L974.6 171.1 L978.0 187.5 L974.6 194.7 L960.9 215.1 L956.5 219.3 L953.9 224.9 L952.1 256.8 L947.0 264.1 L929.9 281.4 L926.3 289.8 L918.2 303.1 L899.7 336.2 L884.8 350.4 L876.9 360.5 L880.2 373.3 L879.3 379.4 L880.5 383.8 L885.1 384.4 L888.9 377.2 L893.7 374.6 L896.4 378.5 L901.7 379.9 L906.6 384.2 L913.7 386.0 L903.9 399.6 L886.7 402.3 L880.5 400.2 L866.6 409.9 L854.5 410.0 L848.7 406.0 L857.1 395.8 L860.2 386.6 L865.0 376.0 L858.2 373.6 L844.7 374.7 L834.1 382.7 L834.1 394.1 L835.9 408.3 L836.3 424.3 L830.6 422.2 L830.3 411.4 L826.6 406.5 L822.6 406.2 L818.7 411.8 L814.8 412.5 L808.9 402.8 L805.0 401.0 L797.6 402.5 L781.9 408.8 L774.8 409.9 L772.3 408.8 L769.5 404.8 L766.8 403.9 L762.1 404.9 L756.7 409.0 L753.7 409.9 L750.3 407.5 L742.8 396.4 L738.1 392.4 L731.9 391.2 L712.5 390.8 L710.7 396.8 L706.2 399.8 L700.6 399.2 L695.2 394.7 L699.9 392.9 L702.8 390.0 L703.3 386.8 L700.9 383.8 L697.0 382.9 L689.2 385.8 L685.2 386.6 L683.5 389.1 L685.2 402.5 L680.9 404.9 L676.5 404.9 L672.4 403.4 L669.3 401.0 L667.0 397.2 L663.7 387.7 L660.8 383.8 L655.6 380.2 L653.6 380.6 L651.3 382.6 L645.3 383.8 L638.6 382.5 L613.2 368.3 L601.5 366.5 L597.1 355.9 L597.9 346.7 L599.2 337.9 L605.4 327.7 L613.9 330.2 L618.2 327.7 L620.3 331.1 L621.6 336.6 L623.6 340.4 L649.5 339.9 L655.2 337.3 L661.4 332.9 L665.5 335.1 L669.5 335.3 L678.1 337.5 L685.6 331.6 L689.5 331.8 L692.4 338.3 L695.8 342.5 L700.6 335.5 L704.9 333.0 L706.6 328.6 L693.6 323.1 L694.8 305.9 L697.9 291.4 L698.7 265.8 L694.7 242.0 L684.5 233.2 L680.1 209.9 L689.3 197.1 L697.2 193.6 L709.2 194.5 L712.5 193.2 L714.5 190.6 L717.3 183.4 L719.6 180.2 L726.1 175.3 L738.4 168.6 L743.8 164.5 L780.8 126.8 L787.7 122.0 L825.2 107.5 L832.5 107.2 L845.3 114.2 L875.6 122.4 L893.0 125.2 L899.4 128.3 L907.1 133.7 L914.6 136.1 L932.2 138.3 Z M509.8 144.1 L523.7 156.6 L539.8 167.5 L549.4 180.5 L543.9 199.0 L539.6 203.3 L526.2 214.3 L518.5 218.8 L508.3 229.9 L503.9 233.5 L474.2 235.8 L469.8 237.8 L466.8 247.5 L459.7 253.4 L403.6 273.9 L386.3 285.2 L373.1 299.9 L363.9 316.9 L357.7 323.4 L348.5 326.0 L340.4 329.3 L336.6 337.1 L337.5 346.5 L343.8 354.7 L346.9 351.9 L345.0 350.1 L341.2 343.3 L348.8 340.0 L351.1 347.7 L350.0 367.7 L347.3 372.1 L340.8 376.2 L333.2 379.2 L327.3 380.7 L317.5 381.2 L308.0 380.8 L299.2 378.5 L291.5 373.6 L291.2 367.2 L299.8 360.8 L318.3 351.9 L323.0 346.2 L327.7 336.8 L329.5 326.7 L317.0 301.3 L306.9 297.0 L295.0 287.6 L289.5 281.4 L287.2 275.3 L283.9 268.9 L276.2 262.8 L261.4 253.6 L232.4 226.8 L221.5 219.3 L167.2 193.2 L150.3 190.0 L101.6 190.3 L87.2 185.2 L74.6 175.1 L64.1 163.2 L30.5 114.5 L22.0 73.8 L23.9 62.5 L36.0 60.2 L45.7 60.6 L51.1 64.5 L60.2 76.4 L66.7 78.9 L73.3 77.0 L84.3 69.1 L90.6 73.8 L99.5 76.0 L115.8 77.7 L123.4 79.3 L192.6 103.8 L207.3 98.4 L245.4 98.5 L261.4 95.2 L278.3 82.8 L308.6 53.1 L323.9 45.8 L332.4 45.7 L341.7 47.5 L350.3 51.1 L363.9 60.1 L392.7 66.2 L461.2 95.2 L474.9 104.4 L487.3 115.8 L509.8 144.1 Z M481.1 303.0 L490.6 305.5 L497.3 315.4 L500.9 325.2 L508.4 334.0 L511.9 346.3 L497.2 362.5 L485.5 359.0 L462.4 342.9 L455.5 334.4 L449.6 332.7 L447.0 330.7 L448.3 327.3 L463.1 308.4 L467.5 304.7 L474.8 306.2 L481.1 303.0 Z"/>
<g class="mp-regency">
<text x="215" y="175">BALI</text><text x="800" y="215">LOMBOK</text>
</g>
{pins}
</svg>
<aside class="mp-card" id="mp-card" aria-live="polite">
<p class="mp-empty">Pick an area.</p>
</aside>
</div>
<p class="mp-fine">Coastline from Natural Earth (public domain). Land prices are leasehold per are (100&nbsp;m&sup2;) and move street by street. Permit figures are PBG from empty land.</p>
<script>window.MAP_DATA={data}</script>
</section>"""


def calc_widget():
    """The interactive model. Shared by the home page and the tool page, so the
    markup and the field IDs calc.js depends on stay in one place."""
    return f"""<div class="calc-wrap">
<form id="calc" class="calc-form" onsubmit="return false">

<fieldset class="fs">
<legend>What you are buying</legend>
{choice("tenure", "What you are buying", [("lease", "Leasehold"), ("hgb", "HGB / Hak Pakai"), ("freehold", "Freehold-equivalent")],
        "Leasehold is a contract for a fixed number of years, at the end it returns nothing unless the agreement contains an enforceable extension. HGB and Hak Pakai are registered rights, time-limited but renewable, commonly 30 years plus a 20-year extension and a 30-year renewal, each step subject to approval. Freehold-equivalent means the value does not run down. Hak Milik is not available to foreigners, so this mainly models an Indonesian-held title or a comparison case.")}
{choice("asset", "Property type", [("villa", "Villa"), ("apartment", "Apartment"), ("guesthouse", "Guesthouse")],
        "This only sets sensible starting numbers for rate, occupancy and running costs. Change any field and your value is kept.")}
{choice("revmode", "How it earns", [("nightly", "Nightly rental"), ("monthly", "Long-term rental")],
        "Nightly means short-term accommodation, which is a licensed business activity and attracts OTA commission and PB1. Long-term means a genuine residential tenancy. Different legal activity, far lower costs, and it does not need an accommodation licence.")}
{field("years", "Years remaining on the right", "25",
       "The number of years you actually get. This drives the amortisation. It is the single most important input on the page and the one most often glossed over in a sales pitch.", "1", "term-only")}
{field("residual", "Value left at the end (%)", "0",
       "What the asset is still worth to you when the term expires, as a percentage of what you put in. A plain lease is 0. It reverts to the landowner. HGB defaults to 60% on the assumption renewal succeeds but costs money and carries risk. Set it to 0 to see the worst case.", "5", "term-only")}
</fieldset>

<fieldset class="fs">
<legend>Capital in</legend>
{field("price", "Purchase price or lease premium (USD)", "300000",
       "The headline number, what you hand over for the property or the lease.", "1000")}
{field("build", "Build or renovation (USD)", "0",
       "Construction or refurbishment. Leave at zero if you are buying something finished.", "1000")}
{field("ffe", "Furniture, pool, setup (USD)", "35000",
       "Furniture, fittings and equipment. Routinely underestimated, a villa fit-out to rentable standard is rarely trivial.", "1000")}
{field("tx", "Transaction costs (%)", "7",
       "BPHTB (buyer's transfer tax, around 5% on a titled transfer), notary and PPAT fees, legal due diligence and agent commission. Budget an extra margin for contingencies.", "0.5")}
</fieldset>

<fieldset class="fs">
<legend>Revenue</legend>
{field("adr", "Average nightly rate (USD)", "180",
       "Your average achieved rate across the whole year, not your high-season headline rate.", "5", "nightly-only")}
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
       "What a management company charges, usually on net room revenue after platform commission. Verify the base. A fee on gross is a materially different number.", "1")}
{field("opex", "Staff, utilities, upkeep (USD / month)", "1200",
       "Villa staff, power, water, pool and garden, internet, supplies, repairs. Staffing is the big line and it does not scale down in low season.", "50")}
{field("capex", "Refurbishment reserve (%)", "5",
       "Money set aside for the refit a rental property needs every few years. Almost never shown in a yield projection, which is why projections look better than reality.", "1")}
{field("tax_rate", "Income tax (%)", "22",
       "Tax on profit. 22% is the standard Indonesian corporate rate for a PT PMA. Personal rates and small-business regimes differ, use your actual figure.", "1")}
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
<p>Cumulative position across the term. You start at minus your capital, and the line is where you stand each year. Anything below zero at the end is a loss, whatever the yield said.</p></figcaption>
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
<p>Capital appreciation, currency movement, financing costs, and the risk that the property cannot legally be operated as short-term accommodation at all. That last one is not a rounding error, <a href="{BASE}/company/pt-pma-kbli-closure-bali/">Bali closed the villa and homestay business classifications to new foreign-owned companies in July 2026</a>, and zoning determines whether nightly rental is permitted on the plot before any of these numbers matter.</p>
</div>
{cta("Send me the seller's projection.",
     "If you have a yield sheet from an agent or developer, send it to me with the location and the title type. I'll tell you which assumptions break first, the occupancy, the lease term, the licence, or the zoning. ",
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

    ALL_PAGES.extend(pages)

    for p in pages:
        sib = [s for s in pages if s["category"] == p["category"]][:5]
        write(f'/{p["category"]}/{p["slug"]}/', article(p, sib))

    for k in CATEGORIES:
        cat_pages = [p for p in pages if p["category"] == k]
        write(f"/{k}/", category(k, cat_pages))

    write("/", home(pages))
    write("/calculator/", calculator())
    write("/about/", about_page())
    write("/check/", check_page())
    write("/all/", all_page(pages))
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

    urls = ["/", "/about/", "/all/", "/calculator/", "/check/", "/search/", "/checklist/", "/disclaimer/"] + [f"/{k}/" for k in CATEGORIES] + \
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

Indonesian regulations change frequently and are applied inconsistently between regencies and between individual government offices. A rule that held last quarter in Badung may be administered differently this quarter in Tabanan. Figures on this site, minimum property values, capital thresholds, tax rates, visa income requirements, are the ones in force when the page was written, and they move.

Before you sign anything, transfer any money, or rely on any structure described here, verify it with a licensed Indonesian notary or PPAT, an Indonesian lawyer, and a registered tax consultant. Engage your own, not the seller's.

Treat every figure here as a starting point for your own checking rather than a current fact. Indonesian thresholds, rates and requirements are revised regularly.
"""

CHECKLIST = """
Print this. Take it to viewings. If a seller or agent gets defensive about any line on it, that is the answer.

## Before you pay a deposit

- Original certificate sighted, SHM, SHGB or SHP, not a photocopy, not a photo
- Certificate verified at the local BPN office by your own notary
- Land physically walked with GPS against the cadastral drawing
- Zoning confirmed on GISTARU or at the regency planning office, not from the agent
- Zoning permits your intended use (pink for commercial rental; yellow and green do not)
- No hak tanggungan (mortgage or lien) registered against the title
- No dispute, no overlapping certificate, no sertifikat ganda
- Seller identity confirmed against KTP and family card
- Spouse consent obtained where land is joint marital property
- All heirs identified and consenting where the land came through inheritance
- PBB (annual land tax) receipts current, no arrears

## Before you sign

- Access road confirmed as legal right of way, in writing, with width recorded
- Setbacks checked, beach, river, cliff, and any temple or sacred-site buffer
- PBG (building permit) exists for every structure on the plot
- SLF (fitness certificate) issued
- If leasehold: extension clause is unconditional, priced or formula-based, and binds the owner's heirs and successors
- If leasehold: transfer and sublease rights are explicit
- If buying a company: full corporate, tax and licensing due diligence, and confirmation the LKPM reports are filed
- Your own notary or PPAT engaged, not the one the seller brought

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
