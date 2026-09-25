#!/usr/bin/env python3
"""Read several pages from stdin and write them into content/.

Each page starts with a header line:
===slug|category|order|question|title|summary|applies[|regulation]
then the markdown body until the next header.
"""
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-09-25"
raw = sys.stdin.read()
parts = re.split(r"^===", raw, flags=re.M)
n = 0
for part in parts:
    if not part.strip():
        continue
    head, body = part.split("\n", 1)
    f = [x.strip() for x in head.split("|")]
    slug, cat, order, question, title, summary, applies = f[:7]
    reg = f[7] if len(f) > 7 else ""
    body = body.strip()
    fm = [f"question: {question}", f"title: {title}", f"summary: {summary}",
          f"category: {cat}", f"order: {order}", "risk: none",
          f"regulation: {reg}", f"applies: {applies}", f"verified: {TODAY}"]
    path = os.path.join(ROOT, "content", slug + ".md")
    open(path, "w", encoding="utf-8").write("---\n" + "\n".join(fm) + "\n---\n\n" + body + "\n")
    words = len(body.split())
    flag = "  <-- THIN" if words < 700 else ""
    tl = len(title)
    flag += "  <-- LONG TITLE" if tl > 60 else ""
    print(f"{slug}: {words} words, title {tl}{flag}")
    n += 1
print(f"wrote {n}")
