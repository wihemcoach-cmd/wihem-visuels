#!/usr/bin/env python3
"""Rendu des visuels Wihem · Multipotentielle.
Usage : python3 tools/render.py spec.json [dossier_sortie]
Prérequis : cd tools && npm install @fontsource/bricolage-grotesque @fontsource/dm-sans ; pip install playwright pillow
Spec : {"name":"post-08","type":"carousel"|"image","photo":"ruelle",
 "cover":{"label":"..","l1":"..","l2":"..","size":150},   # carrousel : couverture (photo plein cadre)
 "slides":[{"kind":"creme|dark|bord","label":"..","h":"..","sub":".."}],  # slides 2..N-1 ; la dernière (signature) est ajoutée automatiquement
 "recap":["..",".."],   # optionnel : slide 'À retenir' avant la signature
 "image":{"l1":"..","l2":"..","pos":"center 25%"}}    # image seule : photo plein cadre + 2 lignes
Les photos sont dans photos/<nom>.jpg. Sortie : slideN.jpg (carrousel) ou image.jpg, en 1080x1350."""
import asyncio, os, sys, json
from playwright.async_api import async_playwright
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
F=f"file://{HERE}/node_modules/@fontsource"
CREME,BORD,DARK,B2,CHAMP,BEIGE="#F6EFE7","#6E1428","#2A0B14","#8C2A3E","#E3C59B","#E8DCCD"
CSS=f"""@font-face{{font-family:'Bric';font-weight:800;src:url({F}/bricolage-grotesque/files/bricolage-grotesque-latin-800-normal.woff2)}}
@font-face{{font-family:'DM';font-weight:700;src:url({F}/dm-sans/files/dm-sans-latin-700-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}.s{{width:1080px;height:1350px;position:relative;overflow:hidden}}
.blob{{position:absolute;border-radius:50%}}
.t{{position:absolute;left:110px;right:110px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;font-family:'DM';font-weight:700;line-height:1.18;padding-top:60px}}
.t b{{font-family:'Bric';font-weight:800;letter-spacing:-2px;line-height:1.04}}
.foot{{position:absolute;left:110px;right:110px;bottom:64px;display:flex;justify-content:space-between;font-family:'DM';font-weight:700;font-size:28px;letter-spacing:.2em}}
.lab{{position:absolute;left:110px;top:130px;font-family:'DM';font-weight:700;font-size:30px;letter-spacing:.22em}}
img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.g{{position:absolute;inset:0}}"""
def deco(k):
    return {"dark":f"<div class=blob style='width:700px;height:700px;right:-260px;top:-240px;background:{BORD};opacity:.8'></div>",
     "creme":f"<div class=blob style='width:640px;height:640px;right:-260px;top:-230px;background:{BEIGE}'></div>",
     "bord":f"<div class=blob style='width:700px;height:700px;left:-260px;top:-240px;background:{B2};opacity:.55'></div>"}[k]
def big(t,sz,c): return f"<b style='font-size:{sz}px;color:{c}'>{t}</b>"
def sm(t,sz,mt=34): return f"<span style='font-size:{sz}px;margin-top:{mt}px'>{t}</span>"
def S(k,lab,body,n,N):
    bg={"dark":DARK,"creme":CREME,"bord":BORD}[k]; fg=DARK if k=="creme" else CREME; acc=BORD if k=="creme" else CHAMP
    return f"<div class=s style='background:{bg};color:{fg}'>{deco(k)}<div class=lab style='color:{acc}'>{lab}</div><div class=t>{body}</div><div class=foot style='color:{acc}'><span>WIHEM · MULTIPOTENTIELLE</span><span>{n}/{N}</span></div></div>"
def cover(ph,c):
    s=c.get("size",150)
    return f"<div class=s><img src='file://{ROOT}/photos/{ph}.jpg' style='object-position:{c.get('pos','center top')}'><div class=g style='background:linear-gradient(180deg,rgba(42,11,20,.55) 0%,rgba(42,11,20,0) 30%,rgba(42,11,20,.35) 55%,rgba(42,11,20,.95) 100%)'></div><div class=lab style='color:{CHAMP}'>{c['label']}</div><div class=t style='justify-content:flex-end;padding-bottom:170px'><b style='font-size:{s}px;color:{CREME}'>{c['l1']}</b><b style='font-size:{s}px;color:{CHAMP}'>{c['l2']}</b></div><div class=foot style='color:{CHAMP}'><span>WIHEM · MULTIPOTENTIELLE</span><span>GLISSE →</span></div></div>"
def image(ph,i):
    s=i.get("size",104)
    return f"<div class=s><img src='file://{ROOT}/photos/{ph}.jpg' style='object-position:{i.get('pos','center 25%')}'><div class=g style='background:linear-gradient(180deg,rgba(42,11,20,0) 40%,rgba(42,11,20,.9) 100%)'></div><div class=t style='justify-content:flex-end;padding-bottom:170px'><b style='font-size:{s}px;color:{CREME}'>{i['l1']}</b><b style='font-size:{s}px;color:{CHAMP}'>{i['l2']}</b></div><div class=foot style='color:{CHAMP}'><span>WIHEM · MULTIPOTENTIELLE</span></div></div>"
def build(spec):
    if spec["type"]=="image": return [image(spec["photo"],spec["image"])]
    sl=spec["slides"]; rec=spec.get("recap"); N=len(sl)+2+(1 if rec else 0)
    out=[cover(spec["photo"],spec["cover"])]
    for i,x in enumerate(sl,2):
        c=BORD if x["kind"]=="creme" else CHAMP
        out.append(S(x["kind"],x["label"],big(x["h"],96,c)+sm(x["sub"],56,50),i,N))
    n=len(out)+1
    if rec:
        lis="<br>".join(f"<b style='color:{BORD}'>{j}.</b> {t}" for j,t in enumerate(rec,1))
        out.append(S("creme","À RETENIR",f"<span style='font-size:62px;line-height:1.5;color:{DARK}'>{lis}</span>",n,N)); n+=1
    out.append(S("creme","",big("Ta place",150,BORD)+big("n'est pas dans",150,DARK)+big("une case.",150,BORD),n,N))
    return out
async def main(specf,outdir):
    spec=json.load(open(specf)); d=os.path.join(outdir,spec["name"]); os.makedirs(d,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1080,"height":1350})
        for i,t in enumerate(build(spec),1):
            tmp=os.path.join(d,"_t.html"); open(tmp,"w").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{t}</body></html>")
            await pg.goto("file://"+tmp); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            name="image" if spec["type"]=="image" else f"slide{i}"
            await pg.screenshot(path=os.path.join(d,name+".png"))
            Image.open(os.path.join(d,name+".png")).convert("RGB").save(os.path.join(d,name+".jpg"),quality=92); os.remove(os.path.join(d,name+".png")); os.remove(tmp)
        await b.close()
    print("OK",d)
asyncio.run(main(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,"out")))
