// gen_espectador_r115.js — ensambla la propuesta de modo espectador (3 secciones)
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Header, Footer, PageNumber,
        NumberFormat, AlignmentType, SectionType, TableOfContents,
        P, TNR, buildCoverR1 } = require('./gen_menu_r114_lib.js');
const cont = require('./gen_espectador_r115_cont.js');

const SALIDA = '/home/z/my-project/download/Propuesta_modo_espectador_CrazyPP_r115.docx';

const portada = buildCoverR1({
  title: 'Modo espectador en CrazyPP',
  subtitle: 'Viabilidad, coste en latencia y mecánicas de participación del público en el multijugador',
  englishLabel: 'SPECTATOR MODE DESIGN',
  metaLines: [
    'Proyecto: Crazy Ping Pong (CrazyPP) · versión V3.6.209-SDK6',
    'Base del análisis: capa de red c09_red_netlink, c09b_red_nucleo, c09c_red_social y c12',
    'Método: análisis del código fuente (topología, mensajes y costes medidos) + propuesta de diseño',
    'Fecha: 22 de noviembre de 2026',
  ],
  footerLeft: 'Documento de trabajo · uso interno',
  footerRight: 'CrazyPP · r115',
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
    { properties: { page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 0, bottom: 0, left: 0, right: 0 },
      }},
      children: portada,
    },
    { properties: {
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
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 240 },
          children: [new TextRun({
            text: 'Nota: este índice se genera mediante campos de Word. Tras editar el documento, haga clic derecho sobre el índice y elija Actualizar campos para refrescar los números de página.',
            italics: true, size: 18, color: '888888', font: TNR })],
        }),
        new TableOfContents('Índice', { hyperlink: true, headingStyleRange: '1-3' }),
      ],
    },
    { properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
        },
      },
      headers: { default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Modo espectador · CrazyPP',
          size: 18, color: '808080', font: TNR })],
      })] }) },
      footers: { default: pieNumerada() },
      children: cont,
    },
  ],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(SALIDA, buf);
  console.log('✓ escrito: ' + SALIDA + ' (' + Math.round(buf.length / 1024) + ' KB)');
}).catch(e => { console.error('✗ ' + e.message); process.exit(1); });
