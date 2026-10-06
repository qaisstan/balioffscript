#!/usr/bin/env python3
"""Print each Buyer's Kit page to PDF with headless Chrome.

    python3 tools/make_pdfs.py http://localhost:8792     # a server serving docs/

Writes assets/kit/<TOKEN>/bali-buyers-kit-<lang>.pdf (kept in the repo, copied
into docs/ by build.py) and also straight into docs/ so no rebuild is needed.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import kit as K  # noqa: E402
import guides as G  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main(base, only=None):
    out_dir = os.path.join(ROOT, "assets", "kit", K.TOKEN)
    os.makedirs(out_dir, exist_ok=True)
    jobs = [(f"bali-buyers-kit-{lang}.pdf", f"/kit/{K.TOKEN}/{lang}/") for lang in K.LANGS
            if os.path.exists(os.path.join(K.KIT_SRC, f"{lang}.md"))]
    jobs += [(f"bali-{k}-guide.pdf", G.doc_path(k)) for k in G.GUIDES]   # the topic guides
    for name, path in jobs:
        if only and only not in name:
            continue
        lang = name
        pdf = os.path.join(out_dir, name)
        url = f"{base.rstrip('/')}{path}"
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--virtual-time-budget=15000", f"--print-to-pdf={pdf}", url],
                           capture_output=True, text=True, timeout=180)
        ok = os.path.exists(pdf) and os.path.getsize(pdf) > 10000
        print(lang, "ok" if ok else "FAILED", os.path.getsize(pdf) if ok else r.stderr[-300:])
        if ok:
            dst = os.path.join(ROOT, "docs", "kit", K.TOKEN)
            os.makedirs(dst, exist_ok=True)
            shutil.copy(pdf, dst)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8792", sys.argv[2] if len(sys.argv) > 2 else None)
