#!/usr/bin/env node
/**
 * auditoria_i18n_hall.mjs — FASE 145 (v3.6.143)
 * Localiza las claves de i18n que los CARTELES del Hall pintan sin traducción EN
 * (T() cae a ES ⇒ «carteles solo en castellano»).
 *  1. Extrae los bloques es:{} y en:{} de c00_pre_three.js (brace matching).
 *  2. Reúne las claves T('…') usadas por los pintores del Hall (c08 + drawHall/
 *     salones en c12) y por TODOS los core (contexto global).
 *  3. Reporta: claves SIN EN (caen a castellano), claves SIN ES (imposible),
 *     y claves dinámicas (T('pfx_'+id)) para cubrirlas a mano.
 */
import fs from 'node:fs';
const RAIZ = '/home/z/my-project/upload/src/game/core/';

// ── 1. diccionarios ──────────────────────────────────────────────────────────
const c00 = fs.readFileSync(RAIZ + 'c00_pre_three.js', 'utf8');
function extraerBloque(nombre) {
  const ini = c00.indexOf('  ' + nombre + ': {');
  if (ini < 0) throw new Error('bloque no encontrado: ' + nombre);
  let i = c00.indexOf('{', ini), prof = 0, fin = -1;
  for (; i < c00.length; i++) {
    if (c00[i] === '{') prof++;
    else if (c00[i] === '}') { prof--; if (prof === 0) { fin = i; break; } }
  }
  return c00.slice(c00.indexOf('{', ini), fin + 1);
}
function clavesDe(bloque) {
  const out = new Set();
  for (const m of bloque.matchAll(/(^|[\s{,])['"]?([a-z0-9_]+)['"]?\s*:/g)) out.add(m[2]);
  return out;
}
const esBl = extraerBloque('es'), enBl = extraerBloque('en');
const ES = clavesDe(esBl), EN = clavesDe(enBl);

// ── 2. claves usadas ─────────────────────────────────────────────────────────
const ficherosHall = ['c08_hall_hud.js'];
const ficherosTodos = fs.readdirSync(RAIZ).filter(f => f.startsWith('c') && f.endsWith('.js'));
function clavesUsadas(files) {
  const directas = new Set(), dinamicas = new Set();
  for (const f of files) {
    const txt = fs.readFileSync(RAIZ + f, 'utf8');
    for (const m of txt.matchAll(/\bT\('([a-z0-9_]+)'/g)) directas.add(m[1]);
    for (const m of txt.matchAll(/\bT\('([a-z0-9_]+)'\s*\+/g)) dinamicas.add(m[1]);
    for (const m of txt.matchAll(/\bT\(\s*`([^`$]*)(\$\{)/g)) dinamicas.add(m[1]);
  }
  return { directas, dinamicas };
}
const hall = clavesUsadas(ficherosHall);
const todo = clavesUsadas(ficherosTodos);
// drawHall (c12) repinta los carteles del hall: pulso_*, hall_*, gloria → coger
// también las claves hall_/pulso_/arcono_ usadas en c12
const prefijosHall = ['hall_', 'pulso_', 'arcono_', 'msg_hall', 'hint_hall'];
const clavesHallC12 = [...todo.directas].filter(k => prefijosHall.some(p => k.startsWith(p)));
const clavesHall = new Set([...hall.directas, ...clavesHallC12]);

// ── 3. informe ───────────────────────────────────────────────────────────────
const sinEN = [...clavesHall].filter(k => !EN.has(k)).sort();
const sinENtodos = [...todo.directas].filter(k => !EN.has(k)).sort();
const sinES = [...todo.directas].filter(k => !ES.has(k)).sort();

console.log('══ AUDITORÍA I18N · CARTELES DEL HALL (FASE 145) ══');
console.log('claves hall usadas:', clavesHall.size, '· dicc ES:', ES.size, '· dicc EN:', EN.size);
console.log('\n— HALL: claves sin EN (el visitante inglés las ve en castellano):', sinEN.length);
for (const k of sinEN) console.log('   ·', k);
console.log('\n— GLOBAL: claves sin EN:', sinENtodos.length, '(de', todo.directas.size, 'directas)');
console.log(sinENtodos.slice(0, 80).map(k => '   · ' + k).join('\n'));
console.log('\n— GLOBAL: claves sin ES (error grave):', sinES.length);
for (const k of sinES) console.log('   ·', k);
console.log('\n— prefijos dinámicos (revisar a mano):', [...todo.dinamicas].join(', ') || '(ninguno)');
