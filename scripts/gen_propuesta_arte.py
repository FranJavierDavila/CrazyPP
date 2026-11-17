# -*- coding: utf-8 -*-
"""Genera la PROPUESTA de arte completa (47 recursos candy arcade) + index autónomo con
mockup de menú compuesto y overlays de texto de ejemplo. Salida en download/propuesta_arte_v1/."""
import os, sys
import cairosvg
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prop_base import wrap, P
from prop_bodies import COMPONENTS, ICONS, EXTRAS

BASE = "/home/z/my-project/download/propuesta_arte_v1"
D_SVG, D_PNG = os.path.join(BASE, "svg"), os.path.join(BASE, "png2x")
for d in (D_SVG, D_PNG):
    os.makedirs(d, exist_ok=True)

# ---------- 1. construir todos los SVG ----------
SVG_MAP = {}
count = 0
for name, w, h, guides, sc, body in COMPONENTS:
    SVG_MAP[name] = wrap(w, h, body, guides)
    count += 1
for name, desc, outline, fills, gid, gop in ICONS:
    from prop_base import ico
    SVG_MAP[name] = wrap(128, 128, ico(outline, fills, gid, gop))
    count += 1
for name, w, h, sc, body in EXTRAS:
    SVG_MAP[name] = wrap(w, h, body)
    count += 1
assert count == 47, count
for n, s in SVG_MAP.items():
    with open(os.path.join(D_SVG, n + ".svg"), "w") as f:
        f.write(s)
print("SVGs:", count)

# ---------- 2. PNG 2x limpios (sin guias) ----------
import re
made = []
for name, w, h, guides, sc, body in COMPONENTS:
    cairosvg.svg2png(bytestring=wrap(w, h, body).encode(), write_to=os.path.join(D_PNG, name + ".png"), scale=sc)
    made.append(name)
for name, desc, outline, fills, gid, gop in ICONS:
    from prop_base import ico
    cairosvg.svg2png(bytestring=wrap(128, 128, ico(outline, fills, gid, gop)).encode(),
                     write_to=os.path.join(D_PNG, name + ".png"), scale=2)
    made.append(name)
for name, w, h, sc, body in EXTRAS:
    cairosvg.svg2png(bytestring=wrap(w, h, body).encode(), write_to=os.path.join(D_PNG, name + ".png"), scale=sc)
    made.append(name)
print("PNGs:", len(made))

# ---------- 3. QA alpha ----------
bad = []
for n in sorted(made):
    im = Image.open(os.path.join(D_PNG, n + ".png")).convert("RGBA")
    a = im.getchannel("A")
    cov = sum(1 for v in a.getdata() if v > 10) / (im.width * im.height)
    if cov < 0.005:
        bad.append(n)
print("SOSPECHOSOS:", bad if bad else "ninguno")

# ---------- 4. hoja de contacto ----------
cols, TH, lh, pad = 6, 210, 18, 10
rows = (len(made) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (TH + pad) + pad, rows * (TH + lh + pad) + pad), (14, 14, 22))
dr = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except Exception:
    font = ImageFont.load_default()
for i, n in enumerate(sorted(made)):
    im = Image.open(os.path.join(D_PNG, n + ".png")).convert("RGBA")
    im.thumbnail((TH, TH))
    x, y = pad + (i % cols) * (TH + pad), pad + (i // cols) * (TH + lh + pad)
    sheet.paste(im, (x + (TH - im.width) // 2, y + (TH - im.height) // 2), im)
    dr.text((x + 2, y + TH + 2), n[:30], fill=(220, 220, 230), font=font)
sheet.save("/tmp/render/prop_sheet.png")
print("Hoja: /tmp/render/prop_sheet.png", sheet.size)

# ---------- 5. overlays de texto de ejemplo ----------
def ov(span_cls, content, style):
    return '<span class="%s" style="%s">%s</span>' % (span_cls, style, content)

ARROW_L = '<svg viewBox="0 0 24 24" fill="none" stroke="#F9F9E7" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5 L8 12 L15 19"/></svg>'
X_MARK = '<svg viewBox="0 0 24 24" fill="none" stroke="#F9F9E7" stroke-width="2.6" stroke-linecap="round"><path d="M6 6 L18 18 M18 6 L6 18"/></svg>'
CHEV_R = '<svg viewBox="0 0 24 24" fill="none" stroke="#F1E5AB" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5 L16 12 L9 19"/></svg>'

TT = "font-family:'Chakra Petch',sans-serif;font-weight:800;color:#F9F9E7;text-shadow:0 2px 0 #030715,0 0 14px rgba(2,136,177,.55);"
SS = "font-family:'Rajdhani',sans-serif;font-weight:600;color:#97CED6;text-shadow:0 1px 0 #030715;"
YY = "font-family:'Chakra Petch',sans-serif;font-weight:700;color:#F1E5AB;text-shadow:0 2px 0 #030715;"

def modo_ovr(icon, title, sub, sprite=None):
    o = [ov("ovr-ic", SVG_MAP[icon], "left:43%;top:17.1%;width:13.75%;"),
         ov("ovr-tt", title, "left:6%;top:56.7%;transform:translateY(-50%);width:88%;justify-content:center;font-size:6.9cqw;letter-spacing:.06em;"),
         ov("ovr-ss", sub, "left:6%;top:69.5%;transform:translateY(-50%);width:88%;justify-content:center;font-size:4.2cqw;")]
    if sprite:
        o.append(ov("ovr-ic", SVG_MAP[sprite], "left:77.5%;top:5.7%;width:18.75%;"))
    return "".join(o)

OVR = {
 "panel_base": [
   ov("ovr-ic", ARROW_L, "left:4.4%;top:9.5%;transform:translateY(-50%);width:5.6%;"),
   ov("ovr-tt", "AJUSTES DE PARTIDA", "left:13.75%;top:9.5%;transform:translateY(-50%);font-size:3.8cqw;letter-spacing:.12em;"),
   ov("ovr-ic", X_MARK, "left:89%;top:9.5%;transform:translateY(-50%);width:5.6%;")],
 "btn_primario": [
   ov("ovr-ic", SVG_MAP["ico_jugar"], "left:9%;top:33.3%;width:6.25%;"),
   ov("ovr-tt", "JUGAR PARTIDO", "left:20.6%;top:50%;transform:translateY(-50%);font-size:6.6cqw;letter-spacing:.08em;")],
 "btn_fila": [
   ov("ovr-ic", SVG_MAP["ico_hall"], "left:5.3%;top:32.7%;width:5.6%;"),
   ov("ovr-tt", "ESCOGER HALL", "left:16.25%;top:30%;transform:translateY(-50%);font-size:5.3cqw;letter-spacing:.05em;"),
   ov("ovr-ss", "6 salas · Obsidiana abierta", "left:16.25%;top:66%;transform:translateY(-50%);font-size:3.9cqw;"),
   ov("ovr-ic", CHEV_R, "left:89%;top:50%;transform:translate(-50%,-50%);width:6%;")],
 "tarjeta_hall": [
   ov("ovr-tt", "HALL OBSIDIANA", "left:5%;top:76%;transform:translateY(-50%);font-size:6.3cqw;letter-spacing:.06em;"),
   ov("ovr-ss", "Supera 10 partidos para abrirlo", "left:5%;top:89%;transform:translateY(-50%);font-size:4cqw;"),
   ov("ovr-ic", SVG_MAP["spr_candado"], "left:77.5%;top:6.7%;width:18.75%;")],
 "tarjeta_liga": [
   ov("ovr-tt", "3", "left:5.5%;top:20%;transform:translateY(-50%);font-size:12.5cqw;color:#F1E5AB;"),
   ov("ovr-yy", "×150", "left:66.4%;top:21.3%;transform:translateY(-50%);font-size:5.5cqw;"),
   ov("ovr-ic", SVG_MAP["spr_actual"], "left:36%;top:30%;width:28%;"),
   ov("ovr-tt", "AMATEUR", "left:7.8%;top:84.4%;transform:translateY(-50%);width:84.4%;justify-content:center;font-size:6.6cqw;letter-spacing:.14em;")],
}

# ---------- 6. index_propuesta.html ----------
def card(name, cls="", ovr=""):
    o = '<div class="ovr">%s</div>' % ovr if ovr else ""
    return ('<div class="card %s" data-n="%s"><div class="pv">%s%s</div><h3>%s</h3></div>'
            % (cls, name, SVG_MAP[name], o, name))

cards_abc = (card("panel_base", "", OVR["panel_base"]) + card("btn_primario", "", OVR["btn_primario"])
             + card("btn_secundario") + card("btn_fila", "", OVR["btn_fila"]) + card("btn_circular")
             + card("btn_tab") + card("tarjeta_modo", "", modo_ovr("ico_multijugador", "MULTIJUGADOR", "Salas privadas · ranking"))
             + card("tarjeta_hall", "", OVR["tarjeta_hall"]) + card("tarjeta_liga", "", OVR["tarjeta_liga"]))
cards_de = "".join(card(n) for n, *_ in [(x[0],) for x in COMPONENTS[9:]] ) + \
           "".join(card(n) for n in ["spr_aspa", "spr_candado", "spr_actual", "spr_chincheta_fijada",
                                     "spr_chincheta_libre", "spr_trofeo"])
cards_f = "".join(card(n, "ico") for n, *_ in [(x[0],) for x in ICONS])
cards_g = "".join(card(n) for n in ["fondo_menu", "ilustracion_vacio", "avatar_placeholder"])

mock = """<div class="mock">
%s
<div class="mcontent">
 <div class="mduo">
  <div class="mcard">%s<div class="ovr">%s</div></div>
  <div class="mcard">%s<div class="ovr">%s</div></div>
 </div>
 <div class="mrow">%s<div class="ovr">%s</div></div>
 <div class="ctl">
   <div class="sl">%s<div class="slf">%s</div><div class="slk" style="left:42%%">%s</div></div>
   <div class="tg">%s</div>
 </div>
</div>
</div>""" % (
    SVG_MAP["panel_base"],
    SVG_MAP["tarjeta_modo"], modo_ovr("ico_multijugador", "MULTIJUGADOR", "Salas privadas · ranking", "spr_aspa"),
    SVG_MAP["tarjeta_modo"], modo_ovr("ico_entrenar", "ENTRENAR", "8 disciplinas · Reto semanal"),
    SVG_MAP["btn_fila"], OVR["btn_fila"],
    SVG_MAP["slider_track"], SVG_MAP["slider_fill"], SVG_MAP["slider_knob"],
    SVG_MAP["toggle_on"])

CHIPS = "".join('<div style="background:%s;color:%s">%s<br><small>%s</small></div>'
                % (v, "#030715" if k in ("teal_lt", "ambar", "ambar_lt", "verde_lt", "crema", "teal_pl") else "#F9F9E7",
                   v, k) for k, v in P.items())

html = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Propuesta de arte — CRAZY PING PONG menús v1</title>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700;800&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
<style>
body{background:#020510;color:#F9F9E7;font:15px/1.55 'Rajdhani',system-ui,sans-serif;margin:0;padding:clamp(12px,3vw,36px)}
h1{font-family:'Chakra Petch',sans-serif;font-size:clamp(19px,4.5vw,28px);margin:0 0 4px}
h1 span{color:#F59D1D}
h2{font-family:'Chakra Petch',sans-serif;font-size:clamp(15px,3vw,19px);color:#8FE8F5;border-bottom:1px solid #043B92;padding-bottom:8px;margin:38px 0 14px}
.lead{color:#97CED6;font-size:clamp(14px,2.6vw,17px);max-width:70ch}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}
.chips div{border-radius:10px;padding:8px 12px;font-family:'Chakra Petch';font-size:12px;border:1px solid #12306E;line-height:1.25}
.chips small{opacity:.75}
.mock{container-type:inline-size;position:relative;aspect-ratio:1280/800;margin:0 auto;max-width:960px;
 border-radius:20px;box-shadow:0 18px 60px rgba(2,136,177,.25),0 4px 20px #000}
.mock>svg{position:absolute;inset:0;width:100%;height:100%}
.mcontent{position:absolute;left:3.75%;top:18%;width:92.5%;height:76%;display:flex;flex-direction:column;justify-content:space-between}
.mrow{container-type:inline-size;position:relative}
.mduo{display:flex;gap:2%}
.mcard{container-type:inline-size;position:relative;width:49%}
.mrow>svg,.mcard>svg{width:100%;display:block}
.ctl{display:flex;align-items:center;gap:4%}
.sl{position:relative;width:56%}
.sl>svg{width:100%;display:block}
.slf{position:absolute;left:1%;top:0;width:42%}
.slf svg{width:100%;display:block}
.slk{position:absolute;top:50%;transform:translate(-50%,-50%);width:9.6%}
.slk svg{width:100%;display:block}
.tg{width:14%}
.tg svg{width:100%;display:block}
.ovr{position:absolute;inset:0;pointer-events:none}
.ovr span{position:absolute;display:flex;align-items:center;white-space:nowrap}
.ovr-ic svg{width:100%;height:auto;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55))}
.card{background:#0A1B44;border:1px solid #043B92;border-radius:14px;padding:12px;container-type:inline-size;
 transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(2,136,177,.35)}
.card .pv{position:relative;background:repeating-conic-gradient(#0A1224 0% 25%,#060B18 0% 50%) 0/18px 18px;border-radius:10px}
.card .pv>svg{width:100%;height:auto;display:block}
.card .pv>svg .g{display:none}
.card h3{margin:8px 2px 0;font-family:'Chakra Petch';font-size:13px;color:#8FE8F5;word-break:break-all}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.grid.ico{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}
.grid.ico .pv>svg{max-height:130px}
.note{color:#97CED6;font-size:13px;border-left:3px solid #F59D1D;padding-left:12px;margin:14px 0}
footer{margin-top:40px;color:#4C5170;font-size:12px}
</style></head><body>
<h1>Propuesta de arte <span>· CRAZY PING PONG</span> — menús v1</h1>
<p class="lead">47 recursos rediseñados con la estética arcade brillante de vuestro menú original y la paleta extraída del arte del juego:
chassis azul marino con remaches y rim-light cian, botones de caramelo con brillo diagonal y sombra interna, sockets recesivos para iconos,
acento dorado para competición y halftones de textura. Las zonas de texto siguen LIBRES — aquí se muestran con texto de ejemplo compuesto encima (Rajdhani/Chakra Petch).</p>
<div class="chips">@@CHIPS@@</div>
<h2>Mockup — Menú Principal compuesto</h2>
@@MOCK@@
<div class="note">El texto es una capa HTML/SVG independiente: en el juego lo compone el motor tipográfico sobre las zonas libres. El sprite de estado (aspa verde) se superpone por código según progreso.</div>
<h2>A · Contenedor · B · Botones · C · Tarjetas (con texto de ejemplo)</h2>
<div class="grid">@@ABC@@</div>
<h2>D · Controles · E · Sprites de estado</h2>
<div class="grid">@@DE@@</div>
<h2>F · Iconos (bisel doble trazo + acento de color)</h2>
<div class="grid ico">@@F@@</div>
<h2>G · Extras</h2>
<div class="grid">@@G@@</div>
<div class="note">Nota técnica: los PNG de <code>png2x/</code> se han rasterizado sin filtros (los brillos de filtro fGlow/fShadow se aprecian al abrir los SVG en navegador; los degradados, biseles y sockets sí van horneados en el PNG). Para producción final conviene rasterizar con un motor de navegador.</div>
<footer>Propuesta generada con la paleta dominante extraída de «Menú de ping-pong futurista sin texto.png» · especificación v1 de zonas respetada</footer>
</body></html>"""
html = (html.replace("@@CHIPS@@", CHIPS).replace("@@MOCK@@", mock)
            .replace("@@ABC@@", cards_abc).replace("@@DE@@", cards_de)
            .replace("@@F@@", cards_f).replace("@@G@@", cards_g))

with open(os.path.join(BASE, "index_propuesta.html"), "w") as f:
    f.write(html)
print("index_propuesta.html:", os.path.getsize(os.path.join(BASE, "index_propuesta.html")), "bytes")

# ---------- 7. LEEME-PROPUESTA ----------
leeme = """# PROPUESTA de arte — CRAZY PING PONG menus v1 (estetica candy arcade)

Estetica: la de vuestro menu original (chassis azul marino con remaches, botones caramelo con
brillo diagonal, sockets recesivos para iconos, acento dorado, halftones). Paleta extraida del
propio arte del juego. Zonas de texto LIBRES (spec v1 respetada).

## Paleta del juego (extraida)
#030715 negro · #061848 marino · #043B92 royal · #0288B1 teal · #8FE8F5/#97CED6 teal claro
#F59D1D ambar · #F1E5AB oro suave · #D70B66 magenta · #DF4E45 rojo · #06B469 verde
#30E66D verde neon · #590F65 morado · #4C5170/#83998C acero · #F9F9E7 crema

## Recetas de material (para replicar en Figma/Photoshop)
- CHASSIS (paneles): vertical #0A1B44 -> #061848 -> #030715, borde 3px #043B92, rim interior
  2px #0288B1 al 40%, remache dorado (esferita con ranura) en esquinas, brillo superior blando.
- CARAMEL CTA (btn_primario): #7FD4FF -> #0288B1 -> #043B92 + banda de brillo blanco 55% arriba
  + sombra interna inferior 38% + linea de luz #DFF6FF en el canto superior + glow cian.
- SOCKETS (albergan iconos): radial #01030A -> #050B1C -> #12306E + arco de luz inferior #97CED6.
- DORADO (competencia/trofeos): 5 paradas #FFF6D0 -> #F1E5AB -> #F59D1D -> #B26A08 -> #F7D989.
- ICONOS: doble trazo con bisel (copia oscura +3px debajo) + trazo crema #F9F9E7 + punto de
  acento de color semantico (teal acciones, magenta ritmo/efecto, dorado logros, verde play).
- TARJETA HALL: marco de madera (gWood) con tornillos + interior full-bleed para tu miniatura
  + filete dorado + scrim inferior (lo pone el codigo).
- ESTADOS: aspa verde brillante (superado), candado dorado (bloqueado), anillo dorado con
  esquinas (liga actual), chincheta magenta (fijada) / acero (libre), trofeo dorado completo.

## Ficheros
- svg/ — 47 SVG (abrir en navegador para ver filtros de glow; editables en Figma/Inkscape)
- png2x/ — rasterizados a 2x SIN filtros (degradados/biseles si; glows no)
- index_propuesta.html — autonomo: mockup del menu compuesto + galeria con texto de ejemplo

## Siguiente paso si apruebas la direccion
1. Ajustes de color/forma que indiques (rapidos: todo es parametrico en scripts/prop_base.py).
2. Rasterizado de produccion con navegador headless (filtros incluidos).
3. Integracion en el juego: motor de texto compone sobre las zonas libres (spec v1).
"""
with open(os.path.join(BASE, "LEEME-PROPUESTA.md"), "w") as f:
    f.write(leeme)
print("LEEME-PROPUESTA.md escrito")
print("OK" if not bad else "REVISAR")
