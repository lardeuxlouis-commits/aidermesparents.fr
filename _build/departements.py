"""Pages « APA et EHPAD dans le département » : uniquement des données officielles propres à chaque département."""
import json, os, hashlib, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "_data", "departements.json"), encoding="utf-8"))
NAT = DATA["national"]
DEPS = DATA["departements"]
_ST = json.load(open(os.path.join(ROOT, "_data", "stats_dep.json"), encoding="utf-8"))
SNAT, STATS = _ST["national"], _ST["stats"]
MAJ_STATS = "2026-11-15"  # date d'ajout des statistiques DREES / Insee / CNSA
JOURS = 30.42


def article_dep(nom):
    """« dans le Nord », « en Gironde », « dans la Somme », « à Paris »."""
    n = nom
    special = {"Paris": "à Paris", "La Réunion": "à La Réunion", "Mayotte": "à Mayotte", "Haut-Rhin": "dans le Haut-Rhin"}
    if n in special: return special[n]
    dans_la = ("Loire", "Vienne", "Marne", "Manche", "Meuse", "Somme", "Sarthe", "Creuse", "Drôme", "Nièvre")
    if n in dans_la: return "dans la " + n
    if n.startswith("Haute-"): return "en " + n
    plur = ("Alpes-de-Haute-Provence", "Hautes-Alpes", "Alpes-Maritimes", "Ardennes", "Bouches-du-Rhône", "Côtes-d'Armor", "Deux-Sèvres",
            "Hautes-Pyrénées", "Hauts-de-Seine", "Landes", "Pyrénées-Atlantiques", "Pyrénées-Orientales", "Vosges", "Yvelines")
    if n in plur: return "dans les " + n
    feminins = ("Ardèche", "Ariège", "Aube", "Aude", "Charente", "Charente-Maritime", "Corrèze", "Côte-d'Or", "Dordogne", "Gironde",
                "Loire-Atlantique", "Lozère", "Mayenne", "Meurthe-et-Moselle", "Moselle", "Saône-et-Loire", "Savoie", "Seine-Maritime",
                "Seine-Saint-Denis", "Seine-et-Marne", "Vendée", "Corse-du-Sud", "Martinique", "Guyane", "Guadeloupe")
    if n in feminins: return "en " + n
    if n in ("Ille-et-Vilaine", "Eure-et-Loir", "Indre-et-Loire"): return "en " + n
    if n[0] in "AEIOUÉÈÎÏÔY": return "dans l'" + n
    return "dans le " + n


def de_dep(nom):
    """« de la Gironde », « du Nord », « des Landes », « de l'Ain », « de Paris »."""
    a = article_dep(nom)
    if a.startswith("dans le "): return "du " + nom
    if a.startswith("dans la "): return "de la " + nom
    if a.startswith("dans les "): return "des " + nom
    if a.startswith("à "): return "de " + nom
    if nom[0] in "AEIOUÉÈÎÏÔY": return "de l'" + nom
    if a.startswith("en "): return "de la " + nom
    return "de l'" + nom


def org_dep(d):
    """Nom de l'organisme qui gère l'APA, précédé de son article : « le conseil départemental de la Gironde »."""
    org = d["cd"]["nom"]
    if org.startswith("Conseil départemental"): return "le conseil départemental " + de_dep(d["nom"])
    if org.startswith("Collectivité"): return "la " + org
    return "le " + org


def aupres(org):
    """« auprès du conseil… », « auprès de la Collectivité… »."""
    if org.startswith("le "): return "auprès du " + org[3:]
    return "auprès de " + org


def deps_publies():
    return DEPS


def _e(s):
    import html
    return html.escape(str(s or ""), quote=True)


def _eur(x, dec=2):
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s + " €"


def _var(code, options):
    return options[int(hashlib.md5(code.encode()).hexdigest(), 16) % len(options)]


def _contact_html(c, titre=None):
    if not c: return ""
    lignes = [f"<b>{_e(titre or c['nom'])}</b>"]
    if c.get("adresse"): lignes.append(_e(c["adresse"]))
    if c.get("tel"): lignes.append('Téléphone : <a href="tel:' + _e(c["tel"].replace(" ", "")) + '">' + _e(c["tel"]) + "</a>")
    if c.get("courriel"): lignes.append(f'Courriel : <a href="mailto:{_e(c["courriel"])}">{_e(c["courriel"])}</a>')
    liens = []
    if c.get("site"): liens.append(f'<a href="{_e(c["site"])}" rel="noopener" target="_blank">site officiel</a>')
    if c.get("fiche"): liens.append('<a href="' + _e(c["fiche"]) + '" rel="noopener" target="_blank">fiche de l’annuaire officiel (horaires)</a>')
    if liens: lignes.append(" · ".join(liens))
    return '<div class="contact">' + "<br>".join(lignes) + "</div>"


def _li(c, nom_court=True):
    nom = c["nom"]
    for pre in ("Point d’information local dédié aux personnes âgées - ", "Point d'information local dédié aux personnes âgées - "):
        nom = nom.replace(pre, "")
    tel = c.get("tel") or ""
    h = "<li><b>" + _e(c.get("commune") or nom) + "</b> · " + _e(nom)
    if tel: h += ' · <a href="tel:' + _e(tel.replace(" ", "")) + '">' + _e(tel) + "</a>"
    if c.get("fiche"): h += ' · <a href="' + _e(c["fiche"]) + '" rel="noopener" target="_blank">adresse et horaires</a>'
    return h + "</li>"


def page_dep(d):
    nom, code = d["nom"], d["code"]
    dans = article_dep(nom)
    path = f"/apa/{d['slug']}/"
    eh = d.get("ehpad")
    titre = f"APA {nom} ({code}) : contacts, démarches et prix des EHPAD"
    L = lambda t: len(t.replace("'", "&#x27;"))
    if L(titre) > 62: titre = f"APA {nom} ({code}) : contacts et prix des EHPAD"
    if L(titre) > 62: titre = f"APA {nom} ({code}) : démarches et contacts"
    h1 = f"APA et EHPAD {dans} ({code}) : où s'adresser et combien ça coûte"
    org = org_dep(d)
    if eh:
        mois = (eh["med"] + (eh["g56"] or 0)) * JOURS
        ecart = (eh["med"] - NAT["med"]) / NAT["med"] * 100
        comp = ("au-dessus" if ecart > 0 else "en dessous") + f" de la médiane nationale ({_eur(NAT['med'])})" if abs(ecart) >= 2 else f"proche de la médiane nationale ({_eur(NAT['med'])})"
        chapo = (f"{dans[0].upper() + dans[1:]}, l'APA se demande {aupres(org)}. Les {eh['n']} EHPAD du département qui déclarent leurs prix affichent un prix d'hébergement médian de "
                 f"{_eur(eh['med'])} par jour en 2025, {comp}, soit environ {_eur(mois, 0)} par mois avant les aides.")
        desc = f"APA {dans} : contacts officiels, points d'information seniors et prix des {eh['n']} EHPAD (médiane {_eur(eh['med'])} par jour en 2025)."
    else:
        chapo = f"{dans[0].upper() + dans[1:]}, l'APA se demande {aupres(org)}. Voici les contacts officiels, les points d'information pour les personnes âgées et les démarches."
        desc = f"APA {dans} : où faire la demande, contacts officiels, points d'information pour les personnes âgées et démarches."
    if len(desc) > 158: desc = desc[:155].rsplit(" ", 1)[0] + "…"

    b = []
    if d.get("note"): b.append(f'<aside class="attention"><p class="lab">À savoir</p><p>{_e(d["note"])}</p></aside>')
    b.append(f'<section><h2 id="demande">Où demander l\'APA {dans} ?</h2>')
    b.append(f"<p>{_var(code, ['La demande se fait auprès de la collectivité qui gère l’APA sur le territoire de votre parent.', 'C’est la collectivité ci-dessous qui reçoit les dossiers d’APA et organise la visite d’évaluation à domicile.', 'Le dossier d’APA est instruit par la collectivité suivante, qui envoie ensuite un évaluateur chez votre parent.'])}</p>")
    b.append(_contact_html(d["cd"]))
    if d.get("metro"): b.append(_contact_html(d["metro"], "Métropole de Lyon (pour les habitants de la Métropole)"))
    b.append(f'<p>Formulaire : cerfa n°16301, à envoyer à cette adresse {dans} ({_e(d["cd"].get("commune") or nom)}). Pièces et délais : <a href="/apa/demande/">notre guide de la demande</a>.</p></section>')

    pts = sorted(d["points"], key=lambda c: c.get("commune", ""))
    if pts or d["mda"]:
        b.append(f'<section><h2 id="points">Les lieux d\'information pour les personnes âgées {dans}</h2>')
        if pts:
            b.append(f"<p>{len(pts)} point{'s' if len(pts) > 1 else ''} d'information {'locaux' if len(pts) > 1 else 'local'} pour les personnes âgées (anciennement CLIC) {'sont recensés' if len(pts) > 1 else 'est recensé'} dans l'annuaire officiel. {_var(code + 'q', [('Ils aident' if len(pts) > 1 else 'Il aide') + ' gratuitement à monter le dossier.', ('Ils sont gratuits et peuvent vous aider' if len(pts) > 1 else 'Il est gratuit et peut vous aider') + ' à remplir le dossier.', 'Leur aide pour constituer le dossier est gratuite.'])}</p>")
            b.append('<ul class="lieux">' + "".join(_li(c) for c in pts) + "</ul>")
        if d["mda"]:
            b.append(f"<p>Le département compte aussi {len(d['mda'])} maison{'s' if len(d['mda']) > 1 else ''} de l'autonomie ou antenne{'s' if len(d['mda']) > 1 else ''} de proximité :</p>")
            b.append('<ul class="lieux">' + "".join(_li(c) for c in sorted(d["mda"], key=lambda c: c.get("commune", ""))[:20]) + "</ul>")
        b.append("</section>")

    if eh:
        b.append(f'<section><h2 id="prix">Combien coûte un EHPAD {dans} ?</h2>')
        b.append(f"<p>Prix déclarés par les {eh['n']} EHPAD {dans} à la CNSA pour 2025, chambre seule en hébergement permanent.</p>")
        rows = [("EHPAD ayant déclaré un prix", str(eh["n"])), ("Prix d'hébergement médian", _eur(eh["med"]) + " par jour"),
                ("Les 10 % les moins chers", "moins de " + _eur(eh["p10"]) + " par jour"), ("Les 10 % les plus chers", "plus de " + _eur(eh["p90"]) + " par jour"),
                ("Écart observé", f"de {_eur(eh['min'])} à {_eur(eh['max'])} par jour")]
        if eh.get("g56"): rows.append(("Tarif dépendance GIR 5-6 (médian)", _eur(eh["g56"]) + " par jour"))
        if eh.get("g12"): rows.append(("Tarif dépendance GIR 1-2 (médian)", _eur(eh["g12"]) + " par jour, financé en partie par l'APA"))
        b.append('<div class="tw"><table><tbody>' + "".join(f"<tr><td>{a}</td><td><b>{c}</b></td></tr>" for a, c in rows) + "</tbody></table></div>")
        mois = (eh["med"] + (eh["g56"] or 0)) * JOURS
        b.append(f'<aside class="exemple"><p class="lab">Exemple</p><p>Dans un EHPAD au prix médian du département, hébergement et tarif dépendance de base reviennent à environ {_eur(mois, 0)} par mois. '
                 f'Les aides font baisser ce montant : <a href="/ehpad-prix-aides/">calculer le reste à charge</a>.</p></aside>')
        b.append('<p>Les prix de chaque établissement sont consultables sur le comparateur officiel <a href="https://www.pour-les-personnes-agees.gouv.fr/annuaire-ehpad-et-maisons-de-retraite" rel="noopener" target="_blank">pour-les-personnes-agees.gouv.fr</a>.</p></section>')

    stats_html, stats_faq = bloc_stats(d)
    b.append(stats_html)

    b.append(f'<section><h2 id="montants">Estimer l\'APA d\'un parent qui vit {dans}</h2><p>Le barème est national. Conditions et montants détaillés : <a href="/apa/">notre guide de l\'APA</a>.</p></section>')
    b.append('<div class="calc" data-calc="apa"></div>')

    faq = [(f"Où faire la demande d'APA {dans} ?", aupres(org)[0].upper() + aupres(org)[1:] + (f", joignable au {d['cd']['tel']}" if d['cd'].get('tel') else "") + ". " + _var(code + "r", ["Le formulaire est le cerfa n°16301, identique dans toute la France.", "Le dossier à remplir est le cerfa n°16301, le même partout en France.", "On utilise le formulaire national cerfa n°16301."]))]
    faq += stats_faq
    if eh:
        faq.append((f"Quel est le prix moyen d'un EHPAD {dans} ?", f"Le prix d'hébergement médian est de {_eur(eh['med'])} par jour en 2025 (chambre seule), d'après les prix déclarés par {eh['n']} établissements à la CNSA. Avec le tarif dépendance de base, cela fait environ {_eur((eh['med'] + (eh['g56'] or 0)) * JOURS, 0)} par mois avant aides."))
    if pts:
        faq.append((f"Qui peut m'aider à remplir le dossier APA {dans} ?", (f"Les {len(pts)} points d'information pour les personnes âgées du département aident" if len(pts) > 1 else "Le point d'information pour les personnes âgées du département aide") + " gratuitement à remplir le dossier, tout comme le CCAS de la mairie."))
    if eh:
        faq.append((f"Quel est l'EHPAD le moins cher {dans} ?", f"D'après les prix déclarés à la CNSA pour 2025, le prix d'hébergement le plus bas relevé {dans} est de {_eur(eh['min'])} par jour, et 10 % des établissements sont sous {_eur(eh['p10'])}. " + _var(code + "s", ["Les places habilitées à l'aide sociale sont en général les moins chères.", "Les établissements habilités à l'aide sociale pratiquent souvent les prix les plus bas.", "Pour un budget serré, regardez d'abord les places habilitées à l'aide sociale."])))
    b.append("<section aria-labelledby=\"faq\"><h2 id=\"faq\">Questions fréquentes</h2>" + "".join(f"<details><summary>{_e(q)}</summary><p>{_e(r)}</p></details>" for q, r in faq) + "</section>")
    b.append('<section class="sources"><h2 id="sources">Sources</h2><ul><li>Annuaire de l\'administration (api-lannuaire.service-public.fr), contacts relevés le 12/11/2026</li><li>CNSA, prix hébergement et tarifs dépendance des EHPAD, données brutes 2025 (data.gouv.fr)</li><li>CNSA, montants de l\'APA au 1er janvier 2026</li></ul></section>')
    return {"path": path, "title": titre, "desc": desc, "h1": h1, "chapo": chapo, "body": "".join(b), "faq": faq, "nom": nom, "code": code, "maj": MAJ_STATS if stats_html else None}


# ---------------------------------------------------------------------------
# Statistiques officielles du département (DREES, Insee, CNSA), ajoutées le 15/11/2026.
# Chaque phrase est construite à partir des valeurs : formulation choisie selon l'écart
# à la moyenne nationale, puis variante de tournure tirée du code du département.

SRC_INSEE = ('Source : Insee, <a href="https://www.insee.fr/fr/statistiques/8721456" rel="noopener" target="_blank">estimations de population au 1er janvier 2026</a> '
             '(parues le 13/01/2026) et recensement 2022 via les indicateurs sociaux départementaux de la DREES.')
SRC_DREES = ('Source : DREES, enquête Aide sociale, <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/les-beneficiaires-de-l-aide-sociale-departementale-aux-personnes-agees-ou-handic/" rel="noopener" target="_blank">bénéficiaires payés en décembre 2024</a> '
             '(mise à jour du 03/09/2026) et <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/376_les-depenses-d-aide-sociale-departementale/" rel="noopener" target="_blank">dépenses 2024</a> (mise à jour du 17/04/2026).')
SRC_ISD = ('Source : DREES, <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/639_personnes-agees/" rel="noopener" target="_blank">indicateurs sociaux départementaux, personnes âgées</a> '
           '(mise à jour du 06/10/2026), données 2024 et 2025.')
SRC_ISD_RATIOS = ('Ratios : DREES, <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/639_personnes-agees/" rel="noopener" target="_blank">indicateurs sociaux départementaux</a> (mise à jour du 06/10/2026).')
SRC_CNSA = ('Source : CNSA, <a href="https://www.cnsa.fr/sites/default/files/2026-06/PUB-Rapport_VPG-GMP_2025.pdf" rel="noopener" target="_blank">synthèse des valeurs de point GIR 2025</a> (juin 2026).')


def _n(x):
    return f"{int(round(x)):,}".replace(",", "\u00a0")


def _p(x, dec=1):
    """x en pourcentage déjà multiplié (12.3 -> « 12,3 »)."""
    s = f"{x:.{dec}f}".replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


def _rang(r):
    if not r: return ""
    i, n = r
    if i == 1: return f"le plus élevé des {n} départements renseignés"
    if i == n: return f"le plus bas des {n} départements renseignés"
    if i <= n / 2: return f"{i}e sur {n} départements, du plus élevé au plus bas"
    return f"{n - i + 1}e plus bas sur {n} départements"


def _cmp(v, ref, seuil):
    """'haut', 'bas' ou 'proche' selon l'écart relatif à la référence."""
    e = (v - ref) / ref
    return "haut" if e > seuil else "bas" if e < -seuil else "proche"


def bloc_stats(d):
    code, nom = d["code"], d["nom"]
    s = STATS.get(code) or {}
    if not s: return "", []
    dans = article_dep(nom)
    Dans = dans[0].upper() + dans[1:]
    du = de_dep(nom)
    V = lambda salt, opts: _var(code + salt, opts)
    rhone = code == "69"
    out, faq = [], []

    # --- 1. Les personnes âgées du département (Insee)
    pa = []
    if s.get("p75") and s.get("part75") is not None:
        p75, part, npart = _n(s["p75"]), _p(s["part75"]), _p(SNAT["part75"])
        c = _cmp(s["part75"], SNAT["part75"], 0.12)
        if c == "haut":
            pa.append(V("a", [f"Le département compte plus de grands aînés que la moyenne : {p75} habitants ont 75 ans ou plus au 1er janvier 2026, soit {part} % de la population contre {npart} % en France.",
                              f"Avec {p75} personnes de 75 ans ou plus au 1er janvier 2026, soit {part} % des habitants, la population {du} est nettement plus âgée que celle de la France entière ({npart} %).",
                              f"Au 1er janvier 2026, {part} % des habitants {du} ont 75 ans ou plus, soit {p75} personnes : c'est plus que la moyenne nationale de {npart} %."]))
        elif c == "bas":
            pa.append(V("a", [f"La population est plutôt jeune : {p75} habitants ont 75 ans ou plus au 1er janvier 2026, soit {part} % de la population contre {npart} % en France.",
                              f"Au 1er janvier 2026, les 75 ans ou plus représentent {part} % des habitants {du} ({p75} personnes), moins que la moyenne nationale de {npart} %.",
                              f"Avec {part} % d'habitants de 75 ans ou plus ({p75} personnes au 1er janvier 2026), le département est moins âgé que la France entière ({npart} %)."]))
        else:
            pa.append(V("a", [f"{Dans}, {p75} habitants ont 75 ans ou plus au 1er janvier 2026, soit {part} % de la population, une part proche de la moyenne nationale ({npart} %).",
                              f"Au 1er janvier 2026, le département compte {p75} personnes de 75 ans ou plus, soit {part} % des habitants, à peu près comme la France entière ({npart} %).",
                              f"Les 75 ans ou plus sont {p75} au 1er janvier 2026, soit {part} % des habitants {du}, un niveau voisin de la moyenne nationale ({npart} %)."]))
    if s.get("p75") and s.get("p75_2016"):
        g = (s["p75"] / s["p75_2016"] - 1) * 100; gn = (SNAT["p75"] / SNAT["p75_2016"] - 1) * 100
        zone = ""
        if g >= gn + 6:
            pa.append(V("b", [f"Leur nombre a progressé d'environ {_p(g, 0)} % en dix ans{zone} ({_n(s['p75_2016'])} en 2016), plus vite que dans l'ensemble du pays (+{_p(gn, 0)} %).",
                              f"En dix ans, le nombre de personnes de 75 ans ou plus a augmenté d'environ {_p(g, 0)} %{zone}, contre +{_p(gn, 0)} % en France : la demande d'aide à domicile et de places en établissement suit la même pente."]))
        elif g <= gn - 6:
            pa.append(V("b", [f"Leur nombre a augmenté d'environ {_p(g, 0)} % en dix ans{zone} ({_n(s['p75_2016'])} en 2016), une hausse plus modérée qu'en France (+{_p(gn, 0)} %).",
                              f"Depuis 2016, cette population a crû d'environ {_p(g, 0)} %{zone}, moins vite que la moyenne nationale (+{_p(gn, 0)} %)."]))
        else:
            pa.append(V("b", [f"Leur nombre a augmenté d'environ {_p(g, 0)} % en dix ans{zone} ({_n(s['p75_2016'])} en 2016), un rythme comparable à celui de la France (+{_p(gn, 0)} %).",
                              f"En dix ans, cette population a grossi d'environ {_p(g, 0)} %{zone}, à peu près au même rythme que dans le reste du pays (+{_p(gn, 0)} %)."]))
    if s.get("seules75") is not None:
        x, n = s["seules75"] * 100, SNAT["seules75"] * 100
        c = _cmp(x, n, 0.07)
        lien = '<a href="/teleassistance/">téléassistance</a>'
        if c == "haut":
            pa.append(V("c", [f"L'isolement y est plus fréquent : {_p(x, 0)} % des 75 ans ou plus vivent seuls, contre {_p(n, 0)} % en France (recensement 2022). La {lien} et les visites régulières comptent d'autant plus.",
                              f"Selon le recensement 2022, {_p(x, 0)} % des personnes de 75 ans ou plus vivent seules, au-dessus de la moyenne nationale ({_p(n, 0)} %). Une {lien} peut rassurer la famille à distance."]))
        elif c == "bas":
            pa.append(V("c", [f"Les grands aînés y vivent moins souvent seuls qu'ailleurs : {_p(x, 0)} % des 75 ans ou plus, contre {_p(n, 0)} % en France (recensement 2022).",
                              f"D'après le recensement 2022, {_p(x, 0)} % des 75 ans ou plus vivent seuls, moins que la moyenne nationale ({_p(n, 0)} %)."]))
        else:
            pa.append(V("c", [f"Environ {_p(x, 0)} % des 75 ans ou plus vivent seuls, proche de la moyenne nationale ({_p(n, 0)} %, recensement 2022).",
                              f"Selon le recensement 2022, {_p(x, 0)} % des personnes de 75 ans ou plus vivent seules, comme dans le reste du pays ({_p(n, 0)} %)."]))
    if pa and rhone:
        pa.insert(0, "Les chiffres de population ci-dessous portent sur tout le territoire du Rhône, Métropole de Lyon comprise.")
    if pa:
        h2 = V("h", [f"Les personnes âgées {dans} en chiffres", f"Combien de personnes âgées {dans} ?", f"Le grand âge {dans} : les chiffres officiels"])
        out.append(f'<section><h2 id="population">{h2}</h2><p>' + " ".join(pa) + f'</p><p class="src">{SRC_INSEE}</p></section>')

    # --- 2. L'APA dans le département (DREES)
    ap, rows = [], []
    hors = " (hors Métropole de Lyon)" if rhone else ""
    if s.get("apa"):
        apa, dom, etab = s["apa"], s.get("apa_dom"), s.get("apa_etab")
        if dom and etab:
            pdom, pn = dom / apa * 100, SNAT["apa_dom"] / SNAT["apa"] * 100
            ap.append(V("d", [f"En décembre 2024, {_n(apa)} personnes ont reçu l'APA {dans}{hors} : {_n(dom)} à domicile et {_n(etab)} en établissement.",
                              f"{Dans}{hors}, l'APA a été versée à {_n(apa)} personnes en décembre 2024, dont {_n(dom)} qui vivent chez elles et {_n(etab)} accueillies en établissement.",
                              f"Le département{hors} a payé l'APA à {_n(apa)} bénéficiaires au titre de décembre 2024 : {_n(dom)} à domicile, {_n(etab)} en EHPAD ou autre établissement."]))
            c = _cmp(pdom, pn, 0.08)
            if c == "haut": ap.append(f"L'APA à domicile y pèse plus qu'ailleurs : {_p(pdom, 0)} % des bénéficiaires vivent chez eux, contre {_p(pn, 0)} % en France.")
            elif c == "bas": ap.append(f"La part des bénéficiaires accueillis en établissement est plus forte qu'ailleurs : seuls {_p(pdom, 0)} % vivent à domicile, contre {_p(pn, 0)} % en France.")
            else: ap.append(V("e", [f"Comme dans le reste du pays, la majorité vit à domicile ({_p(pdom, 0)} %, contre {_p(pn, 0)} % en France).",
                                    f"La répartition est proche de la moyenne nationale : {_p(pdom, 0)} % des bénéficiaires vivent à domicile ({_p(pn, 0)} % en France)."]))
        if s.get("tx75") is not None:
            t, tn = s["tx75"] * 100, SNAT["tx75"] * 100
            c = _cmp(t, tn, 0.08)
            r = _rang(s.get("rang_tx75"))
            if c == "haut":
                ap.append(V("f", [f"On compte environ {_p(t, 0)} bénéficiaires pour 100 habitants de 75 ans ou plus, au-dessus de la moyenne nationale ({_p(tn, 0)} pour 100) : c'est le {r}.",
                                  f"Rapporté aux 75 ans ou plus, le recours à l'APA est élevé : {_p(t, 0)} bénéficiaires pour 100 habitants de cet âge, contre {_p(tn, 0)} en France ({r})."]))
            elif c == "bas":
                ap.append(V("f", [f"On compte environ {_p(t, 0)} bénéficiaires pour 100 habitants de 75 ans ou plus, sous la moyenne nationale ({_p(tn, 0)} pour 100) : c'est le {r}. Si votre parent n'a jamais fait la demande, cela vaut la peine de vérifier ses droits.",
                                  f"Le recours à l'APA est plutôt faible rapporté à la population âgée : {_p(t, 0)} bénéficiaires pour 100 habitants de 75 ans ou plus, contre {_p(tn, 0)} en France ({r}). Si votre parent n'a pas encore demandé l'aide, une simulation rapide permet de voir s'il peut y prétendre."]))
            else:
                ap.append(V("f", [f"Cela représente environ {_p(t, 0)} bénéficiaires pour 100 habitants de 75 ans ou plus, proche de la moyenne nationale ({_p(tn, 0)} pour 100).",
                                  f"Rapporté aux 75 ans ou plus, on compte {_p(t, 0)} bénéficiaires pour 100 habitants, un niveau voisin de celui de la France ({_p(tn, 0)})."]))
        if s.get("apa_2014"):
            e = (apa / s["apa_2014"] - 1) * 100; en = (SNAT["apa"] / SNAT["apa_2014"] - 1) * 100
            if abs(e - en) < 2 and e >= 3:
                ap.append(f"Le nombre de bénéficiaires a augmenté d'environ {_p(e, 0)} % depuis 2014 ({_n(s['apa_2014'])} à l'époque), au même rythme qu'en France.")
            elif e >= 3:
                ap.append(V("g", [f"Le nombre de bénéficiaires a augmenté d'environ {_p(e, 0)} % depuis 2014 ({_n(s['apa_2014'])} à l'époque), contre +{_p(en, 0)} % en France.",
                                  f"En dix ans, il est passé de {_n(s['apa_2014'])} à {_n(apa)} bénéficiaires, soit une hausse d'environ {_p(e, 0)} % (+{_p(en, 0)} % au niveau national)."]))
            elif e <= -3:
                ap.append(V("g", [f"Le nombre de bénéficiaires a baissé d'environ {_p(-e, 0)} % depuis 2014 ({_n(s['apa_2014'])} à l'époque), alors qu'il a progressé de {_p(en, 0)} % en France.",
                                  f"En dix ans, il est passé de {_n(s['apa_2014'])} à {_n(apa)} bénéficiaires, soit une baisse d'environ {_p(-e, 0)} %, à rebours de la tendance nationale (+{_p(en, 0)} %)."]))
            else:
                ap.append(f"Le nombre de bénéficiaires est resté presque stable depuis 2014 ({_n(s['apa_2014'])} à l'époque), alors qu'il a progressé de {_p(en, 0)} % en France.")
        rows.append(("Bénéficiaires de l'APA", f"{_n(apa)} (décembre 2024)"))
        ap.append("</p><p>")
        if dom: rows.append(("dont à domicile", _n(dom)))
        if etab: rows.append(("dont en établissement", _n(etab)))
    if s.get("gir12") is not None:
        g, gn = s["gir12"] * 100, SNAT["gir12"] * 100
        lien = '<a href="/grille-aggir/">GIR 1 ou 2</a>'
        c = _cmp(g, gn, 0.1)
        if c == "haut": ap.append(f"Les situations lourdes sont plus fréquentes : {_p(g, 0)} % des bénéficiaires à domicile sont classés en {lien}, les deux niveaux de dépendance les plus élevés, contre {_p(gn, 0)} % en France.")
        elif c == "bas": ap.append(f"À domicile, {_p(g, 0)} % des bénéficiaires sont classés en {lien}, les deux niveaux de dépendance les plus élevés, contre {_p(gn, 0)} % en France : la plupart sont en GIR 3 ou 4.")
        else: ap.append(V("i", [f"À domicile, {_p(g, 0)} % des bénéficiaires sont classés en {lien}, les deux niveaux de dépendance les plus élevés, comme en moyenne en France ({_p(gn, 0)} %).",
                                f"Parmi les bénéficiaires qui vivent chez eux, {_p(g, 0)} % relèvent du {lien}, une proportion proche de la moyenne nationale ({_p(gn, 0)} %)."]))
    if s.get("apa_dom_mois") and s.get("dep_apa_dom"):
        m, mn = s["apa_dom_mois"], SNAT["apa_dom_mois"]
        base = f"En 2024, le département{hors} a consacré environ {_n(s['dep_apa_dom'] / 1e6)} millions d'euros à l'APA à domicile, soit en moyenne près de {_n(m)} € par mois et par bénéficiaire"
        c = _cmp(m, mn, 0.08)
        if c == "haut": ap.append(base + f", au-dessus de la moyenne nationale (environ {_n(mn)} €).")
        elif c == "bas": ap.append(base + f", en dessous de la moyenne nationale (environ {_n(mn)} €).")
        else: ap.append(base + f", proche de la moyenne nationale (environ {_n(mn)} €).")
        ap.append(V("o", ["Ce chiffre est une moyenne : le montant réel dépend du plan d'aide et des revenus de chacun.",
                          "Il s'agit d'une moyenne, le montant versé à votre parent dépendra de son plan d'aide et de ses ressources.",
                          "Ce n'est qu'un ordre de grandeur : chaque montant est calculé selon le plan d'aide et les revenus du bénéficiaire."]))
        rows.append(("Dépense moyenne APA à domicile", f"environ {_n(m)} € par mois et par bénéficiaire (2024)"))
    if s.get("ash"):
        ap.append(V("j", [f"Enfin, {_n(s['ash'])} personnes âgées bénéficiaient fin 2024 de l'<a href=\"/aide-sociale-hebergement/\">aide sociale à l'hébergement</a>, qui paie une partie des frais d'EHPAD quand les revenus ne suffisent pas.",
                          f"Fin 2024, l'<a href=\"/aide-sociale-hebergement/\">aide sociale à l'hébergement</a> prenait en charge une partie des frais d'établissement de {_n(s['ash'])} personnes âgées {dans}."]))
        rows.append(("Aide sociale à l'hébergement", f"{_n(s['ash'])} bénéficiaires (fin 2024)"))
    if ap:
        h2 = V("k", [f"Combien de personnes touchent l'APA {dans} ?", f"L'APA {dans} en chiffres", f"Les bénéficiaires de l'APA {dans}"])
        out.append(f'<section><h2 id="beneficiaires">{h2}</h2><p>' + " ".join(ap) + "</p>")
        if rows: out.append('<div class="tw"><table><tbody>' + "".join(f"<tr><td>{a}</td><td><b>{c}</b></td></tr>" for a, c in rows) + "</tbody></table></div>")
        out.append(f'<p class="src">{SRC_DREES}' + (" " + SRC_ISD_RATIOS if s.get("tx75") is not None or s.get("gir12") is not None else "") + "</p></section>")
        if s.get("apa_dom") and s.get("apa_etab"):
            faq.append((f"Combien de personnes touchent l'APA {dans} ?",
                        f"D'après la DREES, {_n(s['apa'])} personnes ont reçu l'APA {dans}{hors} en décembre 2024 : {_n(s['apa_dom'])} à domicile et {_n(s['apa_etab'])} en établissement."
                        + (f" Cela fait environ {_p(s['tx75'] * 100, 0)} bénéficiaires pour 100 habitants de 75 ans ou plus (moyenne nationale : {_p(SNAT['tx75'] * 100, 0)})." if s.get("tx75") is not None else "")))

    # --- 3. L'offre d'accueil et de soins (DREES, CNSA)
    of = []
    if s.get("places") is not None:
        x, n = s["places"], SNAT["places"]
        c = _cmp(x, n, 0.1)
        if c == "haut":
            of.append(V("l", [f"Le département offre {_n(x)} places d'hébergement pour 1 000 personnes de 75 ans ou plus (EHPAD, résidences autonomie), plus que la moyenne nationale ({_n(n)}). Trouver une place y est en général un peu moins difficile.",
                              f"Avec {_n(x)} places en établissement pour 1 000 habitants de 75 ans ou plus, contre {_n(n)} en France, l'offre d'accueil {du} est plutôt fournie."]))
        elif c == "bas":
            of.append(V("l", [f"Le département ne compte que {_n(x)} places d'hébergement pour 1 000 personnes de 75 ans ou plus (EHPAD, résidences autonomie), contre {_n(n)} en France. Mieux vaut déposer des demandes dans plusieurs établissements, et tôt.",
                              f"L'offre en établissement est plus rare qu'ailleurs : {_n(x)} places pour 1 000 habitants de 75 ans ou plus, contre {_n(n)} en moyenne en France. L'attente pour une place peut donc être plus longue."]))
        else:
            of.append(V("l", [f"Le département compte {_n(x)} places d'hébergement pour 1 000 personnes de 75 ans ou plus (EHPAD, résidences autonomie), un niveau proche de la moyenne nationale ({_n(n)}).",
                              f"Côté établissements, on compte {_n(x)} places pour 1 000 habitants de 75 ans ou plus, à peu près comme en France ({_n(n)})."]))
    if s.get("ssiad") is not None:
        x, n = s["ssiad"], SNAT["ssiad"]
        c = _cmp(x, n, 0.1)
        mot = "plus que" if c == "haut" else "moins que" if c == "bas" else "proche de"
        of.append(V("m", [f"Pour les soins à la maison, les services de soins infirmiers à domicile (SSIAD) proposent {_p(x)} places pour 1 000 habitants de 75 ans ou plus en 2025, {mot} la moyenne nationale ({_p(n)}).",
                          f"En 2025, le département dispose de {_p(x)} places de soins infirmiers à domicile (SSIAD) pour 1 000 personnes de 75 ans ou plus, {mot} la moyenne nationale ({_p(n)})."]))
    if s.get("vpg"):
        v, v24, med = s["vpg"], s.get("vpg_2024"), SNAT["vpg_med"]
        qui = {"67": "La Collectivité européenne d'Alsace", "68": "La Collectivité européenne d'Alsace", "2A": "La Collectivité de Corse", "2B": "La Collectivité de Corse",
               "972": "La Collectivité territoriale de Martinique", "973": "La Collectivité territoriale de Guyane"}.get(code, "Le département")
        evo = "inchangée par rapport à 2024" if v24 == v else f"contre {_eur(v24)} en 2024" if v24 else ""
        pos = "au-dessus de" if v > med + 0.1 else "en dessous de" if v < med - 0.1 else "proche de"
        txt = V("p", [f"{qui} fixe chaque année la valeur du point GIR, qui sert à calculer sa part du financement de la dépendance des résidents d'EHPAD. Elle est de {_eur(v)} en 2025 ({evo}), {pos} la médiane nationale ({_eur(med)}).",
                      f"Pour financer la dépendance des résidents d'EHPAD, {qui[0].lower() + qui[1:]} applique une valeur du point GIR de {_eur(v)} en 2025 ({evo}), {pos} la médiane nationale ({_eur(med)}).",
                      f"La valeur du point GIR, qui fixe la participation de la collectivité au coût de la dépendance en EHPAD, s'établit {dans} à {_eur(v)} en 2025 ({evo}), {pos} la médiane nationale ({_eur(med)})."])
        if rhone and s.get("vpg_metro"): txt += f" Pour les EHPAD de la Métropole de Lyon, c'est la Métropole qui la fixe : {_eur(s['vpg_metro'])} en 2025."
        of.append(txt)
    if of:
        h2 = V("n", [f"Places en EHPAD et soins à domicile {dans}", f"L'offre d'accueil et de soins {dans}", f"EHPAD et soins à domicile {dans} : l'offre disponible"])
        src = []
        if s.get("places") is not None or s.get("ssiad") is not None: src.append(SRC_ISD)
        if s.get("vpg"): src.append(SRC_CNSA)
        out.append(f'<section><h2 id="offre">{h2}</h2><p>' + " ".join(of) + '</p><p class="src">' + " ".join(src) + "</p></section>")
    h = "".join(out).replace("<p> ", "<p>").replace(" </p>", "</p>")
    h = re.sub(r" (%|€)", "\u00a0\\1", h).replace("(+", "(+").replace("+ ", "+")
    return h, faq
