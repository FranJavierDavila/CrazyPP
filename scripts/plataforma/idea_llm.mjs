// Fase F · IDEA → SEMILLA DE CAMPEONATO (generación asistida por IA)
//
// Convierte una descripción libre («campeonato en una estación espacial
// abandonada con un rival robótico…») en la SEMILLA JSON que consume
// crear_campeonato.py --semilla.
//
// Dos motores:
//   1) LLM (z-ai-web-dev-sdk) — si hay .z-ai-config disponible.
//   2) Expandidor determinista — si no hay IA o falla: mapea palabras clave
//      a tema/paleta/poderes y extrae el nombre del rival. SIEMPRE funcional.
//
// En AMBOS casos la semilla pasa por el validador del asistente: la IA no
// publica nada sin validación (regla de la fase F).
//
// Uso:
//   node scripts/plataforma/idea_llm.mjs "una estación espacial abandonada
//        con un rival robótico y tres pruebas" --salida /tmp/semilla.json

import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const salIdx = args.indexOf('--salida');
const salida = salIdx >= 0 ? args[salIdx + 1] : null;
const idea = args.filter((a, i) => i !== salIdx && i !== salIdx + 1).join(' ');

if (!idea.trim()) {
  console.error('Uso: node idea_llm.mjs "<idea del campeonato>" [--salida semilla.json]');
  process.exit(1);
}

/* ------------------------- TEMAS DEL SISTEMA COMÚN ------------------------ */
const TEMAS = {
  espacio: { clave: 'espacio', palabras: ['espacio', 'estación', 'nave', 'galax', 'planeta', 'astronauta', 'robot', 'androide', 'alien', 'marciano', 'orbita'] },
  magia: { clave: 'magia', palabras: ['mago', 'magia', 'dragón', 'hechicero', 'brujo', 'castillo', 'fantas', 'alquimi'] },
  oeste: { clave: 'oeste', palabras: ['oeste', 'forajido', 'sheriff', 'cowboy', 'vaquero', 'saloon', 'desierto', 'revólver'] },
  circo: { clave: 'circo', palabras: ['circo', 'payaso', 'carpa', 'feria', 'carnaval'] },
  selva: { clave: 'selva', palabras: ['selva', 'jungla', 'selvático', 'mono', 'tupido', 'selv'] },
  ciudad: { clave: 'ciudad', palabras: ['ciudad', 'neo', 'urbano', 'calle', 'nocturna', 'ciber', 'neón'] },
  hielo: { clave: 'hielo', palabras: ['hielo', 'ártico', 'nieve', 'glaciar', 'invierno', 'polar'] },
};
const PODERES_POR_TEMA = {
  espacio: [{ kind: 'confeti', name: 'Lluvia de estrellas', chance: 0.3, cooldown: 25, duration: 8 }],
  magia: [{ kind: 'confeti', name: 'Chispas arcanas', chance: 0.3, cooldown: 25, duration: 8 }],
  oeste: [{ kind: 'confeti', name: 'Polvo del desierto', chance: 0.3, cooldown: 25, duration: 8 }],
  circo: [{ kind: 'confeti', name: 'Confeti de carpa', chance: 0.35, cooldown: 22, duration: 8 }],
  selva: [{ kind: 'confeti', name: 'Hojas furiosas', chance: 0.3, cooldown: 25, duration: 8 }],
  ciudad: [{ kind: 'confeti', name: 'Neones locos', chance: 0.3, cooldown: 25, duration: 8 }],
  hielo: [{ kind: 'confeti', name: 'Ventisca', chance: 0.3, cooldown: 25, duration: 8 }],
};

const minus = idea.toLowerCase();
const temaDetectado = Object.values(TEMAS)
  .find((t) => t.palabras.some((p) => minus.includes(p)))?.clave || 'espacio';

function idDesde(idea) {
  const palabras = minus.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ').split(/\s+/)
    .filter((p) => p.length > 3 && !['campeonato', 'ambientado', 'estacion', 'rival'].includes(p));
  const id = palabras.slice(0, 2).join('_').slice(0, 24) || 'nuevo_champ';
  return /^[a-z0-9_-]{2,24}$/.test(id) ? id : 'nuevo_champ';
}

function semillaDeterminista() {
  // nombre del rival: 1) «llamado X» / «llamada X»  2) secuencia en MAYÚSCULAS
  // 3) lo que siga a rival/contra (máx 2 palabras)  4) El Retador
  let nombreRival = null;
  let m = idea.match(/llamad[oa]\s+([A-ZÁÉÍÓÚÑÜ0-9][\w\-. ]{1,30})/);
  if (m) nombreRival = m[1].trim().split(/\s+/).slice(0, 3).join(' ');
  if (!nombreRival) {
    m = idea.match(/\b([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ0-9]{2,}(?:[\s-][A-Z0-9]+){0,2})/);
    if (m) nombreRival = m[1].trim();
  }
  if (!nombreRival) {
    m = minus.match(/(?:rival|contra|versus|vs\.?)\s+((?:[a-záéíóúñü]+[\s-]?){1,2})/);
    if (m) nombreRival = m[1].trim();
  }
  nombreRival = (nombreRival || 'El Retador').replace(/(^|\s)\S/g, (c) => c.toUpperCase());
  return {
    id: idDesde(idea),
    titulo_es: nombreRival === 'El Retador' ? 'Campeonato ' + temaDetectado : nombreRival,
    titulo_en: nombreRival === 'El Retador' ? temaDetectado + ' Championship' : nombreRival,
    descripcion_es: idea.trim().slice(0, 380),
    descripcion_en: idea.trim().slice(0, 380),
    tema: temaDetectado,
    dificultad: 0.9,
    rival: { nombre: nombreRival, estados: ['idle', 'duelo', 'derrotado', 'triunfante'] },
    poderes: PODERES_POR_TEMA[temaDetectado],
    duelos: 3,
    decor: [{ file: 'assets/decor/troquel1.png', h: 1.2, x: -2.30, z: -2.75, sway: 0.5 }],
  };
}

/* ------------------------------ MOTOR LLM -------------------------------- */
async function semillaLLM() {
  const { default: ZAI } = await import('z-ai-web-dev-sdk');
  const zai = await ZAI.create();
  // ejemplo FIJO (no derivado de la idea) para no contaminar a la IA
  const esquema = JSON.stringify({
    id: 'estacion_orbital',
    titulo_es: 'Estación Orbital', titulo_en: 'Orbital Station',
    descripcion_es: 'Duelo contra un androide abandonado en una estación espacial.',
    descripcion_en: 'Duel a rogue android aboard an abandoned space station.',
    tema: 'espacio', dificultad: 0.9,
    rival: { nombre: 'Androide AX-9', estados: ['idle', 'duelo', 'derrotado', 'triunfante'] },
    poderes: [{ kind: 'confeti', name: 'Lluvia de estrellas', chance: 0.3, cooldown: 25, duration: 8 }],
    duelos: 3,
    decor: [{ file: 'assets/decor/troquel1.png', h: 1.2, x: -2.3, z: -2.75, sway: 0.5 }],
  }, null, 1);
  const r = await zai.chat.completions.create({
    messages: [
      {
        role: 'assistant',
        content:
          'Eres el diseñador de campeonatos de CRAZY PING PONG (WebXR, tenis de mesa ' +
          'contra rivales temáticos). Recibes una idea y devuelves SOLO un JSON de ' +
          'semilla con EXACTAMENTE estas claves (sin markdown, sin explicaciones):\n' +
          esquema +
          '\nReglas ESTRICTAS: id en minúsculas_con_guiones (2-24, dos palabras máx, ' +
          'sin palabras genéricas como "campeonato" o "abandonada"); tema ∈ espacio|magia|oeste|circo|selva|ciudad|hielo; ' +
          'dificultad 0.6-1.3; rival.nombre = el nombre PROPIO del rival si la idea lo da ' +
          '(«un rival robótico llamado ANDROIDE AX-9» → "Androide AX-9"), y si no lo da, ' +
          'inventa uno corto temático (máx 3 palabras); titulo_es/en = nombre COMERCIAL del ' +
          'campeonato (2-4 palabras, NUNCA la frase de la idea); descripcion_es/en = 1-2 frases; ' +
          'poderes usa kind=confeti con nombre temático (el resto requiere módulo custom); ' +
          'duelos entre 1 y 5; decor 1-4 troqueles con file assets/decor/troquelN.png.',
      },
      { role: 'user', content: idea },
    ],
    thinking: { type: 'disabled' },
    temperature: 0.7,
  });
  let txt = r?.choices?.[0]?.message?.content || '';
  txt = txt.replace(/```json|```/g, '').trim();
  const ini = txt.indexOf('{');
  const fin = txt.lastIndexOf('}');
  if (ini < 0 || fin <= ini) throw new Error('la IA no devolvió JSON');
  const intento = (t) => {
    try { return JSON.parse(t); } catch (e) { /* */ }
    try {   // reparación ligera: comas colgantes
      return JSON.parse(t.replace(/,\s*([}\]])/g, '$1'));
    } catch (e) { return null; }
  };
  const sem = intento(txt.slice(ini, fin + 1));
  if (!sem) throw new Error('JSON de la IA irrecuperable');
  if (!sem.id || !sem.titulo_es) throw new Error('JSON de la IA incompleto');
  return sem;
}

/* -------------------------------- MAIN ----------------------------------- */
let semilla = null;
let motor = 'determinista';
try {
  semilla = await semillaLLM();
  motor = 'LLM (z-ai-web-dev-sdk)';
} catch (e) {
  console.error('· IA no disponible (' + String(e.message).slice(0, 80) + ') → expandidor determinista');
  semilla = semillaDeterminista();
}

const json = JSON.stringify(semilla, null, 1);
if (salida) {
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  fs.writeFileSync(salida, json, 'utf8');
  console.error(`✓ semilla (${motor}) → ${salida}`);
  console.error('  siguiente paso: python3 scripts/plataforma/crear_campeonato.py --semilla ' + salida);
} else {
  console.log(json);
}
