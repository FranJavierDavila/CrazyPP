// gen_inventario_menu_r114.js — ensambla el documento de inventario de arte del menú
// Arquitectura de 3 secciones: portada (sin numerar) · índice (romanos) · cuerpo (arábigos desde 1)
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Header, Footer, PageNumber,
        NumberFormat, AlignmentType, SectionType, TableOfContents, PageBreak,
        P, TNR, buildCoverR1 } = require('./gen_menu_r114_lib.js');
const cont1 = require('./gen_menu_r114_cont1.js');
const cont2 = require('./gen_menu_r114_cont2.js');

const SALIDA = '/home/z/my-project/download/Inventario_arte_menu_CrazyPP_r114.docx';

const portada = buildCoverR1({
  title: 'Inventario de arte del menú y el hall',
  subtitle: 'Crazy Ping Pong · piezas, recursos y requisitos técnicos para el rediseño pieza a pieza',
  englishLabel: 'MENU ART INVENTORY',
  metaLines: [
    'Proyecto: Crazy Ping Pong (CrazyPP) · versión V3.6.209-SDK6',
    'Base del análisis: código fuente src/game/ y activos en public/assets/',
    'Método: exploración de código y ficha técnica medida en disco',
    'Fecha: 22 de noviembre de 2026',
  ],
  footerLeft: 'Documento de trabajo · uso interno',
  footerRight: 'CrazyPP · r114',
  palette: P.cover,
});

function pieNumerada() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '808080', font: TNR })],
  })] });
}

const doc = new Document({
  styles: { default: { document: {
    run: { font: TNR, size: 24, color: '000000' },
    paragraph: { spacing: { line: 312 } },
  }}},
  features: { updateFields: true },
  sections: [
    { // 1 · Portada — margen 0, sin pie ni numeración
      properties: { page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 0, bottom: 0, left: 0, right: 0 },
      }},
      children: portada,
    },
    { // 2 · Índice — números romanos
      properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN },
        },
      },
      footers: { default: pieNumerada() },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 480, after: 200, line: 380, lineRule: 'atLeast' },
          children: [new TextRun({ text: 'Índice', bold: true, size: 32, font: TNR })],
        }),
        // nota de actualización antes del campo: así nunca desborda a una página vacía
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 240 },
          children: [new TextRun({
            text: 'Nota: este índice se genera mediante campos de Word. Tras editar el documento, haga clic derecho sobre el índice y elija Actualizar campos para refrescar los números de página.',
            italics: true, size: 18, color: '888888', font: TNR })],
        }),
        new TableOfContents('Índice', { hyperlink: true, headingStyleRange: '1-3' }),
        // sin PageBreak: la sección 3 es NEXT_PAGE y ya provoca el salto
      ],
    },
    { // 3 · Cuerpo — números arábigos desde 1
      properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
        },
      },
      headers: { default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Inventario de arte del menú · CrazyPP',
          size: 18, color: '808080', font: TNR })],
      })] }) },
      footers: { default: pieNumerada() },
      children: [...cont1, ...cont2],
    },
  ],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(SALIDA, buf);
  console.log('✓ escrito: ' + SALIDA + ' (' + Math.round(buf.length / 1024) + ' KB)');
}).catch(e => { console.error('✗ ' + e.message); process.exit(1); });
