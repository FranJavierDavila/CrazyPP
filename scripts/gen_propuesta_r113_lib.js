// gen_propuesta_r113.js — Propuesta de limpieza y organización del repositorio
// CRAZY PING PONG · r113 · 2026-11-21 · receta R1 + paleta GO-1 · escena report
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, PageNumber, NumberFormat, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, SectionType, TableOfContents,
  PageBreak, TableLayoutType,
} = require("docx");
const fs = require("fs");

// ── Paleta GO-1 (Graphite Orange) ─────────────────────────────────
const P = {
  bg: "1A2330", accent: "D4875A",
  titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F",
  footerColor: "687078",
  headInk: "1A2330", body: "000000", secondary: "606060",
  tHeaderBg: "D4875A", tHeaderText: "FFFFFF", tInner: "DDD0C8", tSurface: "F8F0EB",
};
const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { ...noBorders, insideHorizontal: NB, insideVertical: NB };
const FONT = { ascii: "Times New Roman", eastAsia: "Times New Roman" };

// ── Titulación de portada (design-system: estimateTextWidth para latín) ──
function estimateTextWidth(text, pt) {
  let w = 0;
  for (const ch of text) {
    const code = ch.codePointAt(0);
    const cjk = (code >= 0x4e00 && code <= 0x9fff) || (code >= 0x3000 && code <= 0x303f);
    w += cjk ? pt * 20 : pt * 11;
  }
  return w;
}
function splitTitleLines(title, maxW, pt) {
  const words = title.split(" ");
  const lines = []; let cur = "";
  for (const word of words) {
    const probe = cur ? cur + " " + word : word;
    if (estimateTextWidth(probe, pt) <= maxW || !cur) cur = probe;
    else { lines.push(cur); cur = word; }
  }
  if (cur) lines.push(cur);
  if (lines.length > 1 && lines[lines.length - 1].length <= 3) {
    const last = lines.pop(); lines[lines.length - 1] += " " + last;
  }
  return lines;
}
function calcTitleLayout(title, maxW, preferredPt = 40, minPt = 24) {
  let pt = preferredPt, lines;
  while (pt >= minPt) {
    lines = splitTitleLines(title, maxW, pt);
    if (lines.length <= 3) break;
    pt -= 2;
  }
  return { titlePt: pt, titleLines: lines };
}
function calcCoverSpacing(p) {
  const SAFETY = 1200;
  const usable = 16838 - SAFETY;
  const titleH = p.titleLineCount * (p.titlePt * 23 + 200);
  const subH = p.hasSubtitle ? (12 * 23 + 600) : 0;
  const engH = p.hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaH = p.metaLineCount * (10 * 23 + 100);
  const content = titleH + subH + engH + metaH + (p.fixedHeight || 400) + 900;
  const rem = Math.max(usable - content, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(rem * 0.45), rawBottom = Math.floor(rem * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  return { topSpacing, bottomSpacing };
}

// ── Receta R1 (Pure Paragraph Left) ───────────────────────────────
function buildCoverR1(config) {
  const padL = 1200, padR = 800;
  const availW = 11906 - padL - padR - 300;
  const { titlePt, titleLines } = calcTitleLayout(config.title, availW, 40, 24);
  const titleSize = titlePt * 2;
  const sp = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel,
    metaLineCount: (config.metaLines || []).length, fixedHeight: 400,
  });
  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: P.accent, space: 12 };
  const ch = [];
  ch.push(new Paragraph({ spacing: { before: sp.topSpacing } }));
  ch.push(new Paragraph({
    indent: { left: padL, right: padR }, spacing: { after: 500 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: P.accent, space: 8 } },
    children: [new TextRun({ text: config.englishLabel.split("").join(" "),
      size: 18, color: P.accent, font: { ascii: "Calibri" }, characterSpacing: 40 })],
  }));
  for (let i = 0; i < titleLines.length; i++) {
    ch.push(new Paragraph({
      indent: { left: padL },
      spacing: { after: i < titleLines.length - 1 ? 100 : 300,
                 line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: titleLines[i], size: titleSize, bold: true,
        color: P.titleColor, font: { ascii: "Arial", eastAsia: "SimHei" } })],
    }));
  }
  ch.push(new Paragraph({
    indent: { left: padL }, spacing: { after: 800 },
    children: [new TextRun({ text: config.subtitle, size: 24, color: P.subtitleColor,
      font: { ascii: "Arial" } })],
  }));
  for (const line of config.metaLines) {
    ch.push(new Paragraph({
      indent: { left: padL + 200 }, spacing: { after: 80 },
      border: { left: accentLeft },
      children: [new TextRun({ text: line, size: 24, color: P.metaColor,
        font: { ascii: "Arial" } })],
    }));
  }
  ch.push(new Paragraph({ spacing: { before: sp.bottomSpacing } }));
  ch.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: config.footerLeft, size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
      new TextRun({ text: "                                        " }),
      new TextRun({ text: config.footerRight, size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: P.bg }, borders: noBorders,
        verticalAlign: "top", children: ch,
      })],
    })],
  })];
}

// ── Helpers de cuerpo ─────────────────────────────────────────────
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text, bold: true, size: 32, color: P.headInk, font: FONT })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120, line: 312 },
    children: [new TextRun({ text, bold: true, size: 28, color: P.headInk, font: FONT })],
  });
}
function body(text, opts = {}) {
  const runs = Array.isArray(text) ? text : [new TextRun({ text, size: 24, color: P.body, font: FONT })];
  return new Paragraph({
    alignment: AlignmentType.LEFT, spacing: { line: 312, after: opts.after ?? 120 },
    children: runs,
  });
}
function run(text, bold = false) {
  return new TextRun({ text, size: 24, color: P.body, bold, font: FONT });
}
function tablaTitulo(text) {
  return new Paragraph({
    keepNext: true, spacing: { before: 160, after: 80, line: 312 },
    children: [new TextRun({ text, bold: true, size: 21, color: P.headInk, font: FONT })],
  });
}
function tabla(headers, rows, widths) {
  const headerRow = new TableRow({
    tableHeader: true, cantSplit: true,
    children: headers.map((t, i) => new TableCell({
      width: { size: widths[i], type: WidthType.PERCENTAGE },
      shading: { type: ShadingType.CLEAR, fill: P.tHeaderBg },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ spacing: { line: 276 },
        children: [new TextRun({ text: t, bold: true, size: 20, color: P.tHeaderText, font: FONT })] })],
    })),
  });
  const dataRows = rows.map((r, idx) => new TableRow({
    cantSplit: true,
    children: r.map((t, i) => new TableCell({
      width: { size: widths[i], type: WidthType.PERCENTAGE },
      shading: { type: ShadingType.CLEAR, fill: idx % 2 === 0 ? "FFFFFF" : P.tSurface },
      margins: { top: 50, bottom: 50, left: 120, right: 120 },
      children: [new Paragraph({ spacing: { line: 276 },
        children: [new TextRun({ text: String(t), size: 20, color: P.body, font: FONT })] })],
    })),
  }));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: P.accent },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: P.accent },
      left: NB, right: NB,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: P.tInner },
      insideVertical: NB,
    },
    rows: [headerRow, ...dataRows],
  });
}

module.exports = { Document, Packer, Paragraph, TextRun, Header, Footer, PageNumber,
  NumberFormat, AlignmentType, SectionType, TableOfContents, PageBreak,
  buildCoverR1, h1, h2, body, run, tablaTitulo, tabla, P, FONT, fs };
