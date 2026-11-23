// gen_menu_r114_lib.js — helpers del documento de inventario de arte (CrazyPP)
// Recetas y reglas: skills/docx design-system.md (R1, DM-1) + common-rules.md
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, PageBreak, Header, Footer, PageNumber, NumberFormat,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
  SectionType, TableLayoutType, TableOfContents,
} = require('docx');
const fs = require('fs');
const path = require('path');

const RAIZ = '/home/z/my-project';
const DIMS = JSON.parse(fs.readFileSync(path.join(RAIZ, 'scripts/_thumbs_dims.json'), 'utf8'));
const ACT = JSON.parse(fs.readFileSync(path.join(RAIZ, 'scripts/_menu_activos.json'), 'utf8'));

// peso total de los JPG del cubemap de una variante ('' = museo) — solo ficheros
// de primer nivel bajo la carpeta (sin recursión a subdirectorios); t en KB → MB
function pesoCubemap(carpeta) {
  const pref = 'assets/hall' + carpeta + '/';
  let t = 0;
  for (const [k, d] of Object.entries(ACT)) {
    if (k.startsWith(pref) && !k.slice(pref.length).includes('/') &&
        k.endsWith('.jpg')) t += d.peso_kb;
  }
  return (t / 1024).toFixed(1).replace('.', ',') + ' MB';
}

// duración del MP3 de una variante (mismo criterio de primer nivel)
function durSala(carpeta) {
  const pref = 'assets/hall' + carpeta + '/';
  const e = Object.entries(ACT).find(([k]) => k.startsWith(pref) &&
    !k.slice(pref.length).includes('/') && k.endsWith('.mp3'));
  return e ? e[1].duracion_s.toFixed(1).replace('.', ',') + ' s' : 'sin música';
}

// ── Paleta DM-1 (Deep Cyan — tech/gaming) con tokens de tabla oscurecidos ──
const P = {
  primary: '0F3049',   // títulos de capítulo
  body: '000000',      // cuerpo negro puro (perfil A informe)
  secondary: '5A6B7A', // pies de figura, notas
  accent: '1B6B7A',    // líneas de tabla
  table: { headerBg: '1B6B7A', headerText: 'FFFFFF', innerLine: 'C8DDE2', surface: 'EDF3F5' },
  cover: { bg: '162235', titleColor: 'FFFFFF', subtitleColor: 'B0B8C0',
           metaColor: '90989F', footerColor: '687078', accent: '37DCF2' },
};

const NB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB,
                       insideHorizontal: NB, insideVertical: NB };
const TNR = { ascii: 'Times New Roman', eastAsia: 'Times New Roman' };

function safeText(v, ph) {
  if (v === undefined || v === null || v === '' || String(v) === 'NaN' ||
      String(v) === 'undefined') return ph || '【Pendiente de dato】';
  return String(v);
}

// ── Título de portada: cálculo de tamaño y cortes consciente de texto latino ──
function estimateTextWidth(text, pt) {
  let w = 0;
  for (const ch of text) {
    const code = ch.codePointAt(0);
    const esCJK = (code >= 0x4E00 && code <= 0x9FFF) || (code >= 0x3000 && code <= 0x303F) ||
                  (code >= 0xFF00 && code <= 0xFFEF);
    w += esCJK ? pt * 20 : pt * 11;
  }
  return w;
}

function splitTitleLines(title, anchoMaxTw, pt) {
  const palabras = title.split(' ');
  const lineas = [];
  let actual = '';
  for (const pal of palabras) {
    const prueba = actual ? actual + ' ' + pal : pal;
    if (estimateTextWidth(prueba, pt) <= anchoMaxTw || !actual) actual = prueba;
    else { lineas.push(actual); actual = pal; }
  }
  if (actual) lineas.push(actual);
  if (lineas.length > 1 && lineas[lineas.length - 1].length <= 4) {
    const ult = lineas.pop();
    lineas[lineas.length - 1] += ' ' + ult;
  }
  return lineas;
}

function calcTitleLayout(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  let titlePt = preferredPt, lineas;
  while (titlePt >= minPt) {
    lineas = splitTitleLines(title, maxWidthTwips, titlePt);
    if (lineas.length <= 3) break;
    titlePt -= 2;
  }
  if (!lineas || lineas.length > 3) {
    lineas = splitTitleLines(title, maxWidthTwips, minPt);
    titlePt = minPt;
  }
  return { titlePt, titleLines: lineas };
}

function calcCoverSpacing(params) {
  const { titleLineCount = 1, titlePt = 36, hasSubtitle = false,
          hasEnglishLabel = false, metaLineCount = 0,
          fixedHeight = 800, pageHeight = 16838 } = params;
  const SAFETY = 1200;
  const usable = pageHeight - SAFETY;
  const titleH = titleLineCount * (titlePt * 23 + 200);
  const subH = hasSubtitle ? (12 * 23 + 600) : 0;
  const engH = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaH = metaLineCount * (10 * 23 + 100);
  const implicito = 3 * 300;
  const contenido = titleH + subH + engH + metaH + fixedHeight + implicito;
  const resto = Math.max(usable - contenido, 400);
  const PIE_MIN = 800;
  const topBruto = Math.floor(resto * 0.45);
  const botBruto = Math.floor(resto * 0.45);
  const bottomSpacing = Math.max(botBruto, PIE_MIN);
  const topSpacing = Math.max(topBruto - Math.max(0, PIE_MIN - botBruto), 400);
  const midSpacing = Math.max(resto - topSpacing - bottomSpacing, 0);
  return { topSpacing, midSpacing, bottomSpacing };
}

// ── Receta R1: portada de párrafos puros, alineada a la izquierda ──
function buildCoverR1(config) {
  const C = config.palette;
  const padL = 1200, padR = 800;
  const anchoDisp = 11906 - padL - padR - 300;
  const { titlePt, titleLines } = calcTitleLayout(config.title, anchoDisp, 40, 24);
  const titleSize = titlePt * 2;
  const spacing = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel,
    metaLineCount: (config.metaLines || []).length, fixedHeight: 400,
  });
  const accentIzq = { style: BorderStyle.SINGLE, size: 8, color: C.accent, space: 12 };
  const hijos = [];
  hijos.push(new Paragraph({ spacing: { before: spacing.topSpacing } }));
  if (config.englishLabel) {
    hijos.push(new Paragraph({
      indent: { left: padL, right: padR }, spacing: { after: 500 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.accent, space: 8 } },
      children: [new TextRun({ text: config.englishLabel.split('').join('  '),
        size: 18, color: C.accent, font: TNR, characterSpacing: 40 })],
    }));
  }
  for (let i = 0; i < titleLines.length; i++) {
    hijos.push(new Paragraph({
      indent: { left: padL },
      spacing: { after: i < titleLines.length - 1 ? 100 : 300,
                 line: Math.ceil(titlePt * 23), lineRule: 'atLeast' },
      children: [new TextRun({ text: titleLines[i], size: titleSize, bold: true,
        color: C.titleColor, font: { eastAsia: 'Arial', ascii: 'Arial' } })],
    }));
  }
  if (config.subtitle) {
    hijos.push(new Paragraph({
      indent: { left: padL, right: padR }, spacing: { after: 800 },
      children: [new TextRun({ text: config.subtitle, size: 24, color: C.subtitleColor,
        font: { eastAsia: 'Arial', ascii: 'Arial' } })],
    }));
  }
  for (const linea of (config.metaLines || [])) {
    hijos.push(new Paragraph({
      indent: { left: padL + 200, right: padR }, spacing: { after: 80 },
      border: { left: accentIzq },
      children: [new TextRun({ text: linea, size: 24, color: C.metaColor,
        font: { eastAsia: 'Arial', ascii: 'Arial' } })],
    }));
  }
  hijos.push(new Paragraph({ spacing: { before: spacing.bottomSpacing } }));
  hijos.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: C.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: config.footerLeft || '', size: 16, color: C.footerColor, font: TNR }),
      new TextRun({ text: '                                        ' }),
      new TextRun({ text: config.footerRight || '', size: 16, color: C.footerColor, font: TNR }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: 'exact' },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: C.bg }, borders: noBorders,
        children: hijos,
      })],
    })],
  })];
}

// ── Helpers de cuerpo ──
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160, line: 380, lineRule: 'atLeast' },
    children: [new TextRun({ text, bold: true, size: 32, color: P.primary, font: TNR })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120, line: 340, lineRule: 'atLeast' },
    children: [new TextRun({ text, bold: true, size: 28, color: P.primary, font: TNR })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 100, line: 312 },
    children: [new TextRun({ text, bold: true, size: 24, color: P.primary, font: TNR })],
  });
}
// párrafo de cuerpo; acepta string o lista de runs {t, b}
function p(contenido, opts = {}) {
  const runs = (Array.isArray(contenido) ? contenido : [{ t: contenido }])
    .map(x => new TextRun({ text: safeText(x.t), bold: !!x.b, size: opts.size || 24,
                            color: opts.color || P.body, font: TNR, italics: !!x.i }));
  return new Paragraph({
    alignment: opts.alinear || AlignmentType.JUSTIFIED,
    spacing: { line: 312, after: opts.after === undefined ? 120 : opts.after },
    children: runs,
  });
}
function nota(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, after: 160 },
    children: [new TextRun({ text: safeText(text), italics: true, size: 20,
                             color: P.secondary, font: TNR })],
  });
}
function vineta(text) {
  const runs = (Array.isArray(text) ? text : [{ t: text }])
    .map(x => new TextRun({ text: safeText(x.t), bold: !!x.b, size: 22, color: P.body, font: TNR }));
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    bullet: { level: 0 },
    spacing: { line: 312, after: 60 },
    children: runs,
  });
}

// Tabla estilo Horizontal-Only con tokens DM-1
function tabla(headers, rows, widths, opts = {}) {
  const fs = opts.size || 20;
  const cab = new TableRow({
    tableHeader: true, cantSplit: true,
    children: headers.map((tx, i) => new TableCell({
      width: { size: widths[i], type: WidthType.PERCENTAGE },
      shading: { type: ShadingType.CLEAR, fill: P.table.headerBg },
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({
        spacing: { line: 276 },
        children: [new TextRun({ text: safeText(tx), bold: true, size: fs,
                                 color: P.table.headerText, font: TNR })],
      })],
    })),
  });
  const filas = rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((celda, i) => new TableCell({
      width: { size: widths[i], type: WidthType.PERCENTAGE },
      shading: opts.cebra && ri % 2 === 0
        ? { type: ShadingType.CLEAR, fill: P.table.surface } : undefined,
      margins: { top: 50, bottom: 50, left: 100, right: 100 },
      children: [new Paragraph({
        spacing: { line: 276 },
        children: [new TextRun({ text: safeText(celda), size: fs, color: P.body, font: TNR })],
      })],
    })),
  }));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: P.accent },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: P.accent },
      left: NB, right: NB,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: P.table.innerLine },
      insideVertical: NB,
    },
    rows: [cab, ...filas],
  });
}

// Figura centrada con miniatura + pie numerado
function figura(clave, anchoPx, pie) {
  const d = DIMS[clave];
  if (!d) throw new Error('miniatura no encontrada: ' + clave);
  const buf = fs.readFileSync(path.join(RAIZ, 'download/_thumbs_r114', d.f));
  const alto = Math.round(anchoPx * d.h / d.w);
  const out = [new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 40 },
    children: [new ImageRun({ data: buf, transformation: { width: anchoPx, height: alto },
                              type: 'png' })],
  })];
  if (pie) {
    out.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 160, line: 276 },
      children: [new TextRun({ text: pie, size: 18, color: P.secondary, font: TNR, italics: true })],
    }));
  }
  return out;
}

module.exports = { Document, Packer, Paragraph, TextRun, Header, Footer, PageNumber,
  NumberFormat, AlignmentType, SectionType, TableOfContents, PageBreak,
  P, TNR, allNoBorders, buildCoverR1, h1, h2, h3, p, nota, vineta, tabla, figura, safeText,
  ACT, pesoCubemap, durSala };
