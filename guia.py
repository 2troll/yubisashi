#!/usr/bin/env python3
"""Genera la guía halal de Kansai en árabe (dalil/) y en indonesio (panduan/).

Datos: datos/lugares.json (exportado de Halal Kansai, src/modules/places/data.ts)
más una traducción por idioma (datos/lugares-ar.json, datos/lugares-id.json).
Regenerar tras tocar los datos:
    python3 guia.py
"""
import html
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = "https://2troll.github.io/yubisashi/"
WHATSAPP = "https://wa.me/34634193106"
TIPOS_ORDEN = ["mosque", "prayer", "restaurant", "shop"]
ICONOS = {"mosque": "🕌", "prayer": "🧎", "restaurant": "🍽️", "shop": "🛍️"}

# Tony no guía en indonesio: a ese público se le ofrece el tour en inglés.
IDIOMAS = {
    "ar": {
        "carpeta": "dalil", "dir": "rtl", "tours": "https://tonykansaiguide.com/ar/",
        "fuente": '"Geeza Pro","Noto Naskh Arabic","Segoe UI",system-ui,sans-serif',
        "ciudades": {"Osaka": "أوساكا", "Kyoto": "كيوتو", "Kobe": "كوبي", "Nara": "نارا",
                     "Izumisano": "إيزوميسانو (مطار كانساي)", "Ibaraki": "إيباراكي", "Kusatsu": "كوساتسو",
                     "Miki": "ميكي", "Yawata": "ياواتا", "Suita": "سويتا", "Sango": "سانغو"},
        "tipos": {"mosque": "مسجد", "prayer": "مصلى", "restaurant": "مطعم", "shop": "متجر"},
        "titulo": "دليل الحلال في كانساي — مطاعم حلال ومساجد في أوساكا وكيوتو",
        "og": "دليل الحلال في كانساي — أوساكا وكيوتو وكوبي ونارا",
        "h1": "دليل الحلال في كانساي",
        "desc": "دليل الحلال في أوساكا وكيوتو وكوبي ونارا: {mosque} مسجدًا و{prayer} مصلى و{restaurant} مطعمًا حلالًا، مع روابط الخرائط. محدث سبتمبر 2026.",
        "lead": "{mosque} مسجدًا و{prayer} مصلى و{restaurant} مطعمًا حلالًا و{shop} متاجر في أوساكا وكيوتو وكوبي ونارا. كل معلومة مأخوذة من الموقع الرسمي للمكان أو من أدلة موثوقة، ومحدثة في سبتمبر 2026.",
        "cta": "<strong>هل تزور أوساكا أو كيوتو؟</strong><br>جولات خاصة باللغة العربية مع توني، مع مطاعم حلال وأوقات الصلاة في البرنامج.",
        "cta_tours": "الجولات بالعربية", "cta_wa": "واتساب",
        "ciudades_t": "المدن:", "jumuah": "صلاة الجمعة:", "mapa": "فتح في خرائط Google",
        "ok": "✔ من الموقع الرسمي", "ext": "من دليل خارجي، يرجى التأكد قبل الزيارة",
        "aviso": "يرجى التأكد من مواعيد العمل قبل الزيارة، فقد تتغير المعلومات. المطاعم المذكورة لا تقدم الكحول.",
        "autor": "إعداد: توني هانما، مرشد سياحي في أوساكا",
        "app": "تطبيق المحادثة للمطاعم", "otra": "Bahasa Indonesia",
    },
    "id": {
        "carpeta": "panduan", "dir": "ltr", "tours": "https://tonykansaiguide.com/en/",
        "fuente": 'system-ui,"Segoe UI","Helvetica Neue",sans-serif',
        "ciudades": {"Osaka": "Osaka", "Kyoto": "Kyoto", "Kobe": "Kobe", "Nara": "Nara",
                     "Izumisano": "Izumisano (Bandara Kansai)", "Ibaraki": "Ibaraki", "Kusatsu": "Kusatsu",
                     "Miki": "Miki", "Yawata": "Yawata", "Suita": "Suita", "Sango": "Sango"},
        "tipos": {"mosque": "Masjid", "prayer": "Ruang salat", "restaurant": "Restoran", "shop": "Toko"},
        "titulo": "Panduan Halal Kansai — Restoran Halal dan Masjid di Osaka, Kyoto",
        "og": "Panduan Halal Kansai — Osaka, Kyoto, Kobe, Nara",
        "h1": "Panduan Halal Kansai",
        "desc": "Panduan halal Osaka, Kyoto, Kobe dan Nara: {mosque} masjid, {prayer} ruang salat dan {restaurant} restoran halal, dengan tautan peta. Diperbarui September 2026.",
        "lead": "{mosque} masjid, {prayer} ruang salat, {restaurant} restoran halal dan {shop} toko di Osaka, Kyoto, Kobe dan Nara. Setiap data diambil dari situs resmi tempat tersebut atau panduan tepercaya, diperbarui September 2026.",
        "cta": "<strong>Berkunjung ke Osaka atau Kyoto?</strong><br>Tur privat dalam bahasa Inggris bersama Tony, pemandu Muslim di Osaka — restoran halal dan waktu salat sudah masuk jadwal.",
        "cta_tours": "Lihat tur", "cta_wa": "WhatsApp",
        "ciudades_t": "Kota:", "jumuah": "Salat Jumat:", "mapa": "Buka di Google Maps",
        "ok": "✔ Dari situs resmi", "ext": "Dari panduan pihak ketiga, mohon cek sebelum berkunjung",
        "aviso": "Mohon cek jam buka sebelum berkunjung, informasi bisa berubah. Restoran dalam daftar ini tidak menyajikan alkohol.",
        "autor": "Disusun oleh Tony Hanma, pemandu wisata di Osaka",
        "app": "Aplikasi percakapan untuk restoran", "otra": "العربية",
    },
}


def tarjeta(p: dict, tr: dict, t: dict, lang: str) -> str:
    nombre, notas_t, jumuah_t = (tr[f"{k}_{lang}"] for k in ("name", "notes", "jumuah"))
    latino = f'<div class="lat" dir="ltr">{html.escape(p["name"])}</div>' if lang == "ar" else ""
    notas = f"<p>{html.escape(notas_t)}</p>" if notas_t else ""
    jumuah = f'<p class="j">{t["jumuah"]} {html.escape(jumuah_t)}</p>' if jumuah_t else ""
    mapa = (f'<a class="mapa" href="https://www.google.com/maps/search/?api=1&amp;query={p["lat"]},{p["lng"]}" '
            f'target="_blank" rel="noopener">{t["mapa"]}</a>') if p.get("lat") else ""
    fuente = f'<span class="ok">{t["ok"]}</span>' if p["verified"] else f'<span class="ext">{t["ext"]}</span>'
    return (f'<article class="c"><div class="t"><span class="tipo">{ICONOS[p["type"]]} {t["tipos"][p["type"]]}</span>{fuente}</div>'
            f'<h3>{html.escape(nombre)}</h3>{latino}{notas}{jumuah}{mapa}</article>')


def pagina(lang: str, lugares: list, tr: dict) -> str:
    t = IDIOMAS[lang]
    url = BASE + t["carpeta"] + "/"
    otro = "id" if lang == "ar" else "ar"
    url_otra = BASE + IDIOMAS[otro]["carpeta"] + "/"

    por_ciudad: dict[str, list] = {}
    for p in lugares:
        por_ciudad.setdefault(p["city"], []).append(p)
    ciudades = sorted(por_ciudad, key=lambda c: -len(por_ciudad[c]))
    indice = " · ".join(f'<a href="#{c}">{t["ciudades"].get(c, c)}</a>' for c in ciudades)
    secciones = ""
    for c in ciudades:
        ps = sorted(por_ciudad[c], key=lambda p: TIPOS_ORDEN.index(p["type"]))
        secciones += (f'<section id="{c}"><h2>{t["ciudades"].get(c, c)} <small>({len(ps)})</small></h2>'
                      f'<div class="g">{"".join(tarjeta(p, tr[p["id"]], t, lang) for p in ps)}</div></section>')

    n = {k: sum(p["type"] == k for p in lugares) for k in TIPOS_ORDEN}
    desc = t["desc"].format(**n)
    alineado = "right" if t["dir"] == "rtl" else "left"
    return f'''<!doctype html>
<html lang="{lang}" dir="{t["dir"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t["titulo"]}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="{lang}" href="{url}">
<link rel="alternate" hreflang="{otro}" href="{url_otra}">
<meta property="og:title" content="{t["og"]}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<style>
:root{{--accent:#1f5f5b;--bg:#fbf8f2;--card:#fff;--ink:#1d1f22;--mute:#5d6166;--line:#e3dccd;--ok:#2f7d4f;--warn:#9a6a12}}
@media (prefers-color-scheme:dark){{:root{{--accent:#6cc2b8;--bg:#15191a;--card:#1f2526;--ink:#eef0ee;--mute:#a7adaa;--line:#2f3739;--ok:#7fd3a0;--warn:#e7b65c}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:{t["fuente"]};line-height:1.7}}
.w{{max-width:1040px;margin:0 auto;padding:0 16px 48px}}
header{{padding:32px 0 8px}}h1{{font-size:clamp(1.6rem,5vw,2.4rem);margin:0 0 8px;color:var(--accent)}}
.lead{{color:var(--mute);margin:0 0 16px}}
.cta{{background:var(--accent);color:#fff;border-radius:16px;padding:16px 18px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;margin:12px 0 20px}}
@media (prefers-color-scheme:dark){{.cta{{color:#0d1213}}}}
.cta a{{background:#fff;color:#1f5f5b;text-decoration:none;font-weight:700;padding:10px 16px;border-radius:99px;white-space:nowrap}}
nav{{font-size:.95rem;margin:8px 0;line-height:2.2}}nav a{{color:var(--accent)}}
h2{{border-bottom:2px solid var(--accent);padding-bottom:4px;margin-top:32px}}h2 small{{color:var(--mute);font-weight:400}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}}
.c{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}}
.c h3{{margin:6px 0 0;font-size:1.15rem}}.lat{{color:var(--mute);font-size:.85rem;text-align:{alineado}}}
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
<h1>{t["h1"]}</h1>
<p class="lead">{t["lead"].format(**n)}</p>
<div class="cta"><div>{t["cta"]}</div>
<div><a href="{t["tours"]}">{t["cta_tours"]}</a> <a href="{WHATSAPP}">{t["cta_wa"]}</a></div></div>
<nav>{t["ciudades_t"]} {indice} · <a href="{url_otra}" lang="{otro}">{t["otra"]}</a></nav>
</header>
{secciones}
<footer>
<p>{t["aviso"]}</p>
<p>{t["autor"]} · <a href="{t["tours"]}">tonykansaiguide.com</a> · <a href="{BASE}">{t["app"]}</a></p>
</footer>
</div></body></html>
'''


def main() -> None:
    lugares = json.loads((AQUI / "datos/lugares.json").read_text(encoding="utf-8"))
    for lang, t in IDIOMAS.items():
        tr = json.loads((AQUI / f"datos/lugares-{lang}.json").read_text(encoding="utf-8"))
        faltan = [p["id"] for p in lugares if p["id"] not in tr]
        if faltan:
            raise SystemExit(f"[{lang}] faltan traducciones para: {', '.join(faltan)}")
        destino = AQUI / t["carpeta"] / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(pagina(lang, lugares, tr), encoding="utf-8")
        print(f"[{lang}] {len(lugares)} lugares → {destino}")


if __name__ == "__main__":
    main()
