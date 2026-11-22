#!/usr/bin/env python3
"""Contact du service APA de chaque département, vérifié le 22/11/2026 → _data/contacts_apa.json.

1. Fiche du département dans l'annuaire officiel pour-les-personnes-agees.gouv.fr (CNSA) :
   adresse de la direction de l'autonomie, téléphone, lien vers la page APA du département.
2. Vérification : le numéro n'est retenu que s'il figure sur le site du département (page APA ou accueil).
   Sinon, pas de numéro : seulement le lien officiel. Jamais de numéro sans source.
3. MANUEL : relevés à la main sur la page APA du département (22/11/2026).
Cache des pages : _build/.cache/contacts/ (non versionné).
"""
import json, re, html, subprocess, os, time, concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "_build", ".cache", "contacts")
DEPS = {d["code"]: d for d in json.load(open(os.path.join(ROOT, "_data", "departements.json")))["departements"]}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
VERIF = "2026-11-22"
ANN = "https://www.pour-les-personnes-agees.gouv.fr/annuaire-departements/"

MANUEL = {
    "22": dict(service="Service APA, direction personnes âgées et personnes handicapées", adresse="9 place du Général-de-Gaulle, CS 42371, 22023 Saint-Brieuc Cedex 1",
               tel="02 96 62 62 22", horaires="du lundi au vendredi, de 8h30 à 17h30", page_apa="https://cotesdarmor.fr/vos-services/l-apa"),
    "43": dict(service="Maison départementale de l'autonomie", adresse="78 bis avenue Maréchal-Foch, 43000 Le Puy-en-Velay",
               tel="04 71 07 21 80", page_apa="https://www.hauteloire.fr/La-mise-en-place-de-l-Aide.html",
               standard="04 71 07 43 43"),
    "65": dict(service="Maison départementale pour l'autonomie (direction de la solidarité départementale)", adresse="Place Ferré, 65000 Tarbes",
               tel="05 62 56 74 28", page_apa="https://www.hautespyrenees.fr/seniors/vivre-a-domicile/lapa-allocation-personnalisee-dautonomie/",
               standard="05 62 56 78 65"),
    "77": dict(service="Direction de l'autonomie, service des prestations", adresse="Hôtel du Département, CS 50377, 77010 Melun Cedex",
               tel="01 64 14 77 77", horaires="du lundi au vendredi, de 8h à 18h (numéro unique du Département)", page_apa="https://www.seine-et-marne.fr/fr/apa-domicile"),
}


def fetch(u):
    f = os.path.join(CACHE, re.sub(r"\W", "_", u)[-100:] + ".html")
    if not os.path.exists(f):
        r = subprocess.run(["curl", "-sL", "-A", UA, "-H", "Accept-Language: fr-FR,fr", "-m", "25", "-o", f, "-w", "%{http_code}", u], capture_output=True, text=True)
        open(f + ".code", "w").write(r.stdout); time.sleep(0.3)
    return open(f, errors="ignore").read() if os.path.exists(f) else ""


def T(x): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))).strip()


def norm(t):
    t = re.sub(r"\D", "", t or "")
    if t.startswith("330"): t = t[2:]
    elif t.startswith("33") and len(t) == 11: t = "0" + t[2:]
    return t


def joli(t):
    n = norm(t)
    if len(n) == 10: return " ".join(n[i:i + 2] for i in range(0, 10, 2)) if not n.startswith("08") or n[:4] not in ("0800", "0801", "0805", "0806") else n[:4] + " " + n[4:7] + " " + n[7:]
    return n


def numeros(s):
    s = T(re.sub(r"(?s)<(script|style).*?</\1>", " ", s))
    return {norm(m) for m in re.findall(r"(?:\+33\s?\(?0?\)?\s?|0)\d(?:[\s.\-]?\d){8}", s)} | {m.replace(" ", "") for m in re.findall(r"\b39 ?\d\d\b", s)}


def fiche(code, slug):
    u = f"{ANN}{slug}-{code.lower()}"
    s = fetch(u)
    i = s.find("app-coordinates")
    if i < 0: return None
    blk = s[i:s.find("app-icones-action", i)]
    g = lambda p: (lambda m: T(m.group(1)) if m else "")(re.search(p, blk, re.S))
    maj = re.search(r"Mis à jour le (\d\d/\d\d/\d{4})", T(s))
    return dict(url=u, maj=maj.group(1) if maj else "", rue=g(r'p-street-address">(.*?)</dd>'), cp=g(r'p-postal-code">(.*?)<'), ville=g(r'p-locality">(.*?)<'),
                tels=[T(t) for t in re.findall(r'p-tel">(.*?)<', blk)], site=(re.search(r'class="u-url" href="([^"]+)"', blk) or [None, ""])[1],
                liens=[(T(t), html.unescape(h)) for h, t in re.findall(r'<li[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></li>', blk)])


def job(code):
    d = DEPS[code]; f = fiche(code, d["slug"])
    page_apa = ""
    if f:
        apa = [u for t, u in f["liens"] if "APA" in t or "allocation personnalisée" in t.lower()]
        page_apa = apa[0] if apa else ""
    urls = [u for u in [page_apa, f and f["site"], d["cd"].get("site")] if u]
    vus = set()
    for u in dict.fromkeys(urls): vus |= numeros(fetch(u))
    out = dict(fiche=f["url"] if f else "", fiche_maj=f["maj"] if f else "", page_apa=page_apa, site=d["cd"].get("site") or (f and f["site"]) or "", verifie=VERIF)
    if f:
        segs = [x.strip() for x in f["rue"].split(" - ") if x.strip() and not x.strip().startswith("Pour ")]
        serv = [x for x in segs if re.search(r"Direction|Maison|Pôle|DGDS|Service", x)]
        out["service"] = serv[0] if serv else ""
        out["adresse"] = ", ".join([x for x in segs if x not in serv[:1]] + [f"{f['cp']} {f['ville']}".strip()])
        out["adresse"] = re.sub(r"\s*[–—]\s*", ", ", re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1-\2", out["adresse"]))
        out["service"] = re.sub(r"\s*[–—]\s*", ", ", out["service"])
    pa = [norm(t) for t in (f["tels"] if f else [])]
    sp = norm(d["cd"].get("tel"))
    if any(t in vus for t in pa): out["tel"], out["tel_lib"] = joli(next(t for t in pa if t in vus)), "service"
    elif sp and sp in vus: out["tel"], out["tel_lib"] = joli(sp), "standard"
    out["tel_src"] = "site" if out.get("tel") else ""
    return code, out


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    res = {}
    with cf.ThreadPoolExecutor(8) as ex:
        for code, o in ex.map(job, sorted(DEPS)): res[code] = o
    for code, m in MANUEL.items():
        res[code].update(m); res[code]["tel_lib"], res[code]["tel_src"] = "service", "manuel"
    json.dump(res, open(os.path.join(ROOT, "_data", "contacts_apa.json"), "w"), ensure_ascii=False, indent=1)
    print(sum(1 for o in res.values() if o.get("tel")), "/", len(res), "numéros vérifiés sur le site du département")
