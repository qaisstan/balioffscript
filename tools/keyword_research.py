#!/usr/bin/env python3
"""Free keyword research from Google autocomplete, per market and language.

    python3 tools/keyword_research.py            # all languages
    python3 tools/keyword_research.py de nl      # only these

Each seed is expanded with a-z (plus the language's own letters) and the
suggestions are kept in Google's order, which roughly follows popularity.
One request every ~0.35 s, and it stops cleanly if Google starts refusing.
Output: data/keywords/<lang>.json  {seed: [suggestions]}.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "keywords")
os.makedirs(OUT, exist_ok=True)

MARKETS = {
    "de": dict(hl="de", gl="de", extra="äöüß", seeds=[
        "villa bali kaufen", "haus auf bali kaufen", "immobilie bali", "bali immobilien kaufen",
        "grundstück bali kaufen", "bali leasehold", "bali investment", "in bali investieren",
        "auswandern bali", "auswandern nach bali", "leben auf bali", "rente auf bali",
        "bali visum", "bali visum langzeit", "bali oder thailand", "bali oder mallorca",
        "bali steuern", "ferienhaus bali", "bali villa vermieten", "bali rendite",
        "als deutscher in bali", "bali kosten leben", "bali digital nomad visum"]),
    "nl": dict(hl="nl", gl="nl", extra="", seeds=[
        "villa kopen bali", "huis kopen bali", "vastgoed bali", "grond kopen bali",
        "bali leasehold", "investeren in bali", "beleggen bali", "emigreren naar bali",
        "wonen op bali", "pensioen bali", "bali visum", "bali of spanje", "bali of thailand",
        "bali belasting", "vakantiehuis bali", "villa bali verhuren", "bali rendement",
        "als nederlander in bali", "kosten levensonderhoud bali", "indonesie huis kopen"]),
    "sv": dict(hl="sv", gl="se", extra="åäö", seeds=[
        "köpa hus bali", "köpa villa bali", "köpa lägenhet bali", "fastighet bali",
        "köpa mark bali", "bali leasehold", "investera bali", "flytta till bali",
        "bo på bali", "pension bali", "bali visum", "bali eller thailand", "bali eller spanien",
        "skatt bali", "hyra ut villa bali", "bali avkastning", "som svensk på bali",
        "leva på bali kostnad", "jobba på distans bali", "köpa hus utomlands"]),
    "no": dict(hl="no", gl="no", extra="æøå", seeds=[
        "kjøpe hus bali", "kjøpe villa bali", "kjøpe leilighet bali", "eiendom bali",
        "kjøpe tomt bali", "bali leasehold", "investere bali", "flytte til bali",
        "bo på bali", "pensjonist bali", "bali visum", "bali eller thailand", "bali eller spania",
        "skatt bali", "leie ut villa bali", "som nordmann på bali", "leve på bali kostnad",
        "kjøpe bolig i utlandet"]),
    "fr": dict(hl="fr", gl="fr", extra="éèàç", seeds=[
        "acheter villa bali", "acheter maison bali", "immobilier bali", "investir bali",
        "investir à bali", "acheter terrain bali", "bali leasehold", "prête nom bali",
        "s'installer à bali", "vivre à bali", "retraite à bali", "visa bali",
        "visa long séjour bali", "bali ou thailande", "bali ou maurice", "fiscalité bali",
        "location villa bali rentabilité", "expatrié bali", "coût de la vie bali",
        "acheter à l'étranger"]),
}


def suggest(q, hl, gl):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        dict(client="firefox", hl=hl, gl=gl, q=q))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "replace"))[1]


def run(lang):
    m = MARKETS[lang]
    path = os.path.join(OUT, lang + ".json")
    try:
        res = json.load(open(path, encoding="utf-8"))
    except Exception:
        res = {}
    letters = list("abcdefghijklmnopqrstuvwxyz" + m["extra"])
    for s in m["seeds"]:
        if s in res:
            continue
        found = []
        for q in [s] + ["%s %s" % (s, l) for l in letters]:
            try:
                for x in suggest(q, m["hl"], m["gl"]):
                    if x not in found:
                        found.append(x)
            except Exception as e:
                print("stopped (Google refused):", e, flush=True)
                json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                return False
            time.sleep(0.35)
        res[s] = found
        json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("%s %-34s %4d" % (lang, s, len(found)), flush=True)
    return True


if __name__ == "__main__":
    for lang in (sys.argv[1:] or list(MARKETS)):
        if not run(lang):
            break
    print("done", flush=True)
