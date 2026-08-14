# Bali Off Script

Static site. No database, no build tools, no monthly cost.

## Where it lives

Repo `qaisstan/balioffscript`, served by GitHub Pages from the `docs/` folder
on `main`:

    https://qaisstan.github.io/balioffscript/

Settings → Pages → Source: `main` branch, folder `/docs`. Custom domain: empty.

The account's `*.github.io` user site is already taken by a separate, unrelated
project — never modify that repo or its Pages settings. This site is therefore
a project page, which is why `BASE` exists in `build.py`. With the custom
domain attached, `BASE` is empty and everything serves from the root.

Do not upload files through GitHub's web interface. It silently drops dotfiles,
which means `docs/.nojekyll` goes missing and the build breaks. Use `git push`.

## Moving to balioffscript.com

Order matters. DNS first, then GitHub, then the build.

1. Buy `balioffscript.com` at Namecheap
2. Namecheap → Domain List → Manage → Advanced DNS. **Delete the two parking
   records Namecheap creates by default**, then add:

       A      @      185.199.108.153
       A      @      185.199.109.153
       A      @      185.199.110.153
       A      @      185.199.111.153
       CNAME  www    qaisstan.github.io.

3. Wait for DNS to resolve — `dig +short balioffscript.com` should return the
   four addresses above
4. Repo → Settings → Pages → Custom domain: `balioffscript.com`, Save. Wait for
   the DNS check to go green, then tick **Enforce HTTPS**
5. In `build.py` set `DOMAIN = "balioffscript.com"`
6. `python3 build.py`, commit, push

Step 5 is one line. `BASE`, `SITE_URL`, every internal link, the sitemap and the
`docs/CNAME` file all follow from it.

Do not set `DOMAIN` before the DNS resolves. GitHub reads `docs/CNAME` as "serve
this site at this domain" and the site goes offline until that domain works.

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
