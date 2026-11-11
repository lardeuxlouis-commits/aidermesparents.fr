#!/usr/bin/env python3
"""Générateur statique de aidermesparents.fr : contenu/*.json -> docs/ (GitHub Pages)."""
import json, glob, os, re, html, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
DOMAIN = "https://aidermesparents.fr"
SITE = "Aider mes parents"
LANCEMENT = "2026-11-12"

E = lambda s: html.escape(str(s or ""), quote=True)


def inline(s):
    """Texte des agents : on échappe, puis **gras** seulement."""
    s = E(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def lien(m):
        t, cible = m.group(1), m.group(2).strip("/")
        if cible in PAGES:
            return f'<a href="/{cible}/">{t}</a>'
        if cible.startswith("https://"):
            return f'<a href="{cible}" rel="noopener" target="_blank">{t}</a>'
        return t
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lien, s)


def strip(s):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", str(s or ""))


# Rubriques : l'ordre fixe la navigation et le hub
RUBRIQUES = [
    ("aides", "Les aides financières", "Ce que votre parent peut toucher, et comment le demander."),
    ("domicile", "Rester à domicile", "Aide à domicile, sécurité, repas, logement adapté."),
    ("etablissement", "EHPAD et résidences", "Les prix, les aides et qui doit payer."),
    ("aidants", "Vous, l'aidant", "Vos droits, votre congé, votre rémunération."),
]
RUB_SLUG = {"aides": "aides-financieres", "domicile": "maintien-a-domicile", "etablissement": "ehpad-et-residences", "aidants": "aidants"}
RUB_PAGE = {
    "aides": ("Aides financières pour personnes âgées : le guide 2026",
              "APA, ASPA, carte mobilité inclusion, Sortir Plus, mutuelle : toutes les aides financières pour un parent âgé, avec les montants 2026.",
              "Aides financières pour les personnes âgées",
              "Une personne âgée peut cumuler plusieurs aides : l'APA si elle perd de l'autonomie, l'ASPA si ses ressources sont faibles, des aides de sa caisse de retraite, et des avantages comme la carte mobilité inclusion. Chacune dépend d'un organisme différent : le département pour l'APA, la caisse de retraite pour l'ASPA et Sortir Plus, la MDPH ou le département pour la carte. Voici chaque aide, ses conditions et ses montants de 2026."),
    "domicile": ("Maintien à domicile des personnes âgées : solutions et aides",
                 "Aide à domicile, téléassistance, portage de repas, adaptation du logement : les solutions pour qu'un parent âgé reste chez lui, et les aides.",
                 "Maintien à domicile : les solutions et les aides",
                 "La plupart des personnes âgées souhaitent rester chez elles le plus longtemps possible. C'est souvent possible en combinant plusieurs services : une aide à domicile pour le quotidien, la téléassistance pour la sécurité, le portage de repas, et des travaux pour adapter le logement. Ces dépenses ouvrent droit à des aides (APA, caisse de retraite, MaPrimeAdapt) et, pour beaucoup, à un crédit d'impôt de 50 %."),
    "etablissement": ("EHPAD et résidences seniors : prix, aides et démarches",
                      "Prix d'un EHPAD, résidence autonomie ou services, aide sociale à l'hébergement, obligation alimentaire : tout pour choisir et financer.",
                      "EHPAD et résidences : choisir et financer",
                      "Quand le maintien à domicile devient trop difficile, plusieurs solutions existent : la résidence autonomie ou la résidence services pour une personne encore autonome, l'EHPAD quand les soins deviennent nécessaires. Le coût varie beaucoup selon l'établissement, et plusieurs aides peuvent réduire la facture. Si les ressources ne suffisent pas, l'aide sociale peut prendre le relais, avec une participation possible des enfants."),
    "aidants": ("Aidants familiaux : droits, congé et aides en 2026",
                "Congé de proche aidant, AJPA, rémunération via l'APA, droit au répit : les droits des enfants et proches qui aident un parent âgé.",
                "Aidants : vos droits quand vous aidez un parent",
                "Aider un parent âgé prend du temps, de l'énergie et parfois de l'argent. La loi reconnaît ce rôle : congé de proche aidant indemnisé, possibilité d'être rémunéré grâce à l'APA de votre parent, droit au répit, trimestres de retraite. Ces droits sont peu connus et souvent sous-utilisés. Voici ce que vous pouvez demander pour vous."),
}
PAGES = {  # slug -> (rubrique, image, libellé court pour le menu et les cartes)
    "apa": ("aides", "accueil", "APA : montant et conditions"),
    "apa/demande": ("aides", "accueil", "Faire la demande d'APA"),
    "grille-aggir": ("aides", "aidant", "Grille AGGIR et niveaux de GIR"),
    "aspa": ("aides", "accueil", "ASPA, le minimum vieillesse"),
    "carte-mobilite-inclusion": ("aides", "aidant", "Carte mobilité inclusion"),
    "sortir-plus": ("aides", "aidant", "Sortir Plus (Agirc-Arrco)"),
    "mutuelle-senior": ("aides", "accueil", "Mutuelle senior et aides"),
    "aide-a-domicile": ("domicile", "aide-domicile", "Aide à domicile : prix et aides"),
    "teleassistance": ("domicile", "teleassistance", "Téléassistance"),
    "portage-de-repas": ("domicile", "aide-domicile", "Portage de repas"),
    "maprimeadapt": ("domicile", "logement", "MaPrimeAdapt : adapter le logement"),
    "ehpad-prix-aides": ("etablissement", "ehpad", "Prix d'un EHPAD et aides"),
    "aide-sociale-hebergement": ("etablissement", "ehpad", "Aide sociale à l'hébergement"),
    "obligation-alimentaire": ("etablissement", "ehpad", "Obligation alimentaire"),
    "residence-senior": ("etablissement", "ehpad", "Résidence services seniors"),
    "aidant-familial": ("aidants", "aidant", "Aidant familial : vos droits"),
    "conge-proche-aidant": ("aidants", "aidant", "Congé de proche aidant et AJPA"),
}
ALT = {
    "accueil": "Une femme serre sa mère âgée dans ses bras, toutes deux rient sur une terrasse ensoleillée",
    "aidant": "Un homme marche bras dessus bras dessous avec son père âgé dans une rue de village",
    "aide-domicile": "Une aide à domicile plie le linge avec une dame âgée dans son salon",
    "teleassistance": "Un homme âgé lit le journal dans son fauteuil avec un bouton de téléassistance autour du cou",
    "ehpad": "Une dame âgée lit un livre dans la salle commune lumineuse d'une résidence",
    "logement": "Une dame âgée sur un monte-escalier, son fils l'attend en bas des marches",
}

CSS = open(os.path.join(ROOT, "_build", "style.css"), encoding="utf-8").read()


def court_txt(t, n=118):
    t = strip(t)
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def url(slug):
    return "/" if slug == "" else f"/{slug}/"


def nav_html(actif=None):
    cur = ' aria-current="true"'
    items = "".join(
        f'<li><a href="/{RUB_SLUG[r]}/"{cur if actif == r else ""}>{E(t)}</a></li>' for r, t, _ in RUBRIQUES)
    return (f'<header class="top"><div class="wrap bar"><a class="logo" href="/" aria-label="{SITE}, accueil">'
            f'<span class="mark" aria-hidden="true"></span><span>aider<b>mes</b>parents</span></a>'
            f'<nav aria-label="Rubriques"><ul>{items}</ul></nav></div></header>')


FOOTER = None


def footer_html(pages):
    cols = ""
    for r, t, _ in RUBRIQUES:
        liens = "".join(f'<li><a href="{url(s)}">{E(PAGES[s][2])}</a></li>' for s in PAGES if PAGES[s][0] == r and s in pages)
        cols += f'<div><h2><a href="/{RUB_SLUG[r]}/">{E(t)}</a></h2><ul>{liens}</ul></div>'
    return (f'<footer><div class="wrap"><div class="fcols">{cols}</div>'
            f'<p class="fnote">aidermesparents.fr est un guide indépendant. Il n\'est rattaché à aucune administration, caisse ou entreprise. '
            f'Les montants sont vérifiés sur les sources officielles citées en bas de chaque page.</p>'
            f'<p class="flinks"><a href="/a-propos/">Qui sommes-nous</a><a href="/mentions-legales/">Mentions légales</a>'
            f'<a href="/confidentialite/">Confidentialité</a></p></div></footer>')


def page(title, desc, path, body, schema, image="accueil", actif=None, foot=""):
    canon = DOMAIN + path
    og_img = f"{DOMAIN}/img/{image}.jpg"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fffaf3">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={ASSET_V}">
{ld}
<script src="/calc.js?v={ASSET_V}" defer></script>
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
{nav_html(actif)}
<main id="contenu">
{body}
</main>
{foot}
</body>
</html>"""


def bloc_html(b):
    t = b.get("type")
    if t == "p":
        return f"<p>{inline(b.get('texte'))}</p>"
    if t == "liste":
        return "<ul>" + "".join(f"<li>{inline(i)}</li>" for i in b.get("items", [])) + "</ul>"
    if t == "etapes":
        return '<ol class="etapes">' + "".join(f"<li>{inline(i)}</li>" for i in b.get("items", [])) + "</ol>"
    if t == "tableau":
        th = "".join(f'<th scope="col">{inline(h)}</th>' for h in b.get("entetes", []))
        rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in b.get("lignes", []))
        return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'
    if t == "exemple":
        return f'<aside class="exemple"><p class="lab">{E(b.get("titre") or "Exemple")}</p><p>{inline(b.get("texte"))}</p></aside>'
    if t == "attention":
        return f'<aside class="attention"><p class="lab">À savoir</p><p>{inline(b.get("texte"))}</p></aside>'
    return ""


def ancre(h2):
    s = re.sub(r"[^a-z0-9]+", "-", strip(h2).lower().translate(str.maketrans("àâäéèêëîïôöùûüç’'", "aaaeeeeiioouuuc  "))).strip("-")
    return s[:60] or "section"


def article(d, pages):
    slug = d["slug"]
    rub, img, court = PAGES[slug]
    rub_t = dict((r, t) for r, t, _ in RUBRIQUES)[rub]
    path = url(slug)
    verif = d.get("date_verification") or LANCEMENT
    date_txt = dt.date.fromisoformat(verif).strftime("%d/%m/%Y")
    secs = d.get("sections", [])
    ids = []
    for s in secs:
        a = ancre(s["h2"]); n = 2
        while a in ids: a = f"{ancre(s['h2'])}-{n}"; n += 1
        ids.append(a)
    toc = "".join(f'<li><a href="#{a}">{E(strip(s["h2"]))}</a></li>' for s, a in zip(secs, ids))
    corps = "".join(f'<section aria-labelledby="{a}"><h2 id="{a}">{E(strip(s["h2"]))}</h2>' + "".join(bloc_html(b) for b in s.get("blocs", [])) + "</section>"
                    for s, a in zip(secs, ids))
    nb_src = len([x for x in d.get("sources", []) if str(x.get("url", "")).startswith("https://")])
    i2 = [m.end() for m in re.finditer("</section>", corps)]
    if len(i2) >= 3:  # encart d'action après la 2e section
        corps = corps[:i2[1]] + CTA_MILIEU + corps[i2[1]:]
    if slug in CALC and i2:  # calculateur après la 1re section
        corps = corps[:i2[0]] + f'<div class="calc" data-calc="{CALC[slug]}"><noscript>Activez JavaScript pour utiliser le calculateur.</noscript></div>' + corps[i2[0]:]
    urg = URGENCE.get(slug)
    urg_html = f'<aside class="urgence"><p class="lab">Ne tardez pas</p><p>{inline(urg)}</p></aside>' if urg else ""
    bref = "".join(f"<li>{inline(x)}</li>" for x in d.get("en_bref", []))
    faq = d.get("faq", [])
    faq_html = ("<section aria-labelledby=\"faq\"><h2 id=\"faq\">Questions fréquentes</h2>" +
                "".join(f"<details><summary>{E(strip(f['q']))}</summary><p>{inline(f['r'])}</p></details>" for f in faq) + "</section>") if faq else ""
    liens = []
    for l in d.get("liens_internes", []):
        s2 = l.get("slug") if isinstance(l, dict) else l
        if s2 in pages and s2 != slug and s2 not in [x[0] for x in liens]:
            liens.append((s2, (l.get("ancre") if isinstance(l, dict) else None) or PAGES[s2][2]))
    for s2 in PAGES:  # compléter avec la même rubrique
        if len(liens) >= 4: break
        if PAGES[s2][0] == rub and s2 != slug and s2 in pages and s2 not in [x[0] for x in liens]:
            liens.append((s2, PAGES[s2][2]))
    lire = "".join(f'<li><a href="{url(s2)}">{E(strip(a)[:1].upper() + strip(a)[1:])}</a></li>' for s2, a in liens[:5])
    sources = "".join(f'<li><a href="{E(x["url"])}" rel="noopener" target="_blank">{E(x.get("titre") or x["url"])}</a></li>'
                      for x in d.get("sources", []) if str(x.get("url", "")).startswith("https://"))
    body = f"""<div class="wrap art">
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="/{RUB_SLUG[rub]}/">{E(rub_t)}</a> › <span>{E(court)}</span></nav>
<header class="ahead">
<h1>{E(strip(d['h1']))}</h1>
<p class="chapo">{inline(d.get('chapo'))}</p>
<ul class="trust"><li>Vérifié le {date_txt}</li><li>{nb_src} sources officielles citées</li><li>Guide indépendant et gratuit</li></ul>
</header>
<figure class="hero-img"><img src="/img/{img}.jpg" srcset="/img/{img}-800.jpg 800w, /img/{img}.jpg 1600w" sizes="(max-width: 900px) 100vw, 860px" width="1600" height="1067" alt="{E(ALT[img])}" fetchpriority="high"></figure>
<div class="cols">
<aside class="side"><div class="bref"><p class="lab">En bref</p><ul>{bref}</ul></div>
<nav class="toc" aria-label="Sommaire"><p class="lab">Sommaire</p><ol>{toc}{'<li><a href="#faq">Questions fréquentes</a></li>' if faq else ''}</ol></nav></aside>
<div class="txt">{urg_html}{corps}{faq_html}{CTA_FIN}
<section class="lire" aria-labelledby="lire"><h2 id="lire">À lire aussi</h2><ul>{lire}</ul></section>
<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources</h2><p>Informations vérifiées le {date_txt}. Les montants évoluent, en général au 1er janvier ou au 1er avril : en cas de doute, la caisse ou le département qui verse l'aide fait foi.</p><ul>{sources}</ul></section>
</div></div></div>"""
    schema = [
        {"@context": "https://schema.org", "@type": "Article", "headline": strip(d["h1"])[:110], "description": d.get("description", ""),
         "image": f"{DOMAIN}/img/{img}.jpg", "datePublished": LANCEMENT, "dateModified": verif, "inLanguage": "fr-FR",
         "author": {"@type": "Organization", "name": SITE, "url": DOMAIN + "/"},
         "publisher": {"@type": "Organization", "name": SITE, "url": DOMAIN + "/", "logo": {"@type": "ImageObject", "url": DOMAIN + "/favicon.svg"}},
         "mainEntityOfPage": DOMAIN + path,
         "citation": [x["url"] for x in d.get("sources", []) if str(x.get("url", "")).startswith("https://")]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": rub_t, "item": f"{DOMAIN}/{RUB_SLUG[rub]}/"},
            {"@type": "ListItem", "position": 3, "name": court, "item": DOMAIN + path}]},
    ]
    if faq:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip(f["q"]), "acceptedAnswer": {"@type": "Answer", "text": strip(f["r"])}} for f in faq]})
    return path, page(d["title"], d["description"], path, body, schema, img, rub, FOOTER)


def rubrique(r, pages, contenus):
    titre, desc, h1, intro = RUB_PAGE[r]
    path = f"/{RUB_SLUG[r]}/"
    items = ""
    for s2 in PAGES:
        if PAGES[s2][0] != r or s2 not in pages: continue
        c = contenus[s2]
        items += (f'<li><a class="card big" href="{url(s2)}"><b>{E(strip(c["h1"]))}</b><span>{inline(c.get("chapo",""))}</span>'
                  f'<i>Lire le guide →</i></a></li>')
    autres = "".join(f'<li><a href="/{RUB_SLUG[x]}/">{E(t)}</a></li>' for x, t, _ in RUBRIQUES if x != r)
    body = f"""<div class="wrap art">
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <span>{E(dict((a, t) for a, t, _ in RUBRIQUES)[r])}</span></nav>
<header class="ahead"><h1>{E(h1)}</h1><p class="chapo">{E(intro)}</p>
<ul class="trust"><li>Montants 2026 vérifiés</li><li>Sources officielles citées</li><li>Indépendant et gratuit</li></ul></header>
<ul class="cards cards1">{items}</ul>
{CTA_FIN}
<section class="lire"><h2>Les autres rubriques</h2><ul>{autres}</ul></section>
</div>"""
    schema = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "description": desc, "url": DOMAIN + path, "inLanguage": "fr-FR",
               "hasPart": [{"@type": "Article", "headline": strip(contenus[s2]["h1"]), "url": DOMAIN + url(s2)} for s2 in PAGES if PAGES[s2][0] == r and s2 in pages]},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Accueil", "item": DOMAIN + "/"},
                  {"@type": "ListItem", "position": 2, "name": h1, "item": DOMAIN + path}]}]
    img = {"aides": "accueil", "domicile": "aide-domicile", "etablissement": "ehpad", "aidants": "aidant"}[r]
    return path, page(titre, desc, path, body, schema, img, r, FOOTER)


def accueil(pages, contenus):
    cartes = ""
    for r, t, sous in RUBRIQUES:
        items = ""
        for s in PAGES:
            if PAGES[s][0] != r or s not in pages: continue
            c = contenus[s]
            items += f'<li><a class="card" href="{url(s)}"><b>{E(PAGES[s][2])}</b><span>{E(court_txt(c.get("description","")))}</span></a></li>'
        cartes += f'<section id="{r}" class="rub" aria-labelledby="h-{r}"><h2 id="h-{r}"><a class="h2l" href="/{RUB_SLUG[r]}/">{E(t)}</a></h2><p class="sous">{E(sous)}</p><ul class="cards">{items}</ul></section>'
    body = f"""<section class="hero"><div class="wrap hgrid">
<div><p class="kicker">Le guide des familles</p>
<h1>Aider ses parents âgés : les aides, les démarches et les bons réflexes</h1>
<p class="lead">APA, aide à domicile, EHPAD, congé de proche aidant… Les aides existent, mais elles sont éparpillées entre l'État, le département, la caisse de retraite et la CAF. Ici, chaque aide est expliquée simplement, avec les montants de 2026 vérifiés sur les sources officielles.</p>
<p class="ctas"><a class="btn" href="/quelles-aides/">Voir les aides de mon parent en 1 minute</a><a class="btn sec" href="/apa/">Tout savoir sur l'APA</a></p>
<ul class="trust"><li>Montants 2026 vérifiés</li><li>Sources officielles citées</li><li>Indépendant et gratuit</li></ul></div>
<figure><img src="/img/accueil.jpg" srcset="/img/accueil-800.jpg 800w, /img/accueil.jpg 1600w" sizes="(max-width: 900px) 100vw, 560px" width="1600" height="1067" alt="{E(ALT['accueil'])}" fetchpriority="high"></figure>
</div></section>
<div class="wrap">
<section class="start" aria-labelledby="h-start"><h2 id="h-start">Par où commencer ?</h2>
<ol class="steps3">
<li><b>Évaluer le besoin</b><span>Le niveau d'autonomie (le GIR) décide de presque tout : <a href="/grille-aggir/">comprendre la grille AGGIR</a>.</span></li>
<li><b>Demander l'aide principale</b><span>Dès le GIR 4, c'est l'APA, versée par le département : <a href="/apa/demande/">monter le dossier</a>.</span></li>
<li><b>Organiser l'aide au quotidien</b><span>Aide à domicile, téléassistance, logement adapté : <a href="/aide-a-domicile/">les solutions et leur prix</a>.</span></li>
</ol></section>
{cartes}
</div>"""
    schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN + "/", "inLanguage": "fr-FR"},
              {"@context": "https://schema.org", "@type": "Organization", "name": SITE, "url": DOMAIN + "/", "logo": DOMAIN + "/favicon.svg"}]
    return page("Aider ses parents âgés : aides, démarches et prix (2026)",
                "APA, aide à domicile, EHPAD, aidants : toutes les aides pour un parent âgé, expliquées simplement avec les montants 2026 vérifiés.",
                "/", body, schema, "accueil", None, FOOTER)


STATIQUES = {
    "a-propos": ("Qui sommes-nous | Aider mes parents", "Pourquoi ce guide existe, comment il est rédigé et vérifié.",
                 "<h1>Qui sommes-nous</h1><p>aidermesparents.fr est né d'un constat simple : quand un parent perd son autonomie, les familles découvrent un maquis d'aides, de dossiers et de délais, répartis entre l'État, le département, la caisse de retraite, la CAF et la mairie. Beaucoup passent à côté d'aides auxquelles leur parent a droit.</p>"
                 "<h2>Comment nous travaillons</h2><ul><li>Chaque montant, plafond et délai est vérifié sur une source officielle, citée en bas de la page.</li><li>Chaque page indique sa date de vérification.</li><li>Nous ne vendons rien aux familles et nous ne sommes rattachés à aucune administration ni caisse.</li><li>Si vous repérez une erreur, écrivez-nous : nous corrigeons sous 48 heures.</li></ul>"
                 "<h2>Contact</h2><p><a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a></p>"),
    "mentions-legales": ("Mentions légales | Aider mes parents", "Mentions légales du site aidermesparents.fr.",
                         "<h1>Mentions légales</h1><h2>Éditeur</h2><p>Louis Lardeux, entrepreneur individuel (micro-entreprise), SIREN 999 443 880, France. Contact : <a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a>.</p>"
                         "<h2>Hébergement</h2><p>GitHub Pages, GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis.</p>"
                         "<h2>Informations</h2><p>Les contenus ont une vocation d'information générale. Ils ne remplacent pas l'avis de l'organisme qui verse l'aide, qui seul fait foi. Les photos d'illustration sont générées et ne représentent pas de personnes réelles.</p>"),
    "confidentialite": ("Confidentialité | Aider mes parents", "Données personnelles et cookies sur aidermesparents.fr.",
                        "<h1>Confidentialité</h1><p>Ce site ne dépose aucun cookie publicitaire et ne vous demande aucune donnée pour être consulté.</p><p>La mesure d'audience, si elle est activée, se fait sans cookie et de façon anonyme.</p><p>Pour toute question : <a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a>.</p>"),
}

CTA_MILIEU = ('<aside class="cta"><div><p class="ctat">Votre parent a peut-être droit à d’autres aides</p>'
              '<p>Répondez à 5 questions et voyez la liste des aides à vérifier pour sa situation. Gratuit, anonyme, 1 minute.</p></div>'
              '<a class="btn" href="/quelles-aides/">Faire le point</a></aside>')
CTA_FIN = ('<aside class="cta fin"><div><p class="ctat">Ne passez pas à côté d’une aide</p>'
           '<p>APA, aide ménagère, crédit d’impôt, aides de la caisse de retraite : les aides se cumulent souvent. Faites le point en 1 minute.</p></div>'
           '<a class="btn" href="/quelles-aides/">Voir les aides de mon parent</a></aside>')
CALC = {"apa": "apa", "aspa": "aspa", "aide-a-domicile": "credit", "ehpad-prix-aides": "ehpad", "conge-proche-aidant": "ajpa"}
URGENCE = {
    "apa": "L'APA n'est due qu'à partir du dépôt du **dossier complet**. Elle ne couvre rien avant : chaque mois d'attente est un mois d'aide perdu.",
    "apa/demande": "Les droits s'ouvrent à la date du **dossier complet**, pas avant. Déposez dès que possible, quitte à compléter ensuite.",
    "grille-aggir": "Dès qu'un GIR 1 à 4 est probable, déposez la demande d'APA : elle n'est due qu'à partir du dossier complet.",
    "aide-sociale-hebergement": "Demandez l'aide sociale dans les **2 mois** qui suivent l'entrée en établissement pour qu'elle couvre les frais depuis l'arrivée.",
    "conge-proche-aidant": "Prévenez votre employeur **1 mois** avant le début du congé (sauf urgence), et faites la demande d'AJPA en parallèle.",
    "ehpad-prix-aides": "La réduction d'impôt de 25 % se déclare chaque printemps sur les frais de l'année précédente : gardez toutes les factures dès maintenant.",
}

QUIZ = open(os.path.join(ROOT, "_build", "quiz.html"), encoding="utf-8").read()
ASSET_V = ""


def main():
    global FOOTER, ASSET_V
    import hashlib
    ASSET_V = hashlib.md5(CSS.encode()).hexdigest()[:8]
    contenus = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "contenu", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("slug") in PAGES:
            contenus[d["slug"]] = d
    pages = set(contenus)
    FOOTER = footer_html(pages)
    for p in glob.glob(os.path.join(OUT, "*")):
        if os.path.basename(p) not in ("img", "CNAME"):
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    def write(path, content):
        fp = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "w", encoding="utf-8").write(content)
    urls = []
    write("/", accueil(pages, contenus)); urls.append(("/", max([c.get("date_verification", LANCEMENT) for c in contenus.values()] or [LANCEMENT])))
    for r, _, _ in RUBRIQUES:
        path, h = rubrique(r, pages, contenus); write(path, h); urls.append((path, max(contenus[x].get("date_verification", LANCEMENT) for x in PAGES if PAGES[x][0] == r and x in contenus)))
    for s in PAGES:
        if s in contenus:
            path, h = article(contenus[s], pages); write(path, h); urls.append((path, contenus[s].get("date_verification", LANCEMENT)))
    write("/quelles-aides/", page("Quelles aides pour mon parent âgé ? Le point en 1 minute",
          "5 questions pour voir les aides à vérifier pour votre parent : APA, ASPA, aide ménagère, crédit d'impôt, MaPrimeAdapt, aides aux aidants.",
          "/quelles-aides/", QUIZ, [{"@context": "https://schema.org", "@type": "WebApplication", "name": "Quelles aides pour mon parent ?", "applicationCategory": "UtilityApplication", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "inLanguage": "fr-FR"}], "accueil", None, FOOTER)); urls.append(("/quelles-aides/", LANCEMENT))
    for s, (t, dsc, b) in STATIQUES.items():
        write(url(s), page(t, dsc, url(s), f'<div class="wrap prose">{b}</div>', [], "accueil", None, FOOTER)); urls.append((url(s), LANCEMENT))
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
        page("Page introuvable | Aider mes parents", "Cette page n'existe pas.", "/404.html", '<div class="wrap prose"><h1>Page introuvable</h1><p><a href="/">Revenir à l\'accueil</a></p></div>', [], "accueil", None, FOOTER).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'))
    open(os.path.join(OUT, "style.css"), "w", encoding="utf-8").write(CSS)
    shutil.copy(os.path.join(ROOT, "_build", "calc.js"), os.path.join(OUT, "calc.js"))
    open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#2f5f8a"/><path d="M32 48s-14-8.5-14-19a8 8 0 0 1 14-5.3A8 8 0 0 1 46 29c0 10.5-14 19-14 19z" fill="#f2b98b"/></svg>')
    open(os.path.join(OUT, "CNAME"), "w").write("aidermesparents.fr\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    sm = "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    llms = [f"# {SITE} (aidermesparents.fr)", "",
            "> Guide indépendant des aides et démarches pour les personnes âgées et leurs enfants aidants en France. Montants 2026 vérifiés sur les sources officielles, citées sur chaque page.", ""]
    for r, t, _ in RUBRIQUES:
        llms += [f"## {t}", ""]
        for s in PAGES:
            if PAGES[s][0] == r and s in contenus:
                c = contenus[s]
                llms.append(f"- [{strip(c['h1'])}]({DOMAIN}{url(s)}): {strip(c.get('chapo',''))}")
        llms.append("")
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\n".join(llms))
    print(len(contenus), "pages de contenu,", len(urls), "URL ->", OUT)


if __name__ == "__main__":
    main()
