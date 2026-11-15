#!/usr/bin/env python3
"""Statistiques officielles par département (DREES, INSEE, CNSA) -> _data/stats_dep.json.

Les fichiers sources sont téléchargés dans _build/.cache/ (non versionné). Relancer ce script
quand une source publie un nouveau millésime, puis departements.py ne change pas : build.py lit stats_dep.json.
"""
import json, os, re, ssl, statistics, sys, urllib.request
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "_build", ".cache")
os.makedirs(CACHE, exist_ok=True)
DREES = "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets"
SRC = {
    "paph": (f"{DREES}/les-beneficiaires-de-l-aide-sociale-departementale-aux-personnes-agees-ou-handic/attachments/paph_les_beneficiaires_de_l_aide_sociale_departementale_series_longues_1996_2024_xlsx", "paph_series.xlsx"),
    "dep": (f"{DREES}/376_les-depenses-d-aide-sociale-departementale/attachments/les_depenses_d_aide_sociale_departementale_series_longues_1999_2024_xlsx", "depenses_series.xlsx"),
    "isd": (f"{DREES}/639_personnes-agees/exports/json", "isd_personnes_agees.json"),
    "insee": ("https://www.insee.fr/fr/statistiques/fichier/8721456/estim-pop-dep-sexe-gca-1975-2026.xlsx", "insee_gca_2026.xlsx"),
    "vpg": ("https://www.cnsa.fr/sites/default/files/2026-06/PUB-Rapport_VPG-GMP_2025.pdf", "cnsa_vpg_2025.pdf"),
}


def get(k):
    url, fn = SRC[k]
    fp = os.path.join(CACHE, fn)
    if not os.path.exists(fp):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (aidermesparents.fr)"})
        open(fp, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    return fp


def code_norm(c):
    if c is None: return None
    c = str(c).strip()
    if re.fullmatch(r"\d", c): c = "0" + c
    return c


def xl_table(path, sheet, header_key="Code département"):
    """{code: {année: valeur}} pour un onglet DREES (une ligne par département, une colonne par année)."""
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and any(isinstance(c, str) and header_key in c for c in r))
    head = [str(c).strip() if c is not None else "" for c in rows[hi]]
    ic = next(i for i, h in enumerate(head) if header_key in h)
    out = {}
    for r in rows[hi + 1:]:
        c = r[ic] if ic < len(r) else None
        lab = " ".join(str(x) for x in r[:3] if x)
        if "France entière" in lab or "métropolitaine et DROM" in lab:
            c = "FR"
        c = code_norm(c)
        if not c or (c != "FR" and not re.fullmatch(r"\d{2,3}|2A|2B|69D|69M|6AE", c)): continue
        if c in out: continue
        vals = {}
        for i, h in enumerate(head):
            if re.fullmatch(r"(19|20)\d\d", h) and i < len(r) and isinstance(r[i], (int, float)):
                vals[int(h)] = r[i]
        out[c] = vals
    return out


def main():
    paph = get("paph"); dep = get("dep")
    apa_tot = xl_table(paph, "Tab4-pa"); apa_dom = xl_table(paph, "Tab5-pa"); apa_etab = xl_table(paph, "Tab6-pa"); ash = xl_table(paph, "Tab10-pa")
    dep_apa_tot = xl_table(dep, "PA-tab3"); dep_apa_dom = xl_table(dep, "PA-tab5")

    isd = json.load(open(get("isd"), encoding="utf-8"))
    I = {}
    for r in isd:
        c = r["code_dep"]
        if c == "NA":
            if r["lib_reg"] != "France entière hors Mayotte": continue
            c = "FR"
        try: v = float(r["value"])
        except (TypeError, ValueError): continue
        I.setdefault(c, {}).setdefault(r["id_indicateur"], {})[int(r["annee"])] = v

    wb = openpyxl.load_workbook(get("insee"), read_only=True, data_only=True)
    def insee(year):
        out = {}
        for r in wb[str(year)].iter_rows(values_only=True):
            if not r or r[0] is None: continue
            lab = str(r[0]).strip()
            if lab == "France métropolitaine et DOM": out["FR"] = (r[6], r[7]); continue
            c = code_norm(lab)
            if re.fullmatch(r"\d{2,3}|2A|2B", c) and isinstance(r[6], (int, float)): out[c] = (r[6], r[7])
        return out
    pop26, pop16 = insee(2026), insee(2016)

    import fitz  # PyMuPDF
    txt = "".join(p.get_text() for p in fitz.open(get("vpg")))
    a = txt.index("VP GIR 2025 \nVP GIR 2024"); b = txt.index("Valeurs moyennes du GMP par département")
    Ls = [l.strip() for l in txt[a:b].split("\n") if l.strip()]
    vpg = {}
    for i in range(len(Ls) - 4):
        if re.fullmatch(r"\d{2,3}|2A/2B|67/68|69M", Ls[i]) and re.fullmatch(r"\d+,\d\d €", Ls[i + 2]) and re.fullmatch(r"\d+,\d\d €", Ls[i + 3]):
            f = lambda s: float(s.replace(" €", "").replace(",", "."))
            for c in Ls[i].split("/"):  # « 2A/2B » (Corse) et « 67/68 » (Alsace) : une seule valeur pour les deux
                vpg[c] = (f(Ls[i + 2]), f(Ls[i + 3]))

    deps = [d["code"] for d in json.load(open(os.path.join(ROOT, "_data", "departements.json"), encoding="utf-8"))["departements"]]
    stats = {}
    def last(dct, key, an):
        return (dct.get(key) or {}).get(an)
    for code in deps:
        k = "69D" if code == "69" else code   # DREES : « Nouveau Rhône », hors Métropole de Lyon
        s = {}
        if code in pop26:
            p75, tot = pop26[code]; s["p75"] = p75; s["pop"] = tot; s["part75"] = round(p75 / tot * 100, 1)
            if code in pop16 and pop16[code][0]: s["p75_2016"] = pop16[code][0]
        for nom, tab in (("apa", apa_tot), ("apa_dom", apa_dom), ("apa_etab", apa_etab), ("ash", ash)):
            v = tab.get(k, {})
            if v.get(2024): s[nom] = int(round(v[2024]))
            if nom == "apa" and v.get(2014): s["apa_2014"] = int(round(v[2014]))
            if nom == "apa_dom" and v.get(2023): s["apa_dom_2023"] = int(round(v[2023]))
        dd = dep_apa_dom.get(k, {}).get(2024); dt_ = dep_apa_tot.get(k, {}).get(2024)
        if dt_: s["dep_apa"] = round(dt_ * 1000)
        if dd: s["dep_apa_dom"] = round(dd * 1000)
        if dd and s.get("apa_dom") and s.get("apa_dom_2023"):
            moy = dd * 1000 / ((s["apa_dom"] + s["apa_dom_2023"]) / 2) / 12
            if 150 <= moy <= 900: s["apa_dom_mois"] = round(moy)
        for nom, ind, an in (("tx75", "pa_part_benef_apa_tot_75p", 2024), ("tx75_dom", "pa_part_benef_apa_dom_75p", 2024),
                             ("gir12", "pa_part_benef_apa_dom_gir1_2", 2024), ("places", "pa_tx_equip_heberg_1000_75p", 2024),
                             ("ssiad", "pa_tx_equip_ssiad_spasad_1000_75p", 2025), ("seules75", "pa_repart_75p_seules", 2022),
                             ("instit75", "pa_repart_75p_institution", 2022)):
            v = last(I.get(k, {}), ind, an)
            if v is not None: s[nom] = v
        if code in vpg: s["vpg"] = vpg[code][0]; s["vpg_2024"] = vpg[code][1]
        if code == "69" and "69M" in vpg: s["vpg_metro"] = vpg["69M"][0]
        stats[code] = s

    nat = {"p75": pop26["FR"][0], "pop": pop26["FR"][1], "part75": round(pop26["FR"][0] / pop26["FR"][1] * 100, 1), "p75_2016": pop16["FR"][0],
           "apa": int(apa_tot["FR"][2024]), "apa_2014": int(apa_tot["FR"][2014]), "apa_dom": int(apa_dom["FR"][2024]), "apa_etab": int(apa_etab["FR"][2024])}
    for nom, ind, an in (("tx75", "pa_part_benef_apa_tot_75p", 2024), ("gir12", "pa_part_benef_apa_dom_gir1_2", 2024), ("places", "pa_tx_equip_heberg_1000_75p", 2024),
                         ("ssiad", "pa_tx_equip_ssiad_spasad_1000_75p", 2025), ("seules75", "pa_repart_75p_seules", 2022)):
        nat[nom] = I["FR"][ind][an]
    vals = [s["apa_dom_mois"] for s in stats.values() if "apa_dom_mois" in s]
    nat["apa_dom_mois_med"] = round(statistics.median(vals))
    fr = dep_apa_dom["FR"]
    nat["apa_dom_mois"] = round(fr[2024] * 1000 / ((apa_dom["FR"][2024] + apa_dom["FR"][2023]) / 2) / 12)
    for key in ("tx75", "places", "gir12", "seules75", "ssiad", "apa_dom_mois", "part75"):  # rangs (1 = valeur la plus élevée)
        ordre = sorted((c for c in stats if key in stats[c] and c not in ("69",) or (c == "69" and key in stats[c] and key not in ("part75",))), key=lambda c: -stats[c][key])
        for i, c in enumerate(ordre): stats[c]["rang_" + key] = [i + 1, len(ordre)]
    nat["vpg_med"] = 7.63  # CNSA, rapport VPG-GMP 2025, page 4 (valeur médiane publiée)
    nat["vpg_moy"] = 7.73
    json.dump({"national": nat, "stats": stats}, open(os.path.join(ROOT, "_data", "stats_dep.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("national", nat)
    for key in ("p75", "apa", "apa_dom", "apa_etab", "ash", "apa_2014", "apa_dom_mois", "tx75", "gir12", "places", "ssiad", "seules75", "vpg"):
        manque = [c for c in deps if key not in stats[c]]
        print(f"{key:13s} manque {len(manque):3d} {manque[:12]}")
    for c in ("01", "59", "69", "75", "2A", "974", "976", "67"):
        print(c, stats[c])


if __name__ == "__main__":
    main()
