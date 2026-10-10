#!/usr/bin/env python3
"""Genera dalil/index.html: guía halal de Kansai en árabe.

Datos: datos/lugares.json (exportado de Halal Kansai, src/modules/places/data.ts)
y datos/lugares-ar.json (nombres y notas en árabe). Regenerar tras tocar los datos:
    python3 guia.py
"""
import html
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
URL = "https://2troll.github.io/yubisashi/dalil/"
TOURS = "https://tonykansaiguide.com/ar/"
WHATSAPP = "https://wa.me/34634193106"

CIUDADES = {"Osaka": "أوساكا", "Kyoto": "كيوتو", "Kobe": "كوبي", "Nara": "نارا",
            "Izumisano": "إيزوميسانو (مطار كانساي)", "Ibaraki": "إيباراكي", "Kusatsu": "كوساتسو",
            "Miki": "ميكي", "Yawata": "ياواتا", "Suita": "سويتا", "Sango": "سانغو"}
TIPOS = {"mosque": ("🕌", "مسجد"), "prayer": ("🧎", "مصلى"),
         "restaurant": ("🍽️", "مطعم"), "shop": ("🛍️", "متجر")}
ORDEN_TIPO = ["mosque", "prayer", "restaurant", "shop"]


def tarjeta(p: dict, ar: dict) -> str:
    icono, tipo = TIPOS[p["type"]]
    notas = f'<p>{html.escape(ar["notes_ar"])}</p>' if ar["notes_ar"] else ""
    jumuah = f'<p class="j">صلاة الجمعة: {html.escape(ar["jumuah_ar"])}</p>' if ar["jumuah_ar"] else ""
    mapa = (f'<a class="mapa" href="https://www.google.com/maps/search/?api=1&amp;query={p["lat"]},{p["lng"]}" '
            f'target="_blank" rel="noopener">فتح في خرائط Google</a>') if p.get("lat") else ""
    fuente = ('<span class="ok">✔ من الموقع الرسمي</span>' if p["verified"]
              else '<span class="ext">من دليل خارجي، يرجى التأكد قبل الزيارة</span>')
    return (f'<article class="c"><div class="t"><span class="tipo">{icono} {tipo}</span>{fuente}</div>'
            f'<h3>{html.escape(ar["name_ar"])}</h3><div class="lat" dir="ltr">{html.escape(p["name"])}</div>'
            f'{notas}{jumuah}{mapa}</article>')


def main() -> None:
    lugares = json.loads((AQUI / "datos/lugares.json").read_text(encoding="utf-8"))
    arabe = json.loads((AQUI / "datos/lugares-ar.json").read_text(encoding="utf-8"))
    faltan = [p["id"] for p in lugares if p["id"] not in arabe]
    if faltan:
        raise SystemExit(f"Faltan traducciones para: {', '.join(faltan)}")

    por_ciudad: dict[str, list] = {}
    for p in lugares:
        por_ciudad.setdefault(p["city"], []).append(p)
    ciudades = sorted(por_ciudad, key=lambda c: -len(por_ciudad[c]))

    indice = " · ".join(f'<a href="#{c}">{CIUDADES.get(c, c)}</a>' for c in ciudades)
    secciones = ""
    for c in ciudades:
        ps = sorted(por_ciudad[c], key=lambda p: ORDEN_TIPO.index(p["type"]))
        secciones += (f'<section id="{c}"><h2>{CIUDADES.get(c, c)} <small>({len(ps)})</small></h2>'
                      f'<div class="g">{"".join(tarjeta(p, arabe[p["id"]]) for p in ps)}</div></section>')

    n = {t: sum(p["type"] == t for p in lugares) for t in TIPOS}
    desc = (f"دليل الحلال في أوساكا وكيوتو وكوبي ونارا: {n['mosque']} مسجدًا و{n['prayer']} مصلى "
            f"و{n['restaurant']} مطعمًا حلالًا، مع روابط الخرائط. محدث سبتمبر 2026.")
    pagina = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>دليل الحلال في كانساي — مطاعم حلال ومساجد في أوساكا وكيوتو</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{URL}">
<meta property="og:title" content="دليل الحلال في كانساي — أوساكا وكيوتو وكوبي ونارا">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL}">
<style>
:root{{--accent:#1f5f5b;--bg:#fbf8f2;--card:#fff;--ink:#1d1f22;--mute:#5d6166;--line:#e3dccd;--ok:#2f7d4f;--warn:#9a6a12}}
@media (prefers-color-scheme:dark){{:root{{--accent:#6cc2b8;--bg:#15191a;--card:#1f2526;--ink:#eef0ee;--mute:#a7adaa;--line:#2f3739;--ok:#7fd3a0;--warn:#e7b65c}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Geeza Pro","Noto Naskh Arabic","Segoe UI",system-ui,sans-serif;line-height:1.7}}
.w{{max-width:1040px;margin:0 auto;padding:0 16px 48px}}
header{{padding:32px 0 8px}}h1{{font-size:clamp(1.6rem,5vw,2.4rem);margin:0 0 8px;color:var(--accent)}}
.lead{{color:var(--mute);margin:0 0 16px}}
.cta{{background:var(--accent);color:#fff;border-radius:16px;padding:16px 18px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;margin:12px 0 20px}}
@media (prefers-color-scheme:dark){{.cta{{color:#0d1213}}}}
.cta a{{background:#fff;color:#1f5f5b;text-decoration:none;font-weight:700;padding:10px 16px;border-radius:99px;white-space:nowrap}}
nav{{font-size:.95rem;margin:8px 0 8px;line-height:2.2}}nav a{{color:var(--accent)}}
h2{{border-bottom:2px solid var(--accent);padding-bottom:4px;margin-top:32px}}h2 small{{color:var(--mute);font-weight:400}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}}
.c{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}}
.c h3{{margin:6px 0 0;font-size:1.15rem}}.lat{{color:var(--mute);font-size:.85rem;text-align:right}}
.c p{{margin:6px 0}}.j{{color:var(--accent);font-weight:700}}
.t{{display:flex;justify-content:space-between;gap:8px;font-size:.8rem;flex-wrap:wrap}}
.tipo{{font-weight:700}}.ok{{color:var(--ok)}}.ext{{color:var(--warn)}}
.mapa{{display:inline-block;margin-top:6px;color:var(--accent);font-weight:700}}
footer{{margin-top:40px;color:var(--mute);font-size:.85rem;border-top:1px solid var(--line);padding-top:12px}}
footer a{{color:var(--accent)}}
</style>
</head>
<body><div class="w">
<header>
<h1>دليل الحلال في كانساي</h1>
<p class="lead">{n['mosque']} مسجدًا و{n['prayer']} مصلى و{n['restaurant']} مطعمًا حلالًا و{n['shop']} متاجر في أوساكا وكيوتو وكوبي ونارا. كل معلومة مأخوذة من الموقع الرسمي للمكان أو من أدلة موثوقة، ومحدثة في سبتمبر 2026.</p>
<div class="cta"><div><strong>هل تزور أوساكا أو كيوتو؟</strong><br>جولات خاصة باللغة العربية مع توني، مع مطاعم حلال وأوقات الصلاة في البرنامج.</div>
<div><a href="{TOURS}">الجولات بالعربية</a> <a href="{WHATSAPP}">واتساب</a></div></div>
<nav>المدن: {indice}</nav>
</header>
{secciones}
<footer>
<p>يرجى التأكد من مواعيد العمل قبل الزيارة، فقد تتغير المعلومات. المطاعم المذكورة لا تقدم الكحول.</p>
<p>إعداد: توني هانما، مرشد سياحي في أوساكا · <a href="{TOURS}">tonykansaiguide.com</a> · <a href="https://2troll.github.io/yubisashi/">تطبيق المحادثة للمطاعم</a></p>
</footer>
</div></body></html>
'''
    destino = AQUI / "dalil" / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(pagina, encoding="utf-8")
    print(f"{len(lugares)} lugares en {len(ciudades)} ciudades → {destino}")


if __name__ == "__main__":
    main()
