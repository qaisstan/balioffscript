"""The Bali Buyer's Kit: the lead magnet.

One free PDF per language. The box that offers it sits inside articles, on the
section pages and on its own landing page. Name, email and WhatsApp are all
required. After submitting, the person gets the download straight away and two
optional taps (budget, timing) that turn into a pre-written WhatsApp message to
Kai. Indonesian numbers get the download and nothing else: no email, no
WhatsApp handoff (his rule).

Every function takes B, the build module, for its helpers and settings.
"""

import json
import os
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
KIT_SRC = os.path.join(ROOT, "kit")

# Unlisted folder the kits are served from. Changing it breaks links in emails
# already sent, so leave it.
TOKEN = "k7q4m2"

# Flip to True once the new apps-script/Code.gs is deployed (it emails the kit).
# Until then the page only promises what it delivers: the instant download.
EMAIL_ON = False

LANGS = ["en", "fr", "de", "nl", "sv", "no"]

UI = {
 "en": dict(
    kicker="Free PDF", title="The Bali Buyer's Kit",
    pitch="The checklist, the 20 questions, the 12 lease clauses and the 15 red flags I go through before anyone signs. Plus the worksheet that shows what a villa really returns.",
    points=["The 9-link chain every Bali deal has to survive", "Documents to request, and what each one proves", "20 questions to ask before you pay a deposit", "12 lease clauses to insist on", "15 red flags", "Net yield worksheet and area cheat sheet"],
    name="First name", email="Email", phone="WhatsApp number", btn="Send me the kit",
    fine="Free. Your details stay with me, never sold or shared.",
    e_name="Please enter your name.", e_email="Please enter a valid email.", e_phone="Please enter a valid WhatsApp number.",
    done_h="It's yours.", dl="Download the kit (PDF)", mailed="A copy is on its way to your inbox too.",
    q_h="Looking at something specific? Two taps and I'll know how to help.",
    q_b="Budget", budgets=["Under $100k", "$100k to $250k", "$250k to $500k", "$500k and above", "Still working it out"],
    q_t="Timing", times=["Ready now", "Within 3 months", "3 to 6 months", "6 months or more", "Just researching"],
    wa="Send it to me on WhatsApp", wa_alt="Or message me on WhatsApp",
    wa_msg="Hi Kai, I'm {name}. I just got the Bali Buyer's Kit.{extra} Could you help me?",
    wa_budget=" Budget: {budget}.", wa_time=" Timing: {time}.",
    id_done="Thank you. Download the kit below.",
    land_title="The Bali Buyer's Kit: free due diligence checklist (PDF)",
    land_desc="Free PDF: the documents, 20 questions, 12 lease clauses, 15 red flags and a net yield worksheet to check a Bali villa or land deal before you sign.",
    land_h="Check a Bali property the way I do, before you sign.",
    land_p="Most Bali deals do not go wrong on price. They go wrong because one link in the chain was never checked: the certificate, the owner, the zoning, the licence. This kit is the order I check them in, written down.",
    by="By Kai, Strategic Investment Adviser"),
 "fr": dict(
    kicker="PDF gratuit", title="Le guide de l'acheteur à Bali",
    pitch="La checklist, les 20 questions, les 12 clauses du bail et les 15 signaux d'alerte que je vérifie avant toute signature. Et la grille qui montre ce qu'une villa rapporte vraiment, en net.",
    points=["Les 9 maillons que chaque achat à Bali doit passer", "Les documents à demander, et ce que chacun prouve", "20 questions à poser avant de verser un acompte", "12 clauses du bail à exiger", "15 signaux d'alerte, dont le prête-nom", "Grille de rendement net et fiche des zones"],
    name="Prénom", email="E-mail", phone="Numéro WhatsApp", btn="Recevoir le guide",
    fine="Gratuit. Tes coordonnées restent chez moi, jamais vendues ni partagées.",
    e_name="Indique ton prénom.", e_email="Indique un e-mail valide.", e_phone="Indique un numéro WhatsApp valide.",
    done_h="Il est à toi.", dl="Télécharger le guide (PDF)", mailed="Une copie arrive aussi dans ta boîte mail.",
    q_h="Tu regardes un bien précis ? Deux clics et je saurai comment t'aider.",
    q_b="Budget", budgets=["Moins de 100 000 €", "100 000 à 250 000 €", "250 000 à 500 000 €", "Plus de 500 000 €", "Pas encore défini"],
    q_t="Calendrier", times=["Prêt maintenant", "D'ici 3 mois", "Dans 3 à 6 mois", "Dans plus de 6 mois", "Je me renseigne"],
    wa="M'écrire sur WhatsApp", wa_alt="Ou écris-moi sur WhatsApp",
    wa_msg="Bonjour Kai, je suis {name}. Je viens de recevoir le guide de l'acheteur à Bali.{extra} Tu peux m'aider ?",
    wa_budget=" Mon budget : {budget}.", wa_time=" Calendrier : {time}.",
    id_done="Merci. Le guide est ci-dessous.",
    land_title="Guide gratuit : acheter une villa à Bali sans se tromper (PDF)",
    land_desc="PDF gratuit : documents, 20 questions, 12 clauses du bail, 15 signaux d'alerte dont le prête-nom, et une grille de rendement net pour acheter à Bali.",
    land_h="Vérifie un bien à Bali comme je le fais, avant de signer.",
    land_p="La plupart des achats à Bali ne ratent pas sur le prix. Ils ratent parce qu'un maillon de la chaîne n'a jamais été vérifié : le titre, le propriétaire, le zonage, la licence. Ce guide, c'est l'ordre dans lequel je les vérifie.",
    by="Par Kai, conseiller en investissement stratégique"),
 "de": dict(
    kicker="Kostenloses PDF", title="Der Bali-Käuferleitfaden",
    pitch="Die Checkliste, die 20 Fragen, die 12 Pachtklauseln und die 15 Warnsignale, die ich prüfe, bevor jemand unterschreibt. Dazu die Rechnung, die zeigt, was eine Villa netto wirklich abwirft.",
    points=["Die 9 Glieder der Kette, die jeder Bali-Deal bestehen muss", "Welche Dokumente Sie verlangen sollten, und was jedes beweist", "20 Fragen vor der ersten Anzahlung", "12 Pachtklauseln, auf die Sie bestehen sollten", "15 Warnsignale, inklusive Strohmann", "Netto-Rendite-Rechnung und Regionen-Übersicht"],
    name="Vorname", email="E-Mail", phone="WhatsApp-Nummer", btn="Leitfaden zusenden",
    fine="Kostenlos. Ihre Daten bleiben bei mir, werden nie verkauft oder weitergegeben.",
    e_name="Bitte geben Sie Ihren Namen ein.", e_email="Bitte geben Sie eine gültige E-Mail ein.", e_phone="Bitte geben Sie eine gültige WhatsApp-Nummer ein.",
    done_h="Hier ist er.", dl="Leitfaden herunterladen (PDF)", mailed="Eine Kopie ist auch per E-Mail unterwegs.",
    q_h="Sie haben ein konkretes Objekt im Blick? Zwei Klicks, und ich weiß, wie ich helfen kann.",
    q_b="Budget", budgets=["Unter 100.000 €", "100.000 bis 250.000 €", "250.000 bis 500.000 €", "Über 500.000 €", "Noch offen"],
    q_t="Zeitrahmen", times=["Sofort", "Innerhalb von 3 Monaten", "In 3 bis 6 Monaten", "In über 6 Monaten", "Ich informiere mich nur"],
    wa="Per WhatsApp schicken", wa_alt="Oder schreiben Sie mir auf WhatsApp",
    wa_msg="Hallo Kai, ich bin {name}. Ich habe gerade den Bali-Käuferleitfaden bekommen.{extra} Können Sie mir helfen?",
    wa_budget=" Mein Budget: {budget}.", wa_time=" Zeitrahmen: {time}.",
    id_done="Danke. Der Leitfaden ist unten.",
    land_title="Villa auf Bali kaufen: kostenlose Checkliste (PDF)",
    land_desc="Kostenloses PDF: Dokumente, 20 Fragen, 12 Pachtklauseln, 15 Warnsignale und eine Netto-Rendite-Rechnung für den Kauf einer Villa auf Bali.",
    land_h="Prüfen Sie eine Bali-Immobilie so wie ich, bevor Sie unterschreiben.",
    land_p="Die meisten Bali-Käufe scheitern nicht am Preis. Sie scheitern, weil ein Glied der Kette nie geprüft wurde: das Zertifikat, der Eigentümer, die Zonierung, die Lizenz. Dieser Leitfaden ist die Reihenfolge, in der ich prüfe.",
    by="Von Kai, Strategic Investment Adviser"),
 "nl": dict(
    kicker="Gratis pdf", title="De Bali-kopersgids",
    pitch="De checklist, de 20 vragen, de 12 leaseclausules en de 15 rode vlaggen die ik doorloop voordat iemand tekent. Plus de rekensom die laat zien wat een villa netto echt oplevert.",
    points=["De 9 schakels die elke Bali-deal moet doorstaan", "Welke documenten je opvraagt, en wat elk bewijst", "20 vragen voordat je een aanbetaling doet", "12 leaseclausules waar je op staat", "15 rode vlaggen, inclusief de stroman", "Netto-rendementsberekening en gebiedenoverzicht"],
    name="Voornaam", email="E-mail", phone="WhatsApp-nummer", btn="Stuur me de gids",
    fine="Gratis. Je gegevens blijven bij mij, nooit verkocht of gedeeld.",
    e_name="Vul je naam in.", e_email="Vul een geldig e-mailadres in.", e_phone="Vul een geldig WhatsApp-nummer in.",
    done_h="Hij is van jou.", dl="Download de gids (pdf)", mailed="Er komt ook een kopie naar je inbox.",
    q_h="Kijk je naar iets concreets? Twee klikken en ik weet hoe ik kan helpen.",
    q_b="Budget", budgets=["Onder € 100.000", "€ 100.000 tot 250.000", "€ 250.000 tot 500.000", "Boven € 500.000", "Weet ik nog niet"],
    q_t="Wanneer", times=["Nu", "Binnen 3 maanden", "Over 3 tot 6 maanden", "Over meer dan 6 maanden", "Ik oriënteer me"],
    wa="Stuur het via WhatsApp", wa_alt="Of stuur me een WhatsApp",
    wa_msg="Hoi Kai, ik ben {name}. Ik heb net de Bali-kopersgids gedownload.{extra} Kun je me helpen?",
    wa_budget=" Mijn budget: {budget}.", wa_time=" Wanneer: {time}.",
    id_done="Dank je. De gids staat hieronder.",
    land_title="Villa kopen op Bali: gratis checklist (pdf)",
    land_desc="Gratis pdf: documenten, 20 vragen, 12 leaseclausules, 15 rode vlaggen en een netto-rendementsberekening om een villa op Bali te kopen zonder verrassingen.",
    land_h="Controleer een woning op Bali zoals ik dat doe, voordat je tekent.",
    land_p="De meeste aankopen op Bali gaan niet mis op de prijs. Ze gaan mis omdat één schakel in de keten nooit is gecontroleerd: het certificaat, de eigenaar, de bestemming, de vergunning. Deze gids is de volgorde waarin ik ze controleer.",
    by="Door Kai, Strategic Investment Adviser"),
 "sv": dict(
    kicker="Gratis pdf", title="Köparguiden för Bali",
    pitch="Checklistan, de 20 frågorna, de 12 klausulerna i leasingavtalet och de 15 varningssignalerna jag går igenom innan någon skriver på. Plus kalkylen som visar vad en villa ger på riktigt, netto.",
    points=["De 9 länkarna varje Bali-affär måste klara", "Vilka dokument du ska begära, och vad varje dokument bevisar", "20 frågor innan du betalar någon handpenning", "12 klausuler i leasingavtalet att kräva", "15 varningssignaler, bland annat bulvaner", "Kalkyl för nettoavkastning och områdesöversikt"],
    name="Förnamn", email="E-post", phone="WhatsApp-nummer", btn="Skicka guiden",
    fine="Gratis. Dina uppgifter stannar hos mig, säljs aldrig och delas aldrig.",
    e_name="Skriv ditt namn.", e_email="Skriv en giltig e-postadress.", e_phone="Skriv ett giltigt WhatsApp-nummer.",
    done_h="Den är din.", dl="Ladda ner guiden (pdf)", mailed="En kopia är också på väg till din inkorg.",
    q_h="Tittar du på något specifikt? Två klick så vet jag hur jag kan hjälpa dig.",
    q_b="Budget", budgets=["Under 1 miljon kr", "1 till 2,5 miljoner kr", "2,5 till 5 miljoner kr", "Över 5 miljoner kr", "Vet inte än"],
    q_t="När", times=["Nu", "Inom 3 månader", "Om 3 till 6 månader", "Om mer än 6 månader", "Jag kollar bara"],
    wa="Skicka till mig på WhatsApp", wa_alt="Eller skriv till mig på WhatsApp",
    wa_msg="Hej Kai, jag heter {name}. Jag laddade precis ner köparguiden för Bali.{extra} Kan du hjälpa mig?",
    wa_budget=" Min budget: {budget}.", wa_time=" När: {time}.",
    id_done="Tack. Guiden finns här nedanför.",
    land_title="Köpa villa på Bali: gratis checklista (pdf)",
    land_desc="Gratis pdf: dokumenten, 20 frågor, 12 klausuler, 15 varningssignaler och en kalkyl för nettoavkastning innan du köper villa eller mark på Bali.",
    land_h="Granska en fastighet på Bali som jag gör, innan du skriver på.",
    land_p="De flesta köp på Bali går inte fel på priset. De går fel för att en länk i kedjan aldrig kontrollerades: lagfarten, ägaren, detaljplanen, tillståndet. Den här guiden är ordningen jag kontrollerar dem i.",
    by="Av Kai, Strategic Investment Adviser"),
 "no": dict(
    kicker="Gratis pdf", title="Kjøperguiden for Bali",
    pitch="Sjekklisten, de 20 spørsmålene, de 12 klausulene i leieavtalen og de 15 faresignalene jeg går gjennom før noen signerer. Pluss regnestykket som viser hva en villa faktisk gir, netto.",
    points=["De 9 leddene hver Bali-handel må tåle", "Hvilke dokumenter du skal be om, og hva hvert av dem beviser", "20 spørsmål før du betaler noe forskudd", "12 klausuler i leieavtalen å kreve", "15 faresignaler, blant annet stråmenn", "Regnestykke for nettoavkastning og områdeoversikt"],
    name="Fornavn", email="E-post", phone="WhatsApp-nummer", btn="Send meg guiden",
    fine="Gratis. Opplysningene dine blir hos meg, aldri solgt eller delt.",
    e_name="Skriv navnet ditt.", e_email="Skriv en gyldig e-postadresse.", e_phone="Skriv et gyldig WhatsApp-nummer.",
    done_h="Den er din.", dl="Last ned guiden (pdf)", mailed="En kopi er også på vei til innboksen din.",
    q_h="Ser du på noe konkret? To klikk, så vet jeg hvordan jeg kan hjelpe.",
    q_b="Budsjett", budgets=["Under 1 million kr", "1 til 2,5 millioner kr", "2,5 til 5 millioner kr", "Over 5 millioner kr", "Vet ikke ennå"],
    q_t="Når", times=["Nå", "Innen 3 måneder", "Om 3 til 6 måneder", "Om mer enn 6 måneder", "Jeg undersøker bare"],
    wa="Send det til meg på WhatsApp", wa_alt="Eller skriv til meg på WhatsApp",
    wa_msg="Hei Kai, jeg heter {name}. Jeg lastet nettopp ned kjøperguiden for Bali.{extra} Kan du hjelpe meg?",
    wa_budget=" Budsjettet mitt: {budget}.", wa_time=" Når: {time}.",
    id_done="Takk. Guiden ligger her nedenfor.",
    land_title="Kjøpe villa på Bali: gratis sjekkliste (pdf)",
    land_desc="Gratis pdf: dokumentene, 20 spørsmål, 12 klausuler, 15 faresignaler og et regnestykke for nettoavkastning før du kjøper villa eller tomt på Bali.",
    land_h="Sjekk en eiendom på Bali slik jeg gjør, før du signerer.",
    land_p="De fleste kjøp på Bali går ikke galt på prisen. De går galt fordi ett ledd i kjeden aldri ble sjekket: hjemmelen, eieren, reguleringen, lisensen. Denne guiden er rekkefølgen jeg sjekker dem i.",
    by="Av Kai, Strategic Investment Adviser"),
}

# Pre-written message behind the WhatsApp link inside the PDF itself.
DOC_WA = {
    "en": "Hi Kai, I read the Bali Buyer's Kit and I would like your help with a property.",
    "fr": "Bonjour Kai, j'ai lu le guide de l'acheteur à Bali et j'aimerais ton avis sur un bien.",
    "de": "Hallo Kai, ich habe den Bali-Käuferleitfaden gelesen und hätte gern Ihre Hilfe bei einer Immobilie.",
    "nl": "Hoi Kai, ik heb de Bali-kopersgids gelezen en wil graag je hulp bij een woning.",
    "sv": "Hej Kai, jag har läst köparguiden för Bali och vill gärna ha din hjälp med en fastighet.",
    "no": "Hei Kai, jeg har lest kjøperguiden for Bali og vil gjerne ha hjelp med en eiendom.",
}

# Which country code the phone field starts on, per language.
DIAL_DEFAULT = {"en": "+61", "fr": "+33", "de": "+49", "nl": "+31", "sv": "+46", "no": "+47"}

# Where each language's landing page lives.
LANDING = {"en": "/buyers-kit/", "fr": "/fr/guide-acheteur/", "de": "/de/kaeuferleitfaden/",
           "nl": "/nl/kopersgids/", "sv": "/sv/kopguide/", "no": "/no/kjoperguide/"}


def pdf_url(B, lang):
    return f"{B.BASE}/kit/{TOKEN}/bali-buyers-kit-{lang}.pdf"


def doc_url(B, lang):
    return f"{B.BASE}/kit/{TOKEN}/{lang}/"


def cfg(B, lang):
    u = UI[lang]
    return {"lang": lang, "endpoint": B.LEAD_ENDPOINT, "wa": B.LEAD_WHATSAPP,
            "pdf": pdf_url(B, lang), "dial": DIAL_DEFAULT[lang],
            "e_name": u["e_name"], "e_email": u["e_email"], "e_phone": u["e_phone"],
            "wa_msg": u["wa_msg"], "wa_budget": u["wa_budget"], "wa_time": u["wa_time"]}


def cover(lang, small=False):
    """The PDF's cover drawn in HTML, so the box shows what you get."""
    u = UI[lang]
    return (f'<div class="kit-cover{" kit-cover-s" if small else ""}" aria-hidden="true">'
            f'<span class="kc-k">Bali Off Script</span>'
            f'<span class="kc-t">{u["title"]}</span>'
            f'<span class="kc-r"></span>'
            f'<span class="kc-l">{" · ".join(["9", "20", "12", "15"])}</span>'
            f'<span class="kc-by">Kai</span></div>')


def box(B, lang="en", where=""):
    """The opt-in. `where` lands in the sheet so we know which spot converts."""
    u = UI[lang]
    c = cfg(B, lang)
    c["where"] = where
    pts = "".join(f"<li>{p}</li>" for p in u["points"][:4])
    bud = "".join(f'<button type="button" class="kit-chip" data-k="budget" data-v="{b}">{b}</button>' for b in u["budgets"])
    tim = "".join(f'<button type="button" class="kit-chip" data-k="timeline" data-v="{t}">{t}</button>' for t in u["times"])
    mailed = f'<p class="kit-mailed">{u["mailed"]}</p>' if EMAIL_ON else ""
    first_wa = B.wa_logo("ig")
    return f"""<section class="kit" id="kit{'-' + where if where else ''}" data-cfg='{json.dumps(c).replace("'", "&#39;")}'>
<div class="kit-in">
{cover(lang)}
<div class="kit-body">
<p class="kit-k">{u["kicker"]}</p>
<h2 class="kit-h">{u["title"]}</h2>
<p class="kit-p">{u["pitch"]}</p>
<ul class="kit-pts">{pts}</ul>
<form class="kit-f" novalidate>
<input type="text" name="company" class="ld-hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<input type="text" name="name" autocomplete="given-name" placeholder="{u["name"]}" aria-label="{u["name"]}" maxlength="80" required>
<input type="email" name="email" autocomplete="email" inputmode="email" placeholder="{u["email"]}" aria-label="{u["email"]}" maxlength="120" required>
<div class="kit-tel"><select name="dial" aria-label="Country code"></select><input type="tel" name="phone" autocomplete="tel-national" inputmode="tel" placeholder="{u["phone"]}" aria-label="{u["phone"]}" maxlength="20" required></div>
<button type="submit" class="kit-btn">{u["btn"]}</button>
<p class="kit-err" role="alert"></p>
<p class="kit-fine">{u["fine"]}</p>
</form>
<div class="kit-done" hidden>
<p class="kit-dh">{u["done_h"]}</p>
<a class="kit-dl" href="{pdf_url(B, lang)}" target="_blank" rel="noopener" download>{B.form_logo("ig")}<span>{u["dl"]}</span></a>
{mailed}
<div class="kit-q">
<p class="kit-qh">{u["q_h"]}</p>
<p class="kit-ql">{u["q_b"]}</p><div class="kit-chips">{bud}</div>
<p class="kit-ql">{u["q_t"]}</p><div class="kit-chips">{tim}</div>
<a class="kit-wa" href="#" target="_blank" rel="noopener">{first_wa}<span>{u["wa"]}</span></a>
</div>
<p class="kit-id" hidden>{u["id_done"]}</p>
</div>
</div>
</div>
</section>"""


def mini(B, lang="en"):
    """Rail version: one line and a jump to the full box on the page."""
    u = UI[lang]
    return (f'<a class="kit-mini" href="#kit">{cover(lang, small=True)}'
            f'<span><b>{u["title"]}</b><em>{u["kicker"]} · {u["btn"]}</em></span></a>')


def landing(B, lang="en", head_fn=None, nav_html="", footer_html=""):
    """An indexable page for the kit itself, for 'bali due diligence checklist'
    style searches and for the link in bio."""
    u = UI[lang]
    path = LANDING[lang]
    pts = "".join(f"<li>{p}</li>" for p in u["points"])
    schema = json.dumps({"@context": "https://schema.org", "@type": "WebPage",
                         "name": u["land_title"], "description": u["land_desc"],
                         "url": B.SITE_URL + path, "inLanguage": lang,
                         "isPartOf": {"@type": "WebSite", "name": B.SITE_NAME, "url": B.SITE_URL}})
    return f"""{head_fn(u["land_title"], u["land_desc"], path)}
<script type="application/ld+json">{schema}</script>
{nav_html}
<main class="wrap article kit-land">
<p class="eyebrow">{u["kicker"]}</p>
<h1>{u["land_h"]}</h1>
<p class="standfirst">{u["land_p"]}</p>
<div class="prose"><ul>{pts}</ul></div>
{box(B, lang, "landing")}
</main>
{footer_html}"""


def doc_page(B, lang):
    """The kit itself as a printable page. Chrome turns it into the PDF."""
    meta = B.parse(os.path.join(KIT_SRC, f"{lang}.md"))
    u = UI[lang]
    wa = f"https://wa.me/{B.LEAD_WHATSAPP}?text=" + quote(DOC_WA[lang])
    body = B.md(meta["body"])
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{meta.get("title", u["title"])} | {B.SITE_NAME}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Public+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{B.BASE}/style.css">
</head>
<body class="kitdoc">
<section class="kd-cover">
<p class="kd-brand">Bali Off Script</p>
<h1 class="kd-title">{meta.get("title", u["title"])}</h1>
<p class="kd-sub">{meta.get("subtitle", "")}</p>
<p class="kd-by">{u["by"]}<br>balioffscript.com</p>
</section>
<main class="kd-body prose">
{body}
<p class="kd-cta"><a href="{wa}">WhatsApp: +46 70 008 14 14</a> · <a href="{B.SITE_URL}/">balioffscript.com</a></p>
</main>
</body>
</html>"""
