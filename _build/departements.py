"""Pages « APA et EHPAD dans le département » : uniquement des données officielles propres à chaque département."""
import json, os, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "_data", "departements.json"), encoding="utf-8"))
NAT = DATA["national"]
DEPS = DATA["departements"]
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
    if n[0] in "AEIOUÉÈÎÏÔY": return "dans l'" + n
    return "dans le " + n


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
    org = d["cd"]["nom"]
    if org.startswith("Conseil départemental"): org = f"le conseil départemental ({nom})"
    if eh:
        mois = (eh["med"] + (eh["g56"] or 0)) * JOURS
        ecart = (eh["med"] - NAT["med"]) / NAT["med"] * 100
        comp = ("au-dessus" if ecart > 0 else "en dessous") + f" de la médiane nationale ({_eur(NAT['med'])})" if abs(ecart) >= 2 else f"proche de la médiane nationale ({_eur(NAT['med'])})"
        chapo = (f"{dans[0].upper() + dans[1:]}, l'APA se demande auprès de : {org}. Les {eh['n']} EHPAD du département qui déclarent leurs prix affichent un prix d'hébergement médian de "
                 f"{_eur(eh['med'])} par jour en 2025, {comp}, soit environ {_eur(mois, 0)} par mois avant les aides.")
        desc = f"APA {dans} : contacts officiels, points d'information seniors et prix des {eh['n']} EHPAD (médiane {_eur(eh['med'])} par jour en 2025)."
    else:
        chapo = f"{dans[0].upper() + dans[1:]}, l'APA se demande auprès de : {org}. Voici les contacts officiels, les points d'information pour les personnes âgées et les démarches."
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
            b.append(f"<p>{len(pts)} point{'s' if len(pts) > 1 else ''} d'information local{'aux' if len(pts) > 1 else ''} pour les personnes âgées (anciennement CLIC) {'sont recensés' if len(pts) > 1 else 'est recensé'} dans l'annuaire officiel. Ils renseignent gratuitement sur l'APA, l'aide à domicile et les établissements, et aident à remplir les dossiers.</p>")
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
                 f'La réduction d\'impôt de 25 % (2 500 € par an au maximum) et l\'aide au logement peuvent faire baisser ce montant : estimez le reste à charge avec notre <a href="/ehpad-prix-aides/">calculateur EHPAD</a>.</p></aside>')
        b.append('<p>Les prix de chaque établissement sont consultables sur le comparateur officiel <a href="https://www.pour-les-personnes-agees.gouv.fr/annuaire-ehpad-et-maisons-de-retraite" rel="noopener" target="_blank">pour-les-personnes-agees.gouv.fr</a>.</p></section>')

    b.append(f'<section><h2 id="montants">Estimer l\'APA d\'un parent qui vit {dans}</h2></section>')
    b.append('<div class="calc" data-calc="apa"></div>')

    faq = [(f"Où faire la demande d'APA {dans} ?", f"Auprès de {org}" + (f", joignable au {d['cd']['tel']}" if d['cd'].get('tel') else "") + ". Le formulaire est le cerfa n°16301, identique dans toute la France.")]
    if eh:
        faq.append((f"Quel est le prix moyen d'un EHPAD {dans} ?", f"Le prix d'hébergement médian est de {_eur(eh['med'])} par jour en 2025 (chambre seule), d'après les prix déclarés par {eh['n']} établissements à la CNSA. Avec le tarif dépendance de base, cela fait environ {_eur((eh['med'] + (eh['g56'] or 0)) * JOURS, 0)} par mois avant aides."))
    if pts:
        faq.append((f"Qui peut m'aider à remplir le dossier APA {dans} ?", f"Les {len(pts)} points d'information pour les personnes âgées du département aident gratuitement à remplir le dossier, tout comme le CCAS de la mairie."))
    if eh:
        faq.append((f"Quel est l'EHPAD le moins cher {dans} ?", f"D'après les prix déclarés à la CNSA pour 2025, le prix d'hébergement le plus bas relevé {dans} est de {_eur(eh['min'])} par jour, et 10 % des établissements sont sous {_eur(eh['p10'])}. Les places habilitées à l'aide sociale sont en général les moins chères."))
    b.append("<section aria-labelledby=\"faq\"><h2 id=\"faq\">Questions fréquentes</h2>" + "".join(f"<details><summary>{_e(q)}</summary><p>{_e(r)}</p></details>" for q, r in faq) + "</section>")
    b.append('<section class="sources"><h2 id="sources">Sources</h2><ul><li>Annuaire de l\'administration (api-lannuaire.service-public.fr), contacts relevés le 12/11/2026</li><li>CNSA, prix hébergement et tarifs dépendance des EHPAD, données brutes 2025 (data.gouv.fr)</li><li>CNSA, montants de l\'APA au 1er janvier 2026</li></ul></section>')
    return {"path": path, "title": titre, "desc": desc, "h1": h1, "chapo": chapo, "body": "".join(b), "faq": faq, "nom": nom, "code": code}
