'use strict';
/* EL TALLER UGC · r85 · editor standalone de campeonatos/etapas de CRAZY PING PONG.
 * Sin dependencias. Todo local: carga manifest.json → edita → exporta manifest.json.
 * Contrato soportado: manifest contract 1 de la plantilla unificada (Ronda 25). */

const $ = (id) => document.getElementById(id);
const ESTADOS_RIVAL = ['present', 'idle', 'focused', 'surprised', 'hungry', 'panic',
  'laughing', 'crazy', 'angry', 'picando', 'loosing', 'defeated', 'victory',
  'duelo', 'derrotado', 'triunfante'];
const KINDS_PRUEBA = ['dianas', 'arkanoid', 'objetos', 'escudo', 'impulso', 'tren', 'custom'];
const KINDS_PODER = ['confeti', 'globos', 'mareo', 'orbe', 'arena', 'burla', 'dinamita',
  'disparo', 'estampida', 'split', 'portals', 'fuego', 'sombras', 'crazyball', 'bola'];
const RUTAS_ASSET = /^assets\/[A-Za-z0-9_\-]+\.(png|jpg|jpeg|webp|mp3|wav|ogg|glb|mp4)$/;

let MAN = null;          // manifest vivo
let nodosPx = [];        // [{x,y,r}] píxeles del póster
let imgMapaW = 0, imgMapaH = 0;

/* ------------------------------------------------------------- utilidades */
function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}
function aviso(msg, tipo) {
  const d = $('estado');
  d.className = 'aviso ' + (tipo || 'info');
  d.innerHTML = msg;
}
function download(nombre, texto) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([texto], { type: 'application/json' }));
  a.download = nombre;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

/* ------------------------------------------------- plantilla de partida */
function plantilla() {
  return {
    id: 'mi_campeonato',
    version: 1,
    contract: 1,
    estado: 'borrador',
    title: { es: 'Mi Campeonato', en: 'My Championship' },
    description: { es: 'Descripción corta de la tienda del HUB.', en: 'Short HUB shop description.' },
    tema: 'neutro',
    rival: {
      id: 'mi_campeonato_rival', name: 'RIVAL', kind: 'stock',
      states: ['present', 'idle', 'focused', 'surprised', 'panic', 'laughing',
        'crazy', 'angry', 'picando', 'loosing', 'defeated', 'victory'],
      oppLabel: 'rival',
      personalidad: { agresividad: 3, precision: 3, constancia: 3, caracter: 'frio',
        celebracion: 'Texto del artista', cerebro: 'equilibrado' },
    },
    rivalVisual: { modo: 'precarga', base: 'present.webp', ext: 'webp', alto: 2.15,
      anchoFijo: 0, material: 'basic', alphaTest: 0.25, aspecto: true,
      flotacion: { activo: true, amplitud: 0.012, periodo: 1.4 } },
    storage: 'pp_champ_mi_campeonato_*',
    camino: { patron: 'duelo_prueba',
      dificultad: { modo: 'formula', difMul: 1.0, paso: 0.15, difFinal: 1.35 },
      worldMetric: 'duelwins',
      leyenda: { activa: true, aiMulMul: 1.15, chanceSuma: 0.06, chanceMax: 0.6,
        cooldownResta: 1.5, cooldownMin: 6.0, primerResta: 1.0, primerMin: 3.0, pruebaExtra: 1 } },
    stages: [
      { id: 'duelo1', name: 'Duelo 1', kind: 'duelo' },
      { id: 'prueba1', name: 'Dianas del taller', kind: 'dianas',
        rules: { modo: 'objetivos', objetivo: 6, puntos: 2, premio: 'Trofeo' } },
      { id: 'duelo2', name: 'Duelo 2', kind: 'duelo' },
      { id: 'prueba2', name: 'Moscas veloces', kind: 'dianas',
        rules: { modo: 'movimiento', objetivo: 4, puntos: 3, premio: 'Insignia' } },
      { id: 'final', name: 'DUELO FINAL', kind: 'duelo', rules: { jefe: true } },
    ],
    pruebas: { dianas: { spawnX: 0.85, spawnYMin: 0.45, spawnYMax: 1.3, spawnZMin: -0.55,
      spawnZMax: -1.7, radio: 0.155, hold: { x: 0.0, z: -0.5, T: 1.5, H: 0.42 },
      recambioMs: 900, deadT: 0.7, tiempoBase: 20, tiempoPorObjetivo: 10, tiempoMax: 90 } },
    powers: [
      { kind: 'confeti', name: 'Confeti', icon: 'assets/power_0.png', cooldown: 18,
        duration: 6, warn: 2, activacion: 'rally', chance: 0.35 },
      { kind: 'globos', name: 'Globos', icon: 'assets/power_1.png', cooldown: 20,
        duration: 8, warn: 2, activacion: 'puntos', cadaCuantos: 3 },
    ],
    powerTrigger: { chance: 0.32, cooldown: 13.0, minRallyHits: 1, warn: 2.0,
      bolsa: 'rotatoria', primerCd: 6, garantiaS: 22, postCdMin: 10, postCdMax: 15 },
    audio: { music: 'assets/bso.mp3', musicVolume: 0.18,
      musicOpts: { fadeIn: 0.8, ancla: true, syncMode: 'ramp', gateStart: true,
        gateOn: false, renace: true, stopFade: 0 },
      sounds: { laugh: 'assets/risas.mp3' } },
    room: { floor: 'assets/sala_floor.jpg', ceil: 'assets/sala_ceil.jpg',
      back: 'assets/sala_back.jpg', front: 'assets/sala_front.jpg',
      left: 'assets/sala_left.jpg', right: 'assets/sala_right.jpg' },
    decor: { pieces: [] },
    mapa: { modo: 'canvas', planoW: 1.66, rotY: 0.42 },
    cartel: { cvW: 1024, cvH: 512, w: 2.3, h: 1.15 },
    hud: { activo: true },
    trophy: { name: { es: 'Trofeo', en: 'Trophy' }, arte: 'assets/insignia.png', rotY: 0.62 },
    coronacion: { titulo: { es: '¡CAMPEÓN!', en: 'CHAMPION!' },
      mensaje: { es: 'Has conquistado el campeonato.', en: 'You conquered the championship.' },
      dur: 14, insignia: 'assets/insignia.png', stats: ['puntos', 'duelos', 'fecha'] },
    i18n: {
      es: { bienvenida: 'Bienvenido', instr_titulo: 'Cómo se juega',
        instr_lineas: ['Norma provisional de la prueba'],
        duelo_vs: '¡DUELO! VS RIVAL · Ronda {n}', prueba_vs: '¡PRUEBA! {nombre} · Intento {n}',
        sello_leyenda: 'Sello de leyenda {n} conseguido',
        leyenda_medalla: 'LEYENDA COMPLETA: los 5 sellos son tuyos.',
        coronacion_titulo: '¡CAMPEÓN!', coronacion_msg: 'El trono es tuyo.',
        reset_ok: 'Registros eliminados.' },
      en: { bienvenida: 'Welcome', instr_titulo: 'How to play',
        instr_lineas: ['Provisional trial rule'],
        duelo_vs: 'DUEL! VS RIVAL · Round {n}', prueba_vs: 'TRIAL! {nombre} · Attempt {n}',
        sello_leyenda: 'Legend seal {n} earned',
        leyenda_medalla: 'FULL LEGEND: all 5 seals are yours.',
        coronacion_titulo: 'CHAMPION!', coronacion_msg: 'The throne is yours.',
        reset_ok: 'Records wiped.' },
    },
    rewards: { wins: 'Recompensa por vencer', champion: 'Recompensa por coronar' },
    notes: ['v1 · campeonato generado con EL TALLER UGC (r85)'],
  };
}

/* ------------------------------------------------------------ bindings */
const BIND = [
  ['f_id', 'id', 'txt'], ['f_version', 'version', 'num'], ['f_estado', 'estado', 'txt'],
  ['f_tema', 'tema', 'txt'], ['f_titulo_es', 'title.es', 'txt'], ['f_titulo_en', 'title.en', 'txt'],
  ['f_desc_es', 'description.es', 'txt'], ['f_desc_en', 'description.en', 'txt'],
  ['f_storage', 'storage', 'txt'],
  ['f_rival_nombre', 'rival.name', 'txt'], ['f_rival_kind', 'rival.kind', 'txt'],
  ['f_rival_alto', 'rivalVisual.alto', 'num'], ['f_rival_ext', 'rivalVisual.ext', 'txt'],
  ['f_rival_celebracion', 'rival.personalidad.celebracion', 'txt'],
  ['f_rival_caracter', 'rival.personalidad.caracter', 'txt'],
  ['f_rival_agresividad', 'rival.personalidad.agresividad', 'num'],
  ['f_rival_precision', 'rival.personalidad.precision', 'num'],
  ['f_rival_constancia', 'rival.personalidad.constancia', 'num'],
  ['f_rival_cerebro', 'rival.personalidad.cerebro', 'txt'],
  ['f_difMul', 'camino.dificultad.difMul', 'num'], ['f_paso', 'camino.dificultad.paso', 'num'],
  ['f_difFinal', 'camino.dificultad.difFinal', 'num'], ['f_worldMetric', 'camino.worldMetric', 'txt'],
  ['f_mapa_modo', 'mapa.modo', 'txt'], ['f_mapa_arte', 'mapa.arte', 'txt'],
  ['f_mapa_planoW', 'mapa.planoW', 'num'], ['f_mapa_rotY', 'mapa.rotY', 'num'],
  ['f_pt_chance', 'powerTrigger.chance', 'num'], ['f_pt_cooldown', 'powerTrigger.cooldown', 'num'],
  ['f_pt_bolsa', 'powerTrigger.bolsa', 'txt'],
  ['f_room_floor', 'room.floor', 'txt'], ['f_room_ceil', 'room.ceil', 'txt'],
  ['f_room_back', 'room.back', 'txt'], ['f_room_front', 'room.front', 'txt'],
  ['f_room_left', 'room.left', 'txt'], ['f_room_right', 'room.right', 'txt'],
  ['f_tint_final', 'room.variants.final.tint', 'num'],
  ['f_audio_music', 'audio.music', 'txt'], ['f_audio_vol', 'audio.musicVolume', 'num'],
  ['f_audio_laugh', 'audio.sounds.laugh', 'txt'],
  ['f_trophy_es', 'trophy.name.es', 'txt'], ['f_trophy_en', 'trophy.name.en', 'txt'],
  ['f_insignia', 'trophy.arte', 'txt'],
  ['f_coro_titulo_es', 'coronacion.titulo.es', 'txt'], ['f_coro_titulo_en', 'coronacion.titulo.en', 'txt'],
  ['f_coro_dur', 'coronacion.dur', 'num'],
  ['f_coro_msg_es', 'coronacion.mensaje.es', 'txt'], ['f_coro_msg_en', 'coronacion.mensaje.en', 'txt'],
  ['f_i18n_bienvenida_es', 'i18n.es.bienvenida', 'txt'], ['f_i18n_bienvenida_en', 'i18n.en.bienvenida', 'txt'],
  ['f_i18n_instr_titulo_es', 'i18n.es.instr_titulo', 'txt'], ['f_i18n_instr_titulo_en', 'i18n.en.instr_titulo', 'txt'],
];
function getRuta(o, ruta) {
  return ruta.split('.').reduce((a, k) => (a == null ? a : a[k]), o);
}
function setRuta(o, ruta, v) {
  const ks = ruta.split('.');
  let cur = o;
  for (let i = 0; i < ks.length - 1; i++) {
    if (cur[ks[i]] == null || typeof cur[ks[i]] !== 'object') cur[ks[i]] = {};
    cur = cur[ks[i]];
  }
  cur[ks[ks.length - 1]] = v;
}
function pintarCampos() {
  for (const [id, ruta, tipo] of BIND) {
    const e = $(id);
    if (!e) continue;
    let v = getRuta(MAN, ruta);
    if (tipo === 'num') v = (v == null ? '' : v);
    e.value = (v == null) ? '' : v;
  }
  // chips de estados
  const chips = $('chipsEstados');
  chips.innerHTML = '';
  const actuales = (MAN.rival && MAN.rival.states) || [];
  for (const st of ESTADOS_RIVAL) {
    const c = el('span', 'chip' + (actuales.indexOf(st) >= 0 ? ' on' : ''), st);
    c.onclick = () => {
      const i = MAN.rival.states.indexOf(st);
      if (i >= 0) MAN.rival.states.splice(i, 1); else MAN.rival.states.push(st);
      c.classList.toggle('on');
      validarSilencioso();
    };
    chips.appendChild(c);
  }
  // i18n instr_lineas
  pintarListaTx('listaInstrEs', MAN.i18n.es.instr_lineas || []);
  pintarListaTx('listaInstrEn', (MAN.i18n.en && MAN.i18n.en.instr_lineas) || []);
  pintarEtapas();
  pintarPoderes();
  pintarDecor();
  pintarNodos();
  $('filaMapaArte').style.display = MAN.mapa && MAN.mapa.modo === 'arte' ? 'flex' : 'none';
}
function pintarListaTx(idLista, arr) {
  const caja = $(idLista);
  caja.innerHTML = '';
  arr.forEach((tx, i) => {
    const fila = el('div', 'liTx');
    const inp = document.createElement('input');
    inp.value = tx;
    inp.oninput = () => { arr[i] = inp.value; };
    const del = el('button', 'min', '✕');
    del.onclick = () => { arr.splice(i, 1); pintarListaTx(idLista, arr); };
    fila.appendChild(inp); fila.appendChild(del);
    caja.appendChild(fila);
  });
}

/* --------------------------------------------------------------- etapas */
function pintarEtapas() {
  const caja = $('listaEtapas');
  caja.innerHTML = '';
  const etapas = MAN.stages || [];
  etapas.forEach((st, i) => {
    const d = el('div', 'etapa' + (st.kind === 'duelo' ? ' duelo' : ''));
    const cab = el('div', 'cab');
    cab.appendChild(el('span', 'num', String(i + 1)));
    const inpN = document.createElement('input');
    inpN.value = st.name || '';
    inpN.style.cssText = 'flex:1;min-width:120px;background:#0d1729;border:1px solid #24365c;border-radius:8px;color:#e8eef8;padding:6px 9px;font-weight:700';
    inpN.oninput = () => { st.name = inpN.value; };
    cab.appendChild(inpN);
    const selK = document.createElement('select');
    selK.style.cssText = 'background:#0d1729;border:1px solid #24365c;border-radius:8px;color:#7ec8ff;padding:6px 9px;font-weight:700';
    selK.innerHTML = '<option value="duelo">⚔ duelo</option>' +
      KINDS_PRUEBA.map((k) => '<option value="' + k + '">🎯 ' + k + '</option>').join('');
    selK.value = st.kind;
    selK.onchange = () => { st.kind = selK.value; d.className = 'etapa' + (st.kind === 'duelo' ? ' duelo' : ''); pintarEtapas(); };
    cab.appendChild(selK);
    const btns = [['↑', () => { if (i > 0) { etapas.splice(i - 1, 0, etapas.splice(i, 1)[0]); pintarEtapas(); } }],
      ['↓', () => { if (i < etapas.length - 1) { etapas.splice(i + 1, 0, etapas.splice(i, 1)[0]); pintarEtapas(); } }],
      ['🗑', () => { etapas.splice(i, 1); pintarEtapas(); }]];
    for (const [txt, fn] of btns) {
      const b = el('button', 'min', txt);
      b.onclick = fn;
      cab.appendChild(b);
    }
    d.appendChild(cab);
    if (st.kind !== 'duelo') {
      const reg = el('div', 'reglas');
      const rules = st.rules || (st.rules = {});
      const f = (label, clave, tipo, extra) => {
        const c = el('div', 'campo corto');
        c.innerHTML = '<label>' + label + '</label>';
        const inp = document.createElement('input');
        if (tipo === 'num') inp.type = 'number';
        Object.assign(inp, extra || {});
        inp.value = rules[clave] == null ? '' : rules[clave];
        inp.oninput = () => { rules[clave] = (tipo === 'num') ? (+inp.value || 0) : inp.value; };
        c.appendChild(inp);
        return c;
      };
      const fila1 = el('div', 'fila');
      const selM = el('div', 'campo corto');
      selM.innerHTML = '<label>modo</label>';
      const s = document.createElement('select');
      s.innerHTML = '<option>objetivos</option><option>movimiento</option><option>contrarreloj</option>';
      s.value = rules.modo || 'objetivos';
      s.onchange = () => { rules.modo = s.value; };
      selM.appendChild(s);
      fila1.appendChild(selM);
      fila1.appendChild(f('objetivo', 'objetivo', 'num', { min: 1, max: 30, step: 1 }));
      fila1.appendChild(f('puntos', 'puntos', 'num', { min: 1, max: 10, step: 1 }));
      const pre = el('div', 'campo');
      pre.innerHTML = '<label>premio</label>';
      const inpP = document.createElement('input');
      inpP.value = rules.premio || '';
      inpP.oninput = () => { rules.premio = inpP.value; };
      pre.appendChild(inpP);
      fila1.appendChild(pre);
      reg.appendChild(fila1);
      d.appendChild(reg);
    }
    caja.appendChild(d);
  });
  $('infoCamino').textContent = etapas.length + ' etapas · patrón recomendado: duelo → prueba → duelo → prueba → DUELO FINAL';
}

/* --------------------------------------------------------------- poderes */
function pintarPoderes() {
  const caja = $('listaPoderes');
  caja.innerHTML = '';
  (MAN.powers || []).forEach((p, i) => {
    const fila = el('div', 'fila');
    const mk = (label, clave, tipo, min, max, step) => {
      const c = el('div', 'campo ' + (tipo === 'txt' ? '' : 'corto'));
      c.innerHTML = '<label>' + label + '</label>';
      const inp = document.createElement('input');
      if (tipo === 'num') { inp.type = 'number'; inp.min = min; inp.max = max; inp.step = step; }
      inp.value = p[clave] == null ? '' : p[clave];
      inp.oninput = () => { p[clave] = (tipo === 'num') ? (+inp.value || 0) : inp.value; };
      c.appendChild(inp);
      return c;
    };
    const selK = el('div', 'campo corto');
    selK.innerHTML = '<label>kind</label>';
    const s = document.createElement('select');
    s.innerHTML = KINDS_PODER.map((k) => '<option>' + k + '</option>').join('');
    s.value = p.kind;
    s.onchange = () => { p.kind = s.value; };
    selK.appendChild(s);
    fila.appendChild(selK);
    fila.appendChild(mk('nombre', 'name', 'txt'));
    fila.appendChild(mk('icono', 'icon', 'txt'));
    fila.appendChild(mk('chance', 'chance', 'num', 0, 1, 0.01));
    fila.appendChild(mk('cooldown', 'cooldown', 'num', 4, 60, 1));
    fila.appendChild(mk('duración', 'duration', 'num', 2, 30, 1));
    const b = el('button', 'min', '🗑');
    b.onclick = () => { MAN.powers.splice(i, 1); pintarPoderes(); };
    fila.appendChild(b);
    caja.appendChild(fila);
  });
}

/* ---------------------------------------------------------------- decor */
function pintarDecor() {
  const caja = $('listaDecor');
  caja.innerHTML = '';
  const piezas = (MAN.decor && MAN.decor.pieces) || [];
  piezas.forEach((p, i) => {
    const fila = el('div', 'fila');
    const mk = (label, clave, min, max, step) => {
      const c = el('div', 'campo corto');
      c.innerHTML = '<label>' + label + '</label>';
      const inp = document.createElement('input');
      inp.type = 'number'; inp.min = min; inp.max = max; inp.step = step;
      inp.value = p[clave] == null ? '' : p[clave];
      inp.oninput = () => { p[clave] = +inp.value || 0; };
      c.appendChild(inp);
      return c;
    };
    const cF = el('div', 'campo');
    cF.innerHTML = '<label>fichero (assets/…)</label>';
    const inpF = document.createElement('input');
    inpF.value = p.file || '';
    inpF.oninput = () => { p.file = inpF.value; };
    cF.appendChild(inpF);
    fila.appendChild(cF);
    fila.appendChild(mk('alto m', 'h', 0.1, 3, 0.05));
    fila.appendChild(mk('x', 'x', -3, 3, 0.05));
    fila.appendChild(mk('z', 'z', -3.4, 0, 0.05));
    fila.appendChild(mk('sway', 'sway', 0, 1.2, 0.05));
    const b = el('button', 'min', '🗑');
    b.onclick = () => { piezas.splice(i, 1); pintarDecor(); };
    fila.appendChild(b);
    caja.appendChild(fila);
  });
}

/* ----------------------------------------------------------------- mapa */
function pintarNodos() {
  const caja = $('listaNodos');
  caja.innerHTML = '';
  const nodos = (MAN.mapa && MAN.mapa.nodos) || [];
  $('infoNodos').textContent = nodos.length + ' nodos · deben ser EXACTAMENTE ' +
    (MAN.stages || []).length + ' (uno por etapa, en orden)';
  nodos.forEach((n, i) => {
    const fila = el('div', 'liTx');
    fila.style.margin = '4px 0';
    const inp = document.createElement('input');
    inp.value = 'nodo ' + (i + 1) + ' · x ' + n.x + ' · y ' + n.y + ' · r ' + (n.r || 110);
    inp.readOnly = true;
    const bDel = el('button', 'min', '🗑');
    bDel.onclick = () => { nodos.splice(i, 1); pintarNodos(); marcaNodos(); };
    fila.appendChild(inp); fila.appendChild(bDel);
    caja.appendChild(fila);
  });
  marcaNodos();
}
function marcaNodos() {
  const wrap = $('mapaWrap');
  wrap.querySelectorAll('.marcaNodo').forEach((m) => m.remove());
  const img = wrap.querySelector('img');
  if (!img || !img.naturalWidth) return;
  const esc = img.clientWidth / imgMapaW;
  (MAN.mapa && MAN.mapa.nodos || []).forEach((n, i) => {
    const m = el('div', 'marcaNodo', String(i + 1));
    const r = (n.r || 110) * esc;
    m.style.cssText += 'left:' + n.x * esc + 'px;top:' + n.y * esc + 'px;width:' + r * 2 + 'px;height:' + r * 2 + 'px;';
    wrap.appendChild(m);
  });
}
function cargarImagenMapa(file) {
  const img = new Image();
  img.onload = () => {
    imgMapaW = img.naturalWidth; imgMapaH = img.naturalHeight;
    $('mapaCaja').hidden = false;
    const wrap = $('mapaWrap');
    wrap.innerHTML = '';
    wrap.appendChild(img);
    img.onclick = (ev) => {
      if (!MAN.mapa) MAN.mapa = {};
      if (!Array.isArray(MAN.mapa.nodos)) MAN.mapa.nodos = [];
      const r = img.getBoundingClientRect();
      const x = Math.round((ev.clientX - r.left) * imgMapaW / r.width);
      const y = Math.round((ev.clientY - r.top) * imgMapaH / r.height);
      MAN.mapa.nodos.push({ x, y, r: 110, ts: 1 });
      pintarNodos();
    };
    marcaNodos();
    aviso('Póster cargado (' + imgMapaW + '×' + imgMapaH + '). CLIC sobre cada medallón, EN ORDEN de etapas.', 'ok');
  };
  img.src = URL.createObjectURL(file);
}

/* --------------------------------------------------------------- export */
function manifestFinal() {
  // reconcilia nodos con etapas + limpia huecos
  const m = JSON.parse(JSON.stringify(MAN));
  m.id = String(m.id || 'mi_campeonato').toLowerCase().replace(/[^a-z0-9_-]/g, '_');
  m.storage = 'pp_champ_' + m.id + '_*';
  m.rival.id = m.id + '_rival';
  m.contract = 1;
  if (m.mapa && m.mapa.modo === 'arte') {
    if (!m.mapa.arte) { delete m.mapa.nodos; }
    if (m.mapa.nodos && m.mapa.nodos.length !== m.stages.length) {
      aviso('⚠ Nodos del mapa (' + m.mapa.nodos.length + ') ≠ etapas (' + m.stages.length + ') — el juego caería a rejilla. Igálalos.', 'err');
    }
  } else if (m.mapa) {
    delete m.mapa.nodos;
  }
  if (m.note && String(m.note).trim()) {
    m.notes = (m.notes || []).concat([String(m.note).trim()]);
  }
  delete m.note;
  return m;
}
function validar(man) {
  const errs = [], oks = [];
  const m = man || MAN;
  if (!m) return ['sin manifest cargado'];
  if (!/^[a-z0-9_-]{2,24}$/.test(m.id || '')) errs.push('id inválido (^[a-z0-9_-]{2,24}$)');
  if (!m.title || !m.title.es) errs.push('title.es obligatorio');
  if ((m.title && m.title.es || '').length > 40) errs.push('title.es supera 40 caracteres');
  const etapas = m.stages || [];
  if (etapas.length < 2) errs.push('al menos 2 etapas');
  const ids = new Set();
  for (let i = 0; i < etapas.length; i++) {
    const s = etapas[i];
    if (!s.id) errs.push('etapa ' + (i + 1) + ' sin id');
    else if (ids.has(s.id)) errs.push('id de etapa duplicado: ' + s.id);
    if (s.id) ids.add(s.id);
    if (!['duelo'].concat(KINDS_PRUEBA).includes(s.kind)) errs.push('etapa ' + (i + 1) + ' kind desconocido: ' + s.kind);
    if (s.kind !== 'duelo' && !s.rules) errs.push('prueba ' + (i + 1) + ' sin rules (modo/objetivo)');
  }
  if (etapas.length && etapas[etapas.length - 1].kind !== 'duelo') {
    oks.push('la última etapa NO es duelo: la coronación funcionará igual (el FINAL del arte puede ser prueba)');
  }
  const rutas = [];
  const scan = (o) => {
    if (typeof o === 'string') { if (RUTAS_ASSET.test(o)) rutas.push(o); return; }
    if (Array.isArray(o)) { o.forEach(scan); return; }
    if (o && typeof o === 'object') { Object.values(o).forEach(scan); }
  };
  scan({ a: m.room, b: m.audio, c: m.powers, d: m.decor, e: m.trophy, f: m.coronacion, g: m.mapa, h: m.rivalVisual });
  const dupAssets = rutas.filter((r) => r.startsWith('assets/') && !/\.(jpg|jpeg)$/.test(r));
  if (m.rival.states && m.rival.states.length < 2) errs.push('el rival necesita al menos 2 estados');
  if (m.mapa && m.mapa.modo === 'arte' && (!m.mapa.nodos || m.mapa.nodos.length !== etapas.length)) {
    errs.push('mapa modo arte con ' + ((m.mapa.nodos || []).length) + ' nodos ≠ ' + etapas.length + ' etapas (o usa modo canvas)');
  }
  for (const p of (m.powers || [])) {
    if (!KINDS_PODER.includes(p.kind)) errs.push('poder kind desconocido: ' + p.kind);
    /* r85 · chance sólo manda en activacion 'rally'; los de 'puntos' usan
     * cadaCuantos (convención valle/halloween — el orbe espectral no lleva chance) */
    if (p.activacion === 'puntos') {
      if (!(p.cadaCuantos >= 1)) errs.push('poder ' + p.kind + ': activacion puntos necesita cadaCuantos >= 1');
    } else if (!(p.chance >= 0 && p.chance <= 1)) {
      errs.push('poder ' + p.kind + ': chance fuera de 0..1');
    }
  }
  return errs;
}
function validarSilencioso() {
  const errs = validar();
  aviso(errs.length ? ('⚠ ' + errs.join(' · ')) : '✔ Sin errores de validación (' + (MAN.stages || []).length + ' etapas).', errs.length ? 'err' : 'ok');
}

/* ---------------------------------------------------------------- carga */
function cargarManifest(texto) {
  try {
    MAN = JSON.parse(texto);
  } catch (e) {
    aviso('✗ JSON inválido: ' + e.message, 'err');
    return;
  }
  if (!MAN.stages || !MAN.rival) {
    aviso('✗ No parece un manifest de campeonato (faltan stages/rival).', 'err');
    return;
  }
  if (MAN.mapa && MAN.mapa.nodos) nodosPx = MAN.mapa.nodos;
  pintarCampos();
  aviso('✔ Manifest cargado: <b>' + (MAN.title ? MAN.title.es : MAN.id) + '</b> · ' + MAN.stages.length + ' etapas.', 'ok');
}

/* --------------------------------------------------------------- eventos */
$('btnCargar').onclick = () => $('cargaMan').click();
$('cargaMan').onchange = (ev) => {
  const f = ev.target.files[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = () => cargarManifest(String(r.result));
  r.readAsText(f);
};
$('btnPlantilla').onclick = () => { MAN = plantilla(); pintarCampos(); aviso('🌱 Plantilla nueva: <b>' + MAN.id + '</b>. Cambia el id, el título y las etapas.', 'ok'); };
$('btnValidar').onclick = () => { if (MAN) validarSilencioso(); };
$('btnExportar').onclick = () => {
  if (!MAN) { aviso('Carga o crea un campeonato primero.', 'err'); return; }
  const m = manifestFinal();
  const txt = JSON.stringify(m, null, 2);
  $('dlgJsonPre').textContent = txt;
  $('dlgJson').showModal();
  $('btnDescargar').onclick = () => download('manifest.json', txt);
  $('btnCopiar').onclick = async () => {
    try { await navigator.clipboard.writeText(txt); $('btnCopiar').textContent = '✔ Copiado'; setTimeout(() => { $('btnCopiar').textContent = '📋 Copiar'; }, 1500); } catch (e) { /* */ }
  };
};
$('btnGuia').onclick = () => $('dlgGuia').showModal();
$('btnAddDuelo').onclick = () => {
  if (!MAN) return;
  const n = (MAN.stages || []).filter((s) => s.id.startsWith('duelo')).length + 1;
  MAN.stages.push({ id: 'duelo' + n, name: 'Duelo ' + n, kind: 'duelo' });
  pintarEtapas(); pintarNodos();
};
$('btnAddPrueba').onclick = () => {
  if (!MAN) return;
  const n = (MAN.stages || []).filter((s) => s.id.startsWith('prueba')).length + 1;
  MAN.stages.push({ id: 'prueba' + n, name: 'Prueba ' + n, kind: 'dianas',
    rules: { modo: 'objetivos', objetivo: 6, puntos: 2, premio: 'Premio' } });
  pintarEtapas(); pintarNodos();
};
$('btnAddPoder').onclick = () => {
  if (!MAN) return;
  MAN.powers.push({ kind: 'confeti', name: 'Nuevo poder', icon: 'assets/power_' + MAN.powers.length + '.png',
    cooldown: 18, duration: 6, warn: 2, activacion: 'rally', chance: 0.32 });
  pintarPoderes();
};
$('btnAddDecor').onclick = () => {
  if (!MAN) return;
  if (!MAN.decor) MAN.decor = {};
  if (!Array.isArray(MAN.decor.pieces)) MAN.decor.pieces = [];
  MAN.decor.pieces.push({ file: 'assets/decor' + (MAN.decor.pieces.length + 1) + '.png', h: 1.1, x: -2.3, z: -2.45, sway: 0.4 });
  pintarDecor();
};
document.querySelectorAll('[data-addtx]').forEach((b) => {
  b.onclick = () => {
    const cual = b.dataset.addtx;
    const arr = (cual === 'instrEs') ? MAN.i18n.es.instr_lineas : MAN.i18n.en.instr_lineas;
    arr.push('');
    pintarListaTx(cual === 'instrEs' ? 'listaInstrEs' : 'listaInstrEn', arr);
  };
});
$('cargaMapa').onchange = (ev) => { if (ev.target.files[0]) cargarImagenMapa(ev.target.files[0]); };
$('btnNodoClear').onclick = () => { if (MAN && MAN.mapa) { MAN.mapa.nodos = []; pintarNodos(); } };
$('f_mapa_modo').addEventListener('change', () => {
  $('filaMapaArte').style.display = $('f_mapa_modo').value === 'arte' ? 'flex' : 'none';
});
document.querySelectorAll('.seccion > h2').forEach((h) => {
  h.onclick = () => h.parentElement.classList.toggle('abierta');
});
window.addEventListener('resize', () => marcaNodos());
aviso('Carga un <b>manifest.json</b> o empieza de cero con la plantilla. La guía tiene la convención de arte.', 'info');
