// Generador del informe de RE-AUDITORÍA — CRAZY PING PONG r111
// Ruta Create + escena Report (Perfil A) + portada R1/DM-1 + TOC 3 secciones.
// Mismo formato que la auditoría r109 (scripts/gen_docx/informe.js).
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, PageNumber, NumberFormat, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, SectionType, TableOfContents,
  PageBreak, TableLayoutType,
} = require("docx");
const fs = require("fs");
const { findings, estadoRows, descartes, descartesNuevos, bateriasOk, bateriasFallidas, estructura } = require("./datos_r111.js");

// ── Paleta DM-1 (Deep Cyan — tech) + tokens de tabla ──
const P = {
  bg: "162235", accent: "37DCF2",
  titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F", footerColor: "687078",
  heading: "0A1628", body: "000000", secondary: "55606B",
  tHeaderBg: "1B6B7A", tHeaderText: "FFFFFF", tInnerLine: "C8DDE2", tSurface: "EDF3F5",
  sevAlto: "B03A2E", sevMedio: "B9770E", sevBajo: "1B6B7A",
};
const FONT_BODY = { ascii: "Times New Roman", eastAsia: "SimSun" };
const FONT_HEAD = { ascii: "Times New Roman", eastAsia: "SimHei" };
const FONT_MONO = { ascii: "Courier New", eastAsia: "SimSun" };

const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };

// ── Utilidades de portada (design-system.md) ──
function splitTitleLines(title, charsPerLine) {
  if (title.length <= charsPerLine) return [title];
  const breakAfter = new Set([..."，。、；：！？", ..."的与和及之在于为", ..."-_—–·/", ..." \t"]);
  const lines = []; let remaining = title;
  while (remaining.length > charsPerLine) {
    let breakAt = -1;
    for (let i = charsPerLine; i >= Math.floor(charsPerLine * 0.6); i--) {
      if (i < remaining.length && breakAfter.has(remaining[i - 1])) { breakAt = i; break; }
    }
    if (breakAt === -1) {
      const limit = Math.min(remaining.length, Math.ceil(charsPerLine * 1.3));
      for (let i = charsPerLine + 1; i < limit; i++) {
        if (breakAfter.has(remaining[i - 1])) { breakAt = i; break; }
      }
    }
    if (breakAt === -1) breakAt = charsPerLine;
    lines.push(remaining.slice(0, breakAt).trim());
    remaining = remaining.slice(breakAt).trim();
  }
  if (remaining) lines.push(remaining);
  if (lines.length > 1 && lines[lines.length - 1].length <= 2) {
    const last = lines.pop(); lines[lines.length - 1] += last;
  }
  return lines;
}
function calcTitleLayout(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  const charWidth = (pt) => pt * 11.5;
  const charsPerLine = (pt) => Math.floor(maxWidthTwips / charWidth(pt));
  let titlePt = preferredPt, lines;
  while (titlePt >= minPt) {
    const cpl = charsPerLine(titlePt);
    if (cpl < 2) { titlePt -= 2; continue; }
    lines = splitTitleLines(title, cpl);
    if (lines.length <= 3) break;
    titlePt -= 2;
  }
  if (!lines || lines.length > 3) { lines = splitTitleLines(title, charsPerLine(minPt)); titlePt = minPt; }
  return { titlePt, titleLines: lines };
}
function calcCoverSpacing(params) {
  const { titleLineCount = 1, titlePt = 36, hasSubtitle = false, hasEnglishLabel = false,
    metaLineCount = 0, fixedHeight = 800, pageHeight = 16838, marginTop = 0, marginBottom = 0 } = params;
  const SAFETY = 1200;
  const usableHeight = pageHeight - marginTop - marginBottom - SAFETY;
  const titleHeight = titleLineCount * (titlePt * 23 + 200);
  const subtitleHeight = hasSubtitle ? (12 * 23 + 600) : 0;
  const englishLabelHeight = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaHeight = metaLineCount * (10 * 23 + 100);
  const implicitParaHeight = 3 * 300;
  const contentHeight = titleHeight + subtitleHeight + englishLabelHeight + metaHeight + fixedHeight + implicitParaHeight;
  const safeRemaining = Math.max(usableHeight - contentHeight, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(safeRemaining * 0.45), rawBottom = Math.floor(safeRemaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  const midSpacing = Math.max(safeRemaining - topSpacing - bottomSpacing, 0);
  return { topSpacing, midSpacing, bottomSpacing };
}

// ── Portada R1 (Pure Paragraph Left) ──
function buildCoverR1(config) {
  const padL = 1200, padR = 800;
  const availableWidth = 11906 - padL - padR - 300;
  const { titlePt, titleLines } = calcTitleLayout(config.title, availableWidth, 40, 24);
  const titleSize = titlePt * 2;
  const spacing = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel,
    metaLineCount: (config.metaLines || []).length, fixedHeight: 400,
  });
  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: P.accent, space: 12 };
  const children = [];
  children.push(new Paragraph({ spacing: { before: spacing.topSpacing } }));
  if (config.englishLabel) {
    children.push(new Paragraph({
      indent: { left: padL, right: padR }, spacing: { after: 500 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: P.accent, space: 8 } },
      children: [new TextRun({ text: config.englishLabel.split("").join("  "), size: 18, color: P.accent, font: { ascii: "Calibri", eastAsia: "SimHei" }, characterSpacing: 40 })],
    }));
  }
  for (let i = 0; i < titleLines.length; i++) {
    children.push(new Paragraph({
      indent: { left: padL },
      spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: titleLines[i], size: titleSize, bold: true, color: P.titleColor, font: { eastAsia: "SimHei", ascii: "Arial" } })],
    }));
  }
  if (config.subtitle) {
    children.push(new Paragraph({
      indent: { left: padL }, spacing: { after: 800 },
      children: [new TextRun({ text: config.subtitle, size: 24, color: P.subtitleColor, font: { eastAsia: "Microsoft YaHei", ascii: "Arial" } })],
    }));
  }
  for (const line of (config.metaLines || [])) {
    children.push(new Paragraph({
      indent: { left: padL + 200 }, spacing: { after: 80 },
      border: { left: accentLeft },
      children: [new TextRun({ text: line, size: 24, color: P.metaColor, font: { eastAsia: "Microsoft YaHei", ascii: "Arial" } })],
    }));
  }
  children.push(new Paragraph({ spacing: { before: spacing.bottomSpacing } }));
  children.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: config.footerLeft || "", size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
      new TextRun({ text: "                                        " }),
      new TextRun({ text: config.footerRight || "", size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({ shading: { type: ShadingType.CLEAR, fill: P.bg }, borders: noBorders, children })],
    })],
  })];
}

// ── Componentes de cuerpo ──
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text, bold: true, size: 32, color: P.heading, font: FONT_HEAD })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120, line: 312 },
    children: [new TextRun({ text, bold: true, size: 28, color: P.heading, font: FONT_HEAD })],
  });
}
function h3(text, colorExtra) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 220, after: 100, line: 312 },
    children: [new TextRun({ text, bold: true, size: 24, color: colorExtra || P.heading, font: FONT_HEAD })],
  });
}
function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312, after: opts.after != null ? opts.after : 120 },
    children: [new TextRun({ text, size: 24, color: P.body, font: FONT_BODY, bold: !!opts.bold })],
  });
}
function bodyRuns(runs, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312, after: opts.after != null ? opts.after : 120 },
    children: runs,
  });
}
function r(text, o = {}) {
  return new TextRun({ text, size: o.size || 24, color: o.color || P.body, font: o.font || FONT_BODY, bold: !!o.bold, italics: !!o.italics });
}
function evidenciaLine(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    indent: { left: 480 },
    spacing: { line: 264, after: 20 },
    border: { left: { style: BorderStyle.SINGLE, size: 6, color: P.tHeaderBg, space: 10 } },
    children: [new TextRun({ text, size: 17, color: "27343E", font: FONT_MONO })],
  });
}
function caption(text) {
  return new Paragraph({
    keepNext: true,
    spacing: { before: 160, after: 80, line: 312 },
    children: [new TextRun({ text, bold: true, size: 21, color: P.heading, font: FONT_BODY })],
  });
}
function celda(text, opts = {}) {
  return new TableCell({
    width: { size: opts.w, type: WidthType.PERCENTAGE },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      spacing: { line: 276 },
      children: [new TextRun({ text, size: opts.size || 20, bold: !!opts.bold, color: opts.color || P.body, font: FONT_BODY })],
    })],
  });
}
function tabla(headers, widths, rows, opts = {}) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: P.tHeaderBg },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: P.tHeaderBg },
      left: NB, right: NB,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: P.tInnerLine },
      insideVertical: NB,
    },
    rows: [
      new TableRow({
        tableHeader: true, cantSplit: true,
        children: headers.map((t, i) => celda(t, { w: widths[i], bold: true, fill: P.tHeaderBg, color: P.tHeaderText, center: true, size: opts.headSize || 20 })),
      }),
      ...rows.map((cells, ri) => new TableRow({
        cantSplit: true,
        children: cells.map((t, i) => celda(t, {
          w: widths[i],
          fill: opts.zebra && ri % 2 === 0 ? P.tSurface : undefined,
          color: opts.cellColors ? opts.cellColors(cells, i) : undefined,
          bold: opts.cellBold ? opts.cellBold(cells, i) : false,
        })),
      })),
    ],
  });
}

// ── Hallazgos ──
const sevColor = { ALTO: P.sevAlto, MEDIO: P.sevMedio, BAJO: P.sevBajo };
const estColor = { ABIERTO: P.sevAlto, PARCIAL: P.sevMedio, CERRADO: P.tHeaderBg, RETIRADO: P.secondary };
function findingBlock(f) {
  const out = [];
  out.push(h3(f.id + " [" + f.sev + " · " + f.estado + "] " + f.titulo, estColor[f.estado] || sevColor[f.sev]));
  out.push(bodyRuns([r("Dónde: ", { bold: true }), r(f.donde, { font: FONT_MONO, size: 19, color: "27343E" })], { after: 80 }));
  out.push(bodyRuns([r("Evidencia (código real, 21-11-2026):", { bold: true })], { after: 40 }));
  for (const line of f.evidencia) out.push(evidenciaLine(line));
  out.push(bodyRuns([r("Análisis: ", { bold: true }), r(f.porque.join(" "))], { after: 80 }));
  out.push(bodyRuns([r("Corrección propuesta: ", { bold: true, color: P.tHeaderBg }), r(f.fix, { italics: true })], { after: 200 }));
  return out;
}

// ── Cuerpo del informe ──
const cuerpo = [];

// 1 · Resumen ejecutivo
cuerpo.push(h1("1. Resumen ejecutivo"));
cuerpo.push(body("El 21 de noviembre de 2026 se realizó una re-auditoría de calidad completa del código del juego CRAZY PING PONG en su versión V3.6.209-SDK6 (commit 8a8d9b2, tras las rondas r110 y r111). Es la segunda auditoría integral del proyecto: la primera (r109, el mismo día) confirmó 18 hallazgos y dejó un plan de acción. Esta re-auditoría responde a una pregunta concreta del dueño — «¿está todo 100% correcto?» — con el método que la casa ya consolidó, más tres capas nuevas: el contraste línea a línea de los 18 hallazgos anteriores contra el código actual, la revisión completa del delta de código añadido desde r109, y la verificación del contrato cliente↔worker de producción, hoy desplegado y operando con un parche anti-cupo propio (r111-b)."));
cuerpo.push(body("El veredicto estructural vuelve a ser favorable: la sintaxis de los 16 subsistemas es correcta, no hay colisiones ni imports rotos, el build es byte-exacto contra el golden re-anclado (12.506.557 bytes, sha256 a627bed1…), la versión 3.6.209-SDK6 es coherente en todas sus manifestaciones y los nueve arneses que cubren el núcleo del juego (trayectorias golden de física, norma ITTF, núcleo binario de red e ICE) pasan sin una sola desviación. La batería se re-ejecutó completa y su resultado es IDÉNTICO al de r109: los mismos 40 arneses, los mismos 9 verdes y los mismos 31 fallidos por las mismas causas (sellos caducados y arneses de eras anteriores) — cero regresiones nuevas del motor."));
cuerpo.push(bodyRuns([
  r("Sobre los 18 hallazgos de r109, el estado hoy es: "),
  r("13 ABIERTOS sin corrección (H1 a H10, H12 del juego y H13/H14 del live-service), 2 CERRADOS en producción (H16 y H17, saneado del pid y de de/para en el worker de telemetría), 2 PARCIALES (H15 y H18) y 1 RETIRADO por carecer de sustento (H11: la cobertura de apoyo que señalaba ya existía en el arnés r102)", { bold: true }),
  r(". Se añade 1 hallazgo nuevo de severidad BAJA (N1: el live-service existe en 4 copias idénticas, riesgo de deriva de mantenimiento). El de mayor gravedad sigue siendo el mismo: cada golpe portalizado en un duelo online viaja con velocidad cero y puede fabricar un punto fantasma. En la práctica: el juego está lejos del 100% en el mismo ángulo muerto que ya señaló r109, porque ninguna de las correcciones propuestas en su plan de acción se ha aplicado todavía al código del juego."),
]));
cuerpo.push(body("A esto se suma una incidencia operativa activa el día de la auditoría: el worker de telemetría de producción (crazypp-tele) lleva horas devolviendo error 1101 porque la cuenta agotó el cupo diario de lecturas del free tier de D1 (error 7500, verificado por SQL directo). No es un defecto de código: se recupera solo a las 00:00 UTC y el parche r111-b ya desplegado (caché del latido y purga throttled) recorta ~90% el quemado de lecturas para que no se repita. La synchronización con GitHub continúa pendiente del GIT_TOKEN (6 commits locales sin empujar, desde r109-c).", { after: 200 }));

// 2 · Alcance y metodología
cuerpo.push(h1("2. Alcance y metodología"));
cuerpo.push(body("El alcance cubre todo el código del juego en el repositorio: los 16 subsistemas del motor en src/game/core/ (12,5 MB ensamblados), los wrappers HTML y sus dos copias (public/ y pages-site/), las gemelas QA de las APIs (presence, invite, telemetria), el worker de producción crazypp-tele (scripts/worker-tele/, incluido su parche r111-b y sus bindings reales verificados por API de Cloudflare) y el mini-servicio de CRAZY TV en sus 4 copias (mini-services/ más staging-v36207/v36209 y release-v36209). La auditoría se ejecutó sobre HEAD local (8a8d9b2), que va POR DELANTE del remoto: el push está pendiente del GIT_TOKEN desde r109-c, así que el local es la versión más avanzada."));
cuerpo.push(body("La metodología aplicó seis capas. Primera, verificación mecánica re-ejecutada: node --check fichero a fichero (16/16 más worker y módulos de red), higiene de placeholders (0 marcas reales: los 72 avisos del barrido son la palabra española «TODO») y comparación del build contra el golden (byte-exacto). Segunda, batería dinámica completa: los 40 arneses de regresión de la casa re-ejecutados con bun y clasificados uno a uno contra la línea base que r109 dejó documentada. Tercera, revisión del delta: análisis completo de las 75 líneas añadidas desde r109 (bump de versión, vigilante de cristales r110 en c07/c12, gobernador VR r111 en c12) más la verificación de que sus piezas nuevas (pendientes(), FIN_PLAZO) son correctas y seguras. Cuarta, contraste de hallazgos: dos revisores en paralelo re-verificaron los 18 de r109 contra el código actual, con localización y evidencia frescas de cada uno. Quinta, contratos: las 6 llamadas del cliente contra las rutas del worker, método y forma. Sexta, servicios y operaciones: bindings reales del worker por API, estado del cupo D1 por SQL directo y estado de la sincronización con GitHub."));
cuerpo.push(body("Dos salvaguardas de honestidad siguen en pie. Los estados (ABIERTO/CERRADO/PARCIAL/RETIRADO) entraron en este informe solo con evidencia literal del código de hoy: los cerrados citan las líneas exactas del worker que los cierran, y el retirado cita el arnés que ya cubría lo que r109 creyó sin cobertura. Y nada fue modificado: esta auditoría es de lectura — los cambios r110/r111 y el parche r111-b del worker ya estaban hechos y desplegados antes de la re-auditoría, y se auditaron como estaban. Los artefactos (batería con salidas completas, diagnosticador del worker por API, generador de este informe) quedaron bajo scripts/ para su repetición.", { after: 200 }));

// 3 · Verificación estructural
cuerpo.push(h1("3. Verificación estructural del motor"));
cuerpo.push(body("La capa mecánica busca las clases de error que tumban o corrompen un bundle de ámbito compartido: sintaxis inválida, colisiones de nombres de nivel superior entre subsistemas que comparten el único ámbito del bundle, imports que el fichero exportador no declara, assets con rutas inexistentes o con caso incorrecto, y divergencia entre las copias del juego. El resultado fue limpio en todas las categorías (tabla 1). El único delta de código desde r109 (75 líneas: bump de versión, vigilante de cristales cripto r110 y gobernador VR r111) se revisó completo y no añade colisiones, exports rotos ni defectos; sus piezas nuevas son seguras (la llamada de c12 está guardada por null-check y el try cubre el frame)."));
cuerpo.push(caption("Tabla 1: Verificación estructural (21-11-2026, commit 8a8d9b2)"));
cuerpo.push(tabla(
  ["Comprobación", "Resultado"],
  [62, 38],
  estructura,
  { zebra: true }
));
cuerpo.push(body("La observación de arquitectura de r109 sigue vigente (no es un defecto): THREE y sus addons se cargan en vivo desde el CDN jsdelivr con versión pinnada 0.170.0 mediante el importmap. Funciona hoy y la versión está fijada, pero convierte al CDN en punto único de fallo para el juego completo en Quest. El capítulo 7 mantiene la recomendación de valorar el vendor local.", { after: 200 }));

// 4 · Batería de regresión
cuerpo.push(h1("4. Resultados de la batería de regresión"));
cuerpo.push(body("La casa mantiene 45 arneses de regresión en scripts/. La re-auditoría ejecutó los mismos 40 que r109 (los 5 restantes son bancos de rendimiento o diagnósticos históricos sin veredicto). El resultado es literalmente el mismo que la línea base: 9 verdes y 31 con fallo, con las mismas salidas y el mismo modo de fallo (los 6 que crashean al arrancar repiten el marco de código de Bun). El dato relevante para el dueño es doble: los nueve verdes son exactamente los arneses que prueban el núcleo vivo del juego (tabla 2), y la clasificación uno a uno de los 31 fallidos no contiene NINGUNA regresión nueva respecto a r109 (tabla 3) — las rondas r110 y r111 no rompieron nada medible."));
cuerpo.push(caption("Tabla 2: Arneses del núcleo — todos en verde"));
cuerpo.push(tabla(
  ["Arnés", "Qué cubre", "Resultado"],
  [34, 42, 24],
  bateriasOk,
  { zebra: true }
));
cuerpo.push(body("El patrón de los fallos es el mismo que r109 clasificó, y las causas siguen sin ser regresiones: diez arneses anclan sellos de versión/fase/tamaño a rondas de octubre y principios de noviembre (pruebas de sello, no de comportamiento, con re-anclaje manual); siete esperan comportamientos cambiados intencionalmente en r109 (candado con migración, FORO3D desbloqueado, rejilla de 5 halls, constantes de poderes en config); qa_net_unit exige una precisión incompatible por diseño con el códec cuantizado PROTO 2; el arnés m7e tiene un artefacto propio (extrae c11 a /tmp e importa solo, cuando CONFIG_TORNEOS vive en c02 — 27 apariciones verificadas en el bundle); worker_r169 y zip_editor dependen de rutas eliminadas en la limpieza r109-b; y cadena_r91/r33-r37 crashean al arrancar por su marco de la era Bun antiguo. La consecuencia práctica tampoco cambió: la batería solo cubre fiablemente el núcleo físico y de red, y el re-anclaje sigue pendiente."));
cuerpo.push(caption("Tabla 3: Clasificación de los 31 arneses fallidos (idéntica a r109)"));
cuerpo.push(tabla(
  ["Arneses (n)", "Motivo del fallo", "Veredicto"],
  [30, 50, 20],
  bateriasFallidas,
  { zebra: true }
));
cuerpo.push(body("Nota r111: el parche del worker (r111-b) vino acompañado de la rotación de la clave de lectura y de dos mejoras en deploy_worker.py (keep_bindings por tipo para preservar TURN_API_TOKEN sin conocer su valor). El arnés del worker (test_worker_r169) sigue sin ejecutar por su dependencia de rutas eliminadas — la verificación del worker se hizo en su lugar por API directa contra producción.", { after: 200 }));

// 5 · Hallazgos: estado y detalle
cuerpo.push(h1("5. Hallazgos: estado y detalle"));
cuerpo.push(body("Los 18 hallazgos de r109 más el nuevo N1 se identifican con los mismos prefijos. La tabla 4 resume el estado de cada uno tras el contraste línea a línea de hoy; las subsecciones 5.2 a 5.5 detallan cada grupo con la evidencia literal del código actual (las líneas citadas corresponden al commit 8a8d9b2). Ninguna corrección del juego fue aplicada por esta auditoría: las de los abiertos siguen siendo propuestas pendientes de aprobación, y las cifras de impacto son estimadas por lectura."));
cuerpo.push(caption("Tabla 4: Estado de los 19 hallazgos (r109 + N1) al 21-11-2026"));
cuerpo.push(tabla(
  ["ID", "Sev.", "Estado", "Nota"],
  [8, 12, 17, 63],
  estadoRows,
  { zebra: true, headSize: 19 }
));

const abiertosJuego = findings.filter((f) => f.estado === "ABIERTO" && ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H12"].includes(f.id));
const abiertosLive = findings.filter((f) => f.estado === "ABIERTO" && ["H13", "H14", "N1"].includes(f.id));
const cerrados = findings.filter((f) => f.estado === "CERRADO");
const parciales = findings.filter((f) => f.estado === "PARCIAL");
const retirados = findings.filter((f) => f.estado === "RETIRADO");

cuerpo.push(h2("5.1 Resumen de estado (tabla 4)"));
cuerpo.push(body("Lectura rápida: 14 abiertos (13 heredados de r109 más el nuevo N1), 2 cerrados en producción, 2 parciales y 1 retirado. Lo más significativo es la permanencia: ningún hallazgo del juego se corrigió desde r109 — el plan de acción de esa auditoría sigue íntegramente pendiente de ejecución.", { after: 120 }));

cuerpo.push(h2("5.2 Hallazgos abiertos del juego (H1 a H10, H12)"));
cuerpo.push(body("Defectos reales con impacto acotado, todos re-verificados hoy en el código vigente: el golpe portalizado online (H1, ALTO), la robustez de la red ante paquetes atrasados o canales medio muertos (H2, H3, H6, H7), el texto de la causa del punto para el anfitrión (H4), el salto visual del handoff (H5), la estadística de saques que alimenta logros y puertas (H8, H9) y la precisión del apoyo con rotación de muñeca (H10), más la inconsistencia del saque durante la cuenta atrás online (H12). Ninguno tumba el juego; H1 sigue siendo el único con efecto visible en partidas online normales.", { after: 120 }));
for (const f of abiertosJuego) cuerpo.push(...findingBlock(f));

cuerpo.push(h2("5.3 Hallazgos abiertos del live-service (H13, H14, N1)"));
cuerpo.push(body("El relay de CRAZY TV conserva los dos defectos de propiedad/contador señalados por r109 (el código de las 4 copias es idéntico y no cambió), y la re-auditoría añade un hallazgo de mantenimiento: el servicio está replicado en 4 ficheros idénticos que hoy ayudan (arreglar una es arreglar todas) pero que divergirán silenciosamente en cuanto alguien arregle una sola copia.", { after: 120 }));
for (const f of abiertosLive) cuerpo.push(...findingBlock(f));

cuerpo.push(h2("5.4 Hallazgos cerrados desde r109 (H16, H17)"));
cuerpo.push(body("Dos hallazgos de validación de entrada quedaron cerrados en la ruta que importa — el worker de telemetría de producción, donde viven los datos reales — gracias al trabajo de las rondas r109 (FASE 171) y r111-b. Las gemelas QA de Next.js (receptores de desarrollo) conservan el patrón antiguo; su arreglo queda como higiene, no como riesgo.", { after: 120 }));
for (const f of cerrados) cuerpo.push(...findingBlock(f));

cuerpo.push(h2("5.5 Parciales (H15, H18) y retirado (H11)"));
cuerpo.push(body("H15 (validación de publish del live-service) ganó la mitad de tipo pero no la de longitudes. H18 (telemetría) cerró la mitad peligrosa: el DELETE de purga de producción hoy exige la clave (403 sin ella); el CORS abierto se mantiene por diseño del cliente público y la gemela QA sigue sin token. H11 se retira: la cobertura de apoyo que r109 dio por ausente ya existía en el arnés anti-robótico r102 y en los P0 — el matiz sim/real de los predictores sigue siendo una mejora de precisión de la IA, no una carencia de regresión.", { after: 120 }));
for (const f of parciales) cuerpo.push(...findingBlock(f));
for (const f of retirados) cuerpo.push(...findingBlock(f));

// 6 · Descartes verificados
cuerpo.push(h1("6. Descartes verificados"));
cuerpo.push(body("Una auditoría honesta documenta también lo que se sospechó y resultó estar bien: evita re-auditar lo mismo y da al dueño una imagen real de la cobertura. Las diecisiete sospechas de la tabla 5 heredan de r109 (el código que cubren no cambió) y siguen descartadas; la tabla 6 recoge las verificaciones nuevas o re-anchadas de esta re-auditoría, incluida la revisión completa del delta r110/r111 y la clasificación del incidente operativo del worker."));
cuerpo.push(caption("Tabla 5: Sospechas descartadas en r109 — vigentes (código sin cambios)"));
cuerpo.push(tabla(
  ["Sospecha auditada", "Resultado de la verificación"],
  [40, 60],
  descartes,
  { zebra: true }
));
cuerpo.push(caption("Tabla 6: Verificaciones nuevas o re-anchadas en r111"));
cuerpo.push(tabla(
  ["Verificación", "Resultado"],
  [40, 60],
  descartesNuevos,
  { zebra: true }
));

// 7 · Conclusiones y plan de acción
cuerpo.push(h1("7. Conclusiones y plan de acción"));
cuerpo.push(body("Conclusión general: la estructura sigue sana y el núcleo físico y de red pasa íntegramente los arneses que lo cubren, con cero regresiones en las rondas nuevas (r110 y r111). La respuesta directa a «¿está todo 100% correcto?» es NO, y la razón es concreta y medible: de los 18 defectos que r109 confirmó, 13 siguen abiertos sin una línea de corrección aplicada (el ALTO incluido), a los que se suma el nuevo N1. Lo que sí avanzó desde r109 es la capa de servicios de producción: el worker de telemetría sanea hoy las entradas que r109 señaló (H16, H17) y protege su purga con clave (mitad de H18), y su parche r111-b evita que el cupo del free tier vuelva a tumbar la telemetría con el patrón de lectura del panel."));
cuerpo.push(body("Plan de acción recomendado, por orden de ejecución (todas las correcciones propuestas son quirúrgicas y ninguna toca el golden de trayectorias, salvo H10 que conviene acompañar de un mini-arnés de apoyo con muñeca):"));
cuerpo.push(caption("Tabla 7: Plan de acción actualizado (r111)"));
cuerpo.push(tabla(
  ["Prioridad", "Hallazgos", "Acción", "Esfuerzo"],
  [16, 14, 56, 14],
  [
    ["Inmediata (antes de la próxima ronda online)", "H1, H2, H12", "Enviar la velocidad de salida real del portal en el HIT (o reordenar los bloques 5.55/5.6); añadir la guardia de estado de rally a la rama HANDOFF; añadir la guardia de _netStart a las dos rutas del gatillo de saque. Idéntico al plan de r109: sigue sin ejecutarse.", "Pequeño"],
    ["Corto plazo", "H8, H9, H10, H6, H7, H3", "RallyHits del ace a 0 (c06 y espejo c12); pasar ball.spin al disparo diferido del mishit; término bladeCenterUp en el apoyo; markSent en SNAP; criterio de túnel en _flushEvents; watchdog accesible en v1 y sensible al canal fast.", "Pequeño-medio"],
    ["Decisión del dueño", "H4, H5", "Remapear siempre la causa del claim como proveniente del otro lado; llamar visDelta en el render de la bola o retirar la feature y sus campos.", "Pequeño"],
    ["Servicios (live-service)", "H13, H14, H15, N1", "Verificación de propiedad en state/event; leaveWatch en watch; topes de longitud en publish. Elegir UNA fuente de verdad para el relay y generar staging/release por empaquetado (o check de igualdad en la batería) — aplicar SIEMPRE en las 4 copias.", "Pequeño-medio"],
    ["Higiene de la batería", "31 arneses fallidos", "Re-anclar sellos a un único punto central de versión; reparar o retirar los que dependen de upload/ y editor_src; corregir la extracción de módulo de m7e; registrar la convención del códec en qa_net_unit.", "Medio"],
    ["Higiene de las gemelas QA", "H16, H17, H18 (route.ts)", "Replicar el saneo del worker (pid/de/para con tope) y un token en el DELETE de telemetria de Next.js si esas rutas vuelven a exponerse.", "Pequeño"],
    ["Operaciones", "Worker + GitHub", "Cupo D1: el parche r111-b ya desplegado reduce el quemado; si vuelve a agotarse, valorar el plan pago ($5/mes, cupo x50, aplica al instante). Push de los 6 commits pendientes de GIT_TOKEN. Revocar y rotar los tokens que pasaron por el chat.", "Pequeño"],
    ["Resiliencia (opcional)", "Importmap CDN", "Valorar el vendor local de three@0.170.0 y addons para eliminar el punto único de fallo del CDN en Quest.", "Medio"],
  ],
  { zebra: true }
));
cuerpo.push(body("Cierre del proceso: la re-auditoría no modificó ninguna línea del repositorio. Si el dueño aprueba el plan: prioridad inmediata (H1, H2, H12), regenerar el build, correr la batería y consolidar el re-anclaje en la misma ronda. La repetibilidad queda garantizada bajo scripts/.", { after: 0 }));

// ── Documento ──
const pgSize = { width: 11906, height: 16838 };
const pgMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };

function footerPage(markerColor) {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: markerColor })],
    })],
  });
}
const headerBody = new Header({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "C8DDE2", space: 4 } },
    children: [new TextRun({ text: "Auditoría de calidad · CRAZY PING PONG V3.6.209-SDK6 (re-auditoría r111)", size: 18, color: "808080", font: FONT_BODY })],
  })],
});

const doc = new Document({
  creator: "Auditoría CRAZY PING PONG",
  title: "Auditoría de calidad del código del juego — CRAZY PING PONG re-auditoría r111",
  styles: {
    default: {
      document: {
        run: { font: FONT_BODY, size: 24, color: "000000" },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: {
        run: { font: FONT_HEAD, size: 32, bold: true, color: P.heading },
        paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 },
      },
      heading2: {
        run: { font: FONT_HEAD, size: 28, bold: true, color: P.heading },
        paragraph: { spacing: { before: 240, after: 120, line: 312 }, outlineLevel: 1 },
      },
      heading3: {
        run: { font: FONT_HEAD, size: 24, bold: true, color: P.heading },
        paragraph: { spacing: { before: 220, after: 100, line: 312 }, outlineLevel: 2 },
      },
    },
  },
  sections: [
    { // Sección 1 · Portada (sin numeración)
      properties: { page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverR1({
        title: "Auditoría de calidad del código del juego",
        subtitle: "CRAZY PING PONG · V3.6.209-SDK6 · commit 8a8d9b2 (re-auditoría r111)",
        englishLabel: "QUALITY AUDIT REPORT",
        metaLines: [
          "Alcance: 16 subsistemas · wrappers · worker de producción · live-service (4 copias)",
          "Método: build byte-exacto + 40 arneses + contraste de los 18 hallazgos r109 + delta + contratos",
          "Resultado: 14 abiertos · 2 cerrados · 2 parciales · 1 retirado · núcleo en verde",
          "Fecha: 21 de noviembre de 2026",
        ],
        footerLeft: "CRAZY PING PONG",
        footerRight: "Informe de auditoría interna",
      }),
    },
    { // Sección 2 · Índice (romanos)
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
      },
      footers: { default: footerPage("888887") },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 480, after: 360 },
          children: [new TextRun({ text: "Índice", bold: true, size: 32, color: P.heading, font: FONT_HEAD })],
        }),
        new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({
          spacing: { before: 200 },
          children: [new TextRun({
            text: "Nota: este índice se genera mediante códigos de campo. Tras editar el documento, haga clic derecho sobre el índice y elija «Actualizar campos» para refrescar la paginación.",
            italics: true, size: 18, color: "888888", font: FONT_BODY,
          })],
        }),
        // El salto de sección NEXT_PAGE ya separa el índice del cuerpo:
        // un PageBreak aquí crearía una página en blanco (postcheck).
      ],
    },
    { // Sección 3 · Cuerpo (arábigos desde 1)
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
      },
      headers: { default: headerBody },
      footers: { default: footerPage("808080") },
      children: cuerpo,
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = "/home/z/my-project/download/Auditoria_calidad_CrazyPP_r111.docx";
  fs.writeFileSync(out, buf);
  console.log("OK " + out + " (" + buf.length + " B)");
});
