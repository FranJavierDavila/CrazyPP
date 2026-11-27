#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_experiencia_r117.py — cuerpo del PDF guion de experiencia (ruta Report).
Mismo motor que gen_espectador_analisis_r116.py con todas las correcciones
acumuladas (tablas largas se parten, nota compacta, quote compacto)."""
import os
import sys
import hashlib

PDF_SKILL_DIR = '/home/z/my-project/skills/pdf'
sys.path.insert(0, os.path.join(PDF_SKILL_DIR, 'scripts'))
sys.path.insert(0, '/home/z/my-project/scripts')

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, CondPageBreak,
                                KeepTogether, Image, HRFlowable, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage

# ━━ Tipos (registro + familias + fallback automático) ━━
FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Noto Sans SC', f'{FONT_DIR}/truetype/chinese/NotoSansSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Noto Sans SC Bold', f'{FONT_DIR}/truetype/chinese/NotoSansSC-Bold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif', f'{FONT_DIR}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Bold', f'{FONT_DIR}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Italic', f'{FONT_DIR}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-BoldItalic', f'{FONT_DIR}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')
registerFontFamily('Noto Sans SC', normal='Noto Sans SC', bold='Noto Sans SC Bold')
registerFontFamily('FreeSerif', normal='FreeSerif', bold='FreeSerif-Bold',
                   italic='FreeSerif-Italic', boldItalic='FreeSerif-BoldItalic')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')
from pdf import install_font_fallback
install_font_fallback()

# ━━ Paleta fija del Template 07 (cuerpo azul claro, familia ~215°) ━━
PAGE_BG      = colors.HexColor('#f5f8fc')
SECTION_BG   = colors.HexColor('#edf2f9')
CARD_BG      = colors.HexColor('#e4ecf5')
TABLE_STRIPE = colors.HexColor('#eef3fa')
HEADER_FILL  = colors.HexColor('#1a4a7a')
BORDER       = colors.HexColor('#c0d0e2')
ACCENT       = colors.HexColor('#2d7ab3')
TEXT_PRIMARY = colors.HexColor('#142840')
TEXT_MUTED   = colors.HexColor('#5a7a96')

PAGE_W, PAGE_H = A4
MARGIN = 60.0
TOP_M, BOT_M = 76.0, 68.0
AVAIL_W = PAGE_W - 2 * MARGIN
AVAIL_H = PAGE_H - TOP_M - BOT_M

TITULO_DOC = 'La experiencia del espectador en CrazyPP · guion de experiencia'
SALIDA = '/tmp/render/cuerpo_r117.pdf'

# ━━ Estilos ━━
st_body = ParagraphStyle('Body', fontName='FreeSerif', fontSize=10.5, leading=17,
                         alignment=TA_JUSTIFY, textColor=TEXT_PRIMARY,
                         spaceBefore=0, spaceAfter=9)
st_h1 = ParagraphStyle('H1', fontName='FreeSerif', fontSize=21, leading=26,
                       textColor=HEADER_FILL, spaceBefore=16, spaceAfter=4)
st_h2 = ParagraphStyle('H2', fontName='FreeSerif', fontSize=14.5, leading=19,
                       textColor=TEXT_PRIMARY, spaceBefore=14, spaceAfter=7)
st_bullet = ParagraphStyle('Bullet', fontName='FreeSerif', fontSize=10.5, leading=16,
                           alignment=TA_LEFT, textColor=TEXT_PRIMARY,
                           leftIndent=18, bulletIndent=6, spaceAfter=5)
st_quote = ParagraphStyle('Quote', fontName='FreeSerif-Italic', fontSize=10.5,
                          leading=15.5, alignment=TA_LEFT, textColor=TEXT_PRIMARY)
st_caption = ParagraphStyle('Caption', fontName='FreeSerif', fontSize=8.5, leading=12,
                            alignment=TA_CENTER, textColor=TEXT_MUTED,
                            spaceBefore=0, spaceAfter=0)
st_th = ParagraphStyle('TH', fontName='FreeSerif', fontSize=9, leading=11.5,
                       alignment=TA_CENTER, textColor=colors.white)
st_cell = ParagraphStyle('TD', fontName='FreeSerif', fontSize=8.8, leading=12,
                         alignment=TA_LEFT, textColor=TEXT_PRIMARY)
st_nota = ParagraphStyle('Nota', fontName='FreeSerif', fontSize=8, leading=11.2,
                         alignment=TA_LEFT, textColor=TEXT_MUTED,
                         wordWrap='CJK', leftIndent=14, spaceAfter=4)
st_stat = ParagraphStyle('Stat', fontName='FreeSerif', fontSize=17, leading=20,
                         alignment=TA_CENTER, textColor=ACCENT)
st_statlab = ParagraphStyle('StatLab', fontName='FreeSerif', fontSize=8, leading=10.5,
                            alignment=TA_CENTER, textColor=TEXT_MUTED)
st_toc0 = ParagraphStyle('TOC0', fontName='FreeSerif', fontSize=11.5, leading=17,
                         leftIndent=6, textColor=TEXT_PRIMARY)
st_toc1 = ParagraphStyle('TOC1', fontName='FreeSerif', fontSize=9.5, leading=14,
                         leftIndent=26, textColor=TEXT_MUTED)
st_toc_tit = ParagraphStyle('TOCTit', fontName='FreeSerif', fontSize=20, leading=25,
                            textColor=HEADER_FILL, spaceAfter=14)

# ━━ Plantilla con TOC + reinicio de numeración ━━
class TocDocTemplate(SimpleDocTemplate):
    def __init__(self, *a, **kw):
        SimpleDocTemplate.__init__(self, *a, **kw)
        self._content_start = 10 ** 6

    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            nivel = getattr(flowable, 'bookmark_level', 0)
            texto = getattr(flowable, 'bookmark_text', '')
            clave = getattr(flowable, 'bookmark_key', '')
            if texto.startswith('1 ·'):
                self._content_start = self.page
            pag = self.page - self._content_start + 1 if self.page >= self._content_start else self.page
            self.notify('TOCEntry', (nivel, texto, pag, clave))

ROM = {1: 'i', 2: 'ii', 3: 'iii', 4: 'iv', 5: 'v', 6: 'vi', 7: 'vii', 8: 'viii'}

def _pag_pie(doc):
    if doc.page >= doc._content_start:
        return str(doc.page - doc._content_start + 1)
    return ROM.get(doc.page, str(doc.page))

def al_dibujar_pagina(canv, doc):
    canv.saveState()
    canv.setFillColor(PAGE_BG)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setFont('FreeSerif', 7.5)
    canv.setFillColor(TEXT_MUTED)
    canv.drawString(MARGIN, PAGE_H - 42, TITULO_DOC)
    canv.setStrokeColor(ACCENT)
    canv.setLineWidth(1.2)
    canv.line(MARGIN, PAGE_H - 50, PAGE_W - MARGIN, PAGE_H - 50)
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 52, PAGE_W - MARGIN, 52)
    canv.setFont('FreeSerif', 7.5)
    canv.setFillColor(TEXT_MUTED)
    canv.drawString(MARGIN, 40, 'CrazyPP · guion de experiencia')
    canv.drawRightString(PAGE_W - MARGIN, 40, _pag_pie(doc))
    canv.restoreState()

# ━━ Constructores ━━
_cont_tablas = [0]

def heading(texto, estilo, nivel):
    clave = 'h_%s' % hashlib.md5(texto.encode()).hexdigest()[:8]
    p = Paragraph('<a name="%s"/><b>%s</b>' % (clave, texto), estilo)
    p.bookmark_name = clave
    p.bookmark_level = nivel
    p.bookmark_text = texto
    p.bookmark_key = clave
    return p

def safe_keep(elems, max_h=A4[1] * 0.4):
    total = 0
    for e in elems:
        w, h = e.wrap(AVAIL_W, PAGE_H)
        total += h
    if total <= max_h:
        return [KeepTogether(elems)]
    if len(elems) >= 2:
        return [KeepTogether(elems[:2])] + list(elems[2:])
    return list(elems)

def mk_tabla(cfg):
    _cont_tablas[0] += 1
    n = _cont_tablas[0]
    th = cfg.get('size', 8.8)
    c_head = ParagraphStyle('TH%d' % n, parent=st_th, fontSize=th, leading=th + 2.6)
    c_cell = ParagraphStyle('TD%d' % n, parent=st_cell, fontSize=th, leading=th + 3.2)
    filas = [[Paragraph('<b>%s</b>' % c, c_head) for c in cfg['head']]]
    for r in cfg['rows']:
        filas.append([Paragraph(str(c), c_cell) for c in r])
    anchos = [fr * AVAIL_W for fr in cfg['ratios']]
    assert sum(anchos) <= AVAIL_W + 0.5, 'tabla excede el ancho disponible'
    t = Table(filas, colWidths=anchos, hAlign='CENTER', repeatRows=1)
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5.5),
    ]
    for i in range(1, len(filas)):
        estilo.append(('BACKGROUND', (0, i), (-1, i),
                       TABLE_STRIPE if i % 2 == 1 else colors.white))
    t.setStyle(TableStyle(estilo))
    cap = Paragraph('Tabla %d · %s' % (n, cfg['title']), st_caption)
    out = [Spacer(1, 14)]
    if len(cfg['rows']) <= 8:
        out += safe_keep([t, Spacer(1, 6), cap])
    else:
        out += [t, Spacer(1, 6), cap]
    out.append(Spacer(1, 14))
    return out

def mk_callouts(items):
    ncol = len(items)
    wcol = AVAIL_W / ncol
    fila1 = [Paragraph('<b>%s</b>' % v, st_stat) for v, _ in items]
    fila2 = [Paragraph(l, st_statlab) for _, l in items]
    t = Table([fila1, fila2], colWidths=[wcol] * ncol, hAlign='CENTER')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('BOX', (0, 0), (-1, -1), 1, ACCENT),
        ('INNERGRID', (0, 0), (-1, -1), 0.8, ACCENT),
        ('VALIGN', (0, 0), (-1, 0), 'BOTTOM'),
        ('VALIGN', (0, 1), (-1, 1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('TOPPADDING', (0, 1), (-1, 1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return [Spacer(1, 6), KeepTogether(t), Spacer(1, 14)]

def mk_fig(cfg):
    ruta = cfg['path']
    pil = PILImage.open(ruta)
    ow, oh = pil.size
    maxw = cfg.get('maxw', AVAIL_W)
    maxh = cfg.get('maxh', A4[1] * 0.32)
    ratio = min(maxw / ow, maxh / oh, 1.0)
    img = Image(ruta, width=ow * ratio, height=oh * ratio)
    img.hAlign = 'CENTER'
    cap = Paragraph(cfg['caption'], st_caption)
    out = [Spacer(1, 16)]
    out += safe_keep([img, Spacer(1, 8), cap])
    out.append(Spacer(1, 16))
    return out

def mk_quote(texto):
    p = Paragraph(texto, st_quote)
    t = Table([[p]], colWidths=[AVAIL_W * 0.94], hAlign='CENTER')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    return [Spacer(1, 8), KeepTogether(t), Spacer(1, 12)]

def montar(bloques, story):
    for i, b in enumerate(bloques):
        tipo = b[0]
        sig_es_parrafo = i + 1 < len(bloques) and bloques[i + 1][0] in ('p', 'v')
        if tipo == 'h1':
            story.append(CondPageBreak(AVAIL_H * 0.25))
            h = heading(b[1], st_h1, 0)
            regla = HRFlowable(width='100%', color=ACCENT, thickness=1.2,
                               spaceBefore=1, spaceAfter=10)
            if sig_es_parrafo:
                story += safe_keep([h, regla])
            else:
                story += [h, regla]
        elif tipo == 'h2':
            story.append(CondPageBreak(70))
            h = heading(b[1], st_h2, 1)
            if sig_es_parrafo:
                primero = Paragraph(bloques[i + 1][1], st_body)
                story += safe_keep([h, primero])
                bloques[i + 1] = ('_hecho',)
            else:
                story.append(h)
        elif tipo == 'p':
            story.append(Paragraph(b[1], st_body))
        elif tipo == 'v':
            story.append(Paragraph(b[1], st_bullet, bulletText='•'))
        elif tipo == 'tabla':
            story += mk_tabla(b[1])
        elif tipo == 'callouts':
            story += mk_callouts(b[1])
        elif tipo == 'fig':
            story += mk_fig(b[1])
        elif tipo == 'quote':
            story += mk_quote(b[1])
        elif tipo == 'nota':
            story.append(Paragraph(b[1], st_nota))
        elif tipo == 'spacer':
            story.append(Spacer(1, b[1]))

# ━━ Documento ━━
from contenido_r117_a import BLOQUES_A
from contenido_r117_b import BLOQUES_B

doc = TocDocTemplate(SALIDA, pagesize=A4,
                     leftMargin=MARGIN, rightMargin=MARGIN,
                     topMargin=TOP_M, bottomMargin=BOT_M,
                     title=TITULO_DOC, author='Z.ai', creator='Z.ai',
                     subject='Guion de experiencia del modo espectador para CrazyPP')

toc = TableOfContents()
toc.levelStyles = [st_toc0, st_toc1]

story = []
story.append(Paragraph('<b>Índice</b>', st_toc_tit))
story.append(toc)
story.append(PageBreak())
montar(BLOQUES_A, story)
montar(BLOQUES_B, story)

doc.multiBuild(story, onFirstPage=al_dibujar_pagina, onLaterPages=al_dibujar_pagina)
print('✓ cuerpo generado:', SALIDA)
