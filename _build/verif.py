#!/usr/bin/env python3
"""Contrôles SEO et qualité sur docs/ : à lancer après build.py."""
import glob, os, re, json, collections
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
pb = []; titres = collections.Counter(); descs = collections.Counter(); h1s = collections.Counter()
existe = lambda p: os.path.exists(os.path.join(OUT, p.strip("/"), "index.html")) or p == "/"
for f in glob.glob(OUT + "/**/index.html", recursive=True):
    p = "/" + os.path.relpath(os.path.dirname(f), OUT).replace(".", "") + "/"
    p = p.replace("//", "/")
    h = open(f, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)</title>", h).group(1); d = re.search(r'name="description" content="(.*?)"', h).group(1)
    titres[t] += 1; descs[d] += 1
    n1 = len(re.findall(r"<h1[ >]", h)); h1s[re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1)] += 1
    if n1 != 1: pb.append((p, f"{n1} H1"))
    if len(t) > 62: pb.append((p, f"title {len(t)} car."))
    if len(d) > 160: pb.append((p, f"description {len(d)} car."))
    if re.search("[—–]", re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S).replace("details[open] summary:after{content:\"–\"}", "")): pb.append((p, "tiret long"))
    for a in re.findall(r'href="(/[^"#?]*)', h):
        if a.endswith((".css", ".svg", ".jpg", ".txt", ".xml")): continue
        if not existe(a): pb.append((p, f"lien cassé {a}"))
    for img in re.findall(r"<img [^>]*>", h):
        if 'alt="' not in img: pb.append((p, "image sans alt"))
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try: json.loads(s)
        except Exception: pb.append((p, "JSON-LD invalide"))
for c, txt in ((titres, "title"), (descs, "description"), (h1s, "H1")):
    for k, v in c.items():
        if v > 1: pb.append(("*", f"{txt} en double : {k[:60]}"))
print(len(set(x[0] for x in pb)), "pages avec problème" if pb else "aucun problème")
for p, m in sorted(set(pb)): print(" ", p, "|", m)
