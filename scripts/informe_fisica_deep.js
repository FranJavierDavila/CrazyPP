/* Informe: Análisis profundo de la física de CrazyPP — V3.6.176-SDK6
 * Receta R1 (Pure Paragraph Left) + paleta DM-1 · perfil formal (TNR) · ES
 * TOC de 3 secciones (portada sin pie / índice romano / cuerpo arábigo)
 * Ejecutar: node scripts/informe_fisica_deep.js  → download/…docx
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, PageNumber, NumberFormat, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, SectionType, TableOfContents,
  PageBreak, TableLayoutType,
} = require("docx");
const fs = require("fs");

/* ---------- paleta DM-1 (Deep Cyan — tech) ---------- */
const P = {
  bg: "162235", accent: "37DCF2",
  cover: { titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F", footerColor: "687078" },
  table: { headerBg: "1B6B7A", headerText: "FFFFFF", innerLine: "C8DDE2", surface: "EDF3F5" },
  primary: "162235", body: "000000", secondary: "606060",
};
const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };

/* ---------- helpers de texto (español, perfil formal) ---------- */
const F_BODY = { ascii: "Times New Roman", eastAsia: "Times New Roman" };
const F_HEAD = { ascii: "Times New Roman", eastAsia: "Times New Roman" };

function h1(num, text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text: num + ". " + text, bold: true, size: 32, color: P.primary, font: F_HEAD })],
  });
}
function h2(num, text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120, line: 312 },
    children: [new TextRun({ text: num + " " + text, bold: true, size: 28, color: P.primary, font: F_HEAD })],
  });
}
function p(runsOrText) {
  const runs = typeof runsOrText === "string"
    ? [new TextRun({ text: runsOrText, size: 24, color: P.body, font: F_BODY })]
    : runsOrText;
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312, after: 120 },
    children: runs,
  });
}
function t(text) { return new TextRun({ text, size: 24, color: P.body, font: F_BODY }); }
function b(text) { return new TextRun({ text, bold: true, size: 24, color: P.body, font: F_BODY }); }
function code(text) {
  return new TextRun({ text, size: 21, color: "1B6B7A", font: { ascii: "Consolas", eastAsia: "Consolas" } });
}
function tNota(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, before: 60, after: 120 },
    indent: { left: 400 },
    border: { left: { style: BorderStyle.SINGLE, size: 8, color: P.table.headerBg, space: 8 } },
    children: [new TextRun({ text, italics: true, size: 21, color: P.secondary, font: F_BODY })],
  });
}

/* ---------- tabla estilo Horizontal-Only (DM-1) ---------- */
function tabla(titulo, headers, filas, anchos) {
  const headerCells = headers.map((txt, i) => new TableCell({
    width: { size: anchos[i], type: WidthType.PERCENTAGE },
    shading: { type: ShadingType.CLEAR, fill: P.table.headerBg },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({ spacing: { line: 276 }, children: [
      new TextRun({ text: txt, bold: true, size: 21, color: P.table.headerText, font: F_BODY }),
    ] })],
  }));
  const dataRows = filas.map((fila, ri) => new TableRow({
    cantSplit: true,
    children: fila.map((cell, ci) => new TableCell({
      width: { size: anchos[ci], type: WidthType.PERCENTAGE },
      shading: { type: ShadingType.CLEAR, fill: ri % 2 === 0 ? "FFFFFF" : P.table.surface },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ spacing: { line: 276 }, children: [
        new TextRun({ text: cell, size: 21, color: P.body, font: F_BODY }),
      ] })],
    })),
  }));
  return [
    new Paragraph({
      keepNext: true, spacing: { before: 160, after: 80, line: 312 },
      children: [new TextRun({ text: titulo, bold: true, size: 21, color: P.primary, font: F_BODY })],
    }),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 2, color: P.table.headerBg },
        bottom: { style: BorderStyle.SINGLE, size: 2, color: P.table.headerBg },
        left: NB, right: NB,
        insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: P.table.innerLine },
        insideVertical: NB,
      },
      rows: [new TableRow({ tableHeader: true, cantSplit: true, children: headerCells }), ...dataRows],
    }),
    new Paragraph({ spacing: { after: 120 }, children: [] }),
  ];
}

/* ---------- portada R1 (calcTitleLayout + calcCoverSpacing) ---------- */
function splitTitleLines(title, charsPerLine) {
  if (title.length <= charsPerLine) return [title];
  const breakAfter = new Set([..."，。、；：！？", ..."de y la el en a o u por del ", ..."-_—–·/ \t"]);
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
    const last = lines.pop(); lines[lines.length - 1] += " " + last;
  }
  return lines;
}
function calcTitleLayout(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  // texto latino: ancho medio ≈ pt*11 twips por carácter ( mezcla ES )
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
    metaLineCount = 0, fixedHeight = 800, pageHeight = 16838 } = params;
  const SAFETY = 1200;
  const usableHeight = pageHeight - SAFETY;
  const titleHeight = titleLineCount * (titlePt * 23 + 200);
  const subtitleHeight = hasSubtitle ? (12 * 23 + 600) : 0;
  const englishLabelHeight = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaHeight = metaLineCount * (10 * 23 + 100);
  const implicitParaHeight = 3 * 300;
  const contentHeight = titleHeight + subtitleHeight + englishLabelHeight + metaHeight + fixedHeight + implicitParaHeight;
  const remainingSpace = usableHeight - contentHeight;
  const safeRemaining = Math.max(remainingSpace, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(safeRemaining * 0.45);
  const rawBottom = Math.floor(safeRemaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  const midSpacing = Math.max(safeRemaining - topSpacing - bottomSpacing, 0);
  return { topSpacing, midSpacing, bottomSpacing };
}
function buildCoverR1(config) {
  const C = config.palette;
  const padL = 1200, padR = 800;
  const availableWidth = 11906 - padL - padR - 300;
  const { titlePt, titleLines } = calcTitleLayout(config.title, availableWidth, 40, 24);
  const titleSize = titlePt * 2;
  const spacing = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel,
    metaLineCount: (config.metaLines || []).length, fixedHeight: 400,
  });
  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: C.accent, space: 12 };
  const children = [];
  children.push(new Paragraph({ spacing: { before: spacing.topSpacing } }));
  if (config.englishLabel) {
    children.push(new Paragraph({
      indent: { left: padL, right: padR }, spacing: { after: 500 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.accent, space: 8 } },
      children: [new TextRun({ text: config.englishLabel.split("").join("  "), size: 18, color: C.accent, font: { ascii: "Calibri", eastAsia: "SimHei" }, characterSpacing: 40 })],
    }));
  }
  for (let i = 0; i < titleLines.length; i++) {
    children.push(new Paragraph({
      indent: { left: padL },
      spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: titleLines[i], size: titleSize, bold: true, color: C.cover.titleColor, font: { eastAsia: "SimHei", ascii: "Arial" } })],
    }));
  }
  if (config.subtitle) {
    children.push(new Paragraph({
      indent: { left: padL }, spacing: { after: 800 },
      children: [new TextRun({ text: config.subtitle, size: 24, color: C.cover.subtitleColor, font: { eastAsia: "Microsoft YaHei", ascii: "Arial" } })],
    }));
  }
  for (const line of (config.metaLines || [])) {
    children.push(new Paragraph({
      indent: { left: padL + 200 }, spacing: { after: 80 },
      border: { left: accentLeft },
      children: [new TextRun({ text: line, size: 24, color: C.cover.metaColor, font: { eastAsia: "Microsoft YaHei", ascii: "Arial" } })],
    }));
  }
  children.push(new Paragraph({ spacing: { before: spacing.bottomSpacing } }));
  children.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: C.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: config.footerLeft || "", size: 16, color: C.cover.footerColor, font: { ascii: "Arial" } }),
      new TextRun({ text: "                                        " }),
      new TextRun({ text: config.footerRight || "", size: 16, color: C.cover.footerColor, font: { ascii: "Arial" } }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: C.bg }, borders: noBorders,
        children,
      })],
    })],
  })];
}

/* ---------- pie de página con número ---------- */
function pie() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "808080", font: F_BODY })],
  })] });
}
function cabecera() {
  return new Header({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine, space: 4 } },
    children: [new TextRun({ text: "Análisis profundo de la física de CrazyPP · V3.6.176-SDK6", size: 18, color: "808080", font: F_BODY })],
  })] });
}

module.exports = { Document: null };
/* ================== CONTENIDO ================== */
const cuerpo = [];

/* ---- Resumen ejecutivo ---- */
cuerpo.push(h1("1", "Resumen ejecutivo"));
cuerpo.push(p([b("Objetivo. "), t("Este informe analiza a fondo la física del juego CrazyPP (build V3.6.176-SDK6) para responder a tres sensaciones del propietario: la bola queda «falsamente parada» sobre la pala (no desliza, no obedece a los movimientos sutiles y no se puede empujar para relanzarla), golpear la bola por debajo de la altura de la mesa falla, y en el saque soltar la bola con la pala por debajo de la cota del tablero hace desaparecer la bola. El análisis se apoya en la lectura directa del código fuente (con citas archivo:línea verificadas) y en el estudio técnico de simulación física aportado por el propietario, que sirve de modelo de referencia.")]));
cuerpo.push(p([b("Hallazgo central. "), t("La física actual no es genérica ni mala: es un motor a medida con subpasos de 480 Hz, detección CCD por campos de distancia (SDF) sobre la pala y un bote de mesa acoplado al deslizamiento (slip-coupled) que ya coincide con la física publicada del deporte. Los tres síntomas tienen causas concretas y localizadas: (1) el contacto de reposo pala-bola añadido en las rondas r100-r101 captura y fija la bola con umbrales binarios —fricción estática equivalente a unos 19° de inclinación y despegue solo por encima de 0,5 m/s de pala— y su transporte ignora la velocidad de superficie de la pala (giro de muñeca), por lo que los movimientos sutiles se comen en el filtro de velocidad; (2) los golpes suaves por debajo del plano de la mesa caen en ese mismo secuestro de reposo (por debajo de 0,35 m/s el contacto no emite evento y el árbitro no ve nada) y la cara inferior de la mesa resuelve las penetraciones empujando lateralmente; (3) en el saque, la bola se pega a la mano libre en cinemática pura sin ninguna garantía de posición legal: si la mano está bajo la huella del tablero, la bola queda oculta bajo la mesa, el juez del saque (subida mínima y línea de fondo) reinicia el intento y el rescate a los 8 segundos teleporta la bola sin aviso — de ahí la sensación de desaparición.")]));
cuerpo.push(p([b("Plan propuesto. "), t("Tres paquetes ordenados por impacto y riesgo. P0 (correctivos de juego, sin tocar el modelo): reposición del punto de saque, restricción de la captura de reposo a pala lenta, despegue analógico por empuje sostenido y resolución vertical del fondo de mesa. P1 (fidelidad, siguiendo el estudio): micro-solver de contacto compatible (Hunt-Crossley normal + Cundall-Strack tangencial) para el par bola-pala, velocidad de superficie completa (v + ω×r) en el contacto, y materiales por goma conectados a los perks existentes. P2 (consolidación): Magnus saturante CL(S), estimador Kalman/one-euro de la pala y reloj de microsegundos. El coste estimado de todo el paquete mantiene la física muy por debajo del 3 % del frame (el presupuesto del estudio asigna 0,5 ms en Quest), por lo que el objetivo de 90 FPS no queda comprometido; los riesgos reales son el golden de trayectorias (scripts/test_fisica.mjs), que habrá que re-anclar con el protocolo de la casa, y la regresión de la IA, que predice con las mismas funciones.")]));

/* ---- Alcance y método ---- */
cuerpo.push(h1("2", "Alcance, método y fuentes"));
cuerpo.push(p([t("El análisis cubre la física de la bola, de la pala, de la mesa, de la red, del suelo y del saque del build V3.6.176-SDK6 tal como está en el árbol de trabajo actual. Se leyeron íntegramente los módulos de física c04_fisica_ccd.js (377 líneas) y c05_colisiones_ia_golpeo.js (1.193 líneas), las constantes DIMS y SERVE_TUNE de c02_cfg_escena.js, y por muestreo dirigido el bucle de partida y el flujo del saque en c12_pingponggame.js (2,1 MB, secciones 17.551-17.570, 17.988-18.060, 18.240-18.430, 9.651-9.986). El netcode (c09b_red_nucleo.js) se revisó solo en lo que afecta a la extrapolación del avatar. Existe además en scripts/ un borrador de auditoría previo (informe_auditoria_fisicas_draft.md, 2026-11-12) cuyas conclusiones estructurales coinciden con las de este análisis.")]));
cuerpo.push(p([t("El documento de referencia es el estudio técnico aportado por el propietario (especificación de simulación física para WebXR, 534 líneas), que define un motor de un solo cuerpo dinámico con vuelo RK4 a 1 kHz, CCD por avance conservador sobre SDF, micro-solver de contacto compatible a 20 microsegundos (Hunt-Crossley en la normal, muelle-deslizador de Cundall-Strack en la tangente), estimador de la pala con filtro de Kalman y un presupuesto de rendimiento de 0,5 ms por frame. Este informe contrasta cada pieza del código actual con esa especificación, marca qué adoptar, qué adaptar y qué no conviene tocar todavía, y convierte los tres síntomas del propietario en causas verificables con números y líneas. Ninguna cifra de coste de CPU citada se presenta como medición: son estimaciones del estudio o acotaciones aritméticas del propio código, y el plan de validación de la sección 10 define cómo medirlas en dispositivo.")]));
cuerpo.push(tNota("Convención de citas: c04:195 significa línea 195 de src/game/core/c04_fisica_ccd.js. Los valores de constantes se citan con su línea en c02_cfg_escena.js."));

/* ---- Mapa de la física ---- */
cuerpo.push(h1("3", "Mapa de la física actual"));
cuerpo.push(p([t("La física vive en dos módulos dedicados y un conductor. Todo lo demás del juego (reglas, árbitro, IA, audio, red) consume sus funciones sin reimplementar la física, lo que hace que las mejoras centrally aplicadas propaguen de forma coherente a juego, IA, tutorial y bolas fantasma del multijugador. La tabla 1 resume el reparto exacto.")]));
cuerpo.push(...tabla("Tabla 1 · Reparto de la física por archivo", ["Archivo", "Contenido físico", "Líneas clave"], [
  ["c04_fisica_ccd.js (377 lín.)", "SDF de la hoja y del mango, CCD por avance conservador, aerodinámica (arrastre cuadrático + Magnus lineal + decaimiento del giro), simulador de pala (velocidad lineal filtrada + omega por delta de cuaterniones), bote de mesa slip-coupled, perks por goma", "c04:1 (subpaso 1/480), c04:54 CCD_TUNE, c04:75 BOTE_TUNE, c04:88 sdfBlade, c04:104 sweepBallVsBlade, c04:195 applyAerodynamics, c04:226 updatePaddleSim, c04:296 bounceOnTable"],
  ["c05_colisiones_ia_golpeo.js (1.193 lín.)", "Respuesta de golpeo (restitución, empuje del swing, punto dulce, fricción de goma, spin), contacto de reposo r100/r101, mesa (superficie, fondo, cantos), red, suelo y muros, integrador stepPhysics con subpasos, solvers de IA y de saque", "c05:24 collidePaddleSweep, c05:140 captura de reposo, c05:424 collideTable, c05:524 collideNet, c05:548 collideWorld, c05:645 stepPhysics, c05:785 predictStrike, c05:937 computeShotVelocityReal, c05:1008 simulateServePath, c05:1076 findServeVelocity"],
  ["c12_pingponggame.js (conductor)", "Base temporal dt/dtFis (r43), dilatación _dilF, bola en mano y lanzamiento del saque, juez del saque, inmunidad del toss, rescate anti-desastre", "c12:20190 PASO_TUNE, c12:17551-17557 (dtFis), c12:18278/18315 (stepPhysics), c12:18025-18052 (bola en mano), c12:9958 tossFromHand, c12:18387-18430 (juez del saque)"],
  ["c02_cfg_escena.js", "DIMS: geometría, restituciones, agarres, umbrales de reposo y de saque; interruptor physicsRealism", "c02:2-60 (geometría y física), c02:45-49 (reposo), c02:163-165 (saque), c02:65 physicsRealism=1"],
], [22, 46, 32]));
cuerpo.push(p([t("La integración es semi-implícita de Euler con subpasos calculados dinámicamente: stepPhysics divide el dt físico del frame en pasos de como máximo 1/480 s (tope 96 subpasos, c05:710) y en cada subpaso aplica gravedad, aerodinámica y desplazamiento (c05:720-726), después pala (barrido CCD interpolando la pose de la pala entre los extremos del subpaso, c05:744) y por último mesa, red, suelo y muros (c05:750 y siguientes). La bola del partido integra con el tiempo real del frame capado a 1/12 s (PASO_TUNE.fisMax, c12:20190), una decisión r43 que evita que los bajones de FPS ralenticen la trayectoria. La detección bola-pala es CCD exacta sobre el SDF del disco con grosor y del mango-cápsula, con avance conservador que nunca salta la superficie; el estudio confirma que este es el enfoque correcto (su sección 5 propone exactamente campos de distancia con avance conservador).")]));
cuerpo.push(...tabla("Tabla 2 · Constantes que gobiernan los síntomas analizados", ["Constante (fuente)", "Valor", "Efecto directo"], [
  ["paddleRestSpeed (c02:45)", "0,25 m/s", "Aproximación normal por debajo de esto = APOYO, no golpe (c05:142)"],
  ["paddleRestFric (c02:46)", "0,38", "Fricción tangencial aplicada en cada re-captura del apoyo"],
  ["paddleRestMuS (c02:47)", "0,35", "Fricción estática del transporte: la bola no desliza hasta ~19,3° de inclinación"],
  ["paddleRestDrop (c02:48)", "0,09 s", "Edad del apoyo sin re-confirmar antes de soltar (despegue silencioso)"],
  ["paddleRestCarry (c02:49)", "0,5 m/s", "La pala debe superar esta velocidad para ARRASTRAR y soltar la bola apoyada"],
  ["restEventMin (c02:312)", "0,35 m/s", "Bajo este impacto el contacto NO emite evento: ni audio, ni árbitro (c05:417)"],
  ["velWindow / velLerp (c02:293-294)", "32 ms / 0,90", "Media móvil + lerp de la velocidad de la pala (lag del filtro)"],
  ["paddleVelClamp (c02:34)", "16 m/s", "Techo de velocidad de pala (r113, smash sin recorte)"],
  ["tableRestitution (c02:14)", "0,88", "Bote de mesa; ITTF mide e≈0,87-0,92: correcto"],
  ["airDragK / magnus (c02:13,56)", "0,142 / 0,0035", "Arrastre cuadrático y Magnus LINEAL (sin saturación CL(S))"],
  ["tossMinRise (c02:163)", "0,035 m", "Subida mínima del lanzamiento exigida por el juez del saque"],
  ["serveEndLineTol (c02:164)", "0,45 m", "El golpe de saque debe darse 0,45 m detrás de la línea de fondo"],
], [30, 16, 54]));

/* ---- Diagnóstico 1 ---- */
cuerpo.push(h1("4", "Diagnóstico 1 · La bola «falsamente parada» sobre la pala"));
cuerpo.push(h2("4.1", "Qué existe hoy: captura y transporte r100/r101"));
cuerpo.push(p([t("El juego ya tiene un sistema de contacto de reposo añadido en la ronda r100 y afinado en la r101 tras el rechazo del propietario a la primera versión. La captura vive en collidePaddleSweep: si el golpe es de cara (sin canto ni mango), la pala es del jugador, no hay vuelo de saque y la velocidad normal de aproximación es como máximo paddleRestSpeed (0,25 m/s, c05:140-142), la bola se proyecta a la cara, se le anula la velocidad normal (c05:147), se le aplica una fricción tangencial con acople de giro de cascarón (c05:149-159) y se registra un estado de apoyo en campos de la propia bola (índice de pala, lado, posición local lx/dyy, edad). El transporte complementario corre al principio de stepPhysics (c05:657-708): cada frame, si la bola sigue apoyada, integra un deslizamiento propio con la gravedad proyectada en el plano de la hoja, fricción estática (paddleRestMuS) y cinética (paddleRestFric ×2,2), fija la posición pegada a la cara con la pose nueva de la pala, le asigna la velocidad de la pala más el deslizamiento propio, y aproxima la rodadura con un lerp hacia la omega ideal. El despegue ocurre si la pala supera paddleRestCarry (0,5 m/s), si la bola se desliza fuera del disco (radio interior = hoja menos 35 % del radio de bola, c05:687) o si el apoyo envejece sin re-confirmarse más de paddleRestDrop (0,09 s).")]));
cuerpo.push(h2("4.2", "Por qué no desliza ni obedece a los movimientos sutiles"));
cuerpo.push(p([t("Tres mecanismos convergentes lo explican con números. Primero, la fricción estática es demasiado alta para una bola que en realidad RUEDA: el transporte exige que la aceleración tangencial de la gravedad supere paddleRestMuS por la componente normal (c05:672-676), es decir g·sin(θ) > 0,35·g·cos(θ), lo que ocurre recién a θ ≈ 19,3° de inclinación de la pala. Una bola real sobre goma empieza a rodar con inclinaciones de 5 a 10 grados (la resistencia a la rodadura es una fracción del peso, no la fricción de deslizamiento completa), por eso el propietario percibe que «no obedece»: inclinar la pala 10 grados no mueve nada. Segundo, el transporte asigna a la bola la velocidad lineal de la pala más un deslizamiento propio que solo depende de la gravedad (c05:701-702): la velocidad de superficie completa de un sólido rígido es v_p = v_g + ω × r, y el término de rotación falta; los ajustes finos de muñeca (el gesto que más usa un jugador de mesa para acunar la bola) no mueven la bola ni un milímetro. Tercero, la velocidad de la pala que llega al contacto pasa por la media móvil de 32 ms y un lerp 0,90 (c04:242-253), que es perfecta para swings rápidos pero amortigua justo la banda de movimientos lentos (0,1-0,5 m/s) donde vive el juego fino de la bola parada.")]));
cuerpo.push(h2("4.3", "Por qué no se puede empujar desde la parada"));
cuerpo.push(p([t("El despegue es binario. Mientras la bola está apoyada, la barra CCD la encuentra siempre en contacto (el SDF menos el radio de la bola es menor que el umbral en t=0, c04:108) y el guard de separación (vRelN mayor o igual que 0 devuelve falso, c05:123) no llega a evaluarse contra una bola que viaja pegada: empujar despacio mantiene el apoyo, la bola viaja 1:1 con la pala y no hay golpe. Solo cuando la pala supera paddleRestCarry (0,5 m/s, c05:663) el apoyo se suelta de golpe y el siguiente barrido decide el golpe. El resultado subjetivo es exacto al reporte: un empuje de 0,2-0,4 m/s no hace nada (la bola viaja soldada), y al superar el umbral la bola se desprende de repente sin transición. El estudio define el comportamiento correcto: en contacto compatible la fuerza normal crece con la penetración, así que un empuje lento produce una fuerza pequeña y sostenida que acelera la bola de forma gradual (el efecto catapulta de la energía elástica tangencial, sección 6.2 del estudio), y la salida del contacto es un continuo, no un salto.")]));
cuerpo.push(h2("4.4", "Por qué es «falsa» la parada"));
cuerpo.push(p([t("El apoyo caduca en silencio: si la pose de la pala no re-confirma el contacto en 0,09 s (paddleRestDrop, c05:662), el estado se limpia y la bola entra en física normal sin ningún evento ni corrección de posición — desde fuera se ve una bola que estaba quieta que de repente cae o vuela. Además la rodadura aproximada usa un lerp fijo 0,15 hacia la omega ideal (c05:705) por FRAME, con lo que la bola visualmente puede parecer girada respecto a su traslación. Ninguno de estos mecanismos conserva energía ni garantiza continuidad: son heurísticas de pegado, no un contacto físico. La conclusión de este análisis es que el sistema r100/r101 dio un paso correcto (separar apoyo de golpe) pero lo construyó como anclaje cinemático con umbrales; el estudio ofrece el modelo que sustituye esa familia completa de constantes por física real: micro-solver de contacto con rigidez kn ≈ 2×10^5 N/m^1,5 para la goma (contacto de ~1 ms a 15 m/s), lo que reproduce agarre, deslizamiento, catapulta e inversión parcial del spin sin trucos.")]));

/* ---- Diagnóstico 2 ---- */
cuerpo.push(h1("5", "Diagnóstico 2 · Golpear por debajo de la altura de la mesa"));
cuerpo.push(p([t("El golpe en sí no discrimina altura: el barrido CCD opera en el espacio local de la pala a cualquier cota y la respuesta del golpeo no consulta tableTopY. Lo que falla es lo que rodea al golpe bajo el plano de la mesa, por tres caminos distintos. Primer camino: el secuestro por contacto de reposo. Un levantamiento (scoop) desde abajo suele llegar a la bola con velocidad normal baja; si no llega a 0,35 m/s de impacto ni produce evento (restEventMin, c05:417), la captura de reposo se lo queda sin que el árbitro, el audio o los contadores se enteren — el jugador ve que golpeó y la bola simplemente se pega. Este es el fallo dominante en rally: no es que la física rechace el golpe, es que la captura r101 lo clasifica como apoyo y lo muda.")]));
cuerpo.push(p([t("Segundo camino: la cara inferior de la mesa. La superficie solo botea si la bola desciende desde por encima del plano (prevY mayor o igual que topR y vel.y menor que 0, c05:435). Por debajo existe un plano de fondo a botY = tableTopY − thickness − ballRadius = 0,69 m que rebota hacia abajo con factor 0,45 si la bola lo cruza subiendo desde debajo (c05:494-499), y una banda insideSlab que, para bolas cuyo centro está dentro del prisma de la mesa, resuelve la penetración SOLO horizontalmente: compara la penetración en X y en Z y empuja la bola por el eje de menor penetración con rebote −0,45 (c05:501-521). Una bola golpeada hacia arriba desde dentro de esa banda (pala bajo el tablero) no sale hacia arriba: es expulsada de lado — el «fallo» visible. La resolución correcta sería elegir el eje de mínima penetración entre los TRES ejes (incluida la vertical hacia abajo cuando la bola sube y entró por el fondo), como hace cualquier SDF de caja; el estudio además pide aristas redondeadas de 1-2 mm para que existan bolas de canto honestas (sección 5.1).")]));
cuerpo.push(p([t("Tercer camino, exclusivo del saque: el juez exige la posición reglamentaria detrás de la línea de fondo. Tras cualquier contacto de pala con la bola lanzada, si ball.pos.z no queda por encima de tableCenterZ + tableHalfLength − serveEndLineTol = −0,68 m (c12:18396-18401), el intento se descarta con el aviso de posición (hint_behind) y la bola vuelve a la mano. Con la pala baja cerca del borde de la mesa (z mayor que −0,68), un toque por debajo de la altura del tablero se invalida siempre, aunque la trayectoria hubiera sido jugable. Nótese que la inmunidad del toss (c12:18258-18261) solo desactiva la pala mientras la subida acumulada sea menor que tossMinRise (3,5 cm): protege del roce inicial, no del scoop lento posterior.")]));

/* ---- Diagnóstico 3 ---- */
cuerpo.push(h1("6", "Diagnóstico 3 · El saque con la pala bajo la cota de la mesa"));
cuerpo.push(p([t("Antes del lanzamiento, la bola está en cinemática pura pegada a la mano libre: holdLock activo, velocidad y giro a cero, y posición copiada del mando más un lift constante BALL_HAND_LIFT (c12:18025-18038). No existe ninguna garantía de legalidad ni de visibilidad de esa posición: si el jugador sostiene la mano bajo la huella del tablero, la bola queda bajo el tablero (oculta por la geometría de la mesa — la primera mitad de la sensación de «desaparece») y a una cota desde la que ningún saque legal es posible. Al apretar el gatillo, tossFromHand lanza la bola con la velocidad real de la mano asistida a un mínimo vertical del tier (c12:9958-9967): la subida exigida por el juez es relativa (tossMaxY − tossReleaseY ≥ 3,5 cm, c12:18390), así que puede pasar el chequeo de subida, pero el toque por debajo de la mesa chocará con el juez de posición (hint_behind) o producirá una trayectoria imposible de validar, y en cualquier caso resetToss devuelve la bola a la mano bajo la mesa: bucle de intento fallido.")]));
cuerpo.push(p([t("Si el jugador simplemente deja caer la bola (lanzamiento natural sin gatillo con la mano quieta o bajando), la bola sale con velocidad casi nula, cae, cruza el plano de fondo de la mesa hacia abajo o aterriza en el suelo, y no hay saque; el guardián del lanzamiento espera 8 segundos (c12:18066-18069) antes de pedir «Repite el lanzamiento», y si la bola acabó en un estado irrecuperable, el rescate anti-desastre de collideWorld la teleporta a (0; 0,5; tableCenterZ) sin evento ni sonido (c05:607-616) — esa posición está justo DEBAJO del tablero y dentro de su huella, con lo que la bola reaparece oculta y empujada lateralmente por la banda insideSlab del subpaso siguiente. La suma de bola oculta bajo la mesa, juez que reinicia sin guía y teletransportes silenciosos compone exactamente el síntoma «no funciona y desaparece la bola». La raíz es de diseño: el punto de saque es responsabilidad del jugador, pero el juego no le protege de una pose ilegal ni le da feedback espacial (ningún indicador de la zona reglamentaria, ningún reanclaje de la bola a una cota servible).")]));
cuerpo.push(tNota("Nota de contraste: Eleven Table Tennis ancla la bola del saque a una posición servible delante del jugador; el estudio (sección 11, SpawnBall) define además que la física nace de un estado dado por el juego, no heredado de la mano. El plan P0 adopta esa idea sin copiar nada: reanclar la bola a la zona legal más cercana y avisar con el idioma del juego."));

/* ---- Comparativa con el estudio ---- */
cuerpo.push(h1("7", "Comparativa con el estudio técnico del propietario"));
cuerpo.push(p([t("El estudio ya coincide con el código en los cimientos: un solo cuerpo dinámico (la bola), CCD sobre campos de distancia con avance conservador (el código lo hace exactamente así en c04:104-135 y el estudio lo exige en su sección 5.2), bote impulsivo con fricción tangencial y tope de Coulomb (bounceOnTable, c04:296-323, es una implementación compacta del modelo impulsivo de la sección 6.4 del estudio con inercia de cascarón 2/5 y acoplo 3/2), y cero asignaciones en el camino caliente (los temporales preasignados de c04:6-31). Las diferencias reales se concentran en el modelo de contacto, el estimador de pala y la base temporal. La tabla 3 resume hueco por hueco con veredicto de adopción.")]));
cuerpo.push(...tabla("Tabla 3 · Estudio técnico frente a implementación actual", ["Pieza del estudio", "Estado en el código", "Veredicto"], [
  ["Vuelo RK4 a 1 ms (§4)", "Euler semi-implícito a 480 Hz con dt real del frame (r43)", "Adaptar (P2): para una bola con drag, Euler a 480 Hz ya es estable; RK4 añade precisión de trayectoria marginal y obliga a re-anclar el golden. Prioridad baja"],
  ["Magnus saturante CL(S)=1/(2+1/S) (§4)", "Magnus lineal a·(ω×v) con magnus=0,0035 y tope de juego spinMax=110 rad/s (c02:56-59)", "Adoptar opcional (P2): el lineal sobreestima el lift a spin alto; con el tope actual el error es acotado. Detrás de flag, con golden re-anclado"],
  ["Arrastre cuadrático + Cd≈0,45 (§3-4)", "airDragK=0,142 como factor de Euler cuadrático (c04:205)", "Ya alineado: mismo modelo, distinta parametrización. Validar velocidad terminal ~8,8 m/s en test"],
  ["CCD con TOI sobre SDF (§5)", "Implementado (avance conservador, hoja+canto+esquina, mango cápsula)", "Ya alineado; el estudio añade mesa/red como SDF con TOI común — hoy mesa/red son discretas por subpaso (suficiente a 480 Hz: desplazamiento máximo 18 mm/subpaso a 18 m/s)"],
  ["Micro-solver compatible 20 µs, Hunt-Crossley + Cundall-Strack (§6.2)", "No existe; en su lugar captura de reposo con umbrales (r100/r101) y golpe impulsivo con fricción de goma (c05:290-325)", "ADOPTAR (P1): es el fix raíz del síntoma 1. Reemplaza paddleRest*/velWindow por física continua: agarre, catapulta, rodadura y despegue analógico emergen solos"],
  ["Velocidad de superficie v_p = v_g + ω×r (§6.1, §7.2)", "Parcial: el golpe usa pad.omega para el brush (c05:271-273) pero el transporte de reposo usa solo pad.vel (c05:702)", "ADOPTAR (P1): unificar en una función surfaceVelocity(pad, punto) usada por golpe, reposo y spin"],
  ["Estimador Kalman de la pala + robustez (§7.2, §7.5)", "Media móvil 32 ms + lerp 0,90 + clamp 16 (c04:226-254); sin detección de glitch ni congelación por pérdida de tracking", "Adaptar (P2): Kalman por eje con medición de posición y velocidad del SDK cuando exista; añadir corte de saltos >0,3 m y amortiguado en pérdida de seguimiento"],
  ["Tiempo: reloj µs entero + sim hasta el tiempo de visualización (§2, §7.4, §8)", "dt de frame capado (uiMax 1/30, fisMax 1/12); subpasos alineados al intervalo del frame", "Adaptar (P2): el enfoque actual es robusto en la práctica; el sync por predictedDisplayTime es la mejora fina de latencia del estudio (17.4)"],
  ["Capa de indulgencia separada (§10)", "Existen asistencias ya integradas en el núcleo (hitAssistRadius, serveFlightAssist, tiers de saque, súper imán)", "Ratificar el principio: las nuevas ayudas del plan P0 (reanclaje del saque) deben quedar conmutables y marcadas, sin contaminar el golden"],
  ["Validación en CI: terminal, ITTF, túnel, determinismo (§12.1)", "Golden de trayectorias scripts/test_fisica.mjs + fisica_golden.json (+ _c05) con protocolo de re-anclado por release", "ADOPTAR: añadir los 4 tests físicos del estudio al arnés headless; el re-anclado del golden sigue el protocolo de la casa (bump + sella)"],
], [28, 40, 32]));

/* ---- Plan de mejoras ---- */
cuerpo.push(h1("8", "Plan de mejoras por fases"));
cuerpo.push(h2("8.1", "P0 · Correctivos de juego (sin cambiar el modelo físico)"));
cuerpo.push(p([b("P0-1 · Reanclaje del punto de saque (c12:18025-18038). "), t("Mientras la bola está en mano y el servidor es el jugador, validar la pose: si la bola cae dentro de la huella de la mesa (|x| ≤ halfWidth + radio y z entre C±halfLength) o por debajo de tableTopY + radio, reanclarla a la posición servible más próxima fuera de la huella (empujando z hacia el jugador hasta la línea de fondo + 0,10 m y elevando a la cota de la mano si es servible), con un aviso i18n la primera vez por punto. Con esto la bola nunca nace oculta bajo el tablero y el síntoma de desaparición desaparece por diseño. Es una ayuda marcada y conmutable, coherente con la capa de indulgencia del estudio.")]));
cuerpo.push(p([b("P0-2 · Saque asistido con altura absoluta (c12:9958-9967). "), t("El asistente del lanzamiento fija una velocidad mínima vertical relativa; cuando la bola se suelta por debajo de tableTopY, la subida debe garantizarse sobre la MESA, no sobre el punto de suelta: computar vyMin absoluto como la raíz de 2·g·(tableTopY + 0,10 − ySuelta) combinada con el vyMin del tier. Un saque soltado 30 cm bajo el tablero sube entonces hasta una cota golpeable en lugar de morir en el intento.")]));
cuerpo.push(p([b("P0-3 · La captura de reposo solo con pala quieta (c05:140). "), t("Añadir a la condición de captura el mismo test de «pala quieta» que ya existe para el cooldown (restPadSpeed, c05:738): capturar apoyo únicamente si pad.vel está por debajo de 0,45 m/s. Los levantamientos (scoop) con intención —pala subiendo— quedan entonces fuera del secuestro y atraviesan a la ruta del golpe normal, donde el suelo de salida escalado por velocidad de pala (c05:219-229) ya produce el toque suave correcto. Una línea que separa limpiamente «bola acunada» de «golpe intencional».")]));
cuerpo.push(p([b("P0-4 · Despegue analógico por empuje sostenido (c05:657-708). "), t("Mientras la bola está apoyada, medir la fuerza normal de empuje de la pala (vRelN negativa sostenida durante unos 40 ms, que hoy el guard c05:123 ignora contra bola pegada); al superarla, soltar el apoyo y aplicar el impulso de golpe con restitución reducida proporcional al empuje. El jugador podrá entonces empujar la bola parada con suavidad, acelerarla y soltarla en un continuo — el comportamiento Eleven que pide el propietario. En paralelo, bajar paddleRestCarry de 0,5 a 0,30 y paddleRestMuS de 0,35 a 0,18 (la bola debe empezar a rodar cerca de 10° de inclinación, no a 19°), con re-anclado del golden si el transporte toca alguna trayectoria de test.")]));
cuerpo.push(p([b("P0-5 · Resolución vertical del fondo de mesa (c05:501-521). "), t("Extender la resolución de la banda insideSlab a los tres ejes: calcular también la penetración vertical (hacia abajo cuando la bola sube y entró por el fondo, hacia arriba cuando desciende), elegir el eje de mínima penetración y resolver allí. La bola golpeada desde debajo del tablero sale empujada por la superficie más cercana en lugar de ser expulsada lateralmente; los cantos laterales siguen funcionando igual.")]));
cuerpo.push(p([b("P0-6 · Rescate honesto del saque caído (c12:18066-18069 y c05:607-616). "), t("Reducir el guardián de 8 s a 2,5-3 s cuando la bola toca suelo o mesa sin haber sido golpeada (es un fallo evidente, no hay que esperar), emitir el mensaje con la clave i18n correspondiente, y mover el punto de rescate anti-desastre fuera de la huella de la mesa (por ejemplo z = C + halfLength + 0,5, y = 1,0) para que la bola teleportada sea visible y no rebote contra la banda lateral. Además, el rescate nunca debe ocurrir con el jugador mirando sin explicación: mensaje siempre.")]));
cuerpo.push(h2("8.2", "P1 · Fidelidad de contacto (el modelo del estudio, sección 6)"));
cuerpo.push(p([b("P1-1 · Micro-solver de contacto bola-pala. "), t("Sustituir la familia de heurísticas de reposo por el micro-solver compliant del estudio: al primer contacto (ya detectado por la CCD existente), abrir un contacto con la velocidad de aproximación vn0 y simular en pasos de 20 microsegundos dentro del subpaso de 480 Hz (solo mientras dura el contacto, ~1-2 ms de tiempo simulado), con Hunt-Crossley en la normal (kn de goma ≈ 2×10^5 N/m^1,5, exponente Hertz delta·sqrt(delta)) y Cundall-Strack con límite de Coulomb en la tangente (μ por goma, kappaT ≈ 0,5·kn·sqrt(delta)). La pose de la pala se evalúa en cada micro-paso (interpolación lineal entre las poses τa/τb que el barrido ya maneja). Esto reproduce sin trucos: el agarre de la bola parada, el deslizamiento con transición estática-cinética, la catapulta tangencial, la inversión parcial del spin y el despegue analógico. Los umbrales paddleRest* quedan como guardas de seguridad, no como modelo. Coste: ~60-70 micro-pasos de aritmética escalar por contacto, del orden de 10-90 microsegundos por frame de contacto según la estimación del estudio (sección 9): despreciable frente al presupuesto de 11,1 ms a 90 FPS.")]));
cuerpo.push(p([b("P1-2 · Velocidad de superficie unificada. "), t("Extraer a c04 una función surfaceVelocity(pad, puntoMundo) que devuelva v_g + ω × (punto − centro de pala), reutilizando el omega ya estimado (c04:263-269); consumirla desde el golpeo (hoy cada bloque recomputa su versión: c05:271-273 para el brush, c05:311-313 para la fricción de goma) y desde el contacto de reposo/micro-solver. Elimina la divergencia entre rutas y hace que los giros de muñeca muevan la bola en TODOS los modos, no solo al brush.")]));
cuerpo.push(p([b("P1-3 · Materiales por goma conectados a los perks. "), t("El estudio define una tabla de materiales (goma rápida e≈0,86/μ≈0,9; tacky 0,80/1,3; pips largos 0,75/0,45; antispin 0,70/0,20; madera de canto 0,60/0,35 — sección 13). El juego ya tiene gomas con carácter (PADDLE_PERKS en c04:341-350 con spin/power/control por skin y dual-goma por cara): el paso es mapear cada perk a un registro de material {kn, e, mu, kappaT} y consumirlo desde el micro-solver y del golpeo de canto. Las palas del jugador dejan de ser multiplicadores abstractos y pasan a sentirse distintas en el contacto real (la tacky muerde el saque, el antispin mata el efecto entrante). La IA permanece neutra como hoy (paddlePerkFor ya la excluye, c04:367).")]));
cuerpo.push(h2("8.3", "P2 · Consolidación fina (detrás de flag, con medición en dispositivo)"));
cuerpo.push(p([t("Tres piezas del estudio que conviene programar cuando P0/P1 estén validadas en el visor: (a) Magnus saturante CL(S) = magnusGain/(2 + 1/S) con S = r·|ω×v̂|/|v| (sección 4 del estudio) sustituyendo el término lineal de c04:208-209, con magnusGain calibrado para que el topspin de 100 rev/s a 15 m/s caiga ~15 cm extra en 2 m de vuelo; (b) estimador de pala por filtro de Kalman de aceleración constante por eje (posición σ 1,5 mm + velocidad del SDK cuando linearVelocity no venga a null) con corte de glitches >0,3 m y amortiguado en pérdida de tracking (secciones 7.2 y 7.5), reemplazando la media móvil de c04:240-254; (c) base temporal por tiempo de visualización predicho (frame.predictedDisplayTime, sección 17.4) para cerrar el bucle «lo que ves es lo que colisiona», con fallback al dt de rAF cuando el navegador no lo exponga. Cada pieza va detrás de un flag en DIMS y entra al golden solo tras re-anclar.")]));
cuerpo.push(...tabla("Tabla 4 · Resumen del plan (fase, piezas, riesgo)", ["Fase", "Piezas", "Riesgo principal y mitigación"], [
  ["P0 (correctivo)", "Reanclaje del saque; vyMin absoluto; captura solo con pala quieta; despegue analógico; fondo de mesa 3 ejes; rescate honesto", "Golden de trayectorias: P0-4/P0-5 pueden mover trayectorias de test → re-anclar con protocolo (bump + sella). QA capa nueva de física en el arnés 14/14"],
  ["P1 (fidelidad)", "Micro-solver Hunt-Crossley/Cundall-Strack; surfaceVelocity unificada; materiales por goma", "Sensación distinta a la esperada → calibrar kn/e/μ con la sección 12 del estudio y sesiones del propietario; toggles por material conservando clásica neutra"],
  ["P2 (consolidación)", "Magnus CL(S); Kalman de pala; predictedDisplayTime; (opcional) RK4 1 kHz", "Regresión de trayectorias y de IA → flag DIMS + golden re-anclado por pieza, una a la vez, con bench_fisica_v305.mjs como referencia de coste"],
], [16, 42, 42]));

/* ---- Rendimiento ---- */
cuerpo.push(h1("9", "Rendimiento y el objetivo de 90 FPS"));
cuerpo.push(p([t("El margen para las mejoras es amplio porque la física actual es trivialmente barata: el peor caso del integrador son 96 subpasos de aritmética escalar (dt capado a 1/12 s con subpaso 1/480), y la CCD añade como máximo 32 iteraciones del SDF por pala y por subpaso, con temporales preasignados y cero asignaciones en el camino caliente (c04:6-31, c04:154-160). El estudio asigna a toda la física un presupuesto de 0,5 ms de media y 1,2 ms en el peor frame sobre Quest (secciones 1 y 17.5) y estima menos de 0,2 ms para el conjunto RK4+CCD+contacto en nativo; el JIT de V8 suele multiplicar por 2-4, lo que sigue dejando la física por debajo del 3 % de un frame de 11,1 ms. Las piezas del plan encajan en ese presupuesto: P0 no añade coste (son condiciones y clamps), y P1 solo gasta durante el contacto (60-70 micro-pasos de 20 µs de tiempo simulado por contacto activo, 1-2 contactos por frame como máximo según el propio estudio).")]));
cuerpo.push(p([t("La amenaza real a los 90 FPS en este código no es el número de operaciones sino el recolector de basura, y aquí el informe identifica dos focos concretos que conviene corregir en la misma pasada que P1. Primero, el buffer de velocidad de pala hace push de un objeto literal por frame por pala y shift del más viejo (c04:240-242): a 90 FPS y dos palas son ~180 objetos/segundo de basura evitable; el estudio lo prohíbe explícitamente (sección 17.2) y la corrección es un anillo preasignado de 64 muestras con índices. Segundo, los eventos de colisión se materializan con pos.clone() en cada bote de mesa, red, suelo y pared (c05:489, 520, 539, 575, 586 y siguientes): en un rally con botes frecuentes son decenas de allocations por segundo; el patrón del estudio es un anillo de eventos preasignado que el consumidor lee por índice. Ninguno de los dos focos es urgente por sí solo, pero ambos son exactamente el tipo de pausa de GC que en VR se nota como microtirones, y corregirlos cuesta una tarde. Con eso, la física no solo no amenaza los 90 FPS: queda a años luz del presupuesto.")]));
cuerpo.push(...tabla("Tabla 5 · Presupuesto de frame a 90 FPS (estimaciones del estudio, no mediciones)", ["Parte", "Coste estimado", "Fuente"], [
  ["Vuelo + AABB por frame (~11 pasos)", "~35 µs", "Estudio §9"],
  ["Estimador de 2 palas", "~5 µs", "Estudio §9"],
  ["Un contacto activo (~60 micro-pasos a 20 µs)", "~90 µs", "Estudio §9"],
  ["Total física típica (web/Quest)", "< 0,5 ms (≈ 4,5 % de 11,1 ms)", "Estudio §1 y §17.5"],
  ["Margen del frame a 90 FPS", "11,1 ms totales; el resto es render/escena", "Estudio §1"],
], [40, 32, 28]));

/* ---- Validación ---- */
cuerpo.push(h1("10", "Plan de validación y criterios de aceptación"));
cuerpo.push(p([t("La validación tiene tres anillos. Primer anillo, tests headless de física (el estudio §12.1 aporta la batería; se añaden al arnés Node junto a test_fisica.mjs): velocidad terminal de caída larga ≈ 8,8 m/s con Cd 0,45; bote ITTF de 30,5 cm → 23-26 cm con tableRestitution 0,88 (el valor actual ya cumple); ningún contacto de mesa, red o suelo que aumente la energía mecánica total; 10.000 bolas aleatorias de hasta 40 m/s contra una pala a 30 m/s sin un solo túnel; determinismo de hash de estado a 72, 90 y 120 Hz con las mismas muestras de pala. Segundo anillo, regresión de la casa: golden de trayectorias re-anclado con el protocolo de bump (los cambios de física tocan fisica_golden.json y fisica_golden_c05.json, y el comentario de BOTE_TUNE en c04:66-73 deja claro que el golden manda), batería QA completa 14/14 y capa nueva de QA de física con agujas de los seis correctivos P0. Tercer anillo, criterios del propietario en el visor, que son la única métrica que decide el release:")]));
cuerpo.push(...tabla("Tabla 6 · Criterios de aceptación en el visor (todos P0 + P1)", ["#", "Escenario", "Resultado exigido"], [
  ["1", "Parar la bola con la pala horizontal", "Descansa estable; inclinando 5-10° empieza a rodar suave cuesta abajo"],
  ["2", "Deslizar la pala despacio con la bola encima", "La bola sigue el gesto (incluida la muñeca) con leve retraso; acelerando brusco, se desliza y se sale"],
  ["3", "Empujar una bola parada y relanzarla", "Arranca de forma progresiva con el empuje, rueda, cae y se puede botar de nuevo"],
  ["4", "Soltar la bola del saque con la pala bajo la mesa", "La bola se reancla a posición servible visible (o sube asistida); jamás desaparece bajo el tablero"],
  ["5", "Golpear la bola por debajo de la altura de la mesa", "El scoop con intención golpea (evento + vuelo); nunca queda pegada en silencio"],
  ["6", "Rally largo con FX y sonido", "90 FPS sostenidos sin microtirones de GC; física invisible en el presupuesto"],
], [8, 44, 48]));

/* ---- Conclusiones ---- */
cuerpo.push(h1("11", "Conclusiones y recomendación"));
cuerpo.push(p([t("Los tres síntomas que reporta el propietario no son percepciones: son comportamientos deterministas del código con causas localizadas y verificables. La bola «falsamente parada» es el contacto de reposo r100/r101 operando como anclaje cinemático con umbrales binarios (captura 0,25 m/s, fricción estática equivalente a 19,3°, despegue 0,5 m/s, sin velocidad angular de pala en el transporte); el fallo de los golpes por debajo de la mesa es ese mismo secuestro comiéndose los scoops mudos más una resolución lateral de la cara inferior del tablero y el juez de posición del saque; y la bola que desaparece es la ausencia de reanclaje del punto de saque combinada con el rescate silencioso dentro de la huella de la mesa. Ninguna de las piezas buenas hay que reescribirla: la CCD por SDF, el bote slip-coupled, la base temporal r43 y el integrador de subpasos están al nivel del estudio de referencia.")]));
cuerpo.push(p([t("La recomendación ejecutiva es ejecutar P0 completo en una ronda (seis correctivos acotados, archivos c05 y c12, con QA capa nueva y golden re-anclado si procede), validar los seis criterios del visor con el propietario, y solo entonces entrar en P1 con el micro-solver de contacto del estudio, que es la pieza que convierte el comportamiento Eleven en física en lugar de heurística. P2 queda para después, pieza a pieza y siempre detrás de flag. El orden importa: P0 sin P1 ya elimina los tres defectos reportados; P1 sin P0 los disimularía con un modelo nuevo sobre umbrales viejos. El coste de CPU de todo el plan cabe holgado en el presupuesto del estudio y el riesgo técnico real se concentra en la calibración de la sensación, que exige sesiones con el propietario en el visor, y en la disciplina del golden, que es la red de seguridad que la casa ya sabe manejar.")]));

/* ---- Apéndice ---- */
cuerpo.push(h1("12", "Apéndice · Referencias del código citadas"));
cuerpo.push(...tabla("Tabla 7 · Índice de citas usadas en el diagnóstico", ["Tema", "Cita exacta"], [
  ["Subpaso y tope del integrador", "c04:1 (MAX_SUBSTEP_DT 1/480); c05:710-711 (n y h)"],
  ["Aerodinámica lineal-Magnus", "c04:195-212; c02:13 (airDragK), c02:56 (magnus), c02:60 (spinDecayAir)"],
  ["Filtro de velocidad de pala", "c04:226-254; c02:293-294 (velWindow 32 ms, velLerp 0,90); c02:34 (clamp 16)"],
  ["Omega de muñeca", "c04:256-271; BOTE_TUNE c04:80-81"],
  ["Captura de reposo", "c05:140-169; c02:45 (0,25 m/s)"],
  ["Transporte del apoyo", "c05:657-708; c02:47-49 (muS 0,35, drop 0,09 s, carry 0,5 m/s)"],
  ["Respuesta del golpeo", "c05:171-266 (punto dulce, empuje 0,40, suelo de salida)"],
  ["Fricción de goma y spin", "c05:290-325; c02:74 (rubberGrip), c02:154 (rubberMu)"],
  ["Contactos mudos", "c05:412-420; c02:312 (restEventMin 0,35)"],
  ["Mesa: superficie, fondo, cantos", "c05:424-522 (fondo 494-499; banda lateral 501-521)"],
  ["Suelo y rescate", "c05:548-577; rescate c05:607-616"],
  ["Bola en mano del saque", "c12:18005-18052 (holdLock, BALL_HAND_LIFT)"],
  ["Lanzamiento", "c12:9958-9986 (tossFromHand, vyMin del tier)"],
  ["Juez del saque", "c12:18387-18430 (rise y hint_behind); c02:163-164 (tossMinRise 0,035; tol 0,45)"],
  ["Inmunidad del toss", "c12:18252-18261; guardián 8 s c12:18066-18069"],
  ["Bote de mesa slip-coupled", "c04:296-323; c02:14 (0,88), c02:159-160 (agarre)"],
  ["IA con la misma física", "c05:785-840 (predictStrike), c05:937-1002 (computeShotVelocityReal)"],
  ["Golden de física", "scripts/test_fisica.mjs; scripts/fisica_golden.json; fisica_golden_c05.json"],
], [34, 66]));

/* ================== DOCUMENTO ================== */
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: F_BODY, size: 24, color: P.body },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: {
        run: { font: F_HEAD, size: 32, bold: true, color: P.primary },
        paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 },
      },
      heading2: {
        run: { font: F_HEAD, size: 28, bold: true, color: P.primary },
        paragraph: { spacing: { before: 240, after: 120, line: 312 }, outlineLevel: 1 },
      },
    },
  },
  sections: [
    { /* portada */
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverR1({
        title: "Análisis profundo de la física de CrazyPP",
        subtitle: "Contacto bola-pala, golpes bajo la mesa y saque · diagnóstico con plan de mejoras",
        englishLabel: "PHYSICS DEEP DIVE",
        metaLines: [
          "Versión analizada: V3.6.176-SDK6 (árbol de trabajo actual)",
          "Método: lectura verificada del código fuente + estudio técnico del propietario",
          "Fecha: 18 de noviembre de 2026",
          "Alcance: c04 · c05 · c12 · c02 · golden de física",
        ],
        footerLeft: "CRAZY PING PONG", footerRight: "Informe de física · r86",
        palette: P,
      }),
    },
    { /* índice — romano */
      properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN },
        },
      },
      footers: { default: pie() },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER, spacing: { before: 480, after: 360 },
          children: [new TextRun({ text: "Índice", bold: true, size: 32, font: F_HEAD, color: P.primary })],
        }),
        new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({
          spacing: { before: 200 },
          children: [new TextRun({ text: "Nota: este índice se genera mediante campos. Para actualizar los números de página tras editar el documento, haga clic derecho sobre el índice y elija «Actualizar campos».", italics: true, size: 18, color: "888888", font: F_BODY })],
        }),
        /* sin PageBreak: la sección del cuerpo es NEXT_PAGE (un salto doble genera página en blanco) */
      ],
    },
    { /* cuerpo — arábigo desde 1 */
      properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
        },
      },
      headers: { default: cabecera() },
      footers: { default: pie() },
      children: cuerpo,
    },
  ],
});

const OUT = "/home/z/my-project/download/Analisis_fisica_CrazyPP_r86.docx";
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("OK " + OUT + " (" + buf.length + " B)");
});
