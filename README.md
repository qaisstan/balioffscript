# Bali Off Script

Static site. No database, no build tools, no monthly cost.

## Publish it

1. Create a GitHub repo named `baliofscript.github.io`
2. Upload everything in this folder (drag and drop works in GitHub's web UI)
3. Settings → Pages → Source: `main` branch, folder: `/docs`
4. Live in ~2 minutes

The naming matters: `username.github.io` serves at the domain root, which the
absolute paths in this site need. When you buy the domain, point it at GitHub
Pages — `docs/CNAME` already contains `baliofscript.com`.

## Add a page

1. Copy any file in `content/`, rename it — the filename becomes the URL
2. Edit the frontmatter and body
3. Run `python3 build.py`
4. Commit

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
