// Generador del informe de auditoría — CRAZY PING PONG r109
// Ruta Create + escena Report (Perfil A) + portada R1/DM-1 + TOC 3 secciones.
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, PageNumber, NumberFormat, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, SectionType, TableOfContents,
  PageBreak, TableLayoutType,
} = require("docx");
const fs = require("fs");
const { findings, descartes, bateriasOk, bateriasFallidas, estructura } = require("./datos.js");

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
  // Texto español (latino): ancho medio por carácter ≈ pt*11.5
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
function findingBlock(f) {
  const out = [];
  out.push(h3(f.id + " [" + f.sev + "] " + f.titulo, sevColor[f.sev]));
  out.push(bodyRuns([r("Dónde: ", { bold: true }), r(f.donde, { font: FONT_MONO, size: 19, color: "27343E" })], { after: 80 }));
  out.push(bodyRuns([r("Evidencia (código real):", { bold: true })], { after: 40 }));
  for (const line of f.evidencia) out.push(evidenciaLine(line));
  out.push(bodyRuns([r("Por qué es un bug: ", { bold: true }), r(f.porque.join(" "))], { after: 80 }));
  out.push(bodyRuns([r("Corrección sugerida: ", { bold: true, color: P.tHeaderBg }), r(f.fix, { italics: true })], { after: 200 }));
  return out;
}

// ── Cuerpo del informe ──
const cuerpo = [];

// 1 · Resumen ejecutivo
cuerpo.push(h1("1. Resumen ejecutivo"));
cuerpo.push(body("El 21 de noviembre de 2026 se realizó una auditoría de calidad completa del código del juego CRAZY PING PONG en su versión V3.6.207-SDK6 (commit 669a08e, ronda r109). La auditoría combinó cuatro capas de análisis: verificación estructural automatizada de los 16 subsistemas del motor, regeneración byte-exacto del build contra el golden, ejecución de los 45 arneses de regresión que la propia casa mantiene, y cuatro revisiones profundas en paralelo (física y gesto, red multijugador, bucle y saque del módulo central, y el resto de subsistemas junto a los servicios del lado servidor). Cada hallazgo fue consolidado y re-verificado por lectura directa del código antes de entrar en este informe."));
cuerpo.push(body("El veredicto de partida es favorable: la estructura del código está sana. La sintaxis de los 16 subsistemas es correcta, no existen colisiones de nombres en el ámbito compartido del bundle, todas las dependencias entre ficheros se resuelven, la regeneración del build es byte-exacto contra el golden (12.502.469 bytes, sha256 7c645570…) y los nueve arneses que cubren el núcleo del juego (trayectorias golden de física, norma ITTF de los botes, núcleo binario de red e ICE) pasan sin una sola desviación."));
cuerpo.push(bodyRuns([
  r("La auditoría confirma "),
  r("18 hallazgos reales: 1 de severidad ALTA, 14 MEDIA y 3 BAJA", { bold: true }),
  r(". Ninguno está cubierto por los arneses actuales: afectan a caminos que los golden no recorren (el portal de Duelos Locos online, el handoff de red, el apoyo de la bola con rotación de muñeca, la estadística de saques y la validación de entrada de los servicios). El hallazgo de mayor gravedad afecta a cada golpe portalizado en un duelo online: la velocidad que viaja en el HIT es el vector cero, con bola congelada en el rival y riesgo de reclamación de un punto fantasma."),
]));
cuerpo.push(body("Los 31 arneses de rondas anteriores que hoy fallan no corresponden a regresiones del juego: la clasificación uno a uno (sección 4) muestra que son sellos de versión y fase caducados (esperan 3.6.129 a 3.6.157 y la FASE 160, cuando el juego está en 3.6.207 y FASE 184), expectativas de comportamientos cambiados intencionalmente en la r109 (candado, FORO3D, rejilla de salones) y diez arneses que ni siquiera llegan a arrancar por dependencias eliminadas en la limpieza de esa misma ronda. Recomiendo un re-anclaje sistemático de la batería para recuperar su valor como red de seguridad.", { after: 200 }));

// 2 · Alcance y metodología
cuerpo.push(h1("2. Alcance y metodología"));
cuerpo.push(body("El alcance cubre todo el código del juego en el repositorio: los 16 subsistemas del motor en src/game/core/ (desde el pre-vendor c00 hasta la UI de arranque c13, unos 12,5 MB ensamblados), los wrappers HTML, el motor paralelo de la web Next.js (solo para descartarlo como objetivo), las rutas API de QA del servidor (presence, invite, telemetria, channels) y el mini-servicio de CRAZY TV (mini-services/live-service). El worker de producción crazypp-tele está fuera del repositorio y no pudo auditarse aquí; sus gemelas de QA sí."));
cuerpo.push(body("La metodología aplicó cuatro capas en orden creciente de profundidad. Primera, verificación mecánica: comprobación de sintaxis fichero a fichero con node --check como módulo ES, resolución de cada nombre importado contra las declaraciones reales del fichero exportador, detección de colisiones de declaraciones top-level (los 16 subsistemas comparten un único ámbito en el bundle) y contraste de todas las rutas de assets referenciadas contra los ficheros existentes en public/ (GitHub Pages es sensible a mayúsculas). Segunda, verificación de build: regeneración del juego con el ensamblador oficial y comparación byte-exacto contra el golden. Tercera, capa dinámica: ejecución de los 45 arneses de regresión de la casa con bun, con captura de salida completa de los fallidos para clasificarlos. Cuarta, revisión profunda por zonas: cuatro líneas de auditoría especializada (física y gesto; red; hot paths del módulo central; resto y servidor) que leyeron los ficheros completos de su ámbito y contrastaron cada sospecha con el código circundante."));
cuerpo.push(body("Dos salvaguardas de honestidad atraviesan todo el proceso. Los hallazgos entraron en este informe solo tras la verificación de consolidación: el auditor principal releyó el código de los hallazgos principales (portal, HANDOFF, aces, constantes de poderes, CONFIG_TORNEOS) y descartó los avisos automáticos que resultaron falsos positivos. Y nada fue modificado: esta auditoría es de lectura, todos los ficheros del repositorio quedan intactos, y las correcciones del capítulo 7 son propuestas pendientes de aprobación y ejecución. Los artefactos del proceso (scripts de auditoría mecánica y dinámica, salidas completas de los arneses fallidos) quedaron conservados bajo scripts/ para su repetición.", { after: 200 }));

// 3 · Verificación estructural
cuerpo.push(h1("3. Verificación estructural del motor"));
cuerpo.push(body("La capa mecánica busca las clases de error que tumban o corrompen un bundle de ámbito compartido: sintaxis inválida, dos subsistemas que declaran el mismo nombre de nivel superior (error o sombra silenciosa según el tipo), nombres importados que el fichero exportador no declara (ReferenceError en vivo) y assets referenciados con una ruta que no existe o cuyo caso no coincide exactamente. El resultado fue limpio en las cuatro categorías, como resume la tabla 1. Los 36 avisos que produjo el barrido automático de assets fueron triados uno a uno y todos resultaron falsos positivos: especifiers de import que el ensamblador elimina, rutas construidas por concatenación (como championships/<id>/assets/insignia.png, presente en las cinco variantes) y cadenas que están dentro de comentarios de documentación."));
cuerpo.push(caption("Tabla 1: Verificación estructural (21-11-2026, commit 669a08e)"));
cuerpo.push(tabla(
  ["Comprobación", "Resultado"],
  [62, 38],
  estructura,
  { zebra: true }
));
cuerpo.push(body("Una observación de arquitectura (no es un defecto): THREE y sus addons (GLTFLoader, RoomEnvironment) se cargan en vivo desde el CDN jsdelivr con versión pinnada 0.170.0 mediante el importmap del bundle. Funciona hoy y la versión está fijada, pero convierte al CDN en punto único de fallo para el juego completo: sin red o con el CDN caído, la Quest no arranca partida. En el capítulo 7 se propone valorar el vendor local como mejora de resiliencia.", { after: 200 }));

// 4 · Batería de regresión
cuerpo.push(h1("4. Resultados de la batería de regresión"));
cuerpo.push(body("La casa mantiene 45 arneses de regresión en scripts/. La auditoría instaló dependencias y ejecutó 40 de ellos (los 5 restantes son bancos de rendimiento o diagnósticos históricos sin veredicto). El resultado global es de 9 verdes y 31 con fallo, pero el dato relevante es la distribución: los nueve verdes son exactamente los arneses que prueban el núcleo vivo del juego (tabla 2), y los 31 fallidos se clasifican, uno a uno y con la salida completa capturada, en cinco categorías que no incluyen ninguna regresión del motor (tabla 3)."));
cuerpo.push(caption("Tabla 2: Arneses del núcleo — todos en verde"));
cuerpo.push(tabla(
  ["Arnés", "Qué cubre", "Resultado"],
  [34, 42, 24],
  bateriasOk,
  { zebra: true }
));
cuerpo.push(body("El patrón de los fallos es coherente y explicable. Diez arneses anclan sellos de versión, fase y tamaño de build a rondas de octubre y principios de noviembre (esperan 3.6.129 a 3.6.157, FASE 160, y tamaños de build de ~11,5 MB): son pruebas de sello, no de comportamiento, y quedaron caducos con cada bump porque el re-anclaje era manual. Otras expectativas corresponden a decisiones deliberadas de la r109 que el dueño pidió revertir o cambiar: el candado de la Criptonita vuelve a nacer bloqueado con migración, FORO3D está desbloqueado por orden directa y la rejilla del hall pasó a cinco variantes. El arnés qa_net_unit exige una precisión de 1e-9 en la ida y vuelta del códec de red, incompatible por diseño con el códec cuantizado PROTO 2 vigente (precisión de milímetros, correcta para el juego). El caso de test_m7e merece mención: no es un fallo del juego, sino un artefacto del propio arnés, que extrae el subsistema c11 a un fichero temporal e importa solo; la constante CONFIG_TORNEOS vive en c02 y el juego real la resuelve (27 apariciones verificadas en el bundle)."));
cuerpo.push(caption("Tabla 3: Clasificación de los 31 arneses fallidos"));
cuerpo.push(tabla(
  ["Arneses (n)", "Motivo del fallo", "Veredicto"],
  [30, 50, 20],
  bateriasFallidas,
  { zebra: true }
));
cuerpo.push(body("La consecuencia práctica es que la batería ha perdido su valor como red de seguridad general: hoy solo cubre fiablemente el núcleo físico y de red. La recomendación del capítulo 7 incluye un re-anclaje sistemático (idealmente, un único punto central de versión que los sellos consulten, para que el bump no rompa treinta arneses a la vez) y la reparación de los arneses que dependen de rutas eliminadas en la limpieza r109-b.", { after: 200 }));

// 5 · Hallazgos confirmados
cuerpo.push(h1("5. Hallazgos confirmados"));
cuerpo.push(body("Los 18 hallazgos se agrupan por severidad y se identifican con el prefijo H1 a H18. Cada entrada indica el fichero y las líneas exactas del commit 669a08e, la evidencia literal del código, la explicación del defecto y la corrección propuesta. Ninguna corrección fue aplicada: todas quedan a la espera de la aprobación del dueño, y las cifras de impacto son las estimadas por lectura, no por medición en partida."));
const altos = findings.filter(f => f.sev === "ALTO");
const medios = findings.filter(f => f.sev === "MEDIO");
const bajos = findings.filter(f => f.sev === "BAJO");

cuerpo.push(h2("5.1 Severidad ALTA (1 hallazgo)"));
cuerpo.push(body("Único hallazgo con efecto directo y visible en cada partida online que use el poder afectado. Se recomienda corregir antes de la siguiente ronda con duelo online.", { after: 120 }));
for (const f of altos) cuerpo.push(...findingBlock(f));

cuerpo.push(h2("5.2 Severidad MEDIA (14 hallazgos)"));
cuerpo.push(body("Defectos reales con impacto acotado: robustez de la red multijugador ante paquetes atrasados o canales medio muertos, precisión del apoyo de la bola con giro de muñeca, estadística de saques que alimenta logros y puertas de salones, una inconsistencia del saque durante la cuenta atrás online, y validación de entrada ausente en el relay de CRAZY TV y en las APIs de presencia. Ninguno tumba el juego; todos degradan algo que el dueño ha definido como contrato.", { after: 120 }));
for (const f of medios) cuerpo.push(...findingBlock(f));

cuerpo.push(h2("5.3 Severidad BAJA (3 hallazgos)"));
cuerpo.push(body("Higiene y superficie de ataque de los servicios de apoyo (API de invitaciones y telemetría de QA, y la divergencia de los simuladores de predicción de la IA). Bajo riesgo hoy, corrección barata.", { after: 120 }));
for (const f of bajos) cuerpo.push(...findingBlock(f));

// 6 · Descartes verificados
cuerpo.push(h1("6. Descartes verificados"));
cuerpo.push(body("Una auditoría honesta debe documentar también lo que se sospechó y resultó estar bien: evita re-auditar lo mismo y da al dueño una imagen real de la cobertura. Las diecisiete sospechas de la tabla 4 se plantearon durante la revisión (varias por el historial de la casa, como la fórmula de la curva del gesto corregida en la r100) y quedaron descartadas tras la verificación con el código real. En particular, las cuatro grandes clases de error que la r100 corrigió en su día (curva Catmull-Rom, alias del contacto, sombra del cuerpo y convenios de spin) están hoy sanas."));
cuerpo.push(caption("Tabla 4: Sospechas planteadas y descartadas tras verificación"));
cuerpo.push(tabla(
  ["Sospecha auditada", "Resultado de la verificación"],
  [40, 60],
  descartes,
  { zebra: true }
));

// 7 · Conclusiones y plan de acción
cuerpo.push(h1("7. Conclusiones y plan de acción"));
cuerpo.push(body("Conclusión general: el código del juego está estructuralmente sano y su núcleo físico y de red pasa íntegramente los arneses que lo cubren. Los 18 defectos confirmados residen en el ángulo muerto de esos arneses: los caminos online que solo se activan con poderes y handoffs (H1, H2, H12), los matices de la red a mitad de carrera (H3 a H7), el apoyo con rotación de muñeca (H10), la estadística del saque (H8, H9) y la validación de entrada de los servicios de apoyo (H13 a H18). Ninguno bloquea el juego; uno degrada visiblemente los duelos online con portal."));
cuerpo.push(body("Plan de acción recomendado, por orden de ejecución y con estimación de esfuerzo en cambios sobre src/game/core/ (todas las correcciones propuestas son quirúrgicas y ninguna toca el golden de trayectorias, salvo H10 que conviene acompañar de un mini-arnés de apoyo con muñeca para anclar el nuevo comportamiento)."));
cuerpo.push(caption("Tabla 5: Plan de acción propuesto"));
cuerpo.push(tabla(
  ["Prioridad", "Hallazgos", "Acción", "Esfuerzo"],
  [16, 14, 56, 14],
  [
    ["Inmediata (antes de la próxima ronda online)", "H1, H2, H12", "Enviar la velocidad de salida real del portal en el HIT (o reordenar los bloques 5.55/5.6); añadir la guardia de estado de rally a la rama HANDOFF; añadir la guardia de _netStart a las dos rutas del gatillo de saque.", "Pequeño"],
    ["Corto plazo", "H8, H9, H10, H6, H7, H3", "RallyHits del ace a 0; pasar ball.spin al disparo diferido del mishit; término bladeCenterUp en el apoyo; markSent en SNAP; criterio de túnel en _flushEvents; watchdog accesible en v1 y sensible al canal fast.", "Pequeño-medio"],
    ["Decisión del dueño", "H4, H5", "Remapear siempre la causa del claim como proveniente del otro lado; llamar visDelta en el render de la bola o retirar la feature y sus campos.", "Pequeño"],
    ["Servicios (QA y live-service)", "H13, H14, H15, H16, H17, H18", "Verificación de propiedad en state/event; leaveWatch en watch; regex y recortes en publish, pid, de y para; CORS y token en el DELETE de telemetría.", "Pequeño"],
    ["Higiene de la batería", "31 arneses fallidos", "Re-anclar sellos a un único punto central de versión (que el bump no rompa treinta arneses); reparar o retirar los que dependen de upload/ y editor_src (eliminados en r109-b); corregir la extracción de módulo de m7e; registrar la convención del códec cuantizado en qa_net_unit.", "Medio"],
    ["Resiliencia (opcional)", "Importmap CDN", "Valorar el vendor local de three@0.170.0 y addons para eliminar el punto único de fallo del CDN en Quest.", "Medio"],
  ],
  { zebra: true }
));
cuerpo.push(body("Cierre del proceso: la auditoría no modificó ninguna línea del repositorio. Los artefactos de la auditoría (script mecánico y su informe completo, script de batería con salidas de los 31 fallidos bajo scripts/auditoria_fallos/, y este generador del informe) quedaron guardados bajo scripts/ para que la revisión sea repetible tras aplicar las correcciones. Si el dueño aprueba el plan, el orden natural es ejecutar la prioridad inmediata, regenerar el build con el ensamblador oficial, correr de nuevo la batería y consolidar el re-anclaje en la misma ronda.", { after: 0 }));

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
    children: [new TextRun({ text: "Auditoría de calidad · CRAZY PING PONG V3.6.207-SDK6 (r109)", size: 18, color: "808080", font: FONT_BODY })],
  })],
});

const doc = new Document({
  creator: "Auditoría CRAZY PING PONG",
  title: "Auditoría de calidad del código del juego — CRAZY PING PONG r109",
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
        subtitle: "CRAZY PING PONG · V3.6.207-SDK6 · commit 669a08e (ronda r109)",
        englishLabel: "QUALITY AUDIT REPORT",
        metaLines: [
          "Alcance: 16 subsistemas del motor · wrappers HTML · APIs de QA · live-service",
          "Método: verificación estructural + build byte-exacto + 45 arneses + revisión profunda",
          "Resultado: 18 hallazgos confirmados (1 ALTO · 14 MEDIO · 3 BAJO) · núcleo en verde",
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
  const out = "/home/z/my-project/download/Auditoria_calidad_CrazyPP_r109.docx";
  fs.writeFileSync(out, buf);
  console.log("OK " + out + " (" + buf.length + " B)");
});
