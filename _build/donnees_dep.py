#!/usr/bin/env python3
"""Construit _data/departements.json à partir des données officielles (CNSA prix EHPAD, annuaire de l'administration)."""
import json, csv, re, statistics, unicodedata, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_data")

def dep_of(insee):
    insee = str(insee or "")
    if insee.startswith("97"): return insee[:3]
    return insee[:2]

def slug(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def J(x):
    if isinstance(x, str):
        try: return json.loads(x)
        except Exception: return x
    return x

def contact(r):
    adr = J(r.get("adresse")) or []
    a = adr[0] if adr and isinstance(adr, list) else {}
    lignes = [a.get("complement1"), a.get("complement2"), a.get("numero_voie"), " ".join(x for x in [a.get("code_postal"), a.get("nom_commune")] if x)]
    tel = J(r.get("telephone")) or []
    site = J(r.get("site_internet")) or []
    return {"nom": r.get("nom"), "adresse": ", ".join(x.strip() for x in lignes if x and x.strip()),
            "tel": tel[0]["valeur"] if tel and isinstance(tel, list) else "",
            "site": site[0]["valeur"] if site and isinstance(site, list) else "",
            "courriel": r.get("adresse_courriel") if r.get("adresse_courriel") not in (None, "None") else "",
            "fiche": r.get("url_service_public") or "", "commune": a.get("nom_commune", "")}

deps = {}
for r in json.load(open(os.path.join(D, "annuaire-cg.json"))):
    code = dep_of(r.get("code_insee_commune"))
    nom = re.sub(r"^(Conseil départemental|Département|Collectivité[^-]*)\s*-\s*", "", r["nom"]).strip()
    deps.setdefault(code, {"code": code, "nom": nom, "cd": contact(r), "points": [], "mda": []})
for c in ("975", "977", "978", "98"): deps.pop(c, None)
X = json.load(open(os.path.join(D, "annuaire-extra.json")))
deps["75"]["nom"] = "Paris"
cea = deps["67"]["cd"]; deps["67"]["nom"] = "Bas-Rhin"; deps["67"]["note"] = "Dans le Bas-Rhin, l'APA est gérée par la Collectivité européenne d'Alsace, qui regroupe le Bas-Rhin et le Haut-Rhin."
deps["68"] = {"code": "68", "nom": "Haut-Rhin", "cd": cea, "points": [], "mda": [], "note": "Dans le Haut-Rhin, l'APA est gérée par la Collectivité européenne d'Alsace, qui regroupe le Haut-Rhin et le Bas-Rhin."}
for code, nom, cle, note in (("2A", "Corse-du-Sud", "2A", "En Corse, l'APA est gérée par la Collectivité de Corse, qui a repris les compétences des deux départements."),
                             ("2B", "Haute-Corse", "2A", "En Corse, l'APA est gérée par la Collectivité de Corse, qui a repris les compétences des deux départements."),
                             ("972", "Martinique", "972", "En Martinique, l'APA est gérée par la Collectivité territoriale de Martinique."),
                             ("973", "Guyane", "973", "En Guyane, l'APA est gérée par la Collectivité territoriale de Guyane.")):
    deps[code] = {"code": code, "nom": nom, "cd": contact(X[cle]), "points": [], "mda": [], "note": note}
deps["69"]["note"] = "Attention : si votre parent habite dans la Métropole de Lyon (Lyon, Villeurbanne, Vénissieux…), c'est la Métropole de Lyon qui gère l'APA, pas le département du Rhône."
deps["69"]["metro"] = contact(X["69M"])
for t, k in (("clic", "points"), ("mda", "mda")):
    for r in json.load(open(os.path.join(D, f"annuaire-{t}.json"))):
        code = dep_of(r.get("code_insee_commune"))
        if code in deps: deps[code][k].append(contact(r))

num = lambda v: float(v.replace(",", ".")) if v and v.strip() not in ("", "0") else None
par = {}
with open(os.path.join(D, "cnsa-prix-ehpad-2025.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter=";"):
        fin = row["finessEt"]; code = fin[:3] if fin.startswith("97") else fin[:2]
        if code == "20": code = "2A" if fin[2] in "A0" else "2B"
        p = num(row["prixHebPermCs"]); g56 = num(row["TARIF_GIR_56"])
        if p and 30 <= p <= 400:
            par.setdefault(code, {"heb": [], "g56": [], "g12": []})
            par[code]["heb"].append(p)
            if g56 and g56 < 60: par[code]["g56"].append(g56)
            g12 = num(row["TARIF_GIR_12"])
            if g12 and g12 < 120: par[code]["g12"].append(g12)
allheb = [x for v in par.values() for x in v["heb"]]
nat = {"n": len(allheb), "med": round(statistics.median(allheb), 2)}
for code, d in deps.items():
    v = par.get(code)
    if v and len(v["heb"]) >= 5:
        h = sorted(v["heb"]); q = statistics.quantiles(h, n=10)
        d["ehpad"] = {"n": len(h), "med": round(statistics.median(h), 2), "p10": round(q[0], 2), "p90": round(q[-1], 2), "min": round(h[0], 2), "max": round(h[-1], 2),
                      "g56": round(statistics.median(v["g56"]), 2) if v["g56"] else None, "g12": round(statistics.median(v["g12"]), 2) if v["g12"] else None}
    d["slug"] = slug(d["nom"])
json.dump({"national": nat, "departements": sorted(deps.values(), key=lambda x: x["code"])}, open(os.path.join(D, "departements.json"), "w"), ensure_ascii=False, indent=1)
print(len(deps), "départements ; national", nat)
print("sans prix EHPAD :", [d["code"] for d in deps.values() if "ehpad" not in d])
print("points d'information par dép. (min, médiane, max) :", min(len(d["points"]) for d in deps.values()), statistics.median(len(d["points"]) for d in deps.values()), max(len(d["points"]) for d in deps.values()))
for c in ("59", "75", "2A", "974"): x = deps.get(c); print(c, x and (x["nom"], x["slug"], x.get("ehpad"), len(x["points"]), len(x["mda"]), x["cd"]["tel"]))
