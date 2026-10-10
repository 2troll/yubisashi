#!/usr/bin/env python3
"""Mapa halal A4 (japonés, árabe e inglés) alrededor de una estación, para hoteles.

Uso:
    python3 mapa.py kyoto            # una estación de la lista
    python3 mapa.py todas            # todas
    python3 mapa.py kyoto --km 3     # radio distinto (por defecto 2 km)
Sale mapas/<estacion>.pdf (y el .html del que se imprime). Cada lugar lleva un
QR que lo abre en Google Maps. Datos: datos/lugares.json + datos/lugares-ar.json.
"""
import argparse
import html
import json
import math
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

ESTACIONES = {
    "namba": ("難波駅", "محطة نامبا", "Namba Station", 34.6659, 135.5013),
    "umeda": ("大阪・梅田駅", "محطة أوساكا (أوميدا)", "Osaka / Umeda Station", 34.7025, 135.4959),
    "shin-osaka": ("新大阪駅", "محطة شين أوساكا", "Shin-Osaka Station", 34.7334, 135.5001),
    "kyoto": ("京都駅", "محطة كيوتو", "Kyoto Station", 34.9858, 135.7588),
    "gion": ("祇園四条駅", "محطة غيون شيجو", "Gion-Shijo Station", 35.0037, 135.7722),
    "sannomiya": ("三宮駅", "محطة سانوميا", "Sannomiya Station (Kobe)", 34.6946, 135.1953),
    "nara": ("近鉄奈良駅", "محطة كينتيتسو نارا", "Kintetsu-Nara Station", 34.6845, 135.8270),
}
TIPOS = {"mosque": ("モスク", "مسجد"), "prayer": ("礼拝室", "مصلى"),
         "restaurant": ("レストラン", "مطعم"), "shop": ("ショップ", "متجر")}
VELOCIDAD_M_MIN = 80  # paso normal; da minutos andando aproximados


def km(a, b):
    r = math.radians
    dlat, dlng = r(b[0] - a[0]), r(b[1] - a[1])
    h = math.sin(dlat / 2) ** 2 + math.cos(r(a[0])) * math.cos(r(b[0])) * math.sin(dlng / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def qr_svg(url: str) -> str:
    salida = subprocess.run(["qrencode", "-t", "SVG", "-m", "1", "-o", "-", url],
                            capture_output=True, text=True, check=True).stdout
    return salida[salida.index("<svg"):]


def hacer(clave: str, radio: float, lugares: list, ar: dict) -> None:
    ja, ar_nombre, en, lat, lng = ESTACIONES[clave]
    cerca = sorted(((km((lat, lng), (p["lat"], p["lng"])), p) for p in lugares if p.get("lat")),
                   key=lambda x: x[0])
    cerca = [(d, p) for d, p in cerca if d <= radio][:8]
    if not cerca:
        print(f"{clave}: ningún lugar a menos de {radio} km; prueba con --km mayor")
        return
    # Las notas largas no caben: se quita el lugar más lejano hasta que el PDF tenga una página.
    while True:
        pdf = imprimir(clave, cerca, ja, ar_nombre, en, ar)
        if paginas(pdf) == 1 or len(cerca) == 1:
            break
        cerca = cerca[:-1]
    print(f"{clave}: {len(cerca)} lugares a menos de {radio} km → {pdf}")


def paginas(pdf: Path) -> int:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages:")))


def imprimir(clave, cerca, ja, ar_nombre, en, ar) -> Path:
    tarjetas = ""
    for i, (d, p) in enumerate(cerca, 1):
        minutos = round(d * 1000 / VELOCIDAD_M_MIN)
        tja, tar = TIPOS[p["type"]]
        t = ar[p["id"]]
        url = f"https://www.google.com/maps/search/?api=1&query={p['lat']},{p['lng']}"
        aviso = "" if p["verified"] else " · 第三者ガイドの情報 / من دليل خارجي"
        tarjetas += f'''<div class="c"><div class="qr">{qr_svg(url)}</div><div class="t">
<div class="h"><b>{i}. {html.escape(p["name"])}</b><span class="tag">{tja} · {tar}</span></div>
<div class="ar"><b>{html.escape(t["name_ar"])}</b>{" — " + html.escape(t["notes_ar"]) if t["notes_ar"] else ""}</div>
<div class="en">{html.escape(p["notes"])} · ~{minutos} min walk / 徒歩約{minutos}分{aviso}</div></div></div>'''

    pagina = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><title>{ja}周辺 ハラールマップ</title><style>
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:"Hiragino Sans","Noto Sans JP","Geeza Pro",sans-serif;color:#1d1f22}}
.page{{width:210mm;height:297mm;padding:13mm 14mm;position:relative}}
header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #1f5f5b;padding-bottom:3mm;margin-bottom:4mm}}
h1{{margin:0;font-size:18pt}}.sub{{font-size:9pt;color:#5d6166}}.ar{{direction:rtl;text-align:right;font-family:"Geeza Pro","Noto Naskh Arabic",serif;font-size:10.5pt;margin:1mm 0}}
header .ar{{font-size:16pt;color:#1f5f5b;font-weight:700}}
.c{{display:flex;gap:3.5mm;padding:2.8mm;border:1px solid #e3dccd;border-radius:3mm;margin-bottom:2.4mm;background:#fbf8f2}}
.qr svg{{width:20mm;height:20mm}}.t{{flex:1}}.h{{display:flex;justify-content:space-between;gap:2mm;font-size:10.5pt}}
.tag{{font-size:8pt;color:#1f5f5b;border:1px solid #1f5f5b;border-radius:99px;padding:.4mm 2.2mm;white-space:nowrap;height:fit-content}}
.en{{font-size:8pt;color:#5d6166}}footer{{position:absolute;bottom:9mm;left:14mm;right:14mm;font-size:7.5pt;color:#5d6166;border-top:1px solid #e3dccd;padding-top:2mm}}
</style><div class="page"><header><div><h1>{ja}周辺 ハラールマップ</h1><div class="sub">Halal map around {en} · QRでGoogleマップが開きます</div></div>
<div class="ar">خريطة الحلال حول {ar_nombre}</div></header>
{tarjetas}
<footer>情報は2026年9月時点。ご来店前に営業時間をご確認ください。 · المعلومات حتى سبتمبر 2026، يرجى التأكد من مواعيد العمل قبل الزيارة. · Details as of Sept 2026, please check opening hours.<br>
制作：Tony Hanma · tony@tonykansaiguide.com · 全リスト / القائمة الكاملة: 2troll.github.io/yubisashi/dalil/</footer></div></html>'''

    carpeta = AQUI / "mapas"
    carpeta.mkdir(exist_ok=True)
    html_ruta, pdf_ruta = carpeta / f"{clave}.html", carpeta / f"{clave}.pdf"
    html_ruta.write_text(pagina, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_ruta}", str(html_ruta)], capture_output=True, check=True)
    return pdf_ruta


def main() -> None:
    ap = argparse.ArgumentParser(description="Mapa halal A4 alrededor de una estación")
    ap.add_argument("estacion", help="|".join(ESTACIONES) + "|todas")
    ap.add_argument("--km", type=float, default=2.0)
    a = ap.parse_args()
    claves = list(ESTACIONES) if a.estacion == "todas" else [a.estacion]
    if any(c not in ESTACIONES for c in claves):
        sys.exit(f"Estación desconocida. Opciones: {', '.join(ESTACIONES)}, todas")
    lugares = json.loads((AQUI / "datos/lugares.json").read_text(encoding="utf-8"))
    ar = json.loads((AQUI / "datos/lugares-ar.json").read_text(encoding="utf-8"))
    for c in claves:
        hacer(c, a.km, lugares, ar)


if __name__ == "__main__":
    main()
