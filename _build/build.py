#!/usr/bin/env python3
"""Générateur statique de aidermesparents.fr : contenu/*.json -> docs/ (GitHub Pages)."""
import json, glob, os, re, html, shutil, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import departements as DEP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
DOMAIN = "https://aidermesparents.fr"
SITE = "Aider mes parents"
LANCEMENT = "2026-11-12"
# 19/11/2026 : vente suspendue (audit). 21/11/2026 : rouverte, accès vérifié par le serveur /pay/verifier (VPS).
# Ancien lien : https://buy.stripe.com/14AbIUcRefiy41Faw1cQU00 (Louis désactive lui-même le lien côté Stripe).
# Avant toute réactivation : vérification serveur du paiement (voir l'en-tête de plan.js).
STRIPE_PLAN = "https://buy.stripe.com/14AbIUcRefiy41Faw1cQU00"
# Microsoft Clarity : inactif tant que l'identifiant n'est pas fourni par Louis.
# Mode prévu : sans cookie (consentv2 refusé, réglage « Cookies : off » dans le projet Clarity),
# saisies masquées, jamais chargé sur /mon-plan/, /quelles-aides/ ni /simulateurs/.
CLARITY_ID = None
CLARITY_EXCLU = ("/mon-plan/", "/quelles-aides/", "/simulateurs/", "/404.html")
INDEXNOW = "ec97aa51e6fa335766b8991daee53218"

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
    "aides": ("Aides aux personnes âgées : toutes les aides financières 2026",
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
    "pension-de-reversion": ("aides", "accueil", "Pension de réversion"),
    "allocation-veuvage": ("aides", "accueil", "Allocation veuvage"),
    "pch-apres-60-ans": ("aides", "aidant", "PCH après 60 ans"),
    "apl-ehpad": ("etablissement", "ehpad", "APL en EHPAD"),
    "aide-menagere-caisse-retraite": ("domicile", "aide-domicile", "Aide ménagère de la caisse de retraite"),
    "retour-domicile-apres-hospitalisation": ("domicile", "aide-domicile", "Retour à domicile après l'hôpital"),
    "accueil-familial-personne-agee": ("etablissement", "ehpad", "Accueil familial"),
    "accueil-de-jour-alzheimer": ("etablissement", "ehpad", "Accueil de jour Alzheimer"),
    "parent-ne-peut-plus-vivre-seul": ("aidants", "aidant", "Mon parent ne peut plus vivre seul"),
    "habilitation-familiale": ("aidants", "aidant", "Habilitation familiale"),
    "tutelle-curatelle-parent": ("aidants", "aidant", "Tutelle ou curatelle d'un parent"),
    "mandat-protection-future": ("aidants", "aidant", "Mandat de protection future"),
    "procuration-bancaire-parent": ("aidants", "aidant", "Procuration bancaire"),
    "accueillir-parent-chez-soi": ("aidants", "accueil", "Accueillir un parent chez soi"),
    "parent-victime-arnaque": ("aidants", "aidant", "Mon parent s'est fait arnaquer"),
    "demarchage-abusif-personne-agee": ("aidants", "aidant", "Démarchage abusif d'une personne âgée"),
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
        f'<li><a href="/{RUB_SLUG[r]}/"{cur if actif == r else ""}>{E(t)}</a></li>' for r, t, _ in RUBRIQUES) + '<li><a class="navsim" href="/simulateurs/">Simulateurs</a></li>'
    if STRIPE_PLAN:  # 22/11 : l'offre payante doit se voir partout (retour de Louis : « je n'ai même pas trouvé comment payer »)
        items += f'<li class="navplan-li"><a class="navplan" href="/{VENTE}/"{cur if actif == "vente" else ""}>Mon plan, 7,99 €</a></li>'
    return (f'<header class="top"><div class="wrap bar"><a class="logo" href="/" aria-label="aidermesparents, accueil">'
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


def clarity_tag(path):
    """Balise Clarity, vide tant que CLARITY_ID est None ou sur les pages exclues."""
    if not CLARITY_ID or path in CLARITY_EXCLU:
        return ""
    return ('<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};'
            't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);'
            f'}})(window,document,"clarity","script","{CLARITY_ID}");'
            # pas de consentement envoyé : Clarity fonctionne sans cookie
            'window.clarity("consentv2",{ad_Storage:"denied",analytics_Storage:"denied"});</script>')


VENTE = "plan-d-action"   # page de vente du plan (22/11/2026)
STICKY_EXCLU = ("/plan-d-action/", "/mon-plan/", "/quelles-aides/", "/conditions-de-vente/", "/mentions-legales/", "/confidentialite/", "/404.html")
STICKY_JS = ("<script>(function(){var b=document.getElementById('stk'),K='amp-stk';if(!b)return;var f=0;"
             "try{f=+localStorage.getItem(K)||0}catch(e){}if(Date.now()-f<6048e5)return;"
             "function v(){if(scrollY>500&&innerWidth<=900){b.hidden=false;document.body.classList.add('stk-on');removeEventListener('scroll',v)}}"
             "addEventListener('scroll',v,{passive:true});"
             "b.querySelector('button').addEventListener('click',function(){b.hidden=true;document.body.classList.remove('stk-on');try{localStorage.setItem(K,Date.now())}catch(e){}})})();</script>")


def sticky_html(path):
    """Barre collante mobile (900 px et moins), discrète, fermable (masquée 7 jours), seulement si la vente est active."""
    # 27/11 : désactivée (le contenu d'abord, cf. chute Google du 22/11). Remettre en retirant le return ci-dessous.
    return ""
    if not STRIPE_PLAN or path in STICKY_EXCLU:
        return ""
    return ('<div class="stk" id="stk" hidden><p><b>Le plan d’action</b> pour votre parent, 7,99 €</p>'
            f'<a class="btn warm" href="/{VENTE}/">Voir</a><button type="button" aria-label="Fermer ce bandeau">×</button></div>' + STICKY_JS)


def offre_ctx(titre, texte):
    """Encart d'offre contextuel, court, après l'introduction d'un guide ou d'une page département."""
    if not STRIPE_PLAN:
        return ""
    return (f'<aside class="cta offre-ctx" aria-label="Offre payante"><div><p class="lab">Plan d’action personnalisé, 7,99 €</p><p class="ctat">{E(titre)}</p>'
            f'<p>{E(texte)}</p></div><a class="btn warm" href="/{VENTE}/">Voir le plan</a></aside>')


def offre_fin():
    """Encart de fin de page : l'offre, avec le questionnaire gratuit en alternative."""
    if not STRIPE_PLAN:
        return CTA_FIN
    return ('<aside class="cta fin"><div><p class="ctat">Le plan d’action pour votre parent, 7,99 €</p>'
            '<p>Les aides possibles et leurs montants estimés, l’ordre des démarches, les pièces à réunir et les lettres prêtes. Paiement sécurisé par Stripe, remboursé sous 14 jours sur simple demande.</p>'
            '<p class="aide">Ou faites d’abord le point gratuitement : <a href="/quelles-aides/">les aides de votre parent en 1 minute</a>.</p></div>'
            f'<a class="btn" href="/{VENTE}/">Préparer mon plan</a></aside>')


OFFRE_RUB = {
    "aides": ("Combien votre parent peut-il toucher ?", "Le plan d’action estime chaque aide avec les barèmes 2026, puis donne l’ordre des démarches, les pièces à réunir et les lettres prêtes."),
    "domicile": ("Organiser l’aide à domicile sans rien oublier", "Le plan d’action liste les aides possibles pour votre parent (APA, crédit d’impôt, MaPrimeAdapt), les pièces à réunir et un calendrier daté."),
    "etablissement": ("EHPAD : savoir quoi demander, et avant quand", "Le plan d’action liste les aides possibles (APA, aide sociale, réduction d’impôt), les dates limites et les pièces à réunir pour votre parent."),
    "aidants": ("Gagnez du temps sur les démarches de votre parent", "Le plan d’action réunit les aides possibles, l’ordre des démarches, les pièces et les lettres prêtes, dont la demande de congé de proche aidant."),
}
OFFRE_SLUG = {
    "apa": ("Préparez la demande d’APA sans rien oublier", "Le plan d’action estime l’APA de votre parent selon ses ressources, liste les pièces du dossier et donne les lettres de recours et de révision."),
    "apa/demande": ("Un dossier d’APA complet du premier coup", "Le plan d’action liste les pièces à joindre, date chaque étape et donne les lettres de recours et de révision, avec l’APA estimée pour votre parent."),
    "grille-aggir": ("Le GIR est probable ? Passez à la demande", "Le plan d’action estime l’APA selon le GIR et les ressources de votre parent, et donne l’ordre des démarches et les pièces à réunir."),
}


def page(title, desc, path, body, schema, image="accueil", actif=None, foot=""):
    canon = DOMAIN + path
    og_img = f"{DOMAIN}/img/{image}.jpg"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="msvalidate.01" content="AF248781106582FE1BFC28DA6DBB0B45">
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
<script data-goatcounter="https://aidermesparents.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
{clarity_tag(path)}
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
{nav_html(actif)}
<main id="contenu">
{body}
</main>
{foot}
{sticky_html(path)}
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
    parts = [f'<section aria-labelledby="{a}"><h2 id="{a}">{E(strip(s["h2"]))}</h2>' + "".join(bloc_html(b) for b in s.get("blocs", [])) + "</section>"
             for s, a in zip(secs, ids)]
    nb_src = len([x for x in d.get("sources", []) if str(x.get("url", "")).startswith("https://")])
    apres = {}
    if slug in CALC and parts:  # calculateur après la 1re section
        apres.setdefault(0, []).append(f'<div class="calc" data-clarity-mask="True" data-calc="{CALC[slug]}"><noscript>Activez JavaScript pour utiliser le calculateur.</noscript></div>')
    if False and len(parts) >= 2:  # 27/11 : retiré, l'offre reste en fin de page (offre_fin) ; avant : encart après l'introduction
        t_o, x_o = OFFRE_SLUG.get(slug) or OFFRE_RUB[rub]
        apres.setdefault(1 if slug in CALC and len(parts) >= 3 else 0, []).append(offre_ctx(t_o, x_o))
    corps = "".join(x + "".join(apres.get(i, [])) for i, x in enumerate(parts))
    if slug in ("apa", "apa/demande", "ehpad-prix-aides"):
        corps = '<p class="dep-lien">Votre parent vit dans un département précis ? <a href="/apa/departements/">Contacts et prix des EHPAD, département par département →</a></p>' + corps
    if slug in ("apa", "apa/demande", "ehpad-prix-aides", "aide-sociale-hebergement"):  # maillage vers les pages départementales
        corps += ('<details class="deps-liste"><summary>Choisir le département de votre parent (contacts APA et prix des EHPAD)</summary><ul class="deps">'
                  + "".join(f'<li><a href="/apa/{x["slug"]}/"><span class="num">{E(x["code"])}</span> {E(x["nom"])}</a></li>' for x in DEP.DEPS) + "</ul></details>")
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
<div class="byline"><img src="/img/louis-lardeux-128.jpg" width="40" height="40" alt="Photo de Louis Lardeux" loading="lazy"><span>Par <a href="/a-propos/">Louis Lardeux</a>, fondateur du site</span></div>
<ul class="trust"><li>Vérifié le {date_txt}</li><li>{nb_src} sources officielles citées</li><li>Guide indépendant et gratuit</li></ul>
</header>
<figure class="hero-img"><img src="/img/{img}.jpg" srcset="/img/{img}-800.jpg 800w, /img/{img}.jpg 1600w" sizes="(max-width: 900px) 100vw, 860px" width="1600" height="1067" alt="{E(ALT[img])}" fetchpriority="high"></figure>
<div class="cols">
<aside class="side"><div class="bref"><p class="lab">En bref</p><ul>{bref}</ul></div>
<nav class="toc" aria-label="Sommaire"><p class="lab">Sommaire</p><ol>{toc}{'<li><a href="#faq">Questions fréquentes</a></li>' if faq else ''}</ol></nav></aside>
<div class="txt">{urg_html}{corps}{faq_html}{offre_fin()}
<section class="lire" aria-labelledby="lire"><h2 id="lire">À lire aussi</h2><ul>{lire}</ul></section>
<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources</h2><p>Informations vérifiées le {date_txt}. Les montants évoluent, en général au 1er janvier ou au 1er avril : en cas de doute, la caisse ou le département qui verse l'aide fait foi.</p><ul>{sources}</ul></section>
</div></div></div>"""
    schema = [
        {"@context": "https://schema.org", "@type": "Article", "headline": strip(d["h1"])[:110], "description": d.get("description", ""),
         "image": f"{DOMAIN}/img/{img}.jpg", "datePublished": min(LANCEMENT, verif), "dateModified": verif, "inLanguage": "fr-FR",
         "author": {"@type": "Person", "name": "Louis Lardeux", "url": DOMAIN + "/a-propos/", "image": DOMAIN + "/img/louis-lardeux.jpg", "sameAs": ["https://www.linkedin.com/in/louis-lardeux-96b600254/"]},
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
{offre_fin()}
<section class="lire"><h2>Les autres rubriques</h2><ul>{autres}</ul></section>
</div>"""
    schema = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "description": desc, "url": DOMAIN + path, "inLanguage": "fr-FR",
               "hasPart": [{"@type": "Article", "headline": strip(contenus[s2]["h1"]), "url": DOMAIN + url(s2)} for s2 in PAGES if PAGES[s2][0] == r and s2 in pages]},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Accueil", "item": DOMAIN + "/"},
                  {"@type": "ListItem", "position": 2, "name": h1, "item": DOMAIN + path}]}]
    img = {"aides": "accueil", "domicile": "aide-domicile", "etablissement": "ehpad", "aidants": "aidant"}[r]
    return path, page(titre, desc, path, body, schema, img, r, FOOTER)


def offre_dep(p):
    """Corps de la page département, avec l'encart d'offre après le premier bloc (contact du service APA)."""
    b = p["body"]
    return b  # 27/11 : plus d'encart au milieu, l'offre reste en fin de page
    o = offre_ctx(f"Votre parent vit {DEP.article_dep(p['nom'])} ?",
                  "Le plan d’action estime son APA selon ses ressources, donne l’ordre des démarches, les pièces à réunir et les lettres prêtes.")
    i = b.find("</section>")
    return b[:i + 10] + o + b[i + 10:] if i >= 0 else b + o


def page_departement(d):
    p = DEP.page_dep(d)
    maj_html = f'<p class="maj">Page mise à jour le {dt.date.fromisoformat(p["maj"]).strftime("%d/%m/%Y")}</p>' if p.get("maj") else ""
    body = f"""<div class="wrap art">
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="/apa/">APA</a> › <a href="/apa/departements/">Par département</a> › <span>{E(p['nom'])}</span></nav>
<header class="ahead"><h1>{E(p['h1'])}</h1><p class="chapo">{E(p['chapo'])}</p>
<ul class="trust"><li>Contacts de l'annuaire officiel</li><li>Prix déclarés à la CNSA</li><li>Site indépendant, ce n'est pas le site du département</li></ul>{maj_html}</header>
<div class="txt">{offre_dep(p)}{offre_fin()}
<section class="lire"><h2>À lire aussi</h2><ul><li><a href="/apa/">APA : montant et conditions</a></li><li><a href="/apa/demande/">Faire la demande d'APA</a></li><li><a href="/ehpad-prix-aides/">Prix d'un EHPAD et aides</a></li><li><a href="/apa/departements/">L'APA dans les autres départements</a></li></ul></section></div></div>"""
    schema = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Accueil", "item": DOMAIN + "/"},
                {"@type": "ListItem", "position": 2, "name": "APA", "item": DOMAIN + "/apa/"},
                {"@type": "ListItem", "position": 3, "name": "Par département", "item": DOMAIN + "/apa/departements/"},
                {"@type": "ListItem", "position": 4, "name": p["nom"], "item": DOMAIN + p["path"]}]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in p["faq"]]}]
    if p.get("maj"):
        schema.append({"@context": "https://schema.org", "@type": "WebPage", "name": p["h1"], "url": DOMAIN + p["path"], "inLanguage": "fr-FR",
                       "datePublished": LANCEMENT, "dateModified": p["maj"]})
    h = page(p["title"], p["desc"], p["path"], body, schema, "aidant", "aides", FOOTER)
    if not d.get("ehpad"):  # pas assez de données propres : on ne demande pas l'indexation
        h = h.replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')
    return p["path"], h


def hub_departements():
    # 23/11/2026 : « apa contact téléphone », « apa téléphone », « apa adresse » (Search Console, position 6 à 10, 0 clic) : la page devient l'annuaire des numéros vérifiés.
    rows, n_tel = [], 0
    for d in DEP.DEPS:
        C = DEP.contact_apa(d)
        tel = C.get("tel")
        if tel:
            n_tel += 1
            t = f'<a href="tel:{E(tel.replace(" ", ""))}">{E(tel)}</a>' + (" <small>(standard)</small>" if C.get("tel_lib") == "standard" else "")
        else:
            t = "<small>non confirmé, voir la page</small>"
        rows.append(f'<tr><td><a href="/apa/{d["slug"]}/"><b>{E(d["code"])}</b> {E(d["nom"])}</a></td><td>{t}</td></tr>')
    items = "".join(f'<li><a href="/apa/{d["slug"]}/"><span class="num">{E(d["code"])}</span> {E(d["nom"])}</a></li>' for d in DEP.DEPS)
    maj = DEP._date_fr(DEP.MAJ_CONTACT)
    body = f"""<div class="wrap art"><nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="/apa/">APA</a> › <span>Par département</span></nav>
<header class="ahead"><h1>APA : le téléphone du service dans chaque département</h1><p class="chapo">L'APA se demande au conseil départemental du lieu où vit votre parent (<a href="https://www.service-public.gouv.fr/particuliers/vosdroits/F10009" rel="noopener" target="_blank">service-public.gouv.fr, fiche F10009</a>). Voici le numéro du service APA de {n_tel} départements, vérifié sur le site officiel de chaque département (relevés des 19 et 22 novembre 2026). Cliquez sur un département pour l'adresse, les démarches et les prix des EHPAD.</p></header>
<div class="tw"><table><thead><tr><th scope="col">Département</th><th scope="col">Téléphone du service APA</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="src">Sources : sites officiels des départements et annuaire pour-les-personnes-agees.gouv.fr, consultés le {maj}. Quand nous n'avons pas pu confirmer le numéro sur le site du département, la page du département renvoie vers sa page officielle. Ce site n'est pas celui des départements.</p>
<h2>Tous les départements</h2>
<ul class="deps">{items}</ul>{offre_fin()}</div>"""
    path = "/apa/departements/"
    return path, page("APA : contact et téléphone du service par département", f"Le numéro du service APA de {n_tel} départements, vérifié sur leur site officiel en novembre 2026, avec l'adresse, les démarches et les prix des EHPAD.", path, body,
                      [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "APA : contact et téléphone par département", "url": DOMAIN + path}], "aidant", "aides", FOOTER)


def hero_offre():
    """Bloc offre en haut de l'accueil, au-dessus de la ligne de flottaison (22/11/2026)."""
    if not STRIPE_PLAN:
        return ""
    return (f'<div class="hoffre"><p class="lab">Plan d’action personnalisé</p>'
            '<p class="ho-t">Le plan d’aide complet pour votre parent, prêt en quelques minutes</p>'
            '<ul><li>Les aides possibles et leur <b>montant estimé</b>, avec les barèmes 2026</li>'
            '<li><b>L’ordre des démarches</b>, avec un calendrier et les dates limites</li>'
            '<li><b>Les pièces à réunir</b> et les <b>lettres prêtes</b> à envoyer</li></ul>'
            f'<div class="ho-pay"><p class="ho-prix">7,99 €<small>paiement unique</small></p><a class="btn warm big" href="/{VENTE}/">Préparer mon plan</a></div>'
            '<p class="ho-sur">Paiement sécurisé par Stripe · accès immédiat, à enregistrer en PDF · remboursé sous 14 jours sur simple demande</p></div>')


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
<p class="lead">APA, aide à domicile, EHPAD, congé de proche aidant : chaque aide expliquée simplement, avec les montants 2026 vérifiés sur les sources officielles.</p>
<p class="ctas"><a class="btn" href="/quelles-aides/">Voir les aides de mon parent en 1 minute (gratuit)</a><a class="btn sec" href="/apa/">Tout savoir sur l'APA</a></p>
<ul class="trust"><li>Montants 2026 vérifiés</li><li>Sources officielles citées</li><li>Indépendant et gratuit</li></ul></div>
<figure><img src="/img/accueil.jpg" srcset="/img/accueil-800.jpg 800w, /img/accueil.jpg 1600w" sizes="(max-width: 900px) 100vw, 560px" width="1600" height="1067" alt="{E(ALT['accueil'])}" fetchpriority="high"></figure>
</div></section>
<div class="wrap">
<section class="start" aria-labelledby="h-start"><h2 id="h-start">Par où commencer ?</h2>
<p class="dep-lien">Contacts et prix des EHPAD près de chez votre parent : <a href="/apa/departements/">choisir son département →</a></p>
<ol class="steps3">
<li><b>Évaluer le besoin</b><span>Le niveau d'autonomie (le GIR) décide de presque tout : <a href="/grille-aggir/">comprendre la grille AGGIR</a>.</span></li>
<li><b>Demander l'aide principale</b><span>Dès le GIR 4, c'est l'APA, versée par le département : <a href="/apa/demande/">monter le dossier</a>.</span></li>
<li><b>Organiser l'aide au quotidien</b><span>Aide à domicile, téléassistance, logement adapté : <a href="/aide-a-domicile/">les solutions et leur prix</a>.</span></li>
</ol></section>
{hero_offre()}
{cartes}
</div>"""
    schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN + "/", "inLanguage": "fr-FR"},
              {"@context": "https://schema.org", "@type": "Organization", "name": SITE, "url": DOMAIN + "/", "logo": DOMAIN + "/favicon.svg"}]
    return page("Aider ses parents âgés : aides, démarches et prix (2026)",
                "APA, aide à domicile, EHPAD, aidants : toutes les aides pour un parent âgé, expliquées simplement avec les montants 2026 vérifiés.",
                "/", body, schema, "accueil", None, FOOTER)


STATIQUES = {
    "a-propos": ("Qui sommes-nous | Aider mes parents", "Qui écrit ce guide, comment chaque information est vérifiée, et comment le site est financé.",
                 "<h1>Qui sommes-nous</h1><div class='auteur'><img class='ava' src='/img/louis-lardeux.jpg' width='88' height='88' alt='Photo de Louis Lardeux'><div><b>Louis Lardeux</b><span>Fondateur et éditeur de aidermesparents.fr</span><a href='https://www.linkedin.com/in/louis-lardeux-96b600254/' rel='noopener me' target='_blank'>Mon profil LinkedIn</a></div></div>"
                 "<p>aidermesparents.fr est né d'un constat simple : quand un parent perd son autonomie, les familles découvrent un maquis d'aides, de dossiers et de délais, répartis entre l'État, le département, la caisse de retraite, la CAF et la mairie. Beaucoup passent à côté d'aides auxquelles leur parent a droit, faute de savoir qu'elles existent.</p>"
                 "<p>Je ne suis ni travailleur social, ni avocat, ni notaire. Mon travail consiste à rassembler les règles officielles, à les vérifier une par une et à les expliquer simplement. Quand une situation demande un professionnel (juge, notaire, médecin, assistante sociale), la page le dit.</p>"
                 "<h2>Comment chaque page est vérifiée</h2><ul><li><b>Uniquement des sources officielles</b> pour les montants, plafonds et délais : service-public.gouv.fr, pour-les-personnes-agees.gouv.fr, CNSA, Assurance retraite, CAF, Anah, Légifrance. Elles sont citées en bas de chaque page.</li><li><b>Une date de vérification</b> sur chaque page, mise à jour quand les montants changent (en général au 1er janvier et au 1er avril).</li><li><b>Les calculateurs</b> reprennent les barèmes officiels, et nous refaisons les calculs à la main sur des cas types avant de les publier.</li><li><b>Les données par département</b> viennent de l'annuaire officiel de l'administration et des prix déclarés par les EHPAD à la CNSA.</li></ul>"
                 "<h2>Comment le site est financé</h2><p>Les guides, les questionnaires et les calculateurs sont gratuits. Les démarches elles-mêmes restent gratuites auprès des organismes. Un plan d'action personnalisé payant (7,99 €) est proposé à ceux qui veulent gagner du temps : il reprend les règles des guides gratuits et les applique à la situation de votre parent (montants, ordre des démarches, pièces, lettres). À l'avenir, certaines pages pourront présenter des services partenaires : ils seront toujours signalés comme tels, et ils ne changent jamais le contenu des guides.</p>"
                 "<h2>Une erreur ? Écrivez-nous</h2><p>Si une information vous semble fausse ou dépassée, écrivez à <a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a> : nous vérifions et corrigeons sous 48 heures.</p>"),
    "mentions-legales": ("Mentions légales | Aider mes parents", "Mentions légales du site aidermesparents.fr.",
                         "<h1>Mentions légales</h1><h2>Éditeur</h2><p>Louis Lardeux, entrepreneur individuel (micro-entreprise), SIREN 999 443 880, 63 rue Dostoïevski, A 307, 06560 Valbonne Sophia Antipolis. Contact : <a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a>, téléphone : 07 56 80 68 54.</p>"
                         "<h2>Directeur de la publication</h2><p>Louis Lardeux.</p>"
                         "<h2>Hébergement</h2><p>GitHub Pages, GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis.<!-- À COMPLÉTER : téléphone de l'hébergeur --></p>"
                         "<h2>Informations</h2><p>Les contenus ont une vocation d'information générale. Ils ne remplacent pas l'avis de l'organisme qui verse l'aide, qui seul fait foi. Les photos d'illustration sont générées et ne représentent pas de personnes réelles.</p>"),
    "conditions-de-vente": ("Conditions de vente | Aider mes parents", "Conditions de vente du plan d'action personnalisé.",
                            "<h1>Conditions de vente</h1><h2>Le service</h2><p>Le plan d'action personnalisé est un document numérique généré dans votre navigateur à partir de vos réponses : aides possibles et montants estimés selon les barèmes 2026, ordre des démarches, pièces à fournir, calendrier et modèles de lettres. Il ne constitue pas un conseil juridique. Les démarches auprès des organismes (département, caisses de retraite, CAF, Anah) sont gratuites ; seul l'organisme qui verse une aide décide de son attribution et de son montant.</p>"
                            "<h2>Prix et paiement</h2><p>7,99 € TTC, paiement unique sans abonnement, par carte via Stripe. TVA non applicable, article 293 B du CGI.</p>"
                            "<h2>Accès et droit de rétractation</h2><p>Le plan est accessible immédiatement après le paiement, sur l'appareil utilisé. En cochant la case prévue avant le paiement, vous demandez cet accès immédiat et reconnaissez perdre votre droit de rétractation une fois le plan affiché (article L221-28 du code de la consommation).</p>"
                            "<h2>Remboursement</h2><p>Si le plan ne vous convient pas, écrivez-nous dans les 14 jours suivant l'achat à <a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a> : nous vous remboursons, sans justification.</p>"
                            "<h2>Vendeur</h2><p>Louis Lardeux, entrepreneur individuel, SIREN 999 443 880, 63 rue Dostoïevski, A 307, 06560 Valbonne Sophia Antipolis, contact@aidermesparents.fr, téléphone : 07 56 80 68 54. Médiation de la consommation : en cas de litige non résolu, vous pouvez recourir gratuitement à un médiateur de la consommation.<!-- À COMPLÉTER (Louis) : nom, site et adresse du médiateur --></p>"),
    "confidentialite": ("Confidentialité | Aider mes parents", "Données personnelles et cookies sur aidermesparents.fr.",
                        "<h1>Confidentialité</h1><p>Ce site ne dépose aucun cookie publicitaire et ne vous demande aucune donnée pour être consulté.</p><p>La mesure d'audience est faite avec GoatCounter, sans cookie et de façon anonyme : nous comptons les pages vues et l'usage des calculateurs, sans vous identifier.</p><p>Les réponses aux questionnaires et aux calculateurs restent dans votre navigateur : elles ne nous sont pas envoyées.</p><p>Pour toute question : <a href=\"mailto:contact@aidermesparents.fr\">contact@aidermesparents.fr</a>.</p>"),
}

STATIQUES_MAJ = {"mentions-legales": "2026-11-19", "a-propos": "2026-11-19"}

CTA_MILIEU = ('<aside class="cta"><div><p class="ctat">Votre parent a peut-être droit à d’autres aides</p>'
              '<p>Répondez à 5 questions et voyez la liste des aides à vérifier pour sa situation. Gratuit, anonyme, 1 minute.</p></div>'
              '<a class="btn" href="/quelles-aides/">Faire le point</a></aside>')
CTA_FIN = ('<aside class="cta fin"><div><p class="ctat">Ne passez pas à côté d’une aide</p>'
           '<p>APA, aide ménagère, crédit d’impôt, aides de la caisse de retraite : les aides se cumulent souvent. Faites le point en 1 minute.</p></div>'
           '<a class="btn" href="/quelles-aides/">Voir les aides de mon parent</a></aside>')
CALC = {"apa": "apa", "aspa": "aspa", "aide-a-domicile": "credit", "ehpad-prix-aides": "ehpad", "conge-proche-aidant": "ajpa", "mutuelle-senior": "c2s", "maprimeadapt": "mpa", "aide-sociale-hebergement": "apaetab"}
URGENCE = {
    "apa": "À domicile, les droits à l'APA s'ouvrent à la **notification de la décision**, rendue au plus tard 2 mois après le dossier complet. Rien n'est versé pour la période d'avant : déposez le dossier sans attendre.",
    "apa/demande": "Le département a **2 mois** après le dossier complet pour décider, et à domicile l'APA n'est versée qu'à partir de sa décision. Déposez le dossier dès que possible. En cas d'urgence, demandez l'APA forfaitaire de 1 040,17 € (2026).",
    "grille-aggir": "Dès qu'un GIR 1 à 4 est probable, déposez la demande d'APA : à domicile, elle n'est versée qu'à partir de la décision du département.",
    "aide-sociale-hebergement": "Demandez l'aide sociale dans les **2 mois** qui suivent l'entrée en établissement pour qu'elle couvre les frais depuis l'arrivée.",
    "conge-proche-aidant": "Prévenez votre employeur **1 mois** avant le début du congé (sauf urgence), et faites la demande d'AJPA en parallèle.",
    "ehpad-prix-aides": "La réduction d'impôt de 25 % se déclare chaque printemps sur les frais de l'année précédente : gardez toutes les factures dès maintenant.",
}


VENTE_FAQ = [
    ("Les démarches sont-elles payantes ?", "Non. Les demandes d'APA, d'aide sociale, d'ASPA ou de MaPrimeAdapt sont gratuites auprès des organismes. Le plan est un service privé qui vous fait gagner du temps : il applique les règles officielles à la situation de votre parent."),
    ("Que se passe-t-il après le paiement ?", "Vous revenez sur le site. Si vous avez déjà répondu au questionnaire sur cet appareil, il reste 4 précisions à donner (département, ressources exactes, logement, prénom facultatif) et le plan s'affiche. Sinon, vous répondez d'abord aux 5 questions du questionnaire, en 1 minute."),
    ("Comment je garde mon plan ?", "Il reste disponible sur l'appareil utilisé pour l'achat. Un bouton permet de l'enregistrer en PDF ou de l'imprimer. Stripe vous envoie aussi un reçu par e-mail."),
    ("Les montants sont-ils garantis ?", "Non. Ce sont des estimations faites avec les barèmes officiels de 2026 (CNSA, service-public.gouv.fr). C'est l'organisme qui verse chaque aide qui décide de son attribution et de son montant."),
    ("Mes réponses sont-elles envoyées quelque part ?", "Non. Le plan est calculé dans votre navigateur : vos réponses ne nous sont pas envoyées. Le paiement est traité par Stripe, nous ne voyons pas votre numéro de carte."),
    ("Et si le plan ne me convient pas ?", "Écrivez à contact@aidermesparents.fr dans les 14 jours suivant l'achat : nous vous remboursons, sans justification."),
]
VENTE_RENONCE = ("Je demande l’accès immédiat à mon plan et renonce à mon droit de rétractation une fois le plan affiché "
                 "(art. L221-28 du code de la consommation). Le remboursement sous 14 jours reste valable.")


def form_paiement(n):
    return (f'<form class="vform" action="{E(STRIPE_PLAN)}" method="get" data-href="{E(STRIPE_PLAN)}">'
            f'<label class="chk vchk" for="vr{n}"><input type="checkbox" id="vr{n}" required><span>{E(VENTE_RENONCE)} <a href="/conditions-de-vente/">Conditions de vente</a>.</span></label>'
            f'<p class="vmsg" role="alert" hidden>Cochez la case ci-dessus pour continuer vers le paiement.</p>'
            '<button class="btn warm big vpay" type="submit">Payer 7,99 € et recevoir mon plan</button></form>'
            '<p class="ho-sur">Paiement sécurisé par Stripe · accès immédiat · remboursé sous 14 jours sur simple demande</p>')


VENTE_JS = """<script>(function(){
var q=null;try{q=JSON.parse(localStorage.getItem('amp-quiz')||'null')}catch(e){}
var st=document.getElementById('vstate');if(st&&q)st.textContent='Vos réponses au questionnaire sont gardées sur cet appareil : votre plan s’affichera juste après le paiement.';
document.querySelectorAll('.vform').forEach(function(f){var c=f.querySelector('input[type=checkbox]'),m=f.querySelector('.vmsg');
c.addEventListener('change',function(){f.classList.toggle('ok',c.checked);if(c.checked){m.hidden=true;c.parentNode.classList.remove('flash')}});
c.addEventListener('invalid',function(e){e.preventDefault();m.hidden=false;c.parentNode.classList.add('flash');c.focus()});
f.addEventListener('submit',function(e){e.preventDefault();if(!c.checked){c.dispatchEvent(new Event('invalid'));return}
if(window.goatcounter){try{goatcounter.count({path:'clic-paiement-plan-vente',event:true})}catch(x){}}location.href=f.getAttribute('data-href')})});
})();</script>"""


def page_vente():
    """Page de vente du plan d'action : titre, pour qui, contenu, aperçu, prix, paiement, FAQ, réassurance."""
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(r)}</p></details>" for q, r in VENTE_FAQ)
    body = f"""<div class="wrap vente">
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <span>Le plan d’action</span></nav>
<div class="vtop">
<h1>Le plan d’action pour votre parent : aides, démarches et lettres prêtes</h1>
<div class="vbox" id="prix"><p class="ho-prix">7,99 €<small>TTC, paiement unique, sans abonnement</small></p>
{form_paiement(1)}
<p class="aide" id="vstate">Après le paiement : 5 questions rapides, puis 4 précisions, et votre plan s’affiche.</p></div>
<p class="chapo">Vous répondez à quelques questions, et vous obtenez la liste des aides de votre parent avec leur montant estimé, l’ordre des démarches, les pièces à réunir et les lettres prêtes.</p>
</div>
<section aria-labelledby="v-pour"><h2 id="v-pour">Pour qui ?</h2>
<ul class="vlist"><li>Votre parent commence à avoir besoin d’aide et vous ne savez pas par où commencer.</li>
<li>Vous voulez savoir à combien d’APA, d’ASPA ou d’aide au logement il peut prétendre.</li>
<li>Votre parent entre en EHPAD et vous devez trouver comment payer.</li>
<li>Vous êtes salarié et vous voulez prendre un congé de proche aidant.</li></ul></section>
<section aria-labelledby="v-recu"><h2 id="v-recu">Ce que vous recevez</h2>
<ol class="etapes"><li><b>Les aides possibles et leur montant estimé</b>, calculés avec les barèmes officiels de 2026 : APA selon les ressources exactes de votre parent, ASPA, crédit d’impôt, MaPrimeAdapt, aide sociale en EHPAD, AJPA.</li>
<li><b>Un calendrier daté</b> : quoi faire cette semaine, dans les 2 mois, et au printemps pour les impôts.</li>
<li><b>Pour chaque aide</b> : où envoyer la demande, la liste des pièces à réunir et les délais de réponse.</li>
<li><b>Les lettres prêtes</b> à compléter : recours et révision de l’APA, demande de congé de proche aidant.</li>
<li><b>Les contacts utiles</b> du département de votre parent, et un bouton pour enregistrer le plan en PDF.</li></ol></section>
<section aria-labelledby="v-apercu"><h2 id="v-apercu">Aperçu d’un plan</h2>
<p>Exemple fictif : Monique, 82 ans, vit seule chez elle, a besoin d’aide pour la toilette, 1 400 € de retraite par mois.</p>
<div class="vapercu" aria-label="Extrait d’un plan d’action, exemple fictif"><p class="lab">Extrait du plan</p>
<p class="ho-t">Le plan d’action pour Monique</p>
<div class="plan-total"><p class="lab">Aides financières estimées</p><p class="big">Jusqu’à 1 094 € <small>par mois</small></p><p>Ce sont des maximums : l’APA réelle dépend du plan d’aide décidé après la visite.</p></div>
<ol class="etapes"><li><b>D’ici 7 jours</b> : déposez le dossier APA (cerfa n°16301). Plus tôt il part, plus tôt la décision arrive.</li>
<li><b>Dès maintenant</b> : rassemblez les pièces de chaque aide dans une même pochette.</li></ol>
<div class="plan-aide"><p class="ho-t">1. APA à domicile</p><p class="m">Jusqu’à 713 € par mois en GIR 4, ou 1 094 € en GIR 3</p><p><b>Pièces à rassembler :</b> pièce d’identité, dernier avis d’imposition, RIB, avis de taxe foncière.</p></div>
<p class="aide">Suivent les autres aides (crédit d’impôt, MaPrimeAdapt, Sortir Plus, téléassistance), les lettres et les contacts.</p></div></section>
<section aria-labelledby="v-prix"><h2 id="v-prix">Recevoir le plan</h2>
<div class="vbox vbox2"><p class="ho-prix">7,99 €<small>TTC, paiement unique</small></p>{form_paiement(2)}
<p class="aide">Pas encore décidé ? <a href="/quelles-aides/">Faites d’abord le point gratuitement en 1 minute</a>.</p></div></section>
<section aria-labelledby="v-faq"><h2 id="v-faq">Questions fréquentes</h2>{faq}</section>
<section aria-labelledby="v-conf"><h2 id="v-conf">Pourquoi nous faire confiance</h2>
<ul class="vlist"><li>Les règles viennent uniquement des <b>sources officielles</b> (service-public.gouv.fr, pour-les-personnes-agees.gouv.fr, CNSA), citées sur chaque guide du site.</li>
<li>Les barèmes sont ceux de <b>2026</b>, mis à jour quand ils changent.</li>
<li>Le site est <b>indépendant</b> : il n’est rattaché à aucune administration, caisse ou entreprise. <a href="/a-propos/">Qui écrit ce site</a>.</li>
<li>Une question ? <a href="mailto:contact@aidermesparents.fr">contact@aidermesparents.fr</a>.</li></ul></section>
</div>{VENTE_JS}"""
    path = f"/{VENTE}/"
    schema = [{"@context": "https://schema.org", "@type": "Product", "name": "Plan d'action pour votre parent",
               "description": "Plan d'action personnalisé : aides possibles et montants estimés avec les barèmes 2026, ordre des démarches, pièces à réunir et lettres prêtes.",
               "brand": {"@type": "Brand", "name": SITE},
               "offers": {"@type": "Offer", "price": "7.99", "priceCurrency": "EUR", "availability": "https://schema.org/InStock", "url": DOMAIN + path}},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in VENTE_FAQ]},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Accueil", "item": DOMAIN + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Le plan d'action", "item": DOMAIN + path}]}]
    return path, page("Plan d'action pour votre parent âgé : aides et démarches",
                      "Les aides de votre parent et leur montant estimé, l'ordre des démarches, les pièces et les lettres prêtes. 7,99 €, remboursé sous 14 jours.",
                      path, body, schema, "accueil", "vente", FOOTER)


QUIZ = open(os.path.join(ROOT, "_build", "quiz.html"), encoding="utf-8").read()


def quiz_html():
    """Questionnaire : l'encart d'achat (entre /*OFFRE*/ et /*FINOFFRE*/) n'est gardé que si la vente est active."""
    if STRIPE_PLAN:
        return QUIZ.replace("/*OFFRE*/", "").replace("/*FINOFFRE*/", "").replace("@@STRIPE@@", STRIPE_PLAN)
    q = re.sub(r"/\*OFFRE\*/.*?/\*FINOFFRE\*/", "", QUIZ, flags=re.S)
    assert "7,99" not in q and "@@STRIPE@@" not in q
    return q
PLAN = open(os.path.join(ROOT, "_build", "plan.html"), encoding="utf-8").read()
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
    path, h = hub_departements(); write(path, h); urls.append((path, LANCEMENT))
    for d in DEP.DEPS:
        path, h = page_departement(d); write(path, h)
        if d.get("ehpad"): urls.append((path, DEP.page_dep(d).get("maj") or LANCEMENT))
    for s in PAGES:
        if s in contenus:
            path, h = article(contenus[s], pages); write(path, h); urls.append((path, contenus[s].get("date_verification", LANCEMENT)))
    write("/quelles-aides/", page("Quelles aides pour mon parent âgé ? Le point en 1 minute",
          "5 questions pour voir les aides à vérifier pour votre parent : APA, ASPA, aide ménagère, crédit d'impôt, MaPrimeAdapt, aides aux aidants.",
          "/quelles-aides/", quiz_html(), [{"@context": "https://schema.org", "@type": "WebApplication", "name": "Quelles aides pour mon parent ?", "applicationCategory": "UtilityApplication", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "inLanguage": "fr-FR"}], "accueil", None, FOOTER)); urls.append(("/quelles-aides/", LANCEMENT))
    if STRIPE_PLAN:
        path, h = page_vente(); write(path, h); urls.append((path, "2026-11-22"))
    write("/mon-plan/", page("Votre plan d'action | Aider mes parents", "Votre plan d'action personnalisé pour les aides de votre parent.", "/mon-plan/", PLAN, [], "accueil", None, FOOTER).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'))
    sims = [("apa", "/apa/"), ("aspa", "/aspa/"), ("credit", "/aide-a-domicile/"), ("ehpad", "/ehpad-prix-aides/"), ("apaetab", "/aide-sociale-hebergement/"), ("mpa", "/maprimeadapt/"), ("c2s", "/mutuelle-senior/"), ("ajpa", "/conge-proche-aidant/")]
    sim_body = ('<div class="wrap prose"><nav class="crumbs" aria-label="Fil d\'Ariane"><a href="/">Accueil</a> › <span>Simulateurs</span></nav><h1>Les simulateurs d\'aides pour les personnes âgées</h1>'
                '<p class="chapo">Huit calculateurs gratuits, avec les barèmes officiels de 2026 : APA à domicile et en EHPAD, minimum vieillesse, crédit d\'impôt, reste à charge en EHPAD, MaPrimeAdapt, mutuelle gratuite et allocation de proche aidant. Tout se calcule dans votre navigateur : rien n\'est enregistré.</p>'
                '<ul class="trust"><li>Barèmes officiels 2026</li><li>Aucune donnée enregistrée</li><li>Gratuit</li></ul>'
                + "".join(f'<div class="calc" data-clarity-mask="True" data-calc="{c}"></div><p class="calc-cta"><a href="{u}">Le guide complet →</a></p>' for c, u in sims) + '</div>')
    write("/simulateurs/", page("Simulateurs d'aides pour personnes âgées (2026)", "Calculez gratuitement l'APA, l'ASPA, le reste à charge en EHPAD, MaPrimeAdapt, le crédit d'impôt et la mutuelle gratuite, avec les barèmes 2026.",
          "/simulateurs/", sim_body, [{"@context": "https://schema.org", "@type": "WebApplication", "name": "Simulateurs d'aides pour personnes âgées", "applicationCategory": "FinanceApplication", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "inLanguage": "fr-FR"}], "accueil", None, FOOTER)); urls.append(("/simulateurs/", LANCEMENT))
    for s, (t, dsc, b) in STATIQUES.items():
        h = page(t, dsc, url(s), f'<div class="wrap prose">{b}</div>', [], "accueil", None, FOOTER)
        if s == "conditions-de-vente" and not STRIPE_PLAN:  # vente suspendue : page gardée pour les acheteurs, hors index et sitemap
            write(url(s), h.replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')); continue
        write(url(s), h); urls.append((url(s), STATIQUES_MAJ.get(s, LANCEMENT)))
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
        page("Page introuvable | Aider mes parents", "Cette page n'existe pas.", "/404.html", '<div class="wrap prose"><h1>Page introuvable</h1><p><a href="/">Revenir à l\'accueil</a></p></div>', [], "accueil", None, FOOTER).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'))
    open(os.path.join(OUT, "style.css"), "w", encoding="utf-8").write(CSS)
    shutil.copy(os.path.join(ROOT, "_build", "calc.js"), os.path.join(OUT, "calc.js"))
    shutil.copy(os.path.join(ROOT, "_build", "plan.js"), os.path.join(OUT, "plan.js"))
    open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#2f5f8a"/><path d="M32 48s-14-8.5-14-19a8 8 0 0 1 14-5.3A8 8 0 0 1 46 29c0 10.5-14 19-14 19z" fill="#f2b98b"/></svg>')
    open(os.path.join(OUT, "CNAME"), "w").write("aidermesparents.fr\n")
    open(os.path.join(OUT, INDEXNOW + ".txt"), "w").write(INDEXNOW)
    BOTS_IA = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User",
               "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "Meta-ExternalAgent", "MistralAI-User", "DuckAssistBot"]
    robots = "# Robots des moteurs de recherche et des assistants IA : bienvenus (citation des guides avec un lien).\n"
    robots += "".join(f"User-agent: {b}\nAllow: /\n\n" for b in BOTS_IA)
    robots += "User-agent: *\nContent-Signal: search=yes, ai-input=yes, ai-train=yes\nAllow: /\n\n"
    robots += f"Sitemap: {DOMAIN}/sitemap.xml\n"
    open(os.path.join(OUT, "robots.txt"), "w").write(robots)
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
