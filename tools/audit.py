#!/usr/bin/env python3
"""Audit docs/: broken links, dead anchors, duplicate ids, schema, titles, cards, depth."""
import json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
pages = {}
for dirpath, _, files in os.walk(OUT):
    for f in files:
        if f.endswith(".html"):
            p = os.path.join(dirpath, f)
            url = "/" + os.path.relpath(p, OUT).replace("index.html", "")
            url = url.rstrip("/") + "/" if not url.endswith(".html") else url
            pages[url.replace("//", "/")] = open(p, encoding="utf-8").read()
print(f"{len(pages)} html pages")
problems = collections.defaultdict(list)
ids = {}
for url, html in pages.items():
    page_ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    dup = [i for i, c in collections.Counter(page_ids).items() if c > 1]
    if dup: problems["duplicate ids"].append(f"{url}: {dup}")
    ids[url] = set(page_ids)
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    if t and len(t.group(1)) > 60: problems["title over 60"].append(f"{url}: {len(t.group(1))}")
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not d: problems["no description"].append(url)
    elif len(d.group(1)) < 110: problems["description under 110"].append(f"{url}: {len(d.group(1))}")
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try: json.loads(m)
        except Exception as e: problems["bad json-ld"].append(f"{url}: {e}")
for url, html in pages.items():
    for href in re.findall(r'href="(/[^"]*)"', html):
        target, _, frag = href.partition("#")
        target = target or url
        if not target.endswith("/") and "." not in os.path.basename(target): target += "/"
        if target.endswith("/") and target not in pages:
            if not os.path.exists(os.path.join(OUT, target.strip("/"))):
                problems["broken link"].append(f"{url} -> {href}")
                continue
        if frag and target in pages and frag not in ids[target]:
            problems["dead anchor"].append(f"{url} -> {href}")
# crawl depth from home
seen, depth, frontier = {"/": 0}, 0, ["/"]
while frontier:
    nxt = []
    for u in frontier:
        for href in re.findall(r'href="(/[^"#]*)"', pages.get(u, "")):
            t = href if href.endswith("/") else href + "/"
            if t in pages and t not in seen:
                seen[t] = seen[u] + 1; nxt.append(t)
    frontier = nxt
orphans = [u for u in pages if u not in seen]
if orphans: problems["unreachable"].extend(orphans)
print("max depth", max(seen.values()))
# og cards + cta
for url, html in pages.items():
    if re.search(r'"@type": "Article"', html):
        card = re.search(r'/og/([\w-]+)\.jpg', html)
        if not card or not os.path.exists(os.path.join(OUT, "og", card.group(1) + ".jpg")):
            problems["missing og card"].append(url)
        if "/opportunities/" not in html: problems["no CTA"].append(url)
for k, v in problems.items():
    print(f"\n{k}: {len(v)}")
    for x in v[:12]: print("  ", x)
print("\nOK" if not problems else "\nISSUES")
