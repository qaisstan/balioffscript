"""Bali photos for articles, sections and the Buyer's Kit.

Free-licence images from Unsplash (free for commercial use, no credit
required), served from Unsplash's own CDN. Each pool is a place or a theme;
pick() chooses deterministically from the slug so pages differ but a page keeps
its pictures between builds. Alt text describes the scene for search engines.
"""
import hashlib
import re

CDN = "https://images.unsplash.com/photo-"

POOLS = {
 "uluwatu": ("Cliffs and ocean on the Bukit peninsula, south Bali", [
    "1569271532860-dd35503aaf1f", "1596273214323-a8486cce7c9b", "1598751240191-fbe4a9a30e02",
    "1587015539194-a95a49797b66", "1636619306699-2d27a100605e", "1701252123639-1b90beb60deb",
    "1604842937136-1648761a6256", "1700512825803-b2569dc8e094", "1516859229094-ac3eb898fcc7"]),
 "canggu": ("Canggu coast and rice fields, Bali", [
    "1577344954422-cb7b40658f67", "1519373356-2d641f28c68c", "1598145136670-e4ada43de5b3",
    "1666261012387-3b8d48975c08", "1721984288541-96b644c716d5", "1537074918337-8c826c5e2360"]),
 "seminyak": ("Seminyak beach and pools, Bali", [
    "1571984405176-5958bd9ac31d", "1554445525-07d0b1819efa", "1592411777021-f840022c6292"]),
 "ubud": ("Rice terraces and jungle around Ubud, Bali", [
    "1555400038-63f5ba517a47", "1573593198586-9335916930e5", "1682595950926-fef4d86528d3",
    "1561647994-b8472a2127fd", "1561647994-8202aa46fb21", "1711948699135-779c6ba1f805",
    "1556776265-a2dffedcc4ad", "1566729695626-26b48da825f8", "1565970141923-345a5f05a6e6"]),
 "sanur": ("Sanur beach on Bali's east coast", [
    "1513121939269-0d9d0f2babc7", "1533610376401-26ad24919395", "1589188354515-c6f3a3254bed",
    "1609951586190-90af3296b127", "1733281121131-6aa280eab10f", "1631417765017-08b12e680120"]),
 "penida": ("Nusa Penida cliffs and bays", [
    "1566987827585-6c556cc32848", "1566987827971-f2c40e748a54", "1515932600702-e7937d80ed22",
    "1564092566747-4dd00afb59c8", "1697900126683-fc5ea2a72015", "1592393613858-ed47154c9623"]),
 "lembongan": ("Nusa Lembongan coastline", [
    "1483918040388-de346d6b76c2", "1502290160794-f90c8ed70d2e", "1579340888456-d50f716d20c2",
    "1713835209335-8f6f56dccbc2"]),
 "tanahlot": ("Tanah Lot and the Tabanan coast, Bali", [
    "1553902000-e036b7d05af5", "1555865138-193ba536d7e0", "1588625232507-a337a3bd2e43",
    "1622625653467-2d44f0cc4b08"]),
 "temple": ("Balinese temple", [
    "1544644181-1484b3fdfc62", "1592364395653-83e648b20cc2", "1711609110590-5ad5c4599e56",
    "1501179691627-eeaa65ea017c", "1565970237840-d1c80ed0676a", "1593938637267-7d70420742a3",
    "1546661869-cf589fac7085"]),
 "rice": ("Rice fields in Bali", [
    "1544644181-af0e1e14916f", "1504656920499-6ba6cba050e8", "1608335715837-1994a535d5c3",
    "1586984456747-d78bd259c534", "1513415756790-2ac1db1297d0", "1646928998317-6855a396e55b",
    "1570780728980-63f5a30a1393", "1606942089994-c844a5545223", "1730697897470-0efaee4922de",
    "1701605305492-1cf59783dda1"]),
 "villa": ("Villa with a pool in Bali", [
    "1692736933760-8a8a9b8c1b6f", "1675657144410-0f601cf4edbd", "1627357059324-0346e7f7fb7e",
    "1668854400658-78f2d692b30a", "1694967832949-09984640b143", "1728048756938-de1ccee0ab15",
    "1728049006562-236e5b0dddea", "1607250844650-eae520552a4c", "1693576588461-3ad3dd88371e",
    "1693576588298-823c821d7d9e", "1728050829052-2d1514f1d168", "1728050829093-9ee62013968a",
    "1644027622521-d0ca669c40d7", "1668276490368-409a6002756d", "1562916829-98da73155eef",
    "1644027613475-6bf8ac889599", "1711948728889-614d5d0030f8", "1571635685743-db0db8e31d9a"]),
 "interior": ("Inside a Bali villa", [
    "1613553474179-e1eda3ea5734", "1668277156357-3e174dff9f1a", "1729605411476-defbdab14c54"]),
 "jungle": ("Jungle in Bali", [
    "1557093793-e196ae071479", "1646928229117-08e84cde1692", "1634562144860-e3bfafc887f2",
    "1565970141927-d4591950032e", "1594294737632-1517e40156b9", "1735822210367-c5ba0f5fa3f1",
    "1558005137-d9619a5c539f"]),
 "waterfall": ("Waterfall in Bali", [
    "1552301726-fba9cdb27083", "1695611280324-a5f9b8e8594e", "1676077087620-4ad7eb632b05",
    "1718357168707-86297a530817"]),
 "beach": ("Bali beach at sunset", [
    "1561009226-7a820d647a40", "1566811851038-0580f1fb9082", "1613365891889-7f7e3316be61",
    "1551751336-07e038f36886", "1552272492-3053fbacbf4b", "1604426605647-412fea379480",
    "1560103104-4623c14a473b", "1549692774-59903c83d39e", "1604430289272-0851a606105d",
    "1693576669421-dc2293cd106a", "1575498685808-db3dcba64345"]),
 "surf": ("Surfing in Bali", [
    "1598580420420-a553ba1f442c", "1614734637550-23419251da3a", "1581164197999-99c7d65e8805",
    "1607537826640-5ca23e6df221", "1654137065487-cce388f2c58f"]),
 "volcano": ("Mount Batur and the Kintamani highlands, Bali", [
    "1508591086314-d7deb00cede9", "1518730573647-359c73385dc5", "1600994827732-8c62405ada0c",
    "1681390852996-d7ca802bc4be", "1729959620195-d2947dffebd8", "1609590959678-09adc5cbbe00"]),
 "east": ("East Bali, Sidemen and Amed", [
    "1558501113-b78fe1bedf02", "1664889788538-726f58620607", "1664889050657-5ec9abd9ca00",
    "1646928984876-cdef3a1dc500", "1558501113-63514c1d51d8", "1546661869-cf589fac7085",
    "1668718772169-31f6ecac0b01"]),
 "north": ("North Bali highlands and lakes", [
    "1591325408953-ef9298125f96", "1582583088707-136034c7121c", "1544644181-1484b3fdfc62",
    "1711609110590-5ad5c4599e56"]),
 "lombok": ("Lombok, Indonesia", [
    "1698267703889-06c41f9acba5", "1605752660759-2db7b7de8fa9", "1564221937071-06f02e8c0ba8",
    "1704105677738-2bb9d2d8e8c1", "1542007618896-0e56c92d5591"]),
 "gili": ("The Gili Islands", [
    "1511171908176-ee9b2db9af05", "1581773683009-11e0e759e9ad", "1709483095301-2d1f3e95b1d4",
    "1622916542207-68bc6f3149e4"]),
 "komodo": ("Labuan Bajo and Komodo, Flores", [
    "1589309736404-2e142a2acdf0", "1736523076168-fdda4640f1d8", "1738430275460-b9745a5ae507",
    "1619880938844-30735d3ea768", "1643044034131-001b53336bd0"]),
 "java": ("Mount Bromo, East Java", [
    "1588668214407-6ea9a6d8c272", "1518043610038-064362b44076", "1597553716923-45474a48fbe4",
    "1567320032761-8d7fb7a5aa4e"]),
 "raja": ("Raja Ampat, West Papua", [
    "1516690561799-46d8f74f9abf", "1703769605314-18648cfc3428", "1650445332429-75ceee3f3226",
    "1650509570418-5a9ca4aa01a3"]),
 "islands": ("Islands of Indonesia", [
    "1607427225127-a4ae1d4b050c", "1565369729210-012211942251", "1703769605307-395ace742240",
    "1516690561799-46d8f74f9abf"]),
 "culture": ("Balinese offerings and ceremonies", [
    "1587632467120-c79b296a5dda", "1565970141239-7836886ade57", "1542897730-cc0c1dd8b73b",
    "1720206995488-98098c5a952e", "1769485016814-943270cdb5db", "1542897643-8158da5b4607"]),
 "street": ("Daily life in Bali", [
    "1712213248719-aade0e02a591", "1709435673482-9eb334d5a2ae", "1657123413646-31bb041cab3d",
    "1671080749889-19f8a69deb2b"]),
 "cafe": ("A cafe in Bali", [
    "1555396273-367ea4eb4db5", "1667992403195-d2241a40ca2d", "1745487383873-4c0a1b403e1f"]),
 "airport": ("Arriving in Bali", [
    "1664087061163-8bee2dd70dec", "1715232207853-e4fe86c1feae"]),
 "wellness": ("Yoga and wellness in Bali", [
    "1570559547560-fcba36b64fae", "1509684420792-749974015823", "1679403571902-ff13c0884479",
    "1512587823848-3813fd3c7f8c"]),
 "family": ("Family life in Bali", [
    "1560156606-7b4c0a6fdd6c", "1714890513996-314128ed05b5", "1602594368702-217a7a9cad28"]),
 "palms": ("Palm trees in Bali", [
    "1700600619983-fa0cf8960032", "1601936803782-c294b5eda005", "1608994605211-ba1494f62e2a",
    "1613278435217-de4e5a91a4ee"]),
 "resort": ("Aerial view of a resort in Bali", [
    "1717850702166-4804294d4d4e", "1729606559410-f367a0a31e6b", "1729606558611-824ea9796f3f",
    "1729606558813-1bda04fbb55c"]),
}

# Slug words that point at a place or theme, most specific first.
RULES = [
    (r"nusa-penida|penida", "penida"), (r"lembongan|ceningan", "lembongan"),
    (r"uluwatu|bukit|bingin|padang|balangan|melasti|nusa-dua|ungasan|pecatu|sawangan|jimbaran|benoa|tuban", "uluwatu"),
    (r"canggu|berawa|batu-bolong|pererenan|cemagi|seseh|echo", "canggu"),
    (r"seminyak|umalas|kerobokan|legian|kuta(?!-lombok)", "seminyak"),
    (r"tegallalang|ubud|gianyar|payangan", "ubud"), (r"sanur|denpasar", "sanur"),
    (r"tanah-lot|tabanan|kedungu|medewi|balian|west-coast", "tanahlot"),
    (r"jatiluwih|rice|subak|lp2b|green-zone|zoning|farmland", "rice"),
    (r"munduk|bedugul|lovina|north|singaraja", "north"),
    (r"amed|candidasa|sidemen|karangasem|east-bali|lempuyang", "east"),
    (r"batur|kintamani|volcano|agung", "volcano"),
    (r"lombok|rinjani|mandalika|kuta-lombok", "lombok"), (r"gili", "gili"),
    (r"komodo|labuan|flores", "komodo"), (r"java|bromo|ijen|yogyakarta|jakarta", "java"),
    (r"raja-ampat", "raja"), (r"sumba|sumbawa|islands|indonesia-trip|island", "islands"),
    (r"waterfall", "waterfall"), (r"surf", "surf"), (r"temple|nyepi|ceremony|galungan|offering|culture|etiquette", "temple"),
    (r"market|food|tipping|grocer|restaurant|cafe|coffee|cowork|nomad|remote", "cafe"),
    (r"school|kids|family|child|baby|homeschool", "family"), (r"yoga|wellness|health|mental|spa|hospital|clinic", "wellness"),
    (r"scooter|traffic|driving|transport|grab|road|mobile|sim", "street"),
    (r"visa|kitas|kitap|immigration|airport|arrival|passport|overstay|deport", "airport"),
    (r"interior|furniture|fit-out|design|bedroom|kitchen", "interior"),
    (r"pool|villa|build|construction|roof|bamboo|architect|garden|landscap|termite|maintenance", "villa"),
    (r"beach|sunset|ocean|sea|coast", "beach"),
]

# What a section shows when the slug says nothing specific.
CATEGORY_POOLS = {
    "ownership": ["villa", "rice", "jungle"], "building": ["villa", "jungle", "interior"],
    "visas": ["beach", "temple", "palms"], "company": ["cafe", "villa", "resort"],
    "tax": ["rice", "temple", "beach"], "rental": ["villa", "resort", "interior"],
    "areas": ["resort", "rice", "beach"], "living": ["cafe", "family", "street", "beach"],
    "compare": ["resort", "beach", "islands"], "travel": ["beach", "temple", "waterfall", "culture"],
    "places": ["temple", "rice", "beach", "waterfall"], "islands": ["islands", "gili", "penida"],
    # language sections use their own group keys
    "acheter": ["villa", "rice", "jungle"], "argent": ["villa", "resort", "beach"],
    "vivre": ["cafe", "family", "beach"], "comparer": ["resort", "beach", "islands"], "zones": ["resort", "rice", "beach"],
    "kaufen": ["villa", "rice", "jungle"], "geld": ["villa", "resort", "beach"], "leben": ["cafe", "family", "beach"],
    "vergleich": ["resort", "beach", "islands"], "regionen": ["resort", "rice", "beach"],
    "kopen": ["villa", "rice", "jungle"], "wonen": ["cafe", "family", "beach"], "vergelijk": ["resort", "beach", "islands"],
    "gebieden": ["resort", "rice", "beach"],
    "kopa": ["villa", "rice", "jungle"], "pengar": ["villa", "resort", "beach"], "flytta": ["cafe", "family", "beach"],
    "jamfor": ["resort", "beach", "islands"], "omraden": ["resort", "rice", "beach"],
    "kjope": ["villa", "rice", "jungle"], "penger": ["villa", "resort", "beach"], "flytte": ["cafe", "family", "beach"],
    "sammenlign": ["resort", "beach", "islands"], "omrader": ["resort", "rice", "beach"],
}


def url(pid, w=1200, h=750):
    return f"{CDN}{pid}?w={w}&h={h}&fit=crop&crop=entropy&auto=format&q=70"


def pools_for(slug, category):
    found = []
    for pat, pool in RULES:
        if re.search(pat, slug) and pool not in found:
            found.append(pool)
    for p in CATEGORY_POOLS.get(category, ["beach", "rice", "villa"]):
        if p not in found:
            found.append(p)
    return found


def pick(slug, category, n):
    """n (photo id, alt) pairs for a page, varied by slug, no repeats."""
    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    pools = pools_for(slug, category)
    out, used, i = [], set(), 0
    while len(out) < n and i < n * 6:
        alt, ids = POOLS[pools[i % len(pools)]]
        pid = ids[(seed // (i + 1)) % len(ids)]
        if pid not in used:
            used.add(pid)
            out.append((pid, alt))
        i += 1
    return out


def figure(pid, alt, cls="art-ph", eager=False):
    srcset = ", ".join(f"{url(pid, w, int(w * 0.625))} {w}w" for w in (600, 900, 1200, 1600))
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="{cls}"><img src="{url(pid)}" srcset="{srcset}" '
            f'sizes="(max-width: 48rem) 100vw, 46rem" width="1200" height="750" alt="{alt}" {load} decoding="async"></figure>')


def decorate(slug, category, body_html):
    """Hero picture on top, and one more picture before every second h2."""
    heads = len(re.findall(r"<h2 ", body_html))
    n = 1 + max(2, min(5, heads // 2))
    ph = pick(slug, category, n)
    hero = figure(*ph[0], cls="art-hero", eager=True)
    rest = ph[1:]
    parts = body_html.split("<h2 ")
    out = parts[0]
    k = 0
    for i, part in enumerate(parts[1:], start=1):
        if i % 2 == 0 and k < len(rest):
            out += figure(*rest[k])
            k += 1
        out += "<h2 " + part
    while k < len(rest) and heads < 2:
        out += figure(*rest[k])
        k += 1
    return hero, out
