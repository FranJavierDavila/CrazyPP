#!/usr/bin/env node
/**
 * CRAZY PING PONG · MODULARIZACIÓN P0 · FASE 2
 * GENERADOR: convierte las 14 piezas de src/game/core/ en MÓDULOS ES REALES.
 *
 * Para cada subsistema:
 *   1. Añade un bloque de imports GENERADO (marcado con DEPS-FASE2-INICIO/FIN)
 *      justo tras el primer statement top-level (los tokens de identidad de la
 *      1.ª línea quedan intactos). Cross-file según el grafo de
 *      mod_fase2_analizar.mjs + bindings de biblioteca (three/addons).
 *   2. Prefija con `export ` las declaraciones que OTROS ficheros importan.
 *
 * El ensamblador (build_game.py) hace la transformación inversa («build de
 * inserción»): quita los bloques marcados y los prefijos export → game.html
 * sale BYTE-EXACTO contra el golden. La ejecución real nunca cambia.
 *
 * Idempotente: re-ejecutar produce los mismos ficheros (quita el bloque
 * previo antes de regenerarlo; los prefijos existentes se respetan).
 *
 * Uso: node scripts/mod_fase2_generar.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';
import * as acorn from 'acorn';
import { analizar, declaracionesTop, quitarBloque } from './mod_fase2_analizar.mjs';

const CORE = '/home/z/my-project/src/game/core';
const MARK_INI = '/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */';
const MARK_FIN = '/* DEPS-FASE2-FIN */';

function main() {
  const g = analizar(); // grafo estable (los specifiers de imports no cuentan como refs)

  // exports por fichero: símbolos propios usados por otros
  const exportsDe = new Map();
  for (const a of g.archivos) {
    const propios = [...g.decls.get(a.nombre).keys()];
    exportsDe.set(a.nombre, propios.filter(n => (g.uso.get(n) ?? 0) > 0).sort());
  }

  let totImp = 0, totExp = 0, tocados = 0;
  for (const a of g.archivos) {
    const r = g.resultado.get(a.nombre);
    const src0 = readFileSync(`${CORE}/${a.nombre}`, 'utf8');
    const src1 = quitarBloque(src0); // idempotencia
    const ast = acorn.parse(src1, { ecmaVersion: 'latest', sourceType: 'module', locations: true, allowAwaitOutsideFunction: true });
    const lineas = src1.split('\n');

    // ── 1. prefijos export (línea-based, antes de insertar el bloque) ──
    const decls = declaracionesTop(ast);
    const lineasPrefijadas = new Set();
    for (const n of exportsDe.get(a.nombre)) {
      const d = decls.get(n);
      if (!d) throw new Error(`${a.nombre}: exportado ${n} sin declaración top-level`);
      const idx = d.linea - 1;
      if (lineasPrefijadas.has(idx)) continue; // multi-declarador en la misma línea
      if (!lineas[idx].startsWith('export ')) lineas[idx] = 'export ' + lineas[idx];
      lineasPrefijadas.add(idx);
    }
    totExp += exportsDe.get(a.nombre).length;

    // ── 2. bloque de imports ──
    const imp = [];
    const duenos = [...r.importa.keys()].sort((x, y) =>
      g.archivos.findIndex(q => q.nombre === x) - g.archivos.findIndex(q => q.nombre === y));
    for (const d of duenos) {
      const simbolos = [...r.importa.get(d)].sort().join(', ');
      imp.push(`import { ${simbolos} } from './${d}';`);
    }
    for (const b of r.biblioteca.sort((x, y) => x.fuente.localeCompare(y.fuente) || x.nombre.localeCompare(y.nombre))) {
      imp.push(b.estilo === 'namespace' ? `import * as ${b.nombre} from '${b.fuente}';`
        : b.estilo === 'default' ? `import ${b.nombre} from '${b.fuente}';`
        : `import { ${b.nombre} } from '${b.fuente}';`);
    }
    totImp += imp.length;

    let resultado = lineas.join('\n');
    if (imp.length) {
      // aserción dura: jamás un import del fichero hacia sí mismo
      const self = imp.filter(l => l.includes(`from './${a.nombre}'`));
      if (self.length) throw new Error(`${a.nombre}: bloque con SELF-IMPORT → ${self[0]}`);
      // insertar tras el primer statement top-level (tokens de 1.ª línea intactos)
      const finPrimerStmt = ast.body[0].loc.end.line; // 1-based
      const bloque = [MARK_INI, ...imp, MARK_FIN];
      lineas.splice(finPrimerStmt, 0, ...bloque);
      resultado = lineas.join('\n');
    }

    if (resultado !== src0) { writeFileSync(`${CORE}/${a.nombre}`, resultado); tocados++; }
  }

  console.log(`✓ módulos ES generados: ${tocados}/${g.archivos.length} ficheros tocados · ${totExp} exports · ${totImp} imports en bloques marcados`);
  console.log('  siguiente paso: python3 scripts/build_game.py  (debe salir BYTE-EXACTO)');
}

main();
