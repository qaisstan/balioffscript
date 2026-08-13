# Bali Off Script

Static site. No database, no build tools, no monthly cost.

## Where it lives

Repo `qaisstan/balioffscript`, served by GitHub Pages from the `docs/` folder
on `main`:

    https://qaisstan.github.io/balioffscript/

Settings → Pages → Source: `main` branch, folder `/docs`. Custom domain: empty.

`qaisstan.github.io` is not available for this site — it already serves the
personal portfolio at `www.qaisstanikzai.com`. So this is a project page and
lives under a `/balioffscript/` path. That is handled by `BASE` in `build.py`,
which prefixes every internal link.

Do not upload files through GitHub's web interface. It silently drops dotfiles,
which means `docs/.nojekyll` goes missing and the build breaks. Use `git push`.

## Moving to baliofscript.com

The domain is not bought yet. When it is:

1. Buy it, and point DNS at GitHub Pages (four A records for the apex, or a
   CNAME record for `www` → `qaisstan.github.io`)
2. Settings → Pages → Custom domain: enter it, save, tick Enforce HTTPS.
   GitHub writes its own `docs/CNAME` file
3. In `build.py` set `BASE = ""` and `SITE_URL = "https://baliofscript.com"`
4. `python3 build.py`, commit, push

Do not create `docs/CNAME` by hand before the domain resolves — GitHub reads it
as "serve this site at this domain" and the site goes offline until it does.

## Add a page

1. Copy any file in `content/`, rename it — the filename becomes the URL
2. Edit the frontmatter and body
3. Run `python3 build.py`
4. Commit and push — `git add -A && git commit -m "New page" && git push`

Never edit anything inside `docs/` by hand. `build.py` deletes and rewrites
that whole folder every run.

Frontmatter fields:

    question:    the headline, and the SEO title
    summary:     one sentence, shown in search results and cards
    category:    ownership | visas | company | tax | building | rental | areas
    order:       sort position within the category
    risk:        critical | high | medium | info  (colours the stamp)
    regulation:  the legal citation shown in the stamp
    applies:     who this affects
    verified:    date you last checked it — keep this honest
    reel:        Instagram permalink, optional; embeds the video on the page

Body supports headings, bold, lists, tables, links, `code`, and `>` for a pull quote.

## Adding your Reels

Paste the Instagram permalink into the `reel:` field:

    reel: https://www.instagram.com/reel/ABC123/

The embed renders above the contact block. Pages without a reel just skip it.

## What's built in

- Client-side search across every page (`/search/`)
- sitemap.xml and robots.txt
- FAQPage structured data on every answer
- Canonical URLs and Open Graph tags
- Mobile nav, keyboard focus, reduced-motion support

## Before you go live

Search and replace the Instagram handle in `build.py` if it changes, and read
`/disclaimer/`. You are publishing legal and tax information as an adviser —
the verified date on each page is what makes that defensible. Keep it current.
