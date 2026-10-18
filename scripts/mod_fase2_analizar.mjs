#!/usr/bin/env node
/**
 * CRAZY PING PONG · MODULARIZACIÓN P0 · FASE 2
 * ANALIZADOR DE DEPENDENCIAS de los 14 subsistemas de src/game/core/.
 *
 * Parsea cada pieza con acorn (ESM, ecmaVersion latest) y construye el grafo
 * REAL de dependencias: qué símbolos top-level declara cada fichero, qué
 * símbolos de OTROS ficheros usa, a cuáles REASIGNA (mutación — import no
 * reasignable, así que se documentan pero no se importan), qué bindings de
 * biblioteca (three/addons) usa cada uno y si hay declaraciones duplicadas
 * o ciclos de importación.
 *
 * Salida: src/game/DEPS.json + src/game/DEPENDENCIAS.md + informe en consola.
 *
 * Precisión: AST completo (sin ruido de strings/comentarios). Las
 * referencias sombreadas por bindings locales anidados pueden sobre-reportar
 * un import (legal e inofensivo en ESM); NUNCA se generan edges para
 * declaraciones duplicadas (ambiguas) ni para símbolos mutados (import sería
 * ilegal). Limitación documentada en DEPENDENCIAS.md.
 *
 * Uso: node scripts/mod_fase2_analizar.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';
import * as acorn from 'acorn';

const RAIZ = '/home/z/my-project';
const CORE = `${RAIZ}/src/game/core`;
const SALIDA_JSON = `${RAIZ}/src/game/DEPS.json`;
const SALIDA_MD = `${RAIZ}/src/game/DEPENDENCIAS.md`;

// Orden canónico — espejo de ORDER en scripts/build_game.py
const FICHEROS = [
  'c00_pre_three.js',
  'c01_modelos_3d.js',
  'c02_cfg_escena.js',
  'c03_audio_voz.js',
  'c04_fisica_ccd.js',
  'c05_colisiones_ia_golpeo.js',
  'c06_logros_stats_ia_rival.js',
  'c07_escena_sala.js',
  'c08_hall_hud.js',
  'c09_red_netlink.js',
  'c10_menu_saque.js',
  'c11_champloader.js',
  'c12_pingponggame.js',
  'c13_ui_arranque.js',
];

/** Quita los bloques de imports generados (marcados) de una pieza.
 *  El análisis corre SIEMPRE sobre fuente pura: así los bloques generados
 *  no contaminan el grafo (ni sus specifiers ni sus bindings como "reales"). */
export function quitarBloque(src) {
  const lineas = src.split('\n');
  const fuera = [];
  let saltando = false;
  for (const l of lineas) {
    if (l.includes('DEPS-FASE2-INICIO')) { saltando = true; continue; }
    if (l.includes('DEPS-FASE2-FIN')) { saltando = false; continue; }
    if (!saltando) fuera.push(l);
  }
  return fuera.join('\n');
}

export function parsear(nombre) {
  const src = quitarBloque(readFileSync(`${CORE}/${nombre}`, 'utf8'));
  const ast = acorn.parse(src, {
    ecmaVersion: 'latest',
    sourceType: 'module',
    locations: true,
    allowAwaitOutsideFunction: true,
  });
  return { nombre, src, ast };
}

/** Nombres que liga un patrón de declaración/asignación (con destructuring). */
export function nombresPatron(p, out = []) {
  if (!p) return out;
  switch (p.type) {
    case 'Identifier':
      out.push(p.name); break;
    case 'ObjectPattern':
      for (const q of p.properties) nombresPatron(q.type === 'RestElement' ? q.argument : (q.value ?? q.argument), out);
      break;
    case 'ArrayPattern':
      for (const e of p.elements) nombresPatron(e, out);
      break;
    case 'AssignmentPattern':
      nombresPatron(p.left, out); break;
    case 'RestElement':
      nombresPatron(p.argument, out); break;
  }
  return out;
}

/** Declaraciones top-level: nombre -> { linea, tipo } (línea del statement).
 *  Desenvuelve ExportNamed/DefaultDeclaration (piezas ya generadas por la fase 2). */
export function declaracionesTop(ast) {
  const decl = new Map();
  for (const st0 of ast.body) {
    const st = (st0.type === 'ExportNamedDeclaration' || st0.type === 'ExportDefaultDeclaration')
      ? st0.declaration : st0;
    if (!st) continue;
    if (st.type === 'VariableDeclaration') {
      for (const d of st.declarations) {
        for (const n of nombresPatron(d.id)) decl.set(n, { linea: st.loc.start.line, tipo: st.kind });
      }
    } else if (st.type === 'FunctionDeclaration' && st.id) {
      decl.set(st.id.name, { linea: st.loc.start.line, tipo: 'function' });
    } else if (st.type === 'ClassDeclaration' && st.id) {
      decl.set(st.id.name, { linea: st.loc.start.line, tipo: 'class' });
    }
  }
  return decl;
}

/** Bindings de los imports REALES del fichero: nombre -> { fuente, estilo }. */
export function importsReales(ast) {
  const mapa = new Map();
  for (const st of ast.body) {
    if (st.type !== 'ImportDeclaration') continue;
    for (const esp of st.specifiers) {
      const estilo = esp.type === 'ImportNamespaceSpecifier' ? 'namespace'
        : esp.type === 'ImportDefaultSpecifier' ? 'default' : 'nombrado';
      mapa.set(esp.local.name, { fuente: st.source.value, estilo });
    }
  }
  return mapa;
}

/** Recolecta referencias y mutaciones de identificadores (posiciones de binding excluidas). */
export function colectarReferencias(ast) {
  const refs = [];
  const mutas = [];
  const excluidos = new Set();

  function excluirPatron(p) {
    const vis = (x) => {
      if (!x || typeof x.type !== 'string') return;
      if (x.type === 'Identifier') { excluidos.add(x); return; }
      for (const k in x) {
        if (k === 'type' || k === 'start' || k === 'end' || k === 'loc' || k === 'range') continue;
        const v = x[k];
        if (Array.isArray(v)) v.forEach(vis);
        else if (v && typeof v === 'object' && typeof v.type === 'string') vis(v);
      }
    };
    vis(p);
  }

  function walk(n, padre, clave) {
    if (!n || typeof n.type !== 'string' || excluidos.has(n)) return;
    switch (n.type) {
      case 'Identifier': {
        const esMuta =
          (padre?.type === 'AssignmentExpression' && clave === 'left') ||
          padre?.type === 'UpdateExpression' ||
          ((padre?.type === 'ForInStatement' || padre?.type === 'ForOfStatement') && clave === 'left');
        (esMuta ? mutas : refs).push({ nombre: n.name, linea: n.loc.start.line });
        return;
      }
      case 'MemberExpression':
        walk(n.object, n, 'object');
        if (n.computed) walk(n.property, n, 'property');
        return;
      case 'Property':
        if (n.computed) walk(n.key, n, 'key');
        if (n.value) walk(n.value, n, 'value');
        return;
      case 'PropertyDefinition':
      case 'MethodDefinition':
        if (n.computed) walk(n.key, n, 'key');
        if (n.value) walk(n.value, n, 'value');
        return;
      case 'VariableDeclarator':
        excluirPatron(n.id);
        if (n.init) walk(n.init, n, 'init');
        return;
      case 'FunctionDeclaration':
      case 'FunctionExpression':
        if (n.id) excluidos.add(n.id);
        for (const p of n.params) excluirPatron(p);
        walk(n.body, n, 'body');
        return;
      case 'ArrowFunctionExpression':
        for (const p of n.params) excluirPatron(p);
        walk(n.body, n, 'body');
        return;
      case 'ClassDeclaration':
      case 'ClassExpression':
        if (n.id) excluidos.add(n.id);
        if (n.superClass) walk(n.superClass, n, 'superClass');
        walk(n.body, n, 'body');
        return;
      case 'ImportDeclaration':
        for (const esp of n.specifiers) {
          excluidos.add(esp.local);
          if (esp.imported) excluidos.add(esp.imported);
          if (esp.exported) excluidos.add(esp.exported);
        }
        return;
      case 'LabeledStatement':
        walk(n.body, n, 'body'); return;
      case 'BreakStatement':
      case 'ContinueStatement':
        return;
      default: break;
    }
    for (const k in n) {
      if (k === 'type' || k === 'start' || k === 'end' || k === 'loc' || k === 'range') continue;
      const v = n[k];
      if (Array.isArray(v)) { for (const h of v) walk(h, n, k); }
      else if (v && typeof v === 'object' && typeof v.type === 'string') walk(v, n, k);
    }
  }
  walk(ast, null, null);
  return { refs, mutas };
}

/** Grafo completo. Re-ejecutable sobre ficheros ya generados (idempotente). */
export function analizar() {
  const archivos = FICHEROS.map(parsear);
  const decls = new Map(archivos.map(a => [a.nombre, declaracionesTop(a.ast)]));
  const reales = new Map(archivos.map(a => [a.nombre, importsReales(a.ast)]));
  const refsPor = new Map(archivos.map(a => [a.nombre, colectarReferencias(a.ast)]));

  // duplicados top-level entre ficheros (ambiguos: fuera del grafo)
  const titulares = new Map();
  for (const [f, d] of decls) for (const n of d.keys()) {
    if (!titulares.has(n)) titulares.set(n, []);
    titulares.get(n).push(f);
  }
  const duplicados = [...titulares.entries()].filter(([, fs]) => fs.length > 1).map(([n, fs]) => ({ simbolo: n, ficheros: fs }));
  const dupSet = new Set(duplicados.map(d => d.simbolo));

  const dueñoDe = new Map();
  for (const [f, d] of decls) for (const n of d.keys()) if (!dueñoDe.has(n)) dueñoDe.set(n, f);

  // bindings de biblioteca disponibles (hoy: three/addons desde c01)
  const bindingBib = new Map();
  for (const m of reales.values()) for (const [n, info] of m) if (!bindingBib.has(n)) bindingBib.set(n, info);

  const resultado = new Map();
  for (const a of archivos) {
    const mis = decls.get(a.nombre);
    const { refs, mutas } = refsPor.get(a.nombre);
    const importa = new Map();   // ficheroDueño -> Set(símbolos)
    const mutados = new Map();   // símbolo -> ficheroDueño
    const externos = new Map();  // global -> nº de usos
    for (const { nombre } of refs) {
      if (mis.has(nombre) || dupSet.has(nombre)) continue;
      const dueño = dueñoDe.get(nombre);
      if (dueño && dueño !== a.nombre) { // guarda: jamás un import a sí mismo
        if (!importa.has(dueño)) importa.set(dueño, new Set());
        importa.get(dueño).add(nombre);
      } else if (!dueño) externos.set(nombre, (externos.get(nombre) ?? 0) + 1);
    }
    for (const { nombre } of mutas) {
      if (mis.has(nombre) || dupSet.has(nombre)) continue;
      const dueño = dueñoDe.get(nombre);
      if (dueño) {
        mutados.set(nombre, dueño);
        const set = importa.get(dueño);
        if (set) { set.delete(nombre); if (!set.size) importa.delete(dueño); }
      }
    }
    // bindings de biblioteca que este fichero usa y NO importa ya por sí mismo
    // (guarda: jamás un binding declarado por el propio fichero ni self-import)
    const biblioteca = [];
    for (const [n, info] of bindingBib) {
      if (externos.has(n) && !reales.get(a.nombre).has(n) && !mis.has(n)) biblioteca.push({ nombre: n, ...info });
    }
    resultado.set(a.nombre, { importa, mutados, externos, biblioteca });
  }

  // uso por símbolo → candidatos SDK de la Fase 3
  const uso = new Map();
  for (const [, r] of resultado) for (const [, set] of r.importa) for (const n of set) uso.set(n, (uso.get(n) ?? 0) + 1);

  // ciclos del grafo (DFS)
  const ciclos = [];
  const color = new Map();
  const pila = [];
  const dfs = (f) => {
    color.set(f, 1); pila.push(f);
    for (const destino of (resultado.get(f)?.importa?.keys() ?? [])) {
      if (!color.has(destino)) dfs(destino);
      else if (color.get(destino) === 1) {
        const i = pila.indexOf(destino);
        ciclos.push([...pila.slice(i), destino]);
      }
    }
    pila.pop(); color.set(f, 2);
  };
  for (const f of FICHEROS) if (!color.has(f)) dfs(f);

  return { archivos, decls, reales, resultado, duplicados, uso, ciclos, titulares };
}

function principal() {
  const g = analizar();
  const golden = readFileSync(`${RAIZ}/src/game/GOLDEN_SHA256.txt`, 'utf8').split('\n')[0].trim();

  const ficheros = {};
  for (const a of g.archivos) {
    const r = g.resultado.get(a.nombre);
    const exporta = [...g.decls.get(a.nombre).keys()].filter(n => g.uso.get(n) > 0).sort();
    ficheros[a.nombre] = {
      lineas: a.src.split('\n').length,
      declara: g.decls.get(a.nombre).size,
      exporta,
      importa: Object.fromEntries([...r.importa].map(([f, s]) => [f, [...s].sort()])),
      muta: Object.fromEntries(r.mutados),
      biblioteca: r.biblioteca.map(b => `${b.estilo === 'namespace' ? '* as ' : ''}${b.nombre} ← ${b.fuente}`),
      globalesTop: [...r.externos].sort((x, y) => y[1] - x[1]).slice(0, 8).map(([n, c]) => `${n}×${c}`),
    };
  }

  const json = {
    fase: 2, generado: new Date().toISOString(), golden,
    ficheros,
    duplicados: g.duplicados,
    ciclos: g.ciclos,
    sdk_candidatos_fase3: [...g.uso].sort((a, b) => b[1] - a[1]).slice(0, 20).map(([n, c]) => ({ simbolo: n, ficherosQueImportan: c })),
  };
  writeFileSync(SALIDA_JSON, JSON.stringify(json, null, 2) + '\n');

  // ── DEPENDENCIAS.md ──
  const L = [];
  L.push('# CRAZY PING PONG · GRAFO DE DEPENDENCIAS DEL NÚCLEO (fase 2)\n');
  L.push(`Generado por \`scripts/mod_fase2_analizar.mjs\` (acorn, scopes AST). Golden: \`${golden.slice(0, 16)}…\`\n`);
  L.push('## Qué declara, exporta e importa cada subsistema\n');
  L.push('| Fichero | Líneas | Declara | Exporta | Importa desde | Biblioteca |');
  L.push('|---|---|---|---|---|---|');
  for (const a of g.archivos) {
    const f = ficheros[a.nombre];
    const imp = Object.entries(f.importa).map(([f2, s]) => `${f2.replace(/^c(\d+).*/, 'c$1')}(${s.length})`).join(' · ') || '—';
    const bib = f.biblioteca.length ? f.biblioteca.join(', ') : '—';
    L.push(`| ${a.nombre} | ${f.lineas} | ${f.declara} | ${f.exporta.length} | ${imp} | ${bib} |`);
  }
  L.push('\n## Detalle de imports entre ficheros\n');
  for (const a of g.archivos) {
    const f = ficheros[a.nombre];
    L.push(`\n### ${a.nombre} — exporta ${f.exporta.length}, importa ${Object.values(f.importa).flat().length}`);
    if (f.exporta.length) L.push(`- **exporta:** ${f.exporta.join(', ')}`);
    for (const [f2, s] of Object.entries(f.importa)) L.push(`- de \`${f2}\`: ${s.join(', ')}`);
    if (Object.keys(f.muta).length) L.push(`- ⚠ **reasigna (sin import — ámbito compartido en el ensamblado):** ${Object.entries(f.muta).map(([n, d]) => `${n} (declarado en ${d})`).join(', ')}`);
    if (f.globalesTop.length) L.push(`- globales del navegador que usa (top): ${f.globalesTop.join(', ')}`);
  }
  L.push('\n## Candidatos a núcleo SDK (Fase 3)\n');
  L.push('Símbolos más importados entre subsistemas — la columna vertebral del núcleo compartido que la Fase 3 extraerá para los 5 campeonatos:\n');
  for (const c of json.sdk_candidatos_fase3) L.push(`- \`${c.simbolo}\` — lo importan ${c.ficherosQueImportan} ficheros`);
  if (g.duplicados.length) {
    L.push('\n## ⚠ Declaraciones duplicadas (fuera del grafo)\n');
    for (const d of g.duplicados) L.push(`- \`${d.simbolo}\` declarado en: ${d.ficheros.join(', ')}`);
  } else L.push('\nSin declaraciones duplicadas entre ficheros ✓');
  if (g.ciclos.length) {
    L.push('\n## Ciclos de importación (informativo — el ensamblado conserva el orden semántico)\n');
    for (const c of g.ciclos) L.push(`- ${c.join(' → ')}`);
  } else L.push('\nSin ciclos de importación ✓');
  L.push('\n## Limitaciones conocidas\n');
  L.push('- Las referencias sombreadas por bindings locales anidados pueden generar un import sobrante (legal e inofensivo en ESM; el build de inserción lo elimina).');
  L.push('- Un símbolo REASIGNADO desde otro fichero no se importa (los imports de ESM no son reasignables); se lista como «reasigna» y sigue viviendo en el ámbito compartido del ensamblado.');
  L.push('- La ejecución REAL del juego sigue siendo el ensamblado en un solo ámbito (build de inserción, orden semántico preservado). Los módulos son la fuente con dependencias explícitas.\n');
  writeFileSync(SALIDA_MD, L.join('\n'));

  // ── informe en consola ──
  let totImp = 0, totExp = 0;
  for (const a of g.archivos) {
    const r = g.resultado.get(a.nombre);
    const nImp = [...r.importa.values()].reduce((s, x) => s + x.size, 0);
    totImp += nImp; totExp += ficheros[a.nombre].exporta.length;
    console.log(`· ${a.nombre.padEnd(34)} declara ${String(g.decls.get(a.nombre).size).padStart(3)} · exporta ${String(ficheros[a.nombre].exporta.length).padStart(3)} · importa ${String(nImp).padStart(3)} · bib ${r.biblioteca.length}`);
  }
  console.log(`\nTOTAL: ${totExp} exports · ${totImp} imports entre ficheros · duplicados: ${g.duplicados.length} · ciclos: ${g.ciclos.length}`);
  console.log(`→ ${SALIDA_JSON}\n→ ${SALIDA_MD}`);
}

if (import.meta.url === `file://${process.argv[1]}`) principal();
