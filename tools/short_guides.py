"""Short, visual lead-magnet guides (Kai, 10 Oct 2026): phone-sized pages, photos, big numbers, 8 pages each.

Each talking head points to one topic guide; the DM sends the guide's landing page, the form captures name, email
and WhatsApp, and the Sheet's Interest column records which guide they took. Facts come only from the site's own
pages (content/*.md). Never a project name: we find land and projects for people, we don't advertise them.

    python3 tools/short_guides.py            # writes tools/short_guides_out/*.html and the PDFs in docs/kit/<token>/
"""
import html
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import photos as PH  # noqa: E402
import kit as K      # noqa: E402

OUT_HTML = os.path.join(HERE, "short_guides_out")
OUT_PDF = os.path.join(ROOT, "assets", "kit", K.TOKEN)      # build.py copies this into docs/; we copy too
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WA = "https://wa.me/46700081414?text=" + "Hi%20Kai%2C%20I%20read%20your%20guide.%20I%27m%20looking%20at%20"


def img(pool, i=0, w=900, h=560):
    return PH.url(PH.POOLS[pool][1][i % len(PH.POOLS[pool][1])], w, h)


e = html.escape

CSS = """
@page{size:450px 800px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:"Plus Jakarta Sans",Helvetica,Arial,sans-serif;color:#0E2A21;font-size:14px;line-height:1.5}
.pg{width:450px;height:800px;position:relative;overflow:hidden;break-after:page;background:#fff;padding:34px 28px 50px;display:flex;flex-direction:column;gap:14px}
.pg:last-child{break-after:auto}
.mint{background:#E9F4EE}.dark{background:#0B3B2E;color:#fff}
.k{font-size:10.5px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#178A5B}
.dark .k{color:#FFD60A}
h1{font-size:40px;line-height:1.02;font-weight:800;letter-spacing:-.02em}
h2{font-size:28px;line-height:1.08;font-weight:800;letter-spacing:-.015em}
h3{font-size:17px;font-weight:800;line-height:1.2}
p.l{font-size:15px;color:#3E5A50}.dark p.l{color:#CFE5DA}
.y{background:linear-gradient(transparent 58%,#FFD60A 58%);padding:0 2px}
.dark .y{background:none;color:#FFD60A}
.ph{width:calc(100% + 56px);margin:-34px -28px 4px;height:230px;object-fit:cover;display:block}
.ft{position:absolute;left:28px;right:28px;bottom:18px;display:flex;justify-content:space-between;font-size:10px;font-weight:700;color:#7C948A}
.dark .ft{color:#7FB09B}
/* cover */
.cv{padding:0;justify-content:flex-end;color:#fff}
.cv img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cv .sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,30,23,.15) 0%,rgba(7,30,23,.35) 45%,rgba(7,30,23,.92) 100%)}
.cv .in{position:relative;padding:0 28px 46px;display:flex;flex-direction:column;gap:14px}
.cv .tag{display:inline-block;background:#FFD60A;color:#0B3B2E;font-weight:800;font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:6px 10px;border-radius:6px;align-self:flex-start}
.cv h1{font-size:44px}.cv p{font-size:16px;color:#E3F0EA}
.cv .by{font-size:12px;color:#BFD9CC;border-top:1px solid rgba(255,255,255,.25);padding-top:12px}
/* stats */
.stats{display:flex;flex-direction:column;gap:10px}
.st{border-radius:14px;padding:14px 16px;background:#E9F4EE;display:flex;gap:14px;align-items:center}
.st b{font-size:30px;font-weight:800;letter-spacing:-.02em;min-width:118px;line-height:1}
.st span{font-size:13.5px;line-height:1.35}
.st.hot{background:#0B3B2E;color:#fff}.st.hot b{color:#FFD60A}
.st.warn{background:#FFF4C2}
/* rows */
.rows{display:flex;flex-direction:column;border-radius:14px;overflow:hidden;border:1px solid #D7E8DF}
.r{display:grid;grid-template-columns:1fr auto;gap:10px;padding:10px 14px;border-bottom:1px solid #D7E8DF;font-size:13.5px;align-items:center}
.r:last-child{border-bottom:none}.r b{font-weight:800;white-space:nowrap}
.r.h{background:#0B3B2E;color:#fff;font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.dark .rows{border-color:rgba(255,255,255,.18)}.dark .r{border-color:rgba(255,255,255,.18)}
/* area cards */
.ar{display:flex;flex-direction:column;gap:7px}
.ar img{width:100%;height:150px;object-fit:cover;border-radius:14px;display:block}
.ar .nm{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.ar .pr{font-size:12px;font-weight:800;color:#0B3B2E;background:#FFD60A;border-radius:6px;padding:3px 7px;white-space:nowrap}
.ar p{font-size:13px;line-height:1.4}.ar .c{color:#9A3B1E}
/* list */
.ls{display:flex;flex-direction:column;gap:9px}
.li{display:flex;gap:12px;align-items:flex-start}
.li i{flex-shrink:0;width:26px;height:26px;border-radius:50%;background:#0B3B2E;color:#FFD60A;font-style:normal;font-weight:800;font-size:13px;display:grid;place-items:center}
.dark .li i{background:#FFD60A;color:#0B3B2E}
.li div{font-size:13.5px;line-height:1.4}.li b{display:block;font-size:14.5px}
/* two cols */
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.box{border-radius:14px;padding:13px;background:#E9F4EE;font-size:13px;line-height:1.4;display:flex;flex-direction:column;gap:4px}
.box b{font-size:14.5px}.box.g{background:#0B3B2E;color:#fff}.box.g b{color:#FFD60A}
.note{font-size:12.5px;background:#FFF4C2;border-radius:12px;padding:11px 13px;line-height:1.4}
.cta{display:block;background:#FFD60A;color:#0B3B2E;text-decoration:none;font-weight:800;font-size:17px;text-align:center;padding:16px;border-radius:14px}
.small{font-size:10.5px;color:#7FB09B;line-height:1.4}
"""

FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap">'


def cover(title, sub, photo):
    return (f'<section class="pg cv"><img src="{photo}" alt=""><div class="sh"></div><div class="in">'
            f'<span class="tag">Free guide</span><h1>{title}</h1><p>{e(sub)}</p>'
            f'<div class="by">By Kai, Bali property adviser · balioffscript.com</div></div></section>')


def page(body, cls="", photo=None):
    top = f'<img class="ph" src="{photo}" alt="">' if photo else ""
    return f'<section class="pg {cls}">{top}{body}<div class="ft"><span>Bali Off Script</span><span>{{n}}</span></div></section>'


def stats(items):
    return '<div class="stats">' + "".join(f'<div class="st {c}"><b style="font-size:{30 if len(v) <= 6 else 21}px">{v}</b><span>{t}</span></div>' for v, t, c in items) + "</div>"


def rows(head, items):
    h = f'<div class="r h"><span>{head[0]}</span><span>{head[1]}</span></div>' if head else ""
    return '<div class="rows">' + h + "".join(f'<div class="r"><span>{a}</span><b>{b}</b></div>' for a, b in items) + "</div>"


def lst(items):
    return '<div class="ls">' + "".join(f'<div class="li"><i>{i + 1}</i><div><b>{a}</b>{b}</div></div>' for i, (a, b) in enumerate(items)) + "</div>"


def area(name, price, photo, best, catch):
    return (f'<div class="ar"><img src="{photo}" alt=""><div class="nm"><h3>{name}</h3><span class="pr">{price}</span></div>'
            f'<p><b>Best for:</b> {best}</p><p class="c"><b>The catch:</b> {catch}</p></div>')


def help_page(topic_line, wa_topic):
    body = (f'<span class="k">What I do for you</span><h2>You don\'t have to do this alone.</h2>'
            f'<p class="l">{topic_line}</p>'
            + lst([("I find the land", "In the area and budget that fit your plan, with the zoning checked first."),
                   ("I find the right property or project", "Built, off-plan or land to build on. I look at all of them, so you see the honest options."),
                   ("I check everything before you pay", "Certificate, zoning, permits, the lease clauses and the seller."),
                   ("I stay with you to the notary", "Questions answered straight, in plain words, until the keys are yours.")])
            + f'<a class="cta" href="{WA}{wa_topic}">Message me on WhatsApp</a>'
            '<p class="small">Tell me the area, your budget and your timing, and I\'ll tell you what I would check first. '
            'This guide is general information, not legal or tax advice. Rules change: verify with your own notary before you sign.</p>')
    return page(body, "dark")


def build(slug, title, pages):
    out = "".join(p.replace("{n}", str(i + 1)) for i, p in enumerate(pages))
    doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(title)}</title>{FONT}<style>{CSS}</style></head><body>{out}</body></html>'
    os.makedirs(OUT_HTML, exist_ok=True)
    src = os.path.join(OUT_HTML, slug + ".html")
    open(src, "w", encoding="utf-8").write(doc)
    pdf = os.path.join(OUT_PDF, f"bali-{slug}-guide.pdf")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
                    f"--print-to-pdf={pdf}", "file://" + src], check=True, capture_output=True)
    import shutil
    shutil.copy(pdf, os.path.join(ROOT, "docs", "kit", K.TOKEN))
    print(slug, "->", os.path.relpath(pdf, ROOT))


# ---------------------------------------------------------------- the guides

def areas():
    return [
        cover("Where to Buy in Bali: Area by Area", "Land prices, who rents there and the catch in every area. Eight areas, eight minutes.", img("uluwatu", 1, 900, 1600)),
        page('<span class="k">Read this first</span><h2>Bali land is priced <span class="y">per are</span>.</h2>'
             '<p class="l">One are is 100 m². A plot of "5 are" is 500 m². Get this wrong and every listing looks cheap or expensive for the wrong reason.</p>'
             + stats([("1 are", "= 100 m². One hectare is 100 are.", ""),
                      ("Leasehold", "The prices in this guide are leasehold, for the full term. Foreigners can't buy freehold.", ""),
                      ("Zoning", "Two plots at the same price can hold six times more building. The zoning colour decides.", "hot")])
             + '<p class="note">Prices move street by street. Treat them as a starting point for a conversation, not a valuation.</p>', photo=img("rice", 2)),
        page('<span class="k">The west coast</span>'
             + area("Berawa, Canggu", "~$82,500 / are", img("canggu", 0), "the highest, steadiest occupancy in Bali and the easiest resale.",
                    "the return is largely priced in, and your budget buys a shorter lease.")
             + area("Pererenan & Cemagi", "$55k–75k / are", img("canggu", 3), "income at a mid-range budget. A decade more lease for the money.",
                    "constant construction, more green zone, and a higher risk of buying land you can't build on.")),
        page('<span class="k">The south</span>'
             + area("Uluwatu clifftop", "$40k–60k / are", img("uluwatu", 0), "the highest nightly rates on the island for view villas.",
                    "the strictest setbacks. Buildings at Bingin were demolished in 2025.")
             + area("Uluwatu inland & Bukit", "$25k–40k / are", img("surf", 1), "land and room to build, about a third of Berawa's price.",
                    "water supply, and long drives to everything.")),
        page('<span class="k">Calm and steady</span>'
             + area("Sanur", "Best value, established", img("sanur", 0), "families, retirees and the steadiest year-round occupancy.",
                    "lower peak rates. Calm, not a scene.")
             + area("Ubud", "Good land value", img("ubud", 1), "wellness and long-stay guests, above 70% occupancy in the right pockets.",
                    "no beach, humid, and lower nightly rates.")),
        page('<span class="k">The frontier</span>'
             + area("Tabanan coast", "30–50% below Canggu", img("tanahlot", 0), "entry price and upside. The Gilimanuk to Mengwi toll road is targeted for 2027 to 2028.",
                    "the rental market is years behind, and licensing is the hardest on the island.")
             + area("North & East Bali", "Cheapest coast", img("east", 1), "genuine quiet, black sand beaches and a long horizon.",
                    "thin rental demand and limited services. A capital play, not income.")),
        page('<span class="k">Pick by your goal</span><h2>The right area depends on <span class="y">you</span>.</h2>'
             + rows(("If you want", "Look at"), [("Income on a mid budget", "Pererenan"), ("Easiest resale", "Berawa, Seminyak"),
                                                 ("Highest nightly rates", "Uluwatu cliffs"), ("Land to build on", "Pecatu, Ungasan"),
                                                 ("Family life, steady guests", "Sanur"), ("Long-stay wellness guests", "Ubud"),
                                                 ("Upside, long horizon", "Tabanan")])
             + '<p class="note"><b>Under about $300,000, the lease term beats the postcode.</b> More years in a good-enough area usually wins.</p>', "mint"),
        help_page("Tell me what you want from Bali and I'll match it to the right area, then find the land or the property that fits.", "buying%20in%20"),
    ]


def rent():
    return [
        cover("The Bali Rental Income Guide", "What a villa really earns after every cost. The numbers the brochures leave out.", img("villa", 2, 900, 1600)),
        page('<span class="k">The first thing to know</span><h2>The brochure number is <span class="y">gross</span>.</h2>'
             + stats([("8–15%", "The yield on most brochures. A year of bookings divided by the price, before any cost.", "warn"),
                      ("4–6%", "What an average villa really keeps, net, after every cost and tax.", ""),
                      ("7–9%", "Net on a villa that was well bought and is well run. That's a good result.", "hot")])
             + '<p class="l">Bali can be a great buy. Just buy on the net number, never the brochure.</p>', photo=img("villa", 5)),
        page('<span class="k">One villa, real numbers</span><h2>A $300,000 villa, worked out.</h2>'
             '<p class="l">$150 a night, 65% occupancy, a 25-year lease.</p>'
             + rows(None, [("Bookings for the year", "$35,588"), ("Running costs, 45% of gross", "− $16,014"), ("Income tax, 10%", "− $3,559"),
                           ("<b>What reaches you</b>", "$16,015 · 5.3%"), ("The lease running down ($300k ÷ 25)", "− $12,000"),
                           ("<b>Your real economic return</b>", "$4,015 · 1.3%")])
             + '<p class="note">The lease is the hidden cost. A guaranteed extension in the contract changes this whole picture.</p>'),
        page('<span class="k">What guests pay</span><h2>Nightly rates and occupancy</h2>'
             + rows(("Bedrooms", "Base rate a night"), [("One", "$80–110"), ("Two", "$130–180"), ("Three", "$180–260"), ("Four", "$250–350"), ("Five", "$300–450")])
             + rows(("Villa", "Occupancy"), [("Well run, strong area, 1–3 bed", "70–80%"), ("Larger villas", "60–70%"), ("Average villa or location", "50–60%")])
             + '<p class="l" style="font-size:13px">Peak season runs 40 to 70% above the base rate.</p>', "mint"),
        page('<span class="k">Where the money goes</span><h2>Running costs take <span class="y">40–50%</span> of gross.</h2>'
             + rows(None, [("Management", "15–25%"), ("Platform commission", "~15.5%"), ("Accommodation tax (PB1)", "10%"),
                           ("Maintenance", "10–15%"), ("Reserve for pool, roof, aircon", "10–15%"), ("Pool, before repairs", "$100–200/mo"),
                           ("Land and building tax (PBB)", "0.1–0.5%")])
             + '<p class="note">Staff, utilities and insurance come on top. Aircon and a pool pump cost more power than most models assume.</p>', photo=img("villa", 9)),
        page('<span class="k">What earns more</span><h2>Five things that move your rate</h2>'
             + lst([("Walkability", "Guests who can walk to breakfast, beach and dinner pay more and book more."),
                    ("A real view", "Ocean, rice field or valley. The biggest single multiplier."),
                    ("Pool and outdoor space", "Not bedroom count. A great pool beats an extra bedroom."),
                    ("Photography", "Often a bigger difference than the area. And the cheapest fix."),
                    ("Management", "Good management grosses 15 to 25% more on the same villa.")]), photo=img("villa", 15)),
        page('<span class="k">Rent it out legally</span><h2>Licence and tax, in short</h2>'
             + lst([("A licence to list", "Since 31 March 2026, booking platforms need a verified business number with the right classification."),
                    ("10% accommodation tax", "Charged on stays. The platforms don't collect it for you."),
                    ("Income tax on rent", "10% final for a resident individual, 20% for a non-resident."),
                    ("2.5% when you sell", "A final tax on the transfer value.")])
             + '<p class="note">Your home country may tax your worldwide income too. Check before you buy, not after.</p>', "mint"),
        help_page("I'll run your numbers with honest occupancy, check the licence position and find a villa or land that can actually earn.", "a%20rental%20villa%20in%20"),
    ]


def own():
    return [
        cover("Owning Property in Bali as a Foreigner", "The three legal ways to hold property, the nominee trap, and the checks before you pay.", img("villa", 4, 900, 1600)),
        page('<span class="k">The one rule</span><h2>Foreigners can\'t own <span class="y">freehold</span> in Bali.</h2>'
             '<p class="l">Freehold (Hak Milik) is for Indonesian citizens only. No structure changes that. Anything sold to you as "freehold" is something else.</p>'
             + stats([("3", "legal ways for a foreigner to hold property. Each one works well when the paperwork is clean.", "hot")]), photo=img("rice", 0)),
        page('<span class="k">Your three options</span><h2>Side by side</h2>'
             + '<div class="box"><b>1. Leasehold</b>A notarised contract in your own name, usually 25 to 30 years. Any visa, no company, no minimum value. Not registered at the land office.</div>'
             + '<div class="box"><b>2. Hak Pakai</b>A registered right of use in your own name. Needs residency (KITAS or KITAP) and a minimum property value. For a home you live in.</div>'
             + '<div class="box g"><b>3. HGB through a PT PMA</b>A building right held by your own foreign-owned company. For a real business, with yearly accounts, filings and audits.</div>'
             + '<p class="note">Most people buying a home or a rental villa start with a well-written lease.</p>'),
        page('<span class="k">Leasehold</span><h2>The lease is only as good as its <span class="y">last page</span>.</h2>'
             + lst([("At the end, the building goes to the landowner", "Unless the contract says otherwise. The extension clause carries the value."),
                    ("80-year leases are built in steps", "An initial term plus agreed extensions. Read how each extension is priced."),
                    ("No bank mortgage", "There's no registered interest to lend against, so most buyers pay cash."),
                    ("You can only sell if the deed allows it", "Assignment has to be written in."),
                    ("Your heirs only inherit if it says so", "Draft the lease to bind heirs.")]), "mint"),
        page('<span class="k">The trap</span><h2>Never buy through a <span class="y">nominee</span>.</h2>'
             '<p class="l">A nominee puts an Indonesian person\'s name on the certificate, with side contracts that are supposed to protect you.</p>'
             + stats([("Void", "Nominee arrangements have no standing in Indonesian law.", "warn"),
                      ("4/2026", "Perda Bali 4/2026 prohibits helping to set them up.", "warn"),
                      ("Certificate", "If the nominee dies or borrows against it, the name on the paper wins.", "hot")]), photo=img("temple", 2)),
        page('<span class="k">Before you pay anything</span><h2>Six checks, in this order</h2>'
             + lst([("The certificate", "Your own notary checks it at the land office (BPN)."),
                    ("The zoning", "Green zone is farmland. A villa there has no legal footing."),
                    ("The building approval (PBG)", "Every structure on the plot needs one."),
                    ("The fit-for-use certificate (SLF)", "Without it the building isn't lawfully occupiable and is hard to sell."),
                    ("Everyone who must sign", "Spouses and heirs too, not only the person in front of you."),
                    ("The extension clause", "A price and a process, not \"to be discussed\".")])),
        page('<span class="k">The tax side</span><h2>What you pay, in short</h2>'
             + rows(None, [("Rental income, resident", "10% final"), ("Rental income, non-resident", "20%"), ("Accommodation tax on stays", "10%"),
                           ("Land and building tax (PBB)", "0.1–0.5%/yr"), ("When you sell", "2.5% of value")])
             + '<p class="note">If a seller says the papers come after the deposit, that tells you everything.</p>', "mint"),
        help_page("I'll tell you which of the three routes fits your plan, find the property and check every document before any money moves.", "owning%20property%20in%20"),
    ]


def move():
    return [
        cover("Moving to Bali: Visas, Living and Buying", "What life here really costs, which visa fits, where to live and when to buy.", img("sanur", 1, 900, 1600)),
        page('<span class="k">The monthly budget</span><h2>What life in Bali <span class="y">really costs</span></h2>'
             + rows(("Lifestyle", "Per month"), [("Budget: room, scooter, local food", "$600–900"), ("Mid-range: apartment or small villa", "$1,100–1,800"),
                                                 ("Comfortable single", "$1,800–2,500"), ("Couple", "$2,500–3,500"), ("Family with international school", "$4,000–6,500")])
             + '<p class="l" style="font-size:13px">Roughly 50 to 65% cheaper than Western Europe for the same lifestyle. But prices have climbed fast since 2022, most of all in Canggu and Seminyak.</p>', photo=img("cafe", 0)),
        page('<span class="k">Which visa fits</span><h2>Your plan decides the visa</h2>'
             + rows(("If you want to", "Look at"), [("Visit, view property", "Visitor visa"), ("Work remotely, foreign employer", "E33G remote worker"),
                                                    ("Run your own company here", "Investor KITAS"), ("Retire here", "Retirement or Second Home"),
                                                    ("Long stay on savings", "Second Home visa"), ("Settle for good", "KITAP, later")])
             + '<p class="note">Buying property and getting residency are separate questions. Hak Pakai, the right to hold a home in your own name, needs a KITAS or KITAP.</p>', "mint"),
        page('<span class="k">Where to live</span><h2>Pick the area for your life</h2>'
             + rows(("Area", "Suits"), [("Canggu, Berawa", "Working, social"), ("Pererenan", "A quieter Canggu"), ("Seminyak", "Restaurants, walkable"),
                                        ("Sanur", "Families, retirees"), ("Ubud", "Calm, creative, wellness"), ("Uluwatu", "Surf, views, space"),
                                        ("Sidemen, Amed, north", "Real quiet, low cost")]), photo=img("ubud", 3)),
        page('<span class="k">The filters people forget</span><h2>Four things to check first</h2>'
             + lst([("The school", "If you have children, pick the school, then live near it."),
                    ("The hospital", "Serious care is in Denpasar. Ninety minutes matters more at 3am."),
                    ("Traffic at your hours", "Drive it at 8am and 6pm, not at midday."),
                    ("The rainy season", "See the road you'd use every day in February.")])
             + '<p class="note"><b>Rent for a year before you buy</b>, ideally through a wet season. The area that suits a holiday and the area that suits a life are rarely the same.</p>', "mint"),
        page('<span class="k">Honest expectations</span><h2>What nobody tells you</h2>'
             + '<div class="two"><div class="box"><b>Traffic</b>Worse every year in the busy corridors.</div><div class="box"><b>Paperwork</b>Slow, changeable, never quite finished.</div>'
             '<div class="box"><b>Healthcare</b>Good everyday care. Get insurance with evacuation cover.</div><div class="box"><b>Friends</b>People come and go. Build your circle on purpose.</div></div>'
             + stats([("183 days", "Spend more than this in Indonesia in a year and you're a tax resident here, even on foreign income.", "hot")]), photo=img("street", 1)),
        page('<span class="k">Then buying</span><h2>When buying makes sense</h2>'
             + lst([("You've lived here a year", "You know the area, the traffic and the season."),
                    ("You know your visa route", "It decides whether Hak Pakai is open to you."),
                    ("You've decided: home or income", "The area that suits you and the one that fills a booking calendar are often different."),
                    ("Your paperwork checks are done", "Certificate, zoning, permits and the lease clauses, before any deposit.")]), photo=img("villa", 16)),
        help_page("Moving is the big decision. I'll help with where to live and, when you're ready, find the home or land that fits and check it properly.", "moving%20to%20Bali%20and%20"),
    ]


def build_guide():
    return [
        cover("The Bali Villa Build Guide", "Zoning, permits, real build costs and timelines. Before you buy a plot.", img("villa", 0, 900, 1600)),
        page('<span class="k">Before anything else</span><h2>The zoning colour decides <span class="y">everything</span>.</h2>'
             + rows(("Colour", "A villa to rent out?"), [("Green: farmland", "Generally no"), ("Yellow: residential", "Home yes, rental restricted"),
                                                         ("Pink / red: tourism", "Generally yes, with permits"), ("Orange: mixed", "Depends on the plan")])
             + '<p class="note">Green land is cheap for a reason. Sellers often imply the zoning can be changed. It can\'t, not at a buyer\'s request.</p>', photo=img("rice", 6)),
        page('<span class="k">How much you can build</span><h2>Same land, <span class="y">6×</span> the building</h2>'
             + stats([("50 m²", "Maximum footprint on a 500 m² green zone plot at 10% coverage (KDB).", "warn"),
                      ("300 m²", "The same 500 m² in a pink zone at 60% coverage.", "hot")])
             + '<p class="l">Check the coverage (KDB), floor area (KLB), green area (KDH) and every setback for your exact plot before you pay an architect.</p>', "mint"),
        page('<span class="k">The permits</span><h2>Two papers you can\'t skip</h2>'
             + '<div class="box g"><b>PBG: the building approval</b>Replaced the old IMB. Checked against the zoning and building rules for your plot.</div>'
             + '<div class="box"><b>SLF: fit for use</b>Issued after inspection. Without it the building isn\'t lawfully occupiable and is much harder to sell.</div>'
             + '<div class="note"><b>On leased land</b>, the permit is usually applied for in the landowner\'s name. Your lease must give you the right to build and oblige the owner to sign.</div>', photo=img("villa", 11)),
        page('<span class="k">What it costs</span><h2>Build cost per m²</h2>'
             + rows(("Standard", "IDR per m²"), [("Basic", "6M–8M"), ("Good rental standard", "8M–11M"), ("High specification", "11M–15M")])
             + stats([("+40–60%", "The finished cost above the structure quote: pool, landscaping, furniture, permits, architect, power and water.", "warn"),
                      ("15–25%", "What building typically saves against buying the same villa finished. And you start with a full lease term.", "hot")])),
        page('<span class="k">How long it takes</span><h2>Plan for <span class="y">2½–3 years</span> to full income</h2>'
             + rows(None, [("Construction, once permits are in", "6–12 months"), ("Land purchase to first guest", "18–24 months"),
                           ("New listing to steady occupancy", "6–12 months more"), ("Contingency on cost", "10–15%"), ("Contingency on time", "2–3 months")])
             + '<p class="note">Nyepi stops the whole island, and temple ceremonies pause work. Build them into the schedule.</p>', "mint"),
        page('<span class="k">Protect your money</span><h2>Five build rules</h2>'
             + lst([("Pay for finished work only", "Inspected by your architect or project manager, never ahead."),
                    ("Hold 5–10% back", "Until the defects are fixed after handover."),
                    ("Get the full specification first", "Gaps become price increases later."),
                    ("Nothing verbal", "Every change in writing, priced before it's built."),
                    ("Someone on site", "Remote builds without supervision are the ones that overrun.")]), photo=img("jungle", 2)),
        help_page("I'll find land that can actually be built on, check the zoning and permits, and connect you with the right people to build.", "building%20a%20villa%20in%20"),
    ]


def compare():
    return [
        cover("Bali vs Dubai vs Thailand vs Vietnam", "What you own, what $300,000 buys, the yield and the tax. Four markets, one honest table.", img("resort", 0, 900, 1600)),
        page('<span class="k">The snapshot</span><h2>Four markets at a glance</h2>'
             + rows(("Bali", ""), [("You own", "Lease, Hak Pakai, PT PMA"), ("$300k buys", "3–4 bed villa + pool"), ("Net yield, well run", "7–9%")])
             + rows(("Dubai", ""), [("You own", "Freehold, registered"), ("$300k buys", "1–2 bed apartment"), ("Tax on rent", "None in Dubai")])
             + rows(("Thailand", ""), [("You own", "Condo freehold (49% quota)"), ("Villa with land", "30-yr registered lease")])
             + rows(("Vietnam", ""), [("You own", "Apartment, ~50 years"), ("Best for", "Growth, low yield")]), "mint"),
        page('<span class="k">Bali vs Dubai</span><h2>Ownership vs <span class="y">yield</span></h2>'
             + '<div class="two"><div class="box"><b>Dubai wins</b>Freehold in your own name. No tax on rental income. Easy to sell, with public sale prices.</div>'
             '<div class="box g"><b>Bali wins</b>Higher net yield. Real land scarcity. A whole villa you actually use.</div></div>'
             + '<p class="l">Same $300,000: a 1–2 bedroom apartment in Dubai with service charges, or a 3–4 bedroom villa with a pool in Bali, on a 25–30 year lease.</p>'
             '<p class="note">Selling above $750,000 in Bali commonly takes 12 to 24 months. Dubai is far more liquid.</p>', photo=img("villa", 13)),
        page('<span class="k">Bali vs Thailand</span><h2>Registered vs <span class="y">longer</span></h2>'
             + lst([("Thailand: condo freehold", "In your own name, within the building's 49% foreign quota."),
                    ("Thailand: a registered lease", "30 years, on the title deed. Structurally stronger than an Indonesian lease."),
                    ("Bali: longer terms in practice", "50 or 80 years through agreed extensions is common."),
                    ("Bali: higher yields", "Villa letting earns more, with more work and more seasonality."),
                    ("Both: nominees are illegal", "Thailand prosecutes them. In Indonesia they're void.")]), "mint"),
        page('<span class="k">Bali vs Vietnam</span><h2>Growth vs <span class="y">income</span></h2>'
             + '<div class="two"><div class="box"><b>Vietnam</b>Apartments in approved projects, about 50 years, renewable on approval. A growing economy, low yields.</div>'
             '<div class="box g"><b>Bali</b>Villas you can use and rent out. Higher yields, but a weaker ownership position.</div></div>'
             + '<p class="note">In Vietnam the ownership certificate (the "pink book") can be delayed for years on some projects. Paid up, but nothing registered.</p>', photo=img("rice", 8)),
        page('<span class="k">Bali\'s strongest argument</span><h2>They can\'t make more <span class="y">Bali</span>.</h2>'
             + stats([("~15 m", "Height limit. No towers, so supply stays low.", ""),
                      ("~7M", "Foreign arrivals in 2025, up almost 10%.", ""),
                      ("24→32M", "Airport capacity expanding, passengers a year.", "hot")])
             + '<p class="l">Coastal land is fixed and tourism zoning is scarce. That is the core of the case for Bali.</p>'),
        page('<span class="k">So which one?</span><h2>Pick by what matters to you</h2>'
             + rows(("If you want", "Look at"), [("Ownership in your own name", "Dubai"), ("No tax on rent", "Dubai"), ("Easy, fast resale", "Dubai"),
                                                 ("A freehold condo in Asia", "Thailand"), ("Growth over income", "Vietnam"),
                                                 ("Higher net income", "Bali"), ("A home you'll actually use", "Bali")])
             + '<p class="note">Your home country may tax worldwide income wherever the property sits.</p>', "mint"),
        help_page("If Bali fits your plan, I'll show you where it makes sense, find the land or property and check every document.", "comparing%20Bali%20with%20"),
    ]


GUIDES = {"areas": areas, "rent": rent, "own": own, "move": move, "build": build_guide, "compare": compare}
TITLES = {"areas": "Where to Buy in Bali: Area by Area", "rent": "The Bali Rental Income Guide",
          "own": "Owning Property in Bali as a Foreigner", "move": "Moving to Bali: Visas, Living and Buying",
          "build": "The Bali Villa Build Guide", "compare": "Bali vs Dubai vs Thailand vs Vietnam"}

if __name__ == "__main__":
    for slug in (sys.argv[1:] or GUIDES):
        build(slug, TITLES[slug], GUIDES[slug]())
