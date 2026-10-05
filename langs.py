"""Language sections: /fr/, /de/, /nl/, /sv/, /no/.

Not translations of the English site. Each section is written for how buyers
from that country think about Bali: what they compare it with, which words they
search, which tax and pension questions follow them from home. Pages live in
content_i18n/<lang>/<slug>.md and render at /<lang>/<slug>/.

Frontmatter: question (H1), title (SEO title, <= 60 chars), summary, group
(one of the group keys below), order, verified. The FAQ goes under the
language's own FAQ heading (UI[lang]["faq_h"]).

Every function takes B, the build module.
"""

import json
import os
import re
from datetime import date

import kit as K
import photos as PH

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "content_i18n")

UI = {
 "fr": dict(
    name="Français", locale="fr_FR", contact_slug="contact",
    home_title="Acheter à Bali quand on est français : le guide honnête",
    home_desc="Leasehold, prête-nom, rendement net, fiscalité France–Indonésie, retraite et visa : tout ce qu'un Français doit savoir avant d'acheter une villa à Bali.",
    home_h="Acheter à Bali,", home_h2="sans le discours commercial.",
    home_p="Ce que tu peux vraiment posséder, ce que rapporte une villa une fois tous les frais payés, et ce que la France continue de te demander quand tu vis ou investis ici.",
    home_note="Écrit pour les acheteurs français, belges et suisses.",
    groups=[("acheter", "Acheter et posséder", "Leasehold, prête-nom, Hak Pakai, PT PMA et ce que dit vraiment le titre."),
            ("argent", "Rendement et fiscalité", "Rendement net, impôts en Indonésie et en France, financement et frais."),
            ("vivre", "S'installer et visas", "Visa, retraite, CFE et Sécu, école et vie quotidienne."),
            ("comparer", "Bali comparé", "Bali face à l'île Maurice, la Thaïlande, Dubaï et la France."),
            ("zones", "Où acheter", "Canggu, Uluwatu, Ubud, Sanur et les autres, avec leurs vrais pièges.")],
    faq_h="Questions fréquentes", toc_h="Sur cette page", q_h="Questions traitées",
    by="Par", updated="Mis à jour le", min_read="min de lecture", share="Partager",
    home="Accueil", read_next="À lire ensuite", more_in="Aussi dans", all_h="Tous les guides",
    nav_topics="Thèmes", nav_kit="Guide gratuit", nav_contact="Contact", lang_label="Langue",
    cta_k="Tu regardes un bien précis ?",
    cta_b="Dis-moi ce que tu cherches et je reviens vers toi personnellement. Quatre questions, dix secondes, puis WhatsApp s'ouvre directement.",
    cta_btn="M'écrire sur WhatsApp",
    rail_q="Pas sûr de ce que ça change pour le bien que tu regardes ?", rail_btn="Demander à Kai",
    who_h="Je suis Kai.",
    who_p="Je suis conseiller en investissement stratégique à Bali. J'aide les acheteurs étrangers à vérifier une villa, un terrain ou un projet sur plan avant de signer : le titre, le propriétaire, le zonage, le bail, la licence et le vrai rendement.",
    legal="Informations générales, pas un conseil juridique, fiscal ou financier. La réglementation indonésienne change souvent et s'applique différemment selon les régences. Vérifie tout avec ton propre notaire (PPAT), avocat et conseiller fiscal, en Indonésie et en France.",
    role="Conseiller en investissement stratégique",
    f=dict(interest_h="Que cherches-tu à Bali ?", interest_sub="Quatre questions rapides. Ensuite je regarde ce qui te correspond vraiment, et je reviens vers toi moi-même sur WhatsApp.", interests=["Un terrain pour construire", "Une villa terminée pour y vivre ou la louer", "Une villa sur plan comme investissement", "M'installer : location, visa, déménagement"], kit_opt="Juste le guide gratuit de l'acheteur (PDF)", more_site="Lire tous les guides", msg_interest="Je cherche : {interest}. ",
           title="Trouver le bon bien à Bali", desc="Dis-moi ton budget et ton calendrier, je reviens vers toi personnellement avec des opportunités à Bali qui te correspondent vraiment.",
           intro_h="Je t'aide à trouver le bon investissement à Bali.", intro_sub="Quatre questions, dix secondes. Ensuite je regarde ce qui correspond vraiment à ton budget et à ton calendrier, et je reviens vers toi moi-même.",
           go="C'est parti", hint="10 SECONDES", name_h="D'abord, comment tu t'appelles ?", name_sub="Pour savoir à qui je parle.", name_ph="Prénom et nom",
           phone_h="Quel est le meilleur numéro pour te joindre ?", phone_sub="Je l'utilise pour t'écrire directement. Jamais partagé, jamais vendu.", phone_ph="Numéro de téléphone", email_ph="E-mail (facultatif)",
           budget_h="Avec quel budget tu travailles ?", budget_sub="Une fourchette suffit. C'est elle qui décide des zones et des titres réalistes pour toi.",
           time_h="Quand peux-tu investir ?", time_sub="Certaines affaires prennent des mois. D'autres partent en quelques semaines.",
           thanks_h="Merci.", thanks_p="Je vais te contacter personnellement, comprendre ce que tu cherches vraiment, et voir s'il existe à Bali une opportunité qui vaut la peine de t'être présentée.",
           sign="Bien à toi, Kai", fallback="M'envoyer ça sur WhatsApp", back="Retour", cont="Continuer",
           e_name="Indique ton prénom.", e_name_long="Ce nom est trop long.", e_phone="Indique un numéro valide.", e_phone_long="Ce numéro est trop long.", e_email="Cet e-mail ne semble pas correct.",
           msg="Bonjour Kai, je suis {name}. Je viens de remplir le formulaire sur ton site. Budget : {budget}. Calendrier : {when}. Au plaisir d'échanger.")),
 "de": dict(
    name="Deutsch", locale="de_DE", contact_slug="kontakt",
    home_title="Villa auf Bali kaufen als Deutscher: der ehrliche Ratgeber",
    home_desc="Leasehold, Strohmann, Netto-Rendite, Steuern nach dem DBA, Auswandern und Rente: was Deutsche, Österreicher und Schweizer vor dem Kauf auf Bali wissen müssen.",
    home_h="Immobilien auf Bali,", home_h2="ohne Verkaufsprospekt.",
    home_p="Was Sie als Ausländer wirklich besitzen können, was eine Villa nach allen Kosten abwirft, und was das Finanzamt zu Hause weiterhin wissen will.",
    home_note="Geschrieben für Käufer aus Deutschland, Österreich und der Schweiz.",
    groups=[("kaufen", "Kaufen und Eigentum", "Leasehold, Strohmann-Modell, Hak Pakai, PT PMA und was im Zertifikat wirklich steht."),
            ("geld", "Rendite und Steuern", "Netto-Rendite, Steuern in Indonesien und zu Hause, Finanzierung und Nebenkosten."),
            ("leben", "Auswandern und Visum", "Visum, Rente, Krankenversicherung, Abmeldung und Alltag."),
            ("vergleich", "Bali im Vergleich", "Bali gegen Mallorca, Thailand, Dubai und Portugal."),
            ("regionen", "Wo kaufen", "Canggu, Uluwatu, Ubud, Sanur und der Rest, mit den echten Fallstricken.")],
    faq_h="Häufige Fragen", toc_h="Auf dieser Seite", q_h="Beantwortete Fragen",
    by="Von", updated="Aktualisiert am", min_read="Min. Lesezeit", share="Teilen",
    home="Start", read_next="Als Nächstes lesen", more_in="Mehr in", all_h="Alle Ratgeber",
    nav_topics="Themen", nav_kit="Gratis-Leitfaden", nav_contact="Kontakt", lang_label="Sprache",
    cta_k="Sie haben ein konkretes Objekt im Blick?",
    cta_b="Sagen Sie mir, was Sie suchen, und ich melde mich persönlich. Vier Fragen, zehn Sekunden, danach öffnet sich direkt WhatsApp.",
    cta_btn="Per WhatsApp schreiben",
    rail_q="Unsicher, was das für Ihr Objekt bedeutet?", rail_btn="Kai fragen",
    who_h="Ich bin Kai.",
    who_p="Ich bin Strategic Investment Adviser auf Bali. Ich helfe ausländischen Käufern, eine Villa, ein Grundstück oder ein Off-Plan-Projekt zu prüfen, bevor sie unterschreiben: Zertifikat, Eigentümer, Zonierung, Pachtvertrag, Lizenz und echte Rendite.",
    legal="Allgemeine Information, keine Rechts-, Steuer- oder Finanzberatung. Indonesische Vorschriften ändern sich oft und werden je nach Regierungsbezirk unterschiedlich angewendet. Prüfen Sie alles mit Ihrem eigenen Notar (PPAT), Anwalt und Steuerberater, in Indonesien und zu Hause.",
    role="Strategic Investment Adviser",
    f=dict(interest_h="Was suchen Sie auf Bali?", interest_sub="Vier kurze Fragen. Danach schaue ich, was wirklich passt, und melde mich selbst per WhatsApp.", interests=["Ein Grundstück zum Bauen", "Eine fertige Villa zum Wohnen oder Vermieten", "Eine Off-Plan-Villa als Kapitalanlage", "Auswandern: Miete, Visum, Umzug"], kit_opt="Nur den kostenlosen Käuferleitfaden (PDF)", more_site="Alle Ratgeber lesen", msg_interest="Ich suche: {interest}. ",
           title="Die passende Immobilie auf Bali finden", desc="Nennen Sie mir Budget und Zeitrahmen, ich melde mich persönlich mit Bali-Objekten, die wirklich passen.",
           intro_h="Ich helfe Ihnen, das passende Investment auf Bali zu finden.", intro_sub="Vier Fragen, zehn Sekunden. Danach schaue ich, was wirklich zu Ihrem Budget und Zeitrahmen passt, und melde mich selbst.",
           go="Los geht's", hint="10 SEKUNDEN", name_h="Zuerst: Wie heißen Sie?", name_sub="Damit ich weiß, mit wem ich spreche.", name_ph="Vor- und Nachname",
           phone_h="Unter welcher Nummer erreiche ich Sie am besten?", phone_sub="Ich schreibe Ihnen direkt. Die Nummer wird nie weitergegeben oder verkauft.", phone_ph="Telefonnummer", email_ph="E-Mail (optional)",
           budget_h="Mit welchem Budget planen Sie?", budget_sub="Eine grobe Spanne genügt. Sie entscheidet, welche Regionen und Eigentumsformen realistisch sind.",
           time_h="Wann können Sie investieren?", time_sub="Manche Deals brauchen Monate. Andere sind in Wochen weg.",
           thanks_h="Danke.", thanks_p="Ich melde mich persönlich, verstehe, was Sie wirklich suchen, und schaue, ob es auf Bali eine Gelegenheit gibt, die es wert ist, Ihnen gezeigt zu werden.",
           sign="Viele Grüße, Kai", fallback="Per WhatsApp an mich senden", back="Zurück", cont="Weiter",
           e_name="Bitte geben Sie Ihren Namen ein.", e_name_long="Der Name ist zu lang.", e_phone="Bitte geben Sie eine gültige Nummer ein.", e_phone_long="Die Nummer ist zu lang.", e_email="Die E-Mail sieht nicht richtig aus.",
           msg="Hallo Kai, ich bin {name}. Ich habe gerade das Formular auf Ihrer Seite ausgefüllt. Budget: {budget}. Zeitrahmen: {when}. Ich freue mich auf den Kontakt.")),
 "nl": dict(
    name="Nederlands", locale="nl_NL", contact_slug="contact",
    home_title="Villa kopen op Bali als Nederlander: de eerlijke gids",
    home_desc="Leasehold, stroman, netto rendement, box 3 en het belastingverdrag, emigreren en pensioen: wat Nederlanders en Belgen moeten weten voor ze op Bali kopen.",
    home_h="Kopen op Bali,", home_h2="zonder verkooppraatje.",
    home_p="Wat je als buitenlander echt kunt bezitten, wat een villa oplevert na alle kosten, en wat de Belastingdienst thuis nog van je wil weten.",
    home_note="Geschreven voor kopers uit Nederland en België.",
    groups=[("kopen", "Kopen en eigendom", "Leasehold, stroman, Hak Pakai, PT PMA en wat er echt op het certificaat staat."),
            ("geld", "Rendement en belasting", "Netto rendement, belasting in Indonesië en thuis, financiering en kosten koper."),
            ("wonen", "Emigreren en visum", "Visum, AOW en pensioen, zorgverzekering, uitschrijven en dagelijks leven."),
            ("vergelijk", "Bali vergeleken", "Bali tegenover Spanje, Curaçao, Thailand en Portugal."),
            ("gebieden", "Waar kopen", "Canggu, Uluwatu, Ubud, Sanur en de rest, met de echte valkuilen.")],
    faq_h="Veelgestelde vragen", toc_h="Op deze pagina", q_h="Beantwoorde vragen",
    by="Door", updated="Bijgewerkt op", min_read="min lezen", share="Delen",
    home="Home", read_next="Lees hierna", more_in="Meer in", all_h="Alle gidsen",
    nav_topics="Onderwerpen", nav_kit="Gratis gids", nav_contact="Contact", lang_label="Taal",
    cta_k="Kijk je naar een specifieke woning?",
    cta_b="Vertel me wat je zoekt en ik kom persoonlijk bij je terug. Vier vragen, tien seconden, daarna opent WhatsApp direct.",
    cta_btn="Stuur me een WhatsApp",
    rail_q="Twijfel je wat dit betekent voor de woning die jij bekijkt?", rail_btn="Vraag het Kai",
    who_h="Ik ben Kai.",
    who_p="Ik ben strategisch investeringsadviseur op Bali. Ik help buitenlandse kopers een villa, een stuk grond of een project op tekening te controleren voordat ze tekenen: het certificaat, de eigenaar, de bestemming, de lease, de vergunning en het echte rendement.",
    legal="Algemene informatie, geen juridisch, fiscaal of financieel advies. Indonesische regels veranderen vaak en worden per regentschap anders toegepast. Controleer alles met je eigen notaris (PPAT), advocaat en belastingadviseur, in Indonesië en thuis.",
    role="Strategisch investeringsadviseur",
    f=dict(interest_h="Wat zoek je op Bali?", interest_sub="Vier korte vragen. Daarna kijk ik wat echt past, en kom ik zelf bij je terug via WhatsApp.", interests=["Grond om op te bouwen", "Een kant-en-klare villa om te wonen of te verhuren", "Een villa op tekening als belegging", "Wonen: huren, visum, verhuizen"], kit_opt="Alleen de gratis kopersgids (pdf)", more_site="Alle gidsen lezen", msg_interest="Ik zoek: {interest}. ",
           title="De juiste woning op Bali vinden", desc="Vertel me je budget en planning, dan kom ik persoonlijk bij je terug met kansen op Bali die echt passen.",
           intro_h="Ik help je de juiste investering op Bali te vinden.", intro_sub="Vier vragen, tien seconden. Daarna kijk ik wat echt past bij je budget en planning, en kom ik zelf bij je terug.",
           go="Starten", hint="10 SECONDEN", name_h="Eerst: hoe heet je?", name_sub="Zodat ik weet met wie ik praat.", name_ph="Voor- en achternaam",
           phone_h="Op welk nummer kan ik je het best bereiken?", phone_sub="Ik stuur je zelf een bericht. Nooit gedeeld of verkocht.", phone_ph="Telefoonnummer", email_ph="E-mail (optioneel)",
           budget_h="Met welk budget werk je?", budget_sub="Een ruwe indicatie is genoeg. Die bepaalt welke gebieden en eigendomsvormen realistisch zijn.",
           time_h="Wanneer kun je investeren?", time_sub="Sommige deals duren maanden. Andere zijn in weken weg.",
           thanks_h="Dank je.", thanks_p="Ik neem persoonlijk contact op, kijk wat je echt zoekt, en of er op Bali een kans is die het waard is om je te laten zien.",
           sign="Groet, Kai", fallback="Stuur het me via WhatsApp", back="Terug", cont="Verder",
           e_name="Vul je naam in.", e_name_long="Die naam is te lang.", e_phone="Vul een geldig nummer in.", e_phone_long="Dat nummer is te lang.", e_email="Dat e-mailadres lijkt niet te kloppen.",
           msg="Hoi Kai, ik ben {name}. Ik heb net het formulier op je site ingevuld. Budget: {budget}. Wanneer: {when}. Hoor graag van je.")),
 "sv": dict(
    name="Svenska", locale="sv_SE", contact_slug="kontakt",
    home_title="Köpa villa på Bali som svensk: den ärliga guiden",
    home_desc="Leasehold, bulvaner, nettoavkastning, skatt i Sverige, flytt och pension: det svenskar behöver veta innan de köper villa eller mark på Bali.",
    home_h="Köpa på Bali,", home_h2="utan säljsnacket.",
    home_p="Vad du som utlänning faktiskt kan äga, vad en villa ger när alla kostnader är betalda, och vad Skatteverket fortfarande vill veta när du bor eller investerar här.",
    home_note="Skrivet för svenska köpare.",
    groups=[("kopa", "Köpa och äga", "Leasehold, bulvaner, Hak Pakai, PT PMA och vad som faktiskt står på lagfarten."),
            ("pengar", "Avkastning och skatt", "Nettoavkastning, skatt i Indonesien och i Sverige, finansiering och kostnader."),
            ("flytta", "Flytta och visum", "Visum, pension, försäkring, utvandring och vardag."),
            ("jamfor", "Bali jämfört", "Bali mot Spanien, Thailand, Portugal och Dubai."),
            ("omraden", "Var köpa", "Canggu, Uluwatu, Ubud, Sanur och resten, med de verkliga fallgroparna.")],
    faq_h="Vanliga frågor", toc_h="På den här sidan", q_h="Frågor som besvaras",
    by="Av", updated="Uppdaterad", min_read="min läsning", share="Dela",
    home="Start", read_next="Läs härnäst", more_in="Mer om", all_h="Alla guider",
    nav_topics="Ämnen", nav_kit="Gratis guide", nav_contact="Kontakt", lang_label="Språk",
    cta_k="Tittar du på något specifikt?",
    cta_b="Berätta vad du letar efter så hör jag av mig personligen. Fyra frågor, tio sekunder, sedan öppnas WhatsApp direkt.",
    cta_btn="Skriv till mig på WhatsApp",
    rail_q="Osäker på vad det här betyder för det du tittar på?", rail_btn="Fråga Kai",
    who_h="Jag heter Kai.",
    who_p="Jag är strategisk investeringsrådgivare på Bali. Jag hjälper utländska köpare att granska en villa, en tomt eller ett projekt på ritning innan de skriver på: lagfarten, ägaren, detaljplanen, leasingavtalet, tillståndet och den verkliga avkastningen.",
    legal="Allmän information, inte juridisk, skattemässig eller finansiell rådgivning. Indonesiska regler ändras ofta och tillämpas olika mellan regionerna. Kontrollera allt med din egen notarie (PPAT), advokat och skatterådgivare, i Indonesien och i Sverige.",
    role="Strategisk investeringsrådgivare",
    f=dict(interest_h="Vad letar du efter på Bali?", interest_sub="Fyra snabba frågor. Sedan tittar jag på vad som faktiskt passar, och hör av mig själv på WhatsApp.", interests=["Mark att bygga på", "En färdig villa att bo i eller hyra ut", "En villa på ritning som investering", "Flytta hit: hyra, visum, flytt"], kit_opt="Bara den gratis köparguiden (pdf)", more_site="Läs alla guider", msg_interest="Jag letar efter: {interest}. ",
           title="Hitta rätt fastighet på Bali", desc="Berätta din budget och tidsplan så hör jag av mig personligen med möjligheter på Bali som faktiskt passar.",
           intro_h="Jag hjälper dig hitta rätt investering på Bali.", intro_sub="Fyra frågor, tio sekunder. Sedan tittar jag på vad som faktiskt passar din budget och tidsplan, och hör av mig själv.",
           go="Kör", hint="10 SEKUNDER", name_h="Först, vad heter du?", name_sub="Så jag vet vem jag pratar med.", name_ph="För- och efternamn",
           phone_h="Vilket nummer når jag dig bäst på?", phone_sub="Jag skriver till dig direkt. Delas aldrig, säljs aldrig.", phone_ph="Telefonnummer", email_ph="E-post (valfritt)",
           budget_h="Vilken budget har du?", budget_sub="Ett ungefärligt spann räcker. Det avgör vilka områden och ägandeformer som är realistiska.",
           time_h="När kan du investera?", time_sub="Vissa affärer tar månader. Andra försvinner på veckor.",
           thanks_h="Tack.", thanks_p="Jag hör av mig personligen, tar reda på vad du faktiskt letar efter, och ser om det finns en möjlighet på Bali som är värd att visa dig.",
           sign="Hälsningar, Kai", fallback="Skicka det till mig på WhatsApp", back="Tillbaka", cont="Fortsätt",
           e_name="Skriv ditt namn.", e_name_long="Namnet är för långt.", e_phone="Skriv ett giltigt nummer.", e_phone_long="Numret är för långt.", e_email="E-postadressen ser inte rätt ut.",
           msg="Hej Kai, jag heter {name}. Jag fyllde precis i formuläret på din sida. Budget: {budget}. När: {when}. Hörs!")),
 "no": dict(
    name="Norsk", locale="nb_NO", contact_slug="kontakt",
    home_title="Kjøpe villa på Bali som nordmann: den ærlige guiden",
    home_desc="Leasehold, stråmenn, nettoavkastning, skatt og formuesskatt i Norge, flytting og pensjon: det nordmenn bør vite før de kjøper villa eller tomt på Bali.",
    home_h="Kjøpe på Bali,", home_h2="uten salgspraten.",
    home_p="Hva du som utlending faktisk kan eie, hva en villa gir når alle kostnader er betalt, og hva Skatteetaten fortsatt vil vite når du bor eller investerer her.",
    home_note="Skrevet for norske kjøpere.",
    groups=[("kjope", "Kjøpe og eie", "Leasehold, stråmenn, Hak Pakai, PT PMA og hva som faktisk står i hjemmelsdokumentet."),
            ("penger", "Avkastning og skatt", "Nettoavkastning, skatt i Indonesia og i Norge, finansiering og kostnader."),
            ("flytte", "Flytte og visum", "Visum, pensjon, forsikring, utvandring og hverdag."),
            ("sammenlign", "Bali sammenlignet", "Bali mot Spania, Thailand, Portugal og Dubai."),
            ("omrader", "Hvor kjøpe", "Canggu, Uluwatu, Ubud, Sanur og resten, med de virkelige fallgruvene.")],
    faq_h="Vanlige spørsmål", toc_h="På denne siden", q_h="Spørsmål som besvares",
    by="Av", updated="Oppdatert", min_read="min lesing", share="Del",
    home="Start", read_next="Les videre", more_in="Mer om", all_h="Alle guider",
    nav_topics="Temaer", nav_kit="Gratis guide", nav_contact="Kontakt", lang_label="Språk",
    cta_k="Ser du på noe konkret?",
    cta_b="Fortell meg hva du leter etter, så tar jeg kontakt personlig. Fire spørsmål, ti sekunder, så åpnes WhatsApp direkte.",
    cta_btn="Skriv til meg på WhatsApp",
    rail_q="Usikker på hva dette betyr for det du ser på?", rail_btn="Spør Kai",
    who_h="Jeg heter Kai.",
    who_p="Jeg er strategisk investeringsrådgiver på Bali. Jeg hjelper utenlandske kjøpere med å sjekke en villa, en tomt eller et prosjekt på tegning før de signerer: hjemmelen, eieren, reguleringen, leieavtalen, lisensen og den virkelige avkastningen.",
    legal="Generell informasjon, ikke juridisk, skattemessig eller finansiell rådgivning. Indonesiske regler endres ofte og praktiseres ulikt mellom regionene. Sjekk alt med din egen notar (PPAT), advokat og skatterådgiver, i Indonesia og i Norge.",
    role="Strategisk investeringsrådgiver",
    f=dict(interest_h="Hva ser du etter på Bali?", interest_sub="Fire raske spørsmål. Så ser jeg på hva som faktisk passer, og tar kontakt selv på WhatsApp.", interests=["Tomt å bygge på", "En ferdig villa å bo i eller leie ut", "En villa på tegning som investering", "Flytte hit: leie, visum, flytting"], kit_opt="Bare den gratis kjøperguiden (pdf)", more_site="Les alle guidene", msg_interest="Jeg ser etter: {interest}. ",
           title="Finn riktig eiendom på Bali", desc="Fortell meg budsjett og tidsplan, så tar jeg kontakt personlig med muligheter på Bali som faktisk passer.",
           intro_h="Jeg hjelper deg å finne riktig investering på Bali.", intro_sub="Fire spørsmål, ti sekunder. Så ser jeg på hva som faktisk passer budsjettet og tidsplanen din, og tar kontakt selv.",
           go="Kjør", hint="10 SEKUNDER", name_h="Først, hva heter du?", name_sub="Så jeg vet hvem jeg snakker med.", name_ph="For- og etternavn",
           phone_h="Hvilket nummer når jeg deg best på?", phone_sub="Jeg skriver til deg direkte. Deles aldri, selges aldri.", phone_ph="Telefonnummer", email_ph="E-post (valgfritt)",
           budget_h="Hvilket budsjett har du?", budget_sub="Et omtrentlig spenn holder. Det avgjør hvilke områder og eierformer som er realistiske.",
           time_h="Når kan du investere?", time_sub="Noen handler tar måneder. Andre forsvinner på uker.",
           thanks_h="Takk.", thanks_p="Jeg tar kontakt personlig, finner ut hva du faktisk leter etter, og ser om det finnes en mulighet på Bali som er verdt å vise deg.",
           sign="Hilsen Kai", fallback="Send det til meg på WhatsApp", back="Tilbake", cont="Fortsett",
           e_name="Skriv navnet ditt.", e_name_long="Navnet er for langt.", e_phone="Skriv et gyldig nummer.", e_phone_long="Nummeret er for langt.", e_email="E-postadressen ser ikke riktig ut.",
           msg="Hei Kai, jeg heter {name}. Jeg fylte nettopp ut skjemaet på siden din. Budsjett: {budget}. Når: {when}. Snakkes!")),
}

ORDER = ["fr", "de", "nl", "sv", "no"]

# A language is published only when it is finished: every page written to full
# depth, its kit PDF printed. Add the code here at that point, not before.
READY = {"fr"}


def pages_for(B, lang):
    d = os.path.join(SRC, lang)
    if not os.path.isdir(d):
        return []
    ps = [B.parse(os.path.join(d, f)) for f in os.listdir(d) if f.endswith(".md")]
    groups = [g[0] for g in UI[lang]["groups"]]
    for p in ps:
        if p.get("group") not in groups:
            raise ValueError(f"{lang}/{p['slug']}: unknown group {p.get('group')}")
    return sorted(ps, key=lambda p: (groups.index(p["group"]), int(p.get("order", "99"))))


def live(B):
    return [l for l in ORDER if l in READY and pages_for(B, l)]


def alternates(B, paths):
    """hreflang links for pages that exist in several languages (home, kit,
    contact). `paths` maps language code to path."""
    out = "".join(f'\n<link rel="alternate" hreflang="{c}" href="{B.SITE_URL}{p}">' for c, p in paths.items())
    if "en" in paths:
        out += f'\n<link rel="alternate" hreflang="x-default" href="{B.SITE_URL}{paths["en"]}">'
    return out


def head(B, lang, title, desc, path, alts=""):
    """B.head, in the right language, with og:locale and hreflang."""
    h = B.head(title, desc, path)
    h = h.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    h = h.replace('<meta property="og:type" content="article">',
                  f'<meta property="og:type" content="article">\n<meta property="og:locale" content="{UI[lang]["locale"]}">', 1)
    if alts:
        h = h.replace("</head>", alts.lstrip("\n") + "\n</head>", 1)
    return h


def nav(B, lang, pages):
    u = UI[lang]
    base = f"{B.BASE}/{lang}/"

    def row(key, name, blurb):
        n = len([p for p in pages if p["group"] == key])
        return (f'<a class="nd-row" href="{base}#{key}"><span class="nd-row-h">{name}<em>{n}</em></span>'
                f'<span class="nd-row-b">{blurb}</span></a>')
    topics = "".join(row(*g) for g in u["groups"])
    langs = "".join(f'<a class="nd-row" href="{B.BASE}{href}" hreflang="{c}"><span class="nd-row-h">{name}</span></a>'
                    for c, name, href in B.live_langs())
    return f"""<header class="masthead">
<div class="wrap masthead-inner">
<a class="wordmark" href="{base}"><span>Bali</span> Off Script</a>
<button class="menu-btn" aria-label="Menu" aria-expanded="false">Menu</button>
<nav class="nav"><div class="nav-inner">
<div class="nav-g"><button class="nav-t" type="button" aria-expanded="false">{u["nav_topics"]}</button><div class="nav-drop"><div class="nd-in">{topics}</div></div></div>
<a class="nav-search" href="{B.BASE}{K.LANDING[lang]}">{u["nav_kit"]}</a>
<a class="nav-search" href="{base}{u["contact_slug"]}/">{u["nav_contact"]}</a>
<div class="nav-g"><button class="nav-t" type="button" aria-expanded="false">{u["lang_label"]}: {lang.upper()}</button><div class="nav-drop"><div class="nd-in">{langs}</div></div></div>
</div></nav>
</div>
</header>"""


def footer(B, lang):
    u = UI[lang]
    return f"""<footer class="foot">
<div class="wrap foot-inner">
<div>
<p class="foot-mark">Bali Off Script</p>
<p class="foot-note">{u["home_note"]}</p>
</div>
<div class="foot-links">
<a href="{B.BASE}/{lang}/">{u["all_h"]}</a>
<a href="{B.BASE}{K.LANDING[lang]}">{u["nav_kit"]}</a>
<a href="{B.BASE}/{lang}/{u["contact_slug"]}/">{u["nav_contact"]}</a>
<a href="{B.BASE}/about/">Kai</a>
</div>
</div>
<div class="wrap foot-langs"><nav class="langs" aria-label="{u["lang_label"]}">{B.lang_links(lang)}</nav></div>
<div class="wrap foot-legal"><p>{u["legal"]}</p></div>
<script src="{B.BASE}/search.js" defer></script><script src="{B.BASE}/kit.js" defer></script>
</footer>
</body>
</html>"""


def cta(B, lang):
    u = UI[lang]
    return f"""<section class="cta">
<div class="cta-id">
{B.portrait()}
<div class="cta-said">
<p class="cta-k">{u["cta_k"]}</p>
<p class="cta-b">{u["cta_b"]}</p>
<p class="cta-by">{B.AUTHOR}, {u["role"]}</p>
</div>
</div>
<div class="cta-acts">
<a class="btn btn-wa" href="{B.BASE}/{lang}/{u["contact_slug"]}/">{B.wa_logo()}<span>{u["cta_btn"]}</span></a>
</div>
</section>"""


def extract_faq(body, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not m:
        return []
    out, q, buf = [], None, []
    for line in m.group(1).split("\n"):
        if line.startswith("### "):
            if q:
                out.append((q, " ".join(buf).strip()))
            q, buf = line[4:].strip(), []
        elif q and line.strip():
            buf.append(re.sub(r"[*`\[\]]|\(/[^)]*\)", "", line.strip()))
    if q:
        out.append((q, " ".join(buf).strip()))
    return [(a, b) for a, b in out if b]


def toc(B, lang, body, extra=()):
    hs = B.headings(body) + list(extra)
    if len(hs) < 3:
        return ""
    items = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in hs)
    return (f'<nav class="toc" aria-label="{UI[lang]["toc_h"]}">'
            f'<p class="toc-h">{UI[lang]["toc_h"]}</p><ol>{items}</ol></nav>')


def article(B, lang, m, pages):
    u = UI[lang]
    gname = dict((g[0], g[1]) for g in u["groups"])[m["group"]]
    path = f'/{lang}/{m["slug"]}/'
    title = m.get("title") or m["question"]
    updated = m.get("verified", str(date.today()))
    faq = extract_faq(m["body"], u["faq_h"])
    prose_src = re.sub(rf"^## {re.escape(u['faq_h'])}\s*$.*?(?=^## |\Z)", "", m["body"], flags=re.M | re.S) if faq else m["body"]
    body_html = B.md(prose_src.rstrip())
    hero, body_html = PH.decorate(m["slug"], m["group"], body_html)
    top, rest = B.split_for_kit(body_html)
    kitb = K.box(B, lang, "article")
    prose = (f'<div class="prose">{top}</div>{kitb}<div class="prose">{rest}</div>' if rest
             else f'<div class="prose">{body_html}</div>{kitb}')
    faq_block = ""
    if faq:
        rows = "".join(f'<details class="fq" id="q-{B.slugify(q)}"><summary>{q}</summary><p>{a}</p></details>' for q, a in faq)
        faq_block = f'<section class="faqs"><h2 id="faq">{u["faq_h"]}</h2>{rows}</section>'
    desc = B.meta_desc(m["summary"], m["body"])
    ents = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq] or \
           [{"@type": "Question", "name": m["question"], "acceptedAnswer": {"@type": "Answer", "text": m["summary"]}}]
    schema = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "FAQPage", "mainEntity": ents, "inLanguage": lang},
        {"@type": "Article", "headline": title, "alternativeHeadline": m["question"], "description": desc,
         "image": f"{B.SITE_URL}/og/default.jpg", "datePublished": updated, "dateModified": updated,
         "inLanguage": lang, "isAccessibleForFree": True,
         "wordCount": len(re.sub(r"[^\w\s]", " ", m["body"]).split()),
         "author": {"@type": "Person", "@id": f"{B.SITE_URL}/#kai", "name": B.AUTHOR, "jobTitle": u["role"],
                    "url": B.SITE_URL + "/about/"},
         "publisher": {"@type": "Organization", "name": B.SITE_NAME, "url": B.SITE_URL,
                       "logo": {"@type": "ImageObject", "url": f"{B.SITE_URL}/icon-512.png"}},
         "mainEntityOfPage": {"@type": "WebPage", "@id": B.SITE_URL + path}, "articleSection": gname},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": u["home"], "item": f"{B.SITE_URL}/{lang}/"},
            {"@type": "ListItem", "position": 2, "name": gname, "item": f"{B.SITE_URL}/{lang}/#{m['group']}"},
            {"@type": "ListItem", "position": 3, "name": title, "item": B.SITE_URL + path}]}]}, ensure_ascii=False)

    same = [p for p in pages if p["group"] == m["group"] and p["slug"] != m["slug"]]
    nxt = same[0] if same else next(p for p in pages if p["slug"] != m["slug"])
    more = "".join(f'<li><a href="{B.BASE}/{lang}/{p["slug"]}/">{p["question"]}</a></li>' for p in same[1:6])
    more_block = f'<div class="on-more"><p class="on-more-h">{u["more_in"]} {gname}</p><ul>{more}</ul></div>' if more else ""
    onward = f"""<section class="onward">
<a class="on-next" href="{B.BASE}/{lang}/{nxt["slug"]}/">
<span class="on-k">{u["read_next"]}</span>
<span class="on-h">{nxt["question"]}</span>
<span class="on-b">{nxt["summary"]}</span>
</a>
{more_block}
</section>"""
    rail_q = ""
    if faq:
        items = "".join(f'<li><a href="#q-{B.slugify(q)}">{q}</a></li>' for q, _ in faq)
        rail_q = f'<nav class="rail-q"><p class="toc-h">{u["q_h"]}</p><ul>{items}</ul></nav>'
    share = B.share_bar(title, path, cls=" sh-rail").replace(">Share<", f">{u['share']}<")
    return f"""{head(B, lang, title, desc, path)}
<script type="application/ld+json">{schema}</script>
{nav(B, lang, pages)}
<main class="wrap article">
<nav class="crumbs" aria-label="Breadcrumb">
<a href="{B.BASE}/{lang}/">{u["home"]}</a><span>/</span><a href="{B.BASE}/{lang}/#{m['group']}">{gname}</a>
</nav>
<h1>{m["question"]}</h1>
<p class="standfirst">{m["summary"]}</p>
<div class="byline">
<span>{u["by"]} {B.AUTHOR}, {u["role"]}</span>
<span>{u["updated"]} <time datetime="{updated}">{updated}</time></span>
<span>{B.read_time(m["body"])} {u["min_read"]}</span>
</div>
<div class="art-grid">
<div class="art-main">
{hero}
{prose}
{faq_block}
{cta(B, lang)}
{onward}
</div>
<aside class="art-rail">
{toc(B, lang, prose_src, [("faq", u["faq_h"])] if faq else [])}
{rail_q}
{K.mini(B, lang)}
{share}
<div class="rail-cta"><p>{u["rail_q"]}</p><a href="{B.BASE}/{lang}/{u["contact_slug"]}/">{B.wa_logo("ig ig-sm")}<span>{u["rail_btn"]}</span></a></div>
</aside>
</div>
</main>
{footer(B, lang)}"""


def home(B, lang, pages, alts):
    u = UI[lang]
    path = f"/{lang}/"
    secs = ""
    used = set()
    for key, name, blurb in u["groups"]:
        ps = [p for p in pages if p["group"] == key]
        if not ps:
            continue
        cards = "".join(f'<li class="card"><a href="{B.BASE}/{lang}/{p["slug"]}/">{B.card_img(p["slug"], p["group"], used)}<h3>{p["question"]}</h3><p>{p["summary"]}</p></a></li>' for p in ps)
        secs += f'<section class="wrap" id="{key}"><h2 class="sec-h">{name}</h2><p class="standfirst">{blurb}</p><ul class="cards">{cards}</ul></section>'
    schema = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": u["home_title"], "description": u["home_desc"], "url": B.SITE_URL + path,
         "inLanguage": lang, "isPartOf": {"@type": "WebSite", "name": B.SITE_NAME, "url": B.SITE_URL},
         "about": {"@type": "Thing", "name": "Bali real estate for foreign buyers"},
         "author": {"@id": f"{B.SITE_URL}/#kai"},
         "hasPart": [{"@type": "Article", "headline": p["question"], "url": f'{B.SITE_URL}/{lang}/{p["slug"]}/'} for p in pages]}]},
        ensure_ascii=False)
    return f"""{head(B, lang, u["home_title"], u["home_desc"], path, alts)}
<script type="application/ld+json">{schema}</script>
{nav(B, lang, pages)}
<main>
<section class="hero-split">
<div class="hero-copy">
<h1 class="hero-h">{u["home_h"]}<br><span>{u["home_h2"]}</span></h1>
<p class="hero-sub">{u["home_p"]}</p>
<p class="hero-note">{u["home_note"]}</p>
<div class="hero-acts">
<a class="lnk lnk-solid" href="#kit">{u["nav_kit"]}</a>
<a class="lnk lnk-wa" href="{B.BASE}/{lang}/{u["contact_slug"]}/">{B.form_logo("ig")}<span>{u["nav_contact"]}</span></a>
</div>
</div>
<div class="hero-fig">
<img src="{B.BASE}/kai-hero.jpg" width="726" height="969" alt="{B.AUTHOR}, {u["role"]}" fetchpriority="high">
<figcaption class="hero-cap"><span>{B.AUTHOR}</span>{u["role"]}</figcaption>
</div>
</section>
<section class="wrap">{K.box(B, lang, "home")}</section>
{secs}
<section class="wrap who-wrap">
<div class="who">
{B.portrait("who-photo")}
<div>
<h2 class="who-h">{u["who_h"]}</h2>
<p class="who-b">{u["who_p"]}</p>
</div>
</div>
</section>
<section class="wrap">{cta(B, lang)}</section>
</main>
{footer(B, lang)}"""


def contact(B, lang, pages, alts):
    """The /opportunities/ form, in this language."""
    u = UI[lang]
    f = u["f"]
    k = K.UI[lang]
    path = f"/{lang}/{u['contact_slug']}/"

    def opts(items):
        return "\n".join(f'<button type="button" class="ld-opt" data-value="{v}" aria-pressed="false"><b>{chr(65 + i)}</b><span>{v}</span></button>'
                         for i, v in enumerate(items))
    # The interest goes first in the message, so Kai sees what they want before the budget.
    msg = f["msg"]
    for word in ("Budget", "Budsjett"):
        if ". " + word in msg:
            msg = msg.replace(". " + word, ". " + f["msg_interest"] + word, 1)
            break
    t = {"lang": lang, "dial": K.DIAL_DEFAULT[lang], "msg": msg}
    for key in ("e_name", "e_name_long", "e_phone", "e_phone_long", "e_email"):
        t[key] = f[key]
    tj = json.dumps(t, ensure_ascii=False).replace("'", "&#39;")
    return f"""{head(B, lang, f["title"], f["desc"], path, alts).replace("<body>", '<body class="lead-body">', 1)}
<main class="lead">
<div class="lead-bg" aria-hidden="true" style="background-image:url({PH.url("1555400038-63f5ba517a47", 1600, 1000)})"></div>
<header class="lead-head">
{B.portrait("lead-photo")}
<div><p class="lead-brand">Bali Off Script</p><p class="lead-who">{B.AUTHOR}, {u["role"]}</p></div>
</header>
<div class="lead-card">
<div class="ld-top"><p class="ld-count" id="ld-count"></p></div>
<div class="ld-track"><span id="ld-bar"></span></div>
<div class="ld-body">
<h1 class="sr-only">{f["title"]}</h1>
<p class="sr-only" id="ld-live" aria-live="polite"></p>
<form id="lead" data-endpoint="{B.LEAD_ENDPOINT}" data-wa="{B.LEAD_WHATSAPP}" data-t='{tj}' novalidate>
<input type="text" name="company" class="ld-hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<input type="hidden" name="budget"><input type="hidden" name="timeline"><input type="hidden" name="interest">
<div class="ld-step on" data-field="interest">
<h2>{f["interest_h"]}</h2>
<p class="ld-sub">{f["interest_sub"]}</p>
<div class="ld-opts">{opts(f["interests"])}
<a class="ld-opt ld-opt-kit" href="{B.BASE}{K.LANDING[lang]}#kit"><b>E</b><span>{f["kit_opt"]}</span></a></div>
</div>
<div class="ld-step" data-field="name">
<h2>{f["name_h"]}</h2><p class="ld-sub">{f["name_sub"]}</p>
<input type="text" name="name" autocomplete="name" autocapitalize="words" spellcheck="false" placeholder="{f["name_ph"]}" maxlength="80" enterkeyhint="next">
<p class="ld-err"></p>
<div class="ld-acts"><button type="button" class="ld-btn ghost" data-back>{f["back"]}</button><button type="button" class="ld-btn" data-next>{f["cont"]}</button></div>
</div>
<div class="ld-step" data-field="phone">
<h2>{f["phone_h"]}</h2><p class="ld-sub">{f["phone_sub"]}</p>
<div class="ld-tel"><select id="ld-dial" aria-label="Country code" autocomplete="tel-country-code"></select>
<input type="tel" name="phone" autocomplete="tel-national" inputmode="tel" placeholder="{f["phone_ph"]}" maxlength="20" enterkeyhint="next"></div>
<input type="email" name="email" class="ld-email" autocomplete="email" inputmode="email" spellcheck="false" placeholder="{f["email_ph"]}" maxlength="120" enterkeyhint="next">
<p class="ld-err"></p>
<div class="ld-acts"><button type="button" class="ld-btn ghost" data-back>{f["back"]}</button><button type="button" class="ld-btn" data-next>{f["cont"]}</button></div>
</div>
<div class="ld-step" data-field="budget"><h2>{f["budget_h"]}</h2><p class="ld-sub">{f["budget_sub"]}</p><div class="ld-opts">{opts(k["budgets"])}</div></div>
<div class="ld-step" data-field="timeline"><h2>{f["time_h"]}</h2><p class="ld-sub">{f["time_sub"]}</p><div class="ld-opts">{opts(k["times"])}</div></div>
<div class="ld-step ld-done">
<div class="ld-tick"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5.5 5.5L20 7"/></svg></div>
<h2>{f["thanks_h"]}</h2>
<p>{f["thanks_p"]}</p>
<p class="ld-sign">{f["sign"]}<span>{u["role"].upper()}</span></p>
<div id="ld-fallback" hidden><a href="#" target="_blank" rel="noopener">{f["fallback"]}</a></div>
</div>
</form>
</div>
</div>
<nav class="lead-more"><a href="{B.BASE}/{lang}/">{f["more_site"]}</a></nav>
</main>
<script src="{B.BASE}/lead.js" defer></script>
</body>
</html>"""


def build(B):
    """Write every language section. Returns [(url, lastmod)] for the sitemap."""
    urls = []
    lv = live(B)
    if not lv:
        return urls
    today = date.today().isoformat()
    home_paths = {"en": "/"}
    home_paths.update({l: f"/{l}/" for l in lv})
    kit_paths = {"en": K.LANDING["en"]}
    kit_paths.update({l: K.LANDING[l] for l in lv})
    for lang in lv:
        pages = pages_for(B, lang)
        u = UI[lang]
        B.write(f"/{lang}/", home(B, lang, pages, alternates(B, home_paths)))
        urls.append((f"/{lang}/", today))
        for p in pages:
            B.write(f"/{lang}/{p['slug']}/", article(B, lang, p, pages))
            urls.append((f"/{lang}/{p['slug']}/", p.get("verified", today)))
        B.write(K.LANDING[lang], K.landing(B, lang,
                head_fn=lambda t, d, pth, _l=lang: head(B, _l, t, d, pth, alternates(B, kit_paths)),
                nav_html=nav(B, lang, pages), footer_html=footer(B, lang)))
        urls.append((K.LANDING[lang], today))
        B.write(f"/{lang}/{u['contact_slug']}/", contact(B, lang, pages, ""))
        urls.append((f"/{lang}/{u['contact_slug']}/", today))
    return urls
