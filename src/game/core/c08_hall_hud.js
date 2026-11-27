export const HALL = {
  cz: -18.5,        // centro de la estancia (pared frontal de la cancha: z -5,55)
  hx: 3.05,         // semiancho · v3.6.28: MISMO ancho que las salas (6,10 m)
  depth: 7.9,       // fondo · v3.6.28: MISMO fondo que las salas (7,90 m)
  h: 2.85,          // misma altura que las salas (2,85 m)
};
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { T, TLang } from './c00_pre_three.js';
import { ARCANO_CFG, DIMS } from './c02_cfg_escena.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */
/* paleta de pieles en el orden de SKINS (la lista vive en el módulo de
 * entrenamiento: colores repetidos aquí a propósito, son estáticos) */
export const HALL_SKIN_IDS = ['clasica', 'fuego', 'hielo', 'oro', 'arcoiris', 'carbon'];
export const HALL_SKIN_COLS = ['#8a6a4a', '#ff5a2a', '#35c4e8', '#f2c14e', '#b07aff', '#ff2d2d'];
/* v3.6.27 · HALL OF FAME: nombres de las pieles para las placas de las
 * vitrinas (duplicado a propósito, igual que los colores — la lista
 * canónica vive en el módulo de entrenamiento y estas son estáticas) */
export const HALL_SKIN_NAMES = [
  { es: 'Clásica', en: 'Classic' },
  { es: 'Fuego', en: 'Fire' },
  { es: 'Hielo', en: 'Ice' },
  { es: 'Oro', en: 'Gold' },
  { es: 'Arcoíris', en: 'Rainbow' },
  { es: 'Pro Carbon', en: 'Pro Carbon' },
];

export function hallCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

/* v3.6.27 · HALL OF FAME — cartel de la pared de la gloria: panel de
 * museo con doble filo dorado, título en degradado de oro y subtítulo
 * entre dos líneas finas. El título SIEMPRE cabe (se encoge). */
export function drawHallSign(cv, title, sub) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const g = x.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#241c15'); g.addColorStop(1, '#120c08');
  x.fillStyle = g;
  x.fillRect(0, 0, W, H);
  x.strokeStyle = '#c9932f'; x.lineWidth = 5;
  x.strokeRect(7, 7, W - 14, H - 14);
  x.strokeStyle = 'rgba(201,147,47,0.35)'; x.lineWidth = 2;
  x.strokeRect(17, 17, W - 34, H - 34);
  // título en degradado de oro (de claro a profundo), sombra suave
  const grad = x.createLinearGradient(0, H * 0.18, 0, H * 0.62);
  grad.addColorStop(0, '#ffe08a'); grad.addColorStop(1, '#c9932f');
  let size = Math.round(H * 0.42);
  x.font = '900 ' + size + 'px system-ui, sans-serif';
  while (x.measureText(title).width > W - 90 && size > 30) {
    size -= 4;
    x.font = '900 ' + size + 'px system-ui, sans-serif';
  }
  x.textAlign = 'center';
  x.fillStyle = grad;
  x.shadowColor = 'rgba(0,0,0,.65)'; x.shadowBlur = 12;
  x.fillText(title, W / 2, H * 0.46);
  x.shadowBlur = 0;
  // subtítulo entre dos líneas doradas (SIEMPRE cabe: se encoge)
  if (sub) {
    x.fillStyle = '#b9a77f';
    let s2 = Math.round(H * 0.155);
    x.font = '600 ' + s2 + 'px system-ui, sans-serif';
    while (x.measureText(sub).width > W - 90 && s2 > 18) {
      s2 -= 2;
      x.font = '600 ' + s2 + 'px system-ui, sans-serif';
    }
    x.fillText(sub, W / 2, H * 0.78);
    x.strokeStyle = 'rgba(201,147,47,0.55)'; x.lineWidth = 2;
    const wSub = x.measureText(sub).width;
    const yL = H * 0.78 - s2 * 0.34;
    x.beginPath();
    x.moveTo(W / 2 - wSub / 2 - 66, yL); x.lineTo(W / 2 - wSub / 2 - 18, yL);
    x.moveTo(W / 2 + wSub / 2 + 18, yL); x.lineTo(W / 2 + wSub / 2 + 66, yL);
    x.stroke();
  }
}

/* r32 (v3.6.128) · PINTOR DEL ICONO DE LA MÚSICA DEL SALÓN — placa
 * redonda 256×256 100 % vectorial (misma técnica del museo: cero bytes
 * nuevos en el bundle). Estados:
 *   · SONANDO    → altavoz dorado con DOS ondas de sonido.
 *   · SILENCIADO → el mismo altavoz apagado (gris) con BARRA ROJA en
 *                  diagonal (censura universal de «mute»).
 * El aro exterior respira en oro para leerse como mando, no como arte. */
export function drawHallMusica(cv, mute) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const C = W / 2, R = W / 2 - 6;
  x.clearRect(0, 0, W, H);
  // placa: disco oscuro con aro dorado doble (familia de las placas)
  x.beginPath(); x.arc(C, C, R, 0, Math.PI * 2);
  const g = x.createRadialGradient(C, C - R * 0.35, R * 0.1, C, C, R);
  g.addColorStop(0, 'rgba(38,30,20,0.94)'); g.addColorStop(1, 'rgba(14,10,6,0.94)');
  x.fillStyle = g; x.fill();
  x.lineWidth = 6; x.strokeStyle = '#c9932f'; x.stroke();
  x.beginPath(); x.arc(C, C, R - 9, 0, Math.PI * 2);
  x.lineWidth = 2; x.strokeStyle = 'rgba(201,147,47,0.4)'; x.stroke();
  // ALTAVOZ vectorial (caja + cono) centrado, ligeramente a la izquierda
  // para dejar aire a las ondas de la derecha
  const s = W / 256;                       // escala de diseño (256 base)
  const cx = C - 14 * s, cy = C;
  const oro = mute ? '#8d8676' : '#ffd257';
  const oro2 = mute ? '#6b665a' : '#c9932f';
  x.save();
  x.translate(cx, cy);
  x.beginPath();                            // caja del altavoz
  x.rect(-30 * s, -16 * s, 22 * s, 32 * s);
  x.moveTo(-8 * s, -16 * s);                // cono
  x.lineTo(14 * s, -32 * s);
  x.lineTo(14 * s, 32 * s);
  x.lineTo(-8 * s, 16 * s);
  x.closePath();
  const gA = x.createLinearGradient(0, -32 * s, 0, 32 * s);
  gA.addColorStop(0, oro); gA.addColorStop(1, oro2);
  x.fillStyle = gA; x.fill();
  x.restore();
  if (!mute) {
    // ondas de sonido (dos arcos dorados a la derecha del cono)
    x.strokeStyle = '#ffd257'; x.lineWidth = 7 * s; x.lineCap = 'round';
    x.beginPath(); x.arc(cx + 18 * s, cy, 20 * s, -0.9, 0.9); x.stroke();
    x.beginPath(); x.arc(cx + 18 * s, cy, 34 * s, -0.8, 0.8); x.stroke();
  } else {
    // barra roja de SILENCIO en diagonal (con halo oscuro para leerse
    // sobre cualquier arte del salón)
    x.strokeStyle = 'rgba(0,0,0,0.55)'; x.lineWidth = 22 * s; x.lineCap = 'round';
    x.beginPath(); x.moveTo(C - 62 * s, C - 62 * s); x.lineTo(C + 62 * s, C + 62 * s); x.stroke();
    x.strokeStyle = '#ff4444'; x.lineWidth = 11 * s;
    x.beginPath(); x.moveTo(C - 62 * s, C - 62 * s); x.lineTo(C + 62 * s, C + 62 * s); x.stroke();
  }
}

/* r23 (v3.6.118) · PARED DE INSIGNIAS DEL HALL (F2 · Hall del Anfitrión):
 * placa de museo 1024×640 que c12.drawHall() repinta con el perfil ACTIVO
 * (el del dueño… o EL DEL ANFITRIÓN cuando el invitado visita su hall
 * online). 100 % procedural — misma técnica que los carteles y las
 * texturas de bola: cero bytes nuevos en el bundle, cero descargas.
 *  · logros: 6 medallones (emoji + nombre) — oro si está conseguido, gris
 *    apagado si no: la vitrina que ANIMA a por él.
 *  · bolas: chips circulares con el color de CADA skin (16) — apagadas las
 *    que el anfitrión no tiene abiertas.
 *  · mesas: paletas de color (5) con la misma regla.
 * Todo lo que pinta llega ya traducido/saneado desde drawHall (c12). */
export function drawHallGloria(cv, d) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const g = x.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#241c15'); g.addColorStop(1, '#120c08');
  x.fillStyle = g;
  x.fillRect(0, 0, W, H);
  x.strokeStyle = '#c9932f'; x.lineWidth = 6;
  x.strokeRect(8, 8, W - 16, H - 16);
  x.strokeStyle = 'rgba(201,147,47,0.35)'; x.lineWidth = 2;
  x.strokeRect(20, 20, W - 40, H - 40);
  // título en oro con sombra (SIEMPRE cabe: se encoge)
  x.textAlign = 'center'; x.textBaseline = 'alphabetic';
  const grad = x.createLinearGradient(0, 24, 0, 104);
  grad.addColorStop(0, '#ffe08a'); grad.addColorStop(1, '#c9932f');
  let ts = 62;
  x.font = '900 ' + ts + 'px system-ui, sans-serif';
  while (x.measureText(d.titulo).width > W - 120 && ts > 30) {
    ts -= 4;
    x.font = '900 ' + ts + 'px system-ui, sans-serif';
  }
  x.fillStyle = grad;
  x.shadowColor = 'rgba(0,0,0,.65)'; x.shadowBlur = 10;
  x.fillText(d.titulo, W / 2, 88);
  x.shadowBlur = 0;
  // subtítulo: las CIFRAS del anfitrión (victorias · racha · ★ · ELO)
  if (d.sub) {
    x.fillStyle = '#b9a77f';
    let s2 = 30;
    x.font = '600 ' + s2 + 'px system-ui, sans-serif';
    while (x.measureText(d.sub).width > W - 120 && s2 > 16) {
      s2 -= 2;
      x.font = '600 ' + s2 + 'px system-ui, sans-serif';
    }
    x.fillText(d.sub, W / 2, 128);
  }
  // — medallones de LOGROS (6): 2 filas × 3 —
  const LG = d.logros || [];
  const mR = 58, mCY = [216, 352], mCX = [222, 512, 802];
  for (let i = 0; i < Math.min(LG.length, 6); i++) {
    const L = LG[i];
    const cx = mCX[i % 3], cy = mCY[Math.floor(i / 3)];
    x.beginPath(); x.arc(cx, cy, mR, 0, Math.PI * 2);
    x.fillStyle = L.on ? '#3a2a14' : '#171a20';
    x.fill();
    x.lineWidth = 6;
    x.strokeStyle = L.on ? '#e9b83c' : '#3a4048';
    x.stroke();
    if (L.on) {
      x.beginPath(); x.arc(cx, cy, mR + 8, 0, Math.PI * 2);
      x.strokeStyle = 'rgba(233,184,60,0.30)'; x.lineWidth = 3;
      x.stroke();
    }
    x.textAlign = 'center'; x.textBaseline = 'middle';
    x.globalAlpha = L.on ? 1 : 0.30;
    x.font = '44px system-ui, sans-serif';
    x.fillText(L.e || '★', cx, cy - 13);
    x.globalAlpha = 1;
    x.font = '700 20px system-ui, sans-serif';
    x.fillStyle = L.on ? '#ffe9a8' : '#5d6570';
    const nm = String(L.n || '').toUpperCase();
    x.fillText(nm.length > 15 ? nm.slice(0, 14) + '…' : nm, cx, cy + 33);
  }
  // — fila de BOLAS (16 skins): chip circular con el color de la skin —
  const BY = 486;
  x.textAlign = 'left'; x.textBaseline = 'middle';
  x.fillStyle = '#b9a77f';
  x.font = '700 21px system-ui, sans-serif';
  x.fillText(T('gloria_bola'), 52, BY);   // v3.6.143: el chip sigue al idioma
  x.textAlign = 'center';
  const BL = d.bolas || [];
  for (let i = 0; i < Math.min(BL.length, 16); i++) {
    const B = BL[i];
    const cx = 210 + i * 47;
    x.globalAlpha = B.on ? 1 : 0.22;
    x.beginPath(); x.arc(cx, BY, 20, 0, Math.PI * 2);
    x.fillStyle = B.col || '#ffffff';
    x.fill();
    x.lineWidth = 3;
    x.strokeStyle = B.on ? 'rgba(233,184,60,0.85)' : '#3a4048';
    x.stroke();
    if (B.on) {   // brillo de goma: arco alto-izquierdo
      x.beginPath(); x.arc(cx - 6, BY - 7, 7, Math.PI * 0.9, Math.PI * 1.55);
      x.strokeStyle = 'rgba(255,255,255,0.75)'; x.lineWidth = 3;
      x.stroke();
    }
    x.globalAlpha = 1;
  }
  // — fila de MESAS (5 aspectos): paleta rectangular redondeada —
  const MY = 560;
  x.textAlign = 'left';
  x.fillStyle = '#b9a77f';
  x.font = '700 21px system-ui, sans-serif';
  x.fillText(T('gloria_mesa'), 52, MY);   // v3.6.143: el chip sigue al idioma
  x.textAlign = 'center';
  const MS = d.mesas || [];
  for (let i = 0; i < Math.min(MS.length, 8); i++) {
    const M = MS[i];
    const cx = 236 + i * 120;
    x.globalAlpha = M.on ? 1 : 0.22;
    if (x.roundRect) {
      x.beginPath(); x.roundRect(cx - 45, MY - 17, 90, 34, 10);
      x.fillStyle = M.col || '#17539e';
      x.fill();
      x.lineWidth = 3;
      x.strokeStyle = M.on ? 'rgba(233,184,60,0.85)' : '#3a4048';
      x.stroke();
    } else {
      x.fillStyle = M.col || '#17539e';
      x.fillRect(cx - 45, MY - 17, 90, 34);
    }
    x.globalAlpha = 1;
  }
}

export function drawHallDoor(cv, label) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  x.fillStyle = 'rgba(10,8,6,0.88)';
  x.fillRect(0, 0, W, H);
  x.strokeStyle = '#c9932f'; x.lineWidth = 4;
  x.strokeRect(6, 6, W - 12, H - 12);
  x.strokeStyle = 'rgba(201,147,47,0.3)'; x.lineWidth = 1.5;
  x.strokeRect(13, 13, W - 26, H - 26);
  x.fillStyle = '#e9c877';
  x.font = '700 72px system-ui, sans-serif';
  x.textAlign = 'center'; x.textBaseline = 'middle';
  x.fillText(label, W / 2, H / 2 + 2);
}

/* v3.6.27 · HALL OF FAME — cabecera de pared (LOGROS CRAZY, PIEL DE PALA):
 * texto dorado con filo inferior y rombo central, estilo placa de museo. */
export function drawHallHeader(cv, title) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  x.textAlign = 'center'; x.textBaseline = 'middle';
  let size = Math.round(H * 0.42);
  x.font = '800 ' + size + 'px system-ui, sans-serif';
  while (x.measureText(title).width > W - 70 && size > 28) {
    size -= 4;
    x.font = '800 ' + size + 'px system-ui, sans-serif';
  }
  const grad = x.createLinearGradient(0, H * 0.2, 0, H * 0.8);
  grad.addColorStop(0, '#ffe08a'); grad.addColorStop(1, '#c9932f');
  x.fillStyle = grad;
  x.shadowColor = 'rgba(0,0,0,.6)'; x.shadowBlur = 8;
  x.fillText(title, W / 2, H * 0.44);
  x.shadowBlur = 0;
  // filo con rombo central
  const yL = H * 0.78;
  x.strokeStyle = 'rgba(201,147,47,0.7)'; x.lineWidth = 3;
  x.beginPath();
  x.moveTo(W * 0.2, yL); x.lineTo(W / 2 - 16, yL);
  x.moveTo(W / 2 + 16, yL); x.lineTo(W * 0.8, yL);
  x.stroke();
  x.fillStyle = '#c9932f';
  x.save();
  x.translate(W / 2, yL); x.rotate(Math.PI / 4);
  x.fillRect(-7, -7, 14, 14);
  x.restore();
}

/* v3.6.27 · Medallón de LOGRO CRAZY (256²): aro dorado + emoji + nombre en
 * dos líneas. Conseguido: oro cálido; pendiente: gris apagado que invita. */
export function drawHallMedal(cv, emoji, name, on) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  const cx = W / 2, cy = H * 0.46, R = W * 0.36;
  x.beginPath(); x.arc(cx, cy, R, 0, Math.PI * 2);
  x.fillStyle = on ? '#3a2a14' : '#171a20';
  x.fill();
  x.lineWidth = 9;
  x.strokeStyle = on ? '#e9b83c' : '#3a4048';
  x.stroke();
  if (on) {
    x.beginPath(); x.arc(cx, cy, R + 10, 0, Math.PI * 2);
    x.strokeStyle = 'rgba(233,184,60,0.32)'; x.lineWidth = 4;
    x.stroke();
  }
  x.textAlign = 'center'; x.textBaseline = 'middle';
  x.globalAlpha = on ? 1 : 0.32;
  x.font = '64px system-ui, sans-serif';
  x.fillText(emoji || '★', cx, cy - 18);
  x.globalAlpha = 1;
  x.font = '700 27px system-ui, sans-serif';
  x.fillStyle = on ? '#ffe9a8' : '#5d6570';
  const words = String(name || '').toUpperCase().split(' ');
  const l1 = words.slice(0, Math.ceil(words.length / 2)).join(' ');
  const l2 = words.slice(Math.ceil(words.length / 2)).join(' ');
  x.fillText(l1, cx, cy + 58);
  if (l2) x.fillText(l2, cx, cy + 88);
}

/* v3.6.27 · Placa de RÉCORD Y RANKING (2048×460): bronce grabado del museo
 * con el historial de carrera del anfitrión: 4 columnas de cifras grandes
 * + fila inferior con el PRO CIRCUITO y las victorias por dificultad. */
export function drawHallRanking(cv, d) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  const bg = x.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#2c2418'); bg.addColorStop(1, '#1a150d');
  x.fillStyle = bg;
  x.fillRect(6, 6, W - 12, H - 12);
  x.strokeStyle = '#c9932f'; x.lineWidth = 5;
  x.strokeRect(8, 8, W - 16, H - 16);
  x.strokeStyle = 'rgba(201,147,47,0.3)'; x.lineWidth = 2;
  x.strokeRect(18, 18, W - 36, H - 36);
  x.textAlign = 'center';
  x.fillStyle = '#e9c877';
  x.font = '800 52px system-ui, sans-serif';
  x.textBaseline = 'alphabetic';
  x.fillText(d.title, W / 2, 74);
  x.strokeStyle = 'rgba(201,147,47,0.45)'; x.lineWidth = 2;
  x.beginPath();
  x.moveTo(W * 0.3, 96); x.lineTo(W * 0.7, 96);
  x.stroke();
  const cols = d.cols || [];
  const cw = W / Math.max(cols.length, 1);
  for (let i = 0; i < cols.length; i++) {
    const c = cols[i];
    const cx = cw * i + cw / 2;
    x.fillStyle = '#ffd257';
    x.font = '900 100px system-ui, sans-serif';
    x.fillText(String(c.v), cx, 218);
    x.fillStyle = '#b9a77f';
    x.font = '700 30px system-ui, sans-serif';
    x.fillText(String(c.l), cx, 268);
    if (i < cols.length - 1) {
      x.strokeStyle = 'rgba(201,147,47,0.22)'; x.lineWidth = 2;
      x.beginPath();
      x.moveTo(cw * (i + 1), 130); x.lineTo(cw * (i + 1), 262);
      x.stroke();
    }
  }
  x.fillStyle = '#c9932f';
  x.font = '700 36px system-ui, sans-serif';
  x.fillText(d.foot, W / 2, 352);
  x.fillStyle = '#8a7a58';
  x.font = '600 26px system-ui, sans-serif';
  x.fillText(d.foot2, W / 2, 408);
}

/* v3.6.27 · Placa de latón de las vitrinas (256×72): nombre de la piel
 * grabado; bloqueada → placa oscura con texto apagado. */
export function drawHallNameplate(cv, text, on) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  const g = x.createLinearGradient(0, 0, 0, H);
  if (on) { g.addColorStop(0, '#d9a441'); g.addColorStop(1, '#8a6420'); }
  else { g.addColorStop(0, '#23262d'); g.addColorStop(1, '#16181d'); }
  x.fillStyle = g;
  x.fillRect(4, 4, W - 8, H - 8);
  x.strokeStyle = on ? 'rgba(60,40,8,0.8)' : 'rgba(120,130,145,0.35)';
  x.lineWidth = 3;
  x.strokeRect(5, 5, W - 10, H - 10);
  x.fillStyle = on ? '#2c1d06' : '#5d6570';
  x.textAlign = 'center'; x.textBaseline = 'middle';
  const t = String(text || '').toUpperCase();
  // SIEMPRE entera: se encoge el tipo hasta caber (nada de cortes feos)
  let fs = 38;
  x.font = '800 ' + fs + 'px system-ui, sans-serif';
  while (x.measureText(t).width > W - 26 && fs > 16) {
    fs -= 2;
    x.font = '800 ' + fs + 'px system-ui, sans-serif';
  }
  x.fillText(t, W / 2, H / 2 + 1);
}

/* v3.6.27 · NEÓN de bienvenida (1024×256, fondo transparente): «CRAZY» en
 * rosa y «PING PONG» en cian, con triple pasada de brillo (halo → cuerpo
 * → alma blanca). Marca del juego: SIN traducción a propósito. */
export function drawHallNeon(cv, text) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  const words = String(text || '').split(' ');
  const i1 = Math.max(1, Math.ceil(words.length / 2));
  const w1 = words.slice(0, i1).join(' ');
  const w2 = words.slice(i1).join(' ');
  x.textBaseline = 'middle';
  x.font = '900 92px system-ui, sans-serif';   // margen para el halo del tubo
  const gap = 30;
  const tw = x.measureText(w1).width + (w2 ? gap + x.measureText(w2).width : 0);
  let sx = W / 2 - tw / 2;
  x.textAlign = 'left';
  const cy = H / 2 + 4;
  const tube = (t, col) => {
    const w = x.measureText(t).width;
    x.shadowColor = col; x.shadowBlur = 36;
    x.fillStyle = col; x.globalAlpha = 0.85;
    x.fillText(t, sx, cy);
    x.shadowBlur = 16; x.globalAlpha = 1;
    x.fillText(t, sx, cy);
    x.shadowBlur = 0;
    x.fillStyle = '#ffffff';
    x.globalAlpha = 0.75;
    x.fillText(t, sx, cy);
    x.globalAlpha = 1;
    sx += w + gap;
  };
  tube(w1, '#ff6a9a');
  if (w2) tube(w2, '#4fd8ff');
}

/* v3.6.27 · Cita de museo bajo los medallones (1024×160, transparente). */
export function drawHallQuote(cv, text) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  x.textAlign = 'center'; x.textBaseline = 'middle';
  x.fillStyle = 'rgba(233,215,170,0.85)';
  x.font = 'italic 600 52px Georgia, serif';
  x.shadowColor = 'rgba(0,0,0,.7)'; x.shadowBlur = 8;
  x.fillText(String(text || ''), W / 2, H / 2);
  x.shadowBlur = 0;
}

/* (v3.6.50 · r58: el pintor de la PLACA DEL TROFEO se retira con él —
 *  petición del dueño: la copa y su haz salen del Hall y el espacio
 *  central queda libre. La placa no tiene ya dónde colgarse.) */

export function createHall(base) {
  /* r24 (v3.6.119) · VARIANTE DE ARTE: 'assets/hall/' (museo, siempre) o
   * 'assets/hall/cabana/' (LA CABAÑA — HALL_VARIANTES en c02). Los seis
   * JPG comparten nombres y proporciones exactas de los planos, así que
   * la caja es LA MISMA: sólo cambia la carpeta que viste los materiales.
   * applyHallVariant() re-viste en vivo sin reconstruir el grupo (la red
   * guarda referencias — igual que applyBallSkin con la bola). */
  const vbase = (typeof base === 'string' && base) ? base : 'assets/hall/';
  const g = new THREE.Group();
  const W = HALL.hx * 2;
  const z0 = HALL.cz - HALL.depth / 2;   // pared FRENTE: la primera que mira el anfitrión
  const z1 = HALL.cz + HALL.depth / 2;   // pared FONDO: la puerta pintada, tras el spawn

  /* v3.6.28 · FASE 30 — EL SALÓN DEL ARTISTA: la estancia adopta las
   * DIMENSIONES EXACTAS de las salas de campeonato (6,10 × 7,90 × 2,85 m,
   * las de createRoom) y se viste con el ARTE DEL ARTISTA mapeado CARA A
   * CARA, como las salas de los campeonatos (patrón createChampRoom v2.85):
   * seis JPG con TextureLoader (SRGBColorSpace + anisotropía 4), carga
   * perezosa y a prueba de fallos — si una imagen no llega, ese plano
   * conserva su color de respaldo y el juego SIGUE. El trofeo de campeón,
   * sus 7 bolas doradas y las 3 luces siguen VIVOS como mobiliario 3D. */
  const loader = new THREE.TextureLoader();
  const texs = {};
  const texPaths = {
    front: vbase + 'frente.jpg',     // 1849×864 → plano 6,10×2,85
    back: vbase + 'fondo.jpg',       // 1849×864 → plano 6,10×2,85 (la puerta)
    left: vbase + 'izquierda.jpg',   // 2395×864 → plano 7,90×2,85 (ventanal)
    right: vbase + 'derecha.jpg',    // 2395×864 → plano 7,90×2,85 (insignias)
    floor: vbase + 'suelo.jpg',      // 1296×1678 → plano 6,10×7,90 (emblema)
    ceil: vbase + 'techo.jpg',       // 1296×1678 → plano 6,10×7,90 (círculo)
  };
  const texMats = {};   // r24 · material por clave — vestir() re-viste en vivo
  const applyTex = (key, mat) => {
    loader.load(texPaths[key], (tex) => {
      try {
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.anisotropy = 4;
        // r24 · re-vestido: el arte anterior se libera (cambio de variante)
        if (texs[key] && texs[key] !== tex && texs[key].dispose) {
          try { texs[key].dispose(); } catch (eDis) { /* */ }
        }
        texs[key] = tex;
        mat.map = tex;
        mat.color.set(0xffffff);
        mat.needsUpdate = true;
      } catch { /* el arte NUNCA rompe el juego */ }
    }, undefined, () => { /* sin arte (file://): plano con su color */ });
  };
  /* r24 · vestir(base): la MISMA estancia con OTRO arte (cambia la
   * carpeta y recarga las 6 claves sobre los materiales registrados).
   * Falla suave: si un JPG no llega, el plano conserva su color. */
  const vestir = (b) => {
    if (typeof b !== 'string' || !b) return;
    texPaths.front = b + 'frente.jpg';
    texPaths.back = b + 'fondo.jpg';
    texPaths.left = b + 'izquierda.jpg';
    texPaths.right = b + 'derecha.jpg';
    texPaths.floor = b + 'suelo.jpg';
    texPaths.ceil = b + 'techo.jpg';
    for (const k in texMats) applyTex(k, texMats[k]);
    // r28 · el mobiliario 3D ES PARTE del vestido: cada salón monta el suyo
    try { if (typeof montarProps === 'function') montarProps(b); } catch (eMP) { /* */ }
  };

  /* ---- paleta del mobiliario 3D (luces, bolas) ----
   *  v3.6.50 (r58): goldMat/silverMat/marbleMat/brassMat RETIRADOS con el
   *  trofeo — nada queda que los use. */
  const woodDark = new THREE.MeshStandardMaterial({ color: 0x3a2716, roughness: 0.9 });

  /* ---- SUELO: el arte trae el emblema elíptico de la casa al centro ---- */
  const floorMat = new THREE.MeshStandardMaterial({ color: 0x2e3238, roughness: 0.9 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(W, HALL.depth), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, 0.001, HALL.cz);
  g.add(floor);
  texMats.floor = floorMat;   // r24 · registro para re-vestido en vivo
  applyTex('floor', floorMat);

  /* ---- TECHO: el arte trae el círculo luminoso sobre el trofeo ---- */
  const ceilMat = new THREE.MeshStandardMaterial({ color: 0x1d2026, roughness: 1 });
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(W, HALL.depth), ceilMat);
  ceil.rotation.x = Math.PI / 2;
  ceil.position.set(0, HALL.h, HALL.cz);
  g.add(ceil);
  texMats.ceil = ceilMat;   // r24 · registro para re-vestido en vivo
  applyTex('ceil', ceilMat);

  /* ---- PAREDES: rotaciones EXACTAS de createRoom (las cuatro leen sin
   * espejo, igual que en los 5 campeonatos). Cada cara, SU material. ---- */
  const wallFrontMat = new THREE.MeshStandardMaterial({ color: 0x272b33, roughness: 0.96 });
  const wallBackMat  = new THREE.MeshStandardMaterial({ color: 0x272b33, roughness: 0.96 });
  const wallLeftMat  = new THREE.MeshStandardMaterial({ color: 0x272b33, roughness: 0.96 });
  const wallRightMat = new THREE.MeshStandardMaterial({ color: 0x272b33, roughness: 0.96 });
  const mkWall = (mat, w, h, x, z, ry) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
    m.position.set(x, HALL.h / 2, z);
    m.rotation.y = ry;
    g.add(m);
    return m;
  };
  const wallLeft  = mkWall(wallLeftMat, HALL.depth, HALL.h, -HALL.hx, HALL.cz, Math.PI / 2);
  const wallRight = mkWall(wallRightMat, HALL.depth, HALL.h, HALL.hx, HALL.cz, -Math.PI / 2);
  const wallFront = mkWall(wallFrontMat, W, HALL.h, 0, z0, 0);
  const wallBack  = mkWall(wallBackMat, W, HALL.h, 0, z1, Math.PI);
  texMats.left = wallLeftMat;    // r24 · registro para re-vestido en vivo
  texMats.right = wallRightMat;
  texMats.front = wallFrontMat;
  texMats.back = wallBackMat;
  applyTex('left', wallLeftMat);
  applyTex('right', wallRightMat);
  applyTex('front', wallFrontMat);
  applyTex('back', wallBackMat);

  /* (v3.6.28: zócalos, cornisa, artesonado y paneles RETIRADOS — el arte
   * del artista los pinta ya en las texturas de techo y paredes) */

  /* ---- LUCES: dos lavados cálidos (v3.6.50: el foco del trofeo se
   *  retira con él — 2 en total) ---- */
  const lampMat = new THREE.MeshStandardMaterial({
    color: 0xfff2cf, emissive: 0xffd9a0, emissiveIntensity: 1.7, roughness: 0.4 });
  const lights = [];
  for (const lx of [-1.7, 1.7]) {
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 10), lampMat);
    lamp.position.set(lx, HALL.h - 0.34, HALL.cz + 2.2);
    g.add(lamp);
    const pl = new THREE.PointLight(0xffd9a0, 1.0, 11, 1.4);
    pl.position.set(lx, HALL.h - 0.5, HALL.cz + 2.0);
    g.add(pl);
    lights.push(pl);
  }
  /* (v3.6.50 · r58 — TROFEO RETIRADO, petición del dueño: «eliminar del
   *  escenario Hall la copa central y el haz de luz que cae sobre ella
   *  para dejar ese espacio libre». Fuera la peana de mármol, la COPA
   *  LATHE, sus asas y bola, el HAZ volumétrico, el anillo dorado del
   *  techo, la placa plateada/oro y su foco: el CENTRO de la estancia
   *  queda LIBRE sobre el emblema del suelo. El arte de las seis caras
   *  conserva la memoria del museo; las 7 bolas doradas siguen vivas.) */

  /* (v3.6.28: peana y planta RETIRADAS — el arte pinta sofás, plantas y
   * mesas en las cuatro paredes; nada 3D que las duplique) */

  /* (v3.6.28: los PINTORES DE PARED del museo — cartel, fila de
   * campeonatos, placa de ranking, medallones, cita, cabeceras, vitrinas
   * de pieles, neón y cartel de puerta — RETIRADOS: el artista pinta
   * gloria, logros, insignias y vitrinas en las texturas de las caras) */

  /* ---- SORPRESA: 7 bolas doradas flotando en vaivén de museo ---- */
  const ballMat2 = new THREE.MeshStandardMaterial({
    color: 0xf6e3ae, emissive: 0x6b4a12, emissiveIntensity: 0.55, roughness: 0.4 });
  const balls = [];
  for (let i = 0; i < 7; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.026 + (i % 3) * 0.007, 12, 10), ballMat2);
    const ang = i * 2.39996;               // ángulo dorado: reparto sin patrón
    const bx = Math.sin(ang) * 1.9;
    const bz = HALL.cz + Math.cos(ang) * 2.3;
    const bfx = {
      x0: bx, y0: 1.25 + (i % 4) * 0.24, ph: ang * 2.1,
      s: 0.55 + (i % 3) * 0.16, a: 0.07 + (i % 2) * 0.035,
    };
    b.position.set(bx, bfx.y0, bz);
    b.userData.fx = bfx;
    g.add(b);
    balls.push(b);
  }

  /* r84 · EL PULSO CRAZY EN LA PUERTA: dos placas de museo (drawHallSign)
   * a los flancos de la pared de la puerta (z1) — «EL PULSO CRAZY · reto
   * de hoy» y «TU RACHA». Los lienzos viajan en userData.hall y c12.drawHall
   * los repinta con i18n viva al entrar (el reto cambia cada medianoche). */
  const pulsoCvL = hallCanvas(1024, 600);
  const pulsoCvR = hallCanvas(1024, 600);
  drawHallSign(pulsoCvL, 'EL PULSO CRAZY', '· · ·');
  drawHallSign(pulsoCvR, 'TU RACHA', '· · ·');
  const pulsoTexL = new THREE.CanvasTexture(pulsoCvL);
  const pulsoTexR = new THREE.CanvasTexture(pulsoCvR);
  try { pulsoTexL.colorSpace = THREE.SRGBColorSpace; pulsoTexL.anisotropy = 4; } catch (eTP1) { /* */ }
  try { pulsoTexR.colorSpace = THREE.SRGBColorSpace; pulsoTexR.anisotropy = 4; } catch (eTP2) { /* */ }
  const pulsoZ = (HALL.cz + HALL.depth / 2) - 0.012;   // un pelín delante del arte
  const pulsoMeshL = new THREE.Mesh(new THREE.PlaneGeometry(0.86, 0.50),
    new THREE.MeshBasicMaterial({ map: pulsoTexL, transparent: true }));
  pulsoMeshL.position.set(-2.55, 1.7, pulsoZ);
  pulsoMeshL.rotation.y = Math.PI;                     // mira hacia dentro (−Z)
  g.add(pulsoMeshL);
  const pulsoMeshR = new THREE.Mesh(new THREE.PlaneGeometry(0.86, 0.50),
    new THREE.MeshBasicMaterial({ map: pulsoTexR, transparent: true }));
  pulsoMeshR.position.set(2.55, 1.7, pulsoZ);
  pulsoMeshR.rotation.y = Math.PI;
  g.add(pulsoMeshR);

  /* r23 (v3.6.118) · PARED DE INSIGNIAS (F2): placa de museo en la pared
   * FRONTAL (la primera que mira el anfitrión al entrar — z0). drawHall()
   * (c12) la repinta con el perfil ACTIVO: el propio, o EL DEL ANFITRIÓN
   * cuando el invitado visita su hall online (hello2 `hp`). */
  const gloriaCv = hallCanvas(1024, 640);
  drawHallGloria(gloriaCv, { titulo: '· · ·', sub: '' });
  const gloriaTex = new THREE.CanvasTexture(gloriaCv);
  try { gloriaTex.colorSpace = THREE.SRGBColorSpace; gloriaTex.anisotropy = 4; } catch (eTG1) { /* */ }
  const gloriaMesh = new THREE.Mesh(new THREE.PlaneGeometry(2.00, 1.25),
    new THREE.MeshBasicMaterial({ map: gloriaTex, transparent: true }));
  gloriaMesh.position.set(0, 1.60, z0 + 0.012);   // un pelín delante del arte
  g.add(gloriaMesh);

  /* =====================================================================
   *  r32 (v3.6.128) · ICONO DE LA MÚSICA DEL SALÓN — placa redonda en la
   *  pared FRONTAL, sobre la placa de insignias (el «equipo de sonido» de
   *  la estancia: la música ambiental del dueño suena mientras el salón
   *  está abierto — canal hall en c03 — y este icono la silencia).
   *  El gatillo VR apuntando al icono lo conmuta (raycast en c12,
   *  onSelectStart); el hover lo agrupa con suavizado (updateHallFx).
   *  Dibujo 100 % vectorial en canvas (256×256): altavoz con ondas
   *  doradas = SONANDO · barra roja en diagonal = SILENCIADO. Sólo se
   *  ve en salones CON música (neón/observatorio/dojo): repinta() decide
   *  visibilidad y estado — drawHall (c12) la llama en cada entrada.
   *  ===================================================================== */
  const musCv = hallCanvas(256, 256);
  drawHallMusica(musCv, false);
  const musTex = new THREE.CanvasTexture(musCv);
  try { musTex.colorSpace = THREE.SRGBColorSpace; musTex.anisotropy = 4; } catch (eTM1) { /* */ }
  const musMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.36, 0.36),
    new THREE.MeshBasicMaterial({ map: musTex, transparent: true }));
  musMesh.position.set(0, 2.42, z0 + 0.016);   // sobre la placa de insignias
  g.add(musMesh);
  const musica = {
    mesh: musMesh, cv: musCv, tex: musTex,
    hover: false,          // el rayo de algún mando encima (c12, ray loop)
    /** Estado + visibilidad: sólo salones CON música enseñan el icono. */
    repinta(mute, visible) {
      try {
        musMesh.visible = !!visible;
        if (!visible) return;
        drawHallMusica(musCv, !!mute);
        musTex.needsUpdate = true;
      } catch { /* el icono nunca rompe el hall */ }
    },
  };

  /* =====================================================================
   *  r39 (v3.6.135) · EL BÚHO DEL ARCANO — placa con el arte del dueño
   *  (assets/hall/arcano.png, 1024×683 RGBA) en la esquina superior
   *  DERECHA de la pared que el anfitrión mira al entrar (z0, «pared del
   *  fondo» de la estancia). El búho emite un LIGERO DESTELLO a través
   *  de sus dos ojos: dos sprites aditivos sobre los centros de los ojos
   *  (medidos sobre el arte: 0.452/0.392 y 0.557/0.376 en fracción del
   *  lienzo) que laten con fases distintas en updateHallFx. El gatillo
   *  VR apuntando al búho abre EL ESPACIO ARCANO (raycast en c12,
   *  mismo patrón que el icono de la música). Mientras llega la textura
   *  (o si falla), un búho vectorial dibujado en canvas hace de fondo.
   *  ===================================================================== */
  // r40 (v3.6.136) · EL BÚHO, UN 25 % MÁS PEQUEÑO (petición del dueño:
  // «el búho, un poco más pequeño, como un 25 % más pequeño que ahora»):
  // 0,78×0,52 → 0,585×0,39 · misma proporción 1024×683 (1.5:1), misma
  // pared y mismos destellos (los ojos escalan con ARC_W/ARC_H).
  // r54 (v3.6.145) · ALINEADO CON LA ESQUINA SUPERIOR DERECHA (petición
  // del dueño: «que se vea bien pero esté lo más ajustado a los bordes»):
  // (2,28 · 2,26) → (2,70 · 2,60) — sube 0,34 m y va a la derecha 0,42 m;
  // con el tamaño 0,585×0,39 quedan ~6 cm libres a pared (3,05) y techo
  // (2,85) — margen justo para el hover ×1,14 sin morder la esquina.
  const ARC_W = 0.585, ARC_H = 0.39;         // proporción 1024×683 (1.5:1)
  const arcCv = hallCanvas(512, 342);
  drawArcanoBuho(arcCv);                      // fallback vectorial (glow azul)
  const arcTex = new THREE.CanvasTexture(arcCv);
  try { arcTex.colorSpace = THREE.SRGBColorSpace; arcTex.anisotropy = 4; } catch (eTA0) { /* */ }
  const arcMesh = new THREE.Mesh(new THREE.PlaneGeometry(ARC_W, ARC_H),
    new THREE.MeshBasicMaterial({ map: arcTex, transparent: true }));
  // r55 · DATA-DRIVEN: la posición vive en ARCANO_CFG.ui.buho (c02) —
  // mover el búho = editar UN dato, sin tocar código del Hall.
  arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,
                       z0 + ARCANO_CFG.ui.buho.zOff);
  g.add(arcMesh);
  try {   // el arte REAL del dueño sustituye al fallback en cuanto llega
    const urlArcano = 'assets/hall/arcano.png';   // fijo del hall (no arte de variante)
    new THREE.TextureLoader().load(urlArcano, (t) => {
      try {
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 4;
        arcMesh.material.map = t;
        arcMesh.material.needsUpdate = true;
        arcTex.dispose();
      } catch { /* seguimos con el fallback */ }
    }, undefined, () => { /* sin arte: el búho vectorial manda */ });
  } catch (eTL0) { /* */ }
  // — los DOS OJOS: sprites de destello en los centros medidos del arte —
  const glintCv = hallCanvas(64, 64);
  {
    const xg = glintCv.getContext('2d');
    const gg = xg.createRadialGradient(32, 32, 2, 32, 32, 30);
    gg.addColorStop(0, 'rgba(235,250,255,0.95)');
    gg.addColorStop(0.35, 'rgba(120,210,255,0.55)');
    gg.addColorStop(1, 'rgba(60,140,255,0)');
    xg.fillStyle = gg;
    xg.fillRect(0, 0, 64, 64);
  }
  const glintTex = new THREE.CanvasTexture(glintCv);
  try { glintTex.colorSpace = THREE.SRGBColorSpace; } catch (eTG0) { /* */ }
  const glints = [];
  for (const rel of [[0.452, 0.392], [0.557, 0.376]]) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glintTex, transparent: true, opacity: 0.3,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    sp.scale.setScalar(0.075);
    sp.position.set((rel[0] - 0.5) * ARC_W, (0.5 - rel[1]) * ARC_H, 0.012);
    arcMesh.add(sp);
    glints.push(sp);
  }
  const arcono = { mesh: arcMesh, glints, hover: false };

  /* =====================================================================
   *  r28 (v3.6.124) · MOBILIARIO 3D POR SALÓN — la lección de los
   *  decorados de La Locura y Wizard (dueño: «los diseñaste tú con
   *  muchísimo más detalle… la diferencia es abismal») es que el lujo
   *  vive en la GEOMETRÍA, no sólo en las texturas. Cada variante monta
   *  SU props 3D (vestir() los reconstruye en vivo; dispose del anterior):
   *    · NEÓN      → dos RECREATIVAS reales flanqueando la mesa (marquesina
   *                  y pantalla EMISIVAS con flicker, panel de mandos)
   *    · OBSERVATORIO → GLOBO TERRÁQUEO flotante con anillo orbital (gira
   *                  y flota en updateHallFx)
   *    · DOJO      → farolillo TŌRŌ de piedra encendido + trío de bambúes
   *  Materiales EMISIVOS — CERO PointLights nuevos (lección v2.92) — y
   *  pegados a las paredes: jamás estorban la mesa ni el juego (el hall
   *  no juega: «el museo no juega», v3.6.30).
   *  ===================================================================== */
  const props = new THREE.Group();
  g.add(props);
  const _propAnim = [];      // meshes con userData de animación (updateHallFx)
  const _propTodo = [];      // todo lo creado (dispose al re-montar)
  const _limpiaProps = () => {
    for (const m of _propTodo) {
      try { if (m.geometry) m.geometry.dispose(); } catch (eG) { /* */ }
      try { if (m.material && m.material.dispose) m.material.dispose(); } catch (eM) { /* */ }
    }
    _propTodo.length = 0;
    _propAnim.length = 0;
    while (props.children.length) props.remove(props.children[0]);
  };
  const _malla = (geo, mat, x, y, z, ry) => {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    if (ry) m.rotation.y = ry;
    props.add(m);
    _propTodo.push(m);
    return m;
  };
  const montarProps = (b) => {
    _limpiaProps();
    const zf = z0 + 0.62;    // pegados a la pared FRONTAL, flancos libres
    if (b === 'assets/hall/neon/') {
      for (const [px, colPant] of [[-2.42, 0x66e2ff], [2.42, 0xff5cb0]]) {
        const cuerpo = new THREE.MeshStandardMaterial({ color: 0x241f3c, roughness: 0.7 });
        _malla(new THREE.BoxGeometry(0.66, 1.58, 0.58), cuerpo, px, 0.79, zf);
        const marq = new THREE.MeshStandardMaterial({
          color: colPant, emissive: colPant, emissiveIntensity: 1.35, roughness: 0.5 });
        _malla(new THREE.BoxGeometry(0.70, 0.16, 0.62), marq, px, 1.67, zf - 0.02);
        const pantMat = new THREE.MeshStandardMaterial({
          color: 0x0a1428, emissive: colPant, emissiveIntensity: 0.85, roughness: 0.25 });
        const pantalla = _malla(new THREE.PlaneGeometry(0.46, 0.36), pantMat, px, 1.18, zf + 0.30);
        pantalla.userData.flicker = pantMat;       // CRT vivo (updateHallFx)
        _propAnim.push(pantalla);
        const mando = new THREE.MeshStandardMaterial({ color: 0x1a1730, roughness: 0.6 });
        _malla(new THREE.BoxGeometry(0.60, 0.10, 0.30), mando, px, 0.92, zf + 0.36);
      }
    } else if (b === 'assets/hall/observatorio/') {
      // GLOBO TERRÁQUEO: textura canvas procedural (océano + continentes)
      const cvG = hallCanvas(256, 128);
      const cx2 = cvG.getContext('2d');
      cx2.fillStyle = '#1a5cb0'; cx2.fillRect(0, 0, 256, 128);
      const rndG = [[36, 34, 44, 20], [120, 26, 40, 16], [190, 60, 34, 18], [80, 84, 30, 13],
        [220, 96, 24, 11], [16, 92, 26, 12], [150, 100, 28, 10], [58, 20, 18, 9]];
      cx2.fillStyle = '#3f8a48';
      for (const [bx2, by2, br2] of rndG) {
        cx2.beginPath();
        cx2.ellipse(bx2 * 2.56, by2 * 1.28, br2 * 2.2, br2 * 1.5, 0.6, 0, Math.PI * 2);
        cx2.fill();
      }
      const texG = new THREE.CanvasTexture(cvG);
      try { texG.colorSpace = THREE.SRGBColorSpace; } catch (eTG2) { /* */ }
      const globoMat = new THREE.MeshStandardMaterial({
        map: texG, emissive: 0x11335f, emissiveIntensity: 0.4, roughness: 0.55 });
      const globo = _malla(new THREE.SphereGeometry(0.30, 24, 18), globoMat,
        -2.35, 1.52, zf + 0.25);
      globo.userData.giro = 0.35;
      globo.userData.flote = 0.05;
      globo.userData.y0 = 1.52;
      globo.userData.fase = 1.3;
      _propAnim.push(globo);
      const anilloMat = new THREE.MeshStandardMaterial({
        color: 0x50c8ff, emissive: 0x50c8ff, emissiveIntensity: 1.1, roughness: 0.4 });
      const anillo = _malla(new THREE.TorusGeometry(0.46, 0.012, 8, 48), anilloMat,
        -2.35, 1.52, zf + 0.25);
      anillo.rotation.x = 1.25;
      anillo.userData.giro = -0.22;
      _propAnim.push(anillo);
    } else if (b === 'assets/hall/dojo/') {
      // TŌRŌ (farolillo de piedra) con luz cálida + trío de bambúes
      const piedra = new THREE.MeshStandardMaterial({ color: 0x8d8d86, roughness: 0.95 });
      const luzMat = new THREE.MeshStandardMaterial({
        color: 0xffd9a0, emissive: 0xffc06a, emissiveIntensity: 1.5, roughness: 0.4 });
      const lx = -2.45, lz = zf + 0.1;
      _malla(new THREE.CylinderGeometry(0.16, 0.20, 0.10, 10), piedra, lx, 0.05, lz);
      _malla(new THREE.CylinderGeometry(0.055, 0.055, 0.62, 8), piedra, lx, 0.40, lz);
      _malla(new THREE.BoxGeometry(0.30, 0.26, 0.30), luzMat, lx, 0.82, lz);
      _malla(new THREE.CylinderGeometry(0.24, 0.06, 0.18, 10), piedra, lx, 1.03, lz);
      // bambúes (varillas con nudos)
      const bambu = new THREE.MeshStandardMaterial({ color: 0x5e8c46, roughness: 0.7 });
      for (const [bx3, alt, tilt] of [[2.42, 1.55, 0.05], [2.58, 1.30, -0.07], [2.30, 1.15, 0.10]]) {
        const bmb = _malla(new THREE.CylinderGeometry(0.030, 0.038, alt, 7), bambu,
          bx3, alt / 2, zf + 0.15);
        bmb.rotation.z = tilt;
      }
    } else if (b === 'assets/hall/rascacielos/') {
      // r38 (v3.6.134) · MAQUETA DEL RASCACIELOS: dos torres con ventanas
      // encendidas (emisivo cálido) + BALIZA ROJA parpadeante en la antena
      // (flicker de updateHallFx — el mobiliario vive como el resto).
      const cvTo = hallCanvas(64, 128);
      const xTo = cvTo.getContext('2d');
      xTo.fillStyle = '#1c2430'; xTo.fillRect(0, 0, 64, 128);
      xTo.fillStyle = '#ffd98a';
      for (let wy = 6; wy < 124; wy += 8) {
        for (let wx = 6; wx < 58; wx += 10) {
          if (Math.random() < 0.62) xTo.fillRect(wx, wy, 5, 4);
        }
      }
      const texTo = new THREE.CanvasTexture(cvTo);
      try { texTo.colorSpace = THREE.SRGBColorSpace; } catch (eTT) { /* */ }
      const torreMat = new THREE.MeshStandardMaterial({
        map: texTo, emissive: 0xffd98a, emissiveMap: texTo,
        emissiveIntensity: 0.55, roughness: 0.6 });
      // torre ALTA (izquierda) + torre BAJA (derecha), pegadas a la pared
      const tAlta = _malla(new THREE.BoxGeometry(0.44, 1.72, 0.40), torreMat,
        -2.40, 0.86, zf + 0.18);
      tAlta.rotation.y = 0.22;
      const tBaja = _malla(new THREE.BoxGeometry(0.38, 1.10, 0.36), torreMat,
        -2.02, 0.55, zf + 0.34);
      tBaja.rotation.y = -0.15;
      // corona de la torre alta + antena + baliza (flicker)
      const coronaMat = new THREE.MeshStandardMaterial({ color: 0x39424e, roughness: 0.5 });
      _malla(new THREE.BoxGeometry(0.48, 0.07, 0.44), coronaMat, -2.40, 1.76, zf + 0.18);
      _malla(new THREE.CylinderGeometry(0.010, 0.014, 0.34, 6), coronaMat,
        -2.40, 1.96, zf + 0.18);
      const balizaMat = new THREE.MeshStandardMaterial({
        color: 0xff3b30, emissive: 0xff2418, emissiveIntensity: 1.8, roughness: 0.3 });
      const baliza = _malla(new THREE.SphereGeometry(0.035, 10, 8), balizaMat,
        -2.40, 2.14, zf + 0.18);
      baliza.userData.flicker = balizaMat;   // parpadeo vivo (updateHallFx)
      _propAnim.push(baliza);
    }
  };
  montarProps(vbase);

  g.userData.hall = {
    /* v3.6.50 (r58): las SEIS CARAS visten el arte del artista (texs llega
     * async; texWant = contrato de las 6 claves). Del museo sobrevive lo
     * VIVO: las 7 bolas doradas y las 2 luces — el trofeo y su haz ya no
     * existen (espacio central libre, petición del dueño). */
    texs, texWant: Object.keys(texPaths),
    base: vbase, vestir,   // r24 · variante de arte activa + re-vestido
    floor, walls: [wallLeft, wallRight, wallFront, wallBack], ceil,
    insigniaCache: {},   // (retirado v3.6.28: las paredes visten arte fijo)
    lights,
    fx: { balls, props: _propAnim },   // r28 · props animables por salón
    pulsoL: { cv: pulsoCvL, tex: pulsoTexL },   // r84 · placas EL PULSO
    pulsoR: { cv: pulsoCvR, tex: pulsoTexR },
    gloria: { cv: gloriaCv, tex: gloriaTex },   // r23 · pared de insignias
    musica,   // r32 · icono de la música del salón (silencio por gatillo)
    arcono,   // r39 · el búho del Arcano (destello en los ojos; entra c12)
  };
  return g;
}

/** r24 (v3.6.119) · RE-VESTIR EL HALL con otra variante de arte (en vivo,
 *  sin reconstruir el grupo — la red y el rig guardan referencias). Devuelve
 *  true si cambió algo. Cadenas ajenas o iguales: no-op. */
export function applyHallVariant(g, base) {
  try {
    const ud = g && g.userData && g.userData.hall;
    if (!ud || typeof ud.vestir !== 'function') return false;
    if (typeof base !== 'string' || !base || ud.base === base) return false;
    ud.vestir(base);
    ud.base = base;
    return true;
  } catch { return false; }
}

/* v3.6.50 (r58) · las sorpresas del museo respiran: las 7 bolas doradas
 * navegan en vaivén. El trofeo, su haz y su anillo se RETIRARON (espacio
 * central libre). SÓLO se llama con el hall visible (desde animate, si
 * inHall): coste cero en la cancha. */
export function updateHallFx(g, dt, now) {
  const ud = g.userData && g.userData.hall;
  if (!ud || !ud.fx) return;
  const fx = ud.fx;
  for (const b of fx.balls) {
    const p = b.userData.fx;
    b.position.y = p.y0 + Math.sin(now * p.s + p.ph) * p.a;
    b.position.x = p.x0 + Math.sin(now * p.s * 0.6 + p.ph * 1.7) * 0.09;
  }
  // r28 · mobiliario 3D del salón VIVO: giro/flote/flicker según userData
  const pr = fx.props;
  if (pr && pr.length) {
    for (const m of pr) {
      const u = m.userData;
      if (u.giro) m.rotation.y += dt * u.giro;
      if (u.flote) m.position.y = u.y0 + Math.sin(now * 0.8 + (u.fase || 0)) * u.flote;
      if (u.flicker) {
        u.flicker.emissiveIntensity = 0.78 + Math.sin(now * 7.3) * 0.16 +
          Math.sin(now * 23.7) * 0.08;
      }
    }
  }
  // r32 · ICONO DE LA MÚSICA: el hover del rayo (c12) lo agranda con
  // suavizado — feedback de «esto es un mando», no un adorno.
  const mu = ud.musica;
  if (mu && mu.mesh && mu.mesh.visible) {
    const tgt = mu.hover ? 1.16 : 1.0;
    const cur = mu.mesh.scale.x || 1;
    mu.mesh.scale.setScalar(cur + (tgt - cur) * Math.min(1, dt * 12));
  }
  // r39 · EL BÚHO DEL ARCANO: el hover lo agranda (mismo lenguaje que el
  // icono de la música) y los DOS OJOS emiten su ligero destello — dos
  // fases distintas, un latido suave que nunca duerme del todo.
  const ar = ud.arcono;
  if (ar && ar.mesh && ar.mesh.visible) {
    const tgtA = ar.hover ? 1.14 : 1.0;
    const curA = ar.mesh.scale.x || 1;
    ar.mesh.scale.setScalar(curA + (tgtA - curA) * Math.min(1, dt * 12));
    if (ar.glints && ar.glints.length === 2) {
      ar.glints[0].material.opacity = 0.30 + Math.sin(now * 2.1) * 0.17 +
        Math.sin(now * 0.7) * 0.08;
      ar.glints[1].material.opacity = 0.30 + Math.sin(now * 2.1 + 1.9) * 0.17 +
        Math.sin(now * 0.7 + 2.6) * 0.08;
    }
  }
}

/* =======================================================================
 *  r39 (v3.6.135) · EL ESPACIO ARCANO — la estancia infinita del búho.
 *  Todo PROCEDURAL (cero assets nuevos): bóveda celeste oscura con la
 *  VÍA LÁCTEA pintada en canvas sobre una esfera invertida, MOTAS AZULES
 *  brillantes que serpentean en el aire (THREE.Points con fase propia),
 *  COMETAS ocasionales que cruzan a lo lejos dejando un halo azul, el
 *  BÚHO presente (el arte del dueño, grande, flotando) y LA GALERÍA:
 *  panel con el icono del poder materializado, su nombre, su tipo
 *  (ataque/defensa/distracción), su descripción y sus métricas, con
 *  flechas ‹ › azules con glow y candado azul translúcido en los
 *  bloqueados. c12 monta el grupo una vez, lo enciende al entrar y
 *  anima con updateArcanoFx.
 *  ======================================================================= */

/** Fallback vectorial del búho (mientras llega el arte del dueño — o si
 *  falla la carga): silueta con ojos encendidos, glow azul del Arcano. */
export function drawArcanoBuho(cv) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  x.fillStyle = 'rgba(4,10,22,0.92)';
  x.fillRect(0, 0, W, H);
  const cx = W / 2, cy = H * 0.52;
  // alas
  x.strokeStyle = '#5fd4ff';
  x.lineWidth = W * 0.02;
  x.shadowColor = 'rgba(70,170,255,0.9)';
  x.shadowBlur = W * 0.05;
  for (const s of [-1, 1]) {
    x.beginPath();
    x.moveTo(cx, cy - H * 0.12);
    x.quadraticCurveTo(cx + s * W * 0.30, cy - H * 0.30, cx + s * W * 0.44, cy + H * 0.05);
    x.quadraticCurveTo(cx + s * W * 0.26, cy + H * 0.02, cx + s * W * 0.13, cy + H * 0.16);
    x.stroke();
  }
  // cuerpo y cabeza
  x.fillStyle = 'rgba(70,170,255,0.85)';
  x.beginPath();
  x.ellipse(cx, cy + H * 0.16, W * 0.09, H * 0.20, 0, 0, Math.PI * 2);
  x.fill();
  x.beginPath();
  x.arc(cx, cy - H * 0.06, W * 0.105, 0, Math.PI * 2);
  x.fill();
  // orejas
  for (const s of [-1, 1]) {
    x.beginPath();
    x.moveTo(cx + s * W * 0.075, cy - H * 0.14);
    x.lineTo(cx + s * W * 0.13, cy - H * 0.30);
    x.lineTo(cx + s * W * 0.015, cy - H * 0.17);
    x.closePath();
    x.fill();
  }
  // ojos encendidos
  x.shadowBlur = W * 0.04;
  x.shadowColor = 'rgba(200,240,255,1)';
  x.fillStyle = '#eafaff';
  for (const s of [-1, 1]) {
    x.beginPath();
    x.arc(cx + s * W * 0.045, cy - H * 0.055, W * 0.026, 0, Math.PI * 2);
    x.fill();
  }
  x.shadowBlur = 0;
}

/** Lienzo de la BÓVEDA — r40 (v3.6.136), petición del dueño: «el fondo
 *  completamente azul oscuro SIN IMAGEN, simulando una noche oscura».
 *  Se retira la Vía Láctea y el campo de estrellas de la r39: la vida del
 *  cielo la ponen las 240 motas y los cometas que serpentean por
 *  DELANTE. Sólo un degradado vertical muy sutil (cenit más profundo,
 *  horizonte un pelo más claro) para dar profundidad sin dejar de ser
 *  «solo color». 1024×512 equirectangular sobre la esfera invertida. */
function pintaBoveda(cv) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const bg = x.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#03061a');     // cenit: azul noche profundo
  bg.addColorStop(0.55, '#071129');  // medio del cielo
  bg.addColorStop(1, '#0a1a36');     // horizonte: el color con el que el
                                     // suelo se funde (CIELO del suelo)
  x.fillStyle = bg;
  x.fillRect(0, 0, W, H);
}

/** MOTAS AZULES: nube de puntos con base + fase propios (serpenteo en
 *  updateArcanoFx). Brillo azul como el búho, aditivas. r40: fog:false —
 *  los destellos flotan a cualquier distancia SIN la niebla de la cancha. */
function montaMotas(N) {
  const base = new Float32Array(N * 3);
  const fase = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const r = 2.2 + Math.random() * 7.5;
    const a = Math.random() * Math.PI * 2;
    base[i * 3] = Math.cos(a) * r;
    base[i * 3 + 1] = 0.4 + Math.random() * 4.4;
    base[i * 3 + 2] = Math.sin(a) * r;
    fase[i] = Math.random() * Math.PI * 2;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(base.slice(), 3));
  // r41 · MOTAS DE POLVO (petición del dueño: «partículas flotantes más
  // pequeñas y circulares, como motas de polvo»): textura radial — punto
  // REDONDO y suave, jamás el cuadrado pelado del PointsMaterial — y la
  // MITAD de tamaño que en la r40.
  const dot = spriteRadial(3, 'rgba(240,250,255,1)', 'rgba(150,215,255,0.72)', 'rgba(90,160,255,0)');
  const mat = new THREE.PointsMaterial({
    color: 0x49b6ff, size: 0.026, map: dot, transparent: true, opacity: 0.9,
    blending: THREE.AdditiveBlending, depthWrite: false, sizeAttenuation: true,
    fog: false,
  });
  const pts = new THREE.Points(geo, mat);
  pts.userData = { base, fase, n: N };
  return pts;
}

/* r41 (v3.6.137) · EL SUELO NEGRO DE LOSETAS — refinamiento del dueño
 * sobre el suelo de la r40: «el patrón de losetas más pequeñas y mejor
 * definidas… vamos a hacer que el suelo sea NEGRO y se descubran las
 * losetas en posiciones aleatorias: en el suelo se verán las LÍNEAS de
 * la matriz de losetas pero su RELLENO azul será aleatorio — unas
 * aparecen, otras se apagan, de forma completamente aleatoria».
 * Tres planos (fog:false en los tres — la niebla de la cancha jamás
 * toca la estancia):
 *  · BASE NEGRA con gradiente radial: negro azulado bajo los pies →
 *    color del horizonte (#0a1a36, el de la bóveda) en el borde — la
 *    costura con el cielo sigue siendo IMPOSIBLE de ver (lección r40);
 *  · r43 · EL TRAZADO DE DESTELLOS (petición del dueño: «eliminar del
 *    suelo el tramado de líneas… que de forma completamente aleatoria se
 *    vean líneas que dibujan algunas partes, que den la sensación de que
 *    en un lado y en otro se dibujan las líneas partiendo de un fondo y
 *    llegando al otro, como destellos que dejan una estela que es la
 *    propia línea, que se ve durante unos 5 segundos y desaparece… varias
 *    líneas que se cruzan tanto en un sentido como en el opuesto,
 *    cruzadas 90 grados, descubriendo la trama fina que existe por debajo
 *    pero que sólo se ve al pasar esta estela de líneas»): FUERA la
 *    matriz estática de la r41 — ahora UN lienzo vivo repinta cada frame
 *    DESTELLOS-corredores que recorren líneas de la retícula fina
 *    (48×48 losetas de 1,5 m) en AMBOS ejes (cruces de 90°) y en AMBOS
 *    sentidos, naciendo en un borde y muriendo en el opuesto; tras la
 *    cabeza viaja la ESTELA = la propia línea (mucho más delgada que la
 *    r41: 0,8 px ≈ 5 cm reales), que aguanta ~5 s y se desvanece. La
 *    trama fina SÓLO existe donde un destello la ha dibujado;
 *  · RELLENOS VIVOS (r41, ahora en el MISMO lienzo): cada celda que un
 *    destello atraviesa puede encender su relleno azul (banda del dueño
 *    #10284e → #1a3868) con envolvente nacer→aguantar→morir — «los
 *    rellenos igual, en esas cuadrículas sutiles y bien definidas». */
function montaSueloArcano() {
  const N = 48;                      // 48×48 losetas de 1,5 m → 72 m (trama fina)
  const LADO = N * 1.5;
  const CIELO = [10, 26, 54];        // #0a1a36 · color del horizonte (bóveda)
  const BANDA = [[16, 40, 78], [26, 56, 104]];   // el rango azul del dueño
  const VIDA = 5.0;                  // r43 · la línea dibujada aguanta ~5 s
  const g = new THREE.Group();
  // — CAPA 0 · la BASE NEGRA (radial al color del horizonte) —
  const bcv = hallCanvas(512, 512);
  const bx = bcv.getContext('2d');
  const bgR = bx.createRadialGradient(256, 256, 30, 256, 256, 256);
  bgR.addColorStop(0, '#03060d');    // negro azulado bajo los pies
  bgR.addColorStop(0.55, '#04070f');
  bgR.addColorStop(1, 'rgb(' + CIELO[0] + ',' + CIELO[1] + ',' + CIELO[2] + ')');
  bx.fillStyle = bgR;
  bx.fillRect(0, 0, 512, 512);
  const bTex = new THREE.CanvasTexture(bcv);
  try { bTex.colorSpace = THREE.SRGBColorSpace; } catch { /* */ }
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(LADO, LADO),
    new THREE.MeshBasicMaterial({ map: bTex, fog: false }));
  mesh.rotation.x = -Math.PI / 2;    // tumbado, mirando arriba
  mesh.position.y = -0.01;
  g.add(mesh);
  // — CAPA 1 · EL TRAZADO VIVO (r43): destellos que DIBUJAN la trama —
  const tcv = hallCanvas(512, 512);
  const tex = new THREE.CanvasTexture(tcv);
  try { tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4; } catch { /* */ }
  const malla = new THREE.Mesh(new THREE.PlaneGeometry(LADO, LADO),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, fog: false }));
  malla.rotation.x = -Math.PI / 2;
  malla.position.y = 0.002;
  g.add(malla);
  const mezcla = () => {
    const k = Math.random();
    return [0, 1, 2].map((i) => Math.round(BANDA[0][i] + (BANDA[1][i] - BANDA[0][i]) * k));
  };
  g.userData = {
    N, paso: 512 / N, tcv, tCtx: tcv.getContext('2d'), tex, mezcla, VIDA,
    trazos: [],     // destellos vivos {ax, ln, desde, hasta, head, vel, t, col, nac}
    lit: [],        // rellenos vivos de celdas atravesadas (envolvente r41)
    prox: 0.4,      // temporizador hasta el próximo destello
  };
  return g;
}

/* r41 · COLORES del halo de los OJOS del búho: azul búho ↔ rojo de
 * bloqueo — el dueño: «un efecto de halo en sus ojos animado que oscila
 * de azul a rojo». Constantes de módulo: cero basura por frame. */
const _ARCO_OJO_A = new THREE.Color(0x49b6ff);
const _ARCO_OJO_B = new THREE.Color(0xff3524);
const _arcoOjoT = new THREE.Color();

/* r41 · COMPOSICIÓN HOLOGRÁFICA del panel (k = 0..1) — la ficha se
 * FORMA sobre el lienzo vivo (petición del dueño: «un efecto de
 * holograma que se va formando, un efecto futurista y llamativo, con
 * disolución»): bandas horizontales que aún viajan y se asientan, una
 * DISOLUCIÓN de motas que se re-compone, el BARRIDO de condensación
 * que baja dejando la ficha fija, líneas de escaneo con parpadeo de
 * encendido y una ABERRACIÓN fantasma que se cierra. A k=1 el llamador
 * copia la base exacta y el efecto duerme (coste cero en reposo). */
function arconoHoloFrame(x, base, k, sem) {
  const W = base.width, H = base.height;
  x.clearRect(0, 0, W, H);
  const rev = Math.min(1.12, k * 1.3);        // frente de condensación
  const revY = rev * H;
  const ruido = (n) => {
    const s = Math.sin(n * 127.1 + sem * 311.7) * 43758.5453;
    return (s - Math.floor(s)) * 2 - 1;
  };
  // — aberración fantasma que se cierra (el holograma «encaja») —
  const ab = (1 - k) * 7;
  x.globalAlpha = 0.20 * (1 - k);
  x.drawImage(base, -ab, 0, W, H);
  x.drawImage(base, ab, 0, W, H);
  x.globalAlpha = 1;
  // — bandas horizontales: cada franja viaja en x y se asienta —
  const NB = 26, bh = H / NB;
  for (let i = 0; i < NB; i++) {
    const y = i * bh;
    if (y > revY) break;                       // aún no condensada
    const viaja = (1 - k) * (1 - y / H);
    x.drawImage(base, 0, y, W, bh, ruido(i + 0.5) * 95 * viaja, y, W, bh);
  }
  // — disolución: motas que aún faltan por condensar (densidad cae) —
  const dens = ((1 - k) * 240) | 0;
  x.globalCompositeOperation = 'destination-out';
  x.fillStyle = '#000';
  for (let i = 0; i < dens; i++) {
    const px = (ruido(i * 1.7 + 3) * 0.5 + 0.5) * W;
    const py = (ruido(i * 2.3 + 7) * 0.5 + 0.5) * revY;
    const r = 1.2 + (ruido(i * 3.1 + 11) * 0.5 + 0.5) * 4.2 * (1 - k);
    x.beginPath();
    x.arc(px, py, r, 0, Math.PI * 2);
    x.fill();
  }
  x.globalCompositeOperation = 'source-over';
  // — barrido: el frente holográfico que baja FORMANDO la ficha —
  if (revY < H - 4) {
    const g = x.createLinearGradient(0, revY - 44, 0, revY + 8);
    g.addColorStop(0, 'rgba(120,200,255,0)');
    g.addColorStop(0.72, 'rgba(150,215,255,0.28)');
    g.addColorStop(1, 'rgba(215,240,255,0.55)');
    x.globalCompositeOperation = 'lighter';
    x.fillStyle = g;
    x.fillRect(0, revY - 44, W, 52);
    x.globalCompositeOperation = 'source-over';
  }
  // — líneas de escaneo + parpadeo de encendido (se calman al asentarse) —
  const flick = 1 - (1 - k) * (0.5 + 0.5 * Math.sin(sem * 1.7 + k * 55));
  x.globalAlpha = (1 - k) * 0.15 * flick;
  x.fillStyle = '#9fd4ff';
  for (let y = 2; y < revY; y += 4) x.fillRect(0, y, W, 1);
  x.globalAlpha = 1;
}

/** r41 · GLIFO DEL CANDADO en SU lienzo (128×128): el candado azul
 *  translúcido de siempre — ahora FLOTANDO DELANTE del medallón (borde
 *  inf-derecho, sin tapar jamás el icono) con su HALO ROJO pulsante
 *  (sprite hermano en montarArcano, animado en updateArcanoFx). */
export function drawArcanoCandado(cv) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  const lx = W / 2, ly = H * 0.56, ls = W * 0.5;
  // discoscape oscuro tras el glifo (legible sobre cualquier ficha)
  x.beginPath();
  x.arc(W / 2, H / 2, W * 0.44, 0, Math.PI * 2);
  x.fillStyle = 'rgba(6,14,30,0.72)';
  x.fill();
  x.lineWidth = 3;
  x.strokeStyle = 'rgba(255,70,50,0.6)';
  x.stroke();
  // cuerpo + arco + mira (la estética azul del búho)
  x.fillStyle = 'rgba(10,26,52,0.8)';
  x.beginPath();
  x.roundRect ? x.roundRect(lx - ls * 0.52, ly - ls * 0.18, ls * 1.04, ls * 0.86, 10)
    : x.rect(lx - ls * 0.52, ly - ls * 0.18, ls * 1.04, ls * 0.86);
  x.fill();
  x.lineWidth = 7;
  x.strokeStyle = 'rgba(120,205,255,0.95)';
  x.beginPath();
  x.arc(lx, ly - ls * 0.18, ls * 0.30, Math.PI, 0);
  x.stroke();
  x.beginPath();
  x.arc(lx, ly + ls * 0.16, ls * 0.075, 0, Math.PI * 2);
  x.fillStyle = 'rgba(120,205,255,0.95)';
  x.fill();
}

/** r43 · TEXTO DE SALIDA del espacio arcano («Cuando apuntamos al icono
 *  del búho encima debe aparecer un texto que diga "Salir" o "Exit",
 *  con letras azules con el halo azulón, también con la misma estética
 *  que el búho»): letras azules con TRIPLE pasada de halo (halo→cuerpo→
 *  alma, la técnica del neón del Hall) en el lienzo 256×96 que cuelga
 *  sobre el búho. c12 la llama con el idioma vivo (T('arcono_salir'));
 *  la visibilidad la conduce updateArcanoFx con el hover del búho. */
export function drawArcanoSalir(cv, txt) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  const t = String(txt || 'Salir');
  x.textAlign = 'center';
  x.textBaseline = 'middle';
  x.font = '800 40px system-ui, sans-serif';
  const cx0 = W / 2, cy0 = H / 2 + 2;
  // — 1 · el HALO AZULÓN: tres pasadas de sombra azul creciente —
  x.shadowColor = 'rgba(73,182,255,0.95)';
  x.fillStyle = 'rgba(73,182,255,0.85)';
  for (const bl of [10, 18, 26]) {
    x.shadowBlur = bl;
    x.fillText(t, cx0, cy0);
  }
  x.shadowBlur = 0;
  // — 2 · el CUERPO azul claro del texto —
  x.fillStyle = '#8fd4ff';
  x.fillText(t, cx0, cy0);
  // — 3 · el ALMA interior casi blanca (la firma del búho) —
  x.fillStyle = 'rgba(235,250,255,0.5)';
  x.fillText(t, cx0, cy0);
}

/** Sprite radial genérico (cabeza de cometa, halo, destello del búho). */
function spriteRadial(r0, c0, c1, c2) {
  const cv = hallCanvas(64, 64);
  const x = cv.getContext('2d');
  const g = x.createRadialGradient(32, 32, r0, 32, 32, 31);
  g.addColorStop(0, c0);
  g.addColorStop(0.4, c1);
  g.addColorStop(1, c2);
  x.fillStyle = g;
  x.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(cv);
  try { t.colorSpace = THREE.SRGBColorSpace; } catch { /* */ }
  return t;
}

/** CHEVRON ‹ › de la galería: flecha azul con glow del búho (el disco
 *  oscuro tras la flecha es el lenguaje de las flechas ‹ › del icono).
 *  r41 · LOS GLIFOS ESTABAN CRUZADOS (informe del dueño: «las flechas
 *  están al revés, intercambiar los iconos»): dir 'L' dibuja AHORA el
 *  chevron ‹ (apunta a la izquierda, va a la IZQUIERDA del panel y
 *  retrocede) y dir 'R' el › (derecha del panel, avanza) — el icono
 *  coincide SIEMPRE con el lado y con la acción. */
export function drawArcanoFlecha(cv, dir) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  // disco oscuro translúcido
  x.beginPath();
  x.arc(W / 2, H / 2, W * 0.44, 0, Math.PI * 2);
  x.fillStyle = 'rgba(6,14,30,0.72)';
  x.fill();
  x.lineWidth = W * 0.045;
  x.strokeStyle = 'rgba(80,180,255,0.85)';
  x.stroke();
  // chevron con glow
  x.strokeStyle = '#8fdcff';
  x.lineWidth = W * 0.075;
  x.lineCap = 'round';
  x.lineJoin = 'round';
  x.shadowColor = 'rgba(80,180,255,0.95)';
  x.shadowBlur = W * 0.09;
  const s = dir === 'L' ? 1 : -1;   // r41 · ‹ a la IZQUIERDA · › a la DERECHA (glifos descruzados)
  x.beginPath();
  x.moveTo(W / 2 + s * W * 0.13, H * 0.27);
  x.lineTo(W / 2 - s * W * 0.13, H * 0.5);
  x.lineTo(W / 2 + s * W * 0.13, H * 0.73);
  x.stroke();
  x.shadowBlur = 0;
}

/** PINTA el panel de la galería. d = {
 *   titulo, sub, pie, idxTxt, nombre, tipoTexto, tipoCol, desc, metricas,
 *   estadoTxt, estadoCol, icono (Image|null), bloqueado } — NUNCA se
 *  corta: todo texto se mide y se encoge. */
export function drawArcanoPanel(cv, d) {
  const x = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  x.clearRect(0, 0, W, H);
  // — cristal azul oscuro con marco del búho —
  const bg = x.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, 'rgba(10,24,48,0.94)');
  bg.addColorStop(0.6, 'rgba(6,14,32,0.96)');
  bg.addColorStop(1, 'rgba(3,8,20,0.97)');
  x.fillStyle = bg;
  if (x.roundRect) { x.beginPath(); x.roundRect(0, 0, W, H, 42); x.fill(); }
  else x.fillRect(0, 0, W, H);
  x.strokeStyle = 'rgba(80,180,255,0.9)';
  x.lineWidth = 5;
  if (x.roundRect) { x.beginPath(); x.roundRect(7, 7, W - 14, H - 14, 38); x.stroke(); }
  else x.strokeRect(7, 7, W - 14, H - 14);
  const envuelve = (txt, fs, col, y0, maxW, maxLn, bold) => {
    x.font = (bold ? '700 ' : '400 ') + fs + 'px system-ui, sans-serif';
    const palabras = String(txt).split(' ');
    const lns = [];
    let cur = '';
    for (const p of palabras) {
      const pr = cur ? cur + ' ' + p : p;
      if (x.measureText(pr).width > maxW && cur) { lns.push(cur); cur = p; }
      else cur = pr;
    }
    if (cur) lns.push(cur);
    x.fillStyle = col;
    x.textAlign = 'left';
    let y = y0;
    for (let i = 0; i < Math.min(lns.length, maxLn); i++) {
      x.fillText(lns[i], 56, y);
      y += fs * 1.3;
    }
    return y;
  };
  // — cabecera: título del Arcano + índice —
  x.textAlign = 'left';
  x.fillStyle = '#8fdcff';
  x.font = '900 46px system-ui, sans-serif';
  x.shadowColor = 'rgba(80,180,255,0.8)';
  x.shadowBlur = 18;
  x.fillText(d.titulo || '', 56, 78);
  x.shadowBlur = 0;
  x.font = '600 27px system-ui, sans-serif';
  x.fillStyle = '#5f88b8';
  x.fillText(d.idxTxt || '', 56, 116);
  x.textAlign = 'right';
  x.font = '700 26px system-ui, sans-serif';
  x.fillStyle = '#5f88b8';
  x.fillText(d.sub || '', W - 56, 78);
  // — icono del poder en su medallón —
  const icX = 56 + 96, icY = 236, icR = 96;
  x.beginPath();
  x.arc(icX, icY, icR, 0, Math.PI * 2);
  x.fillStyle = 'rgba(9,20,42,0.9)';
  x.fill();
  x.lineWidth = 4;
  x.strokeStyle = 'rgba(80,180,255,0.65)';
  x.stroke();
  if (d.icono) {
    const iw = d.icono.width || 64, ih = d.icono.height || 64;
    // r41 · SANGRE COMPLETA (petición del dueño: «deben ser más grande,
    // es la forma que tenemos de identificarlos, deben ocupar TODO el
    // espacio del círculo azul que los perimetra») — recortado al
    // propio círculo, sin letterbox ni margen. Bloqueado: atenuado.
    const k = (icR * 1.96) / Math.max(iw, ih);
    if (d.bloqueado) {
      x.globalAlpha = 0.42;          // el icono se apaga tras el candado
    }
    x.save();
    x.beginPath();
    x.arc(icX, icY, icR - 1, 0, Math.PI * 2);
    x.clip();
    x.drawImage(d.icono, icX - (iw * k) / 2, icY - (ih * k) / 2, iw * k, ih * k);
    x.restore();
    if (d.bloqueado) x.globalAlpha = 1;
  } else {
    x.fillStyle = '#3d5a80';
    x.font = '700 60px system-ui, sans-serif';
    x.textAlign = 'center';
    x.fillText('?', icX, icY + 20);
  }
  // r41 · el candado YA NO se pinta sobre el icono (lo tapaba): ahora
  // es un GRUPO flotante DELANTE del medallón con HALO ROJO pulsante —
  // drawArcanoCandado dibuja el glifo, montarArcano lo cuelga delante
  // del círculo y c12 sincroniza su visibilidad con el estado REAL.
  // — nombre + tipo + estado —
  const txX = 56 + 96 + icR + 34;
  x.textAlign = 'left';
  let nombre = String(d.nombre || '').replace(/[¡!]/g, '').trim();
  x.font = '900 40px system-ui, sans-serif';
  while (x.measureText(nombre).width > W - txX - 56 && nombre.length > 8) {
    nombre = nombre.slice(0, nombre.length - 2);
  }
  x.fillStyle = d.bloqueado ? '#7f9cc0' : '#eaf6ff';
  x.fillText(nombre, txX, 190);
  x.font = '800 27px system-ui, sans-serif';
  x.fillStyle = d.tipoCol || '#8fdcff';
  x.fillText('◈ ' + (d.tipoTexto || ''), txX, 232);
  x.font = '600 24px system-ui, sans-serif';
  x.fillStyle = d.estadoCol || '#7f9cc0';
  x.fillText(d.estadoTxt || '', txX, 270);
  // — descripción —
  let y = envuelve(d.desc || '', 27.5, d.bloqueado ? '#93a9c4' : '#c7d9ee', 390, W - 112, 5);
  // — métricas —
  y += 14;
  x.font = '700 25px system-ui, sans-serif';
  x.fillStyle = '#8fdcff';
  x.fillText('◆ ' + (d.metricasLbl || 'Métricas'), 56, y);
  y += 38;
  y = envuelve(d.metricas || '', 26, '#a8c4e2', y, W - 112, 2);
  // — pie —
  x.font = '600 23px system-ui, sans-serif';
  x.fillStyle = '#4f76a4';
  x.textAlign = 'center';
  x.fillText(d.pie || '', W / 2, H - 34);
  return y;
}

/* =====================================================================
 *  r45+r47 · TRAZOS DE LA CONSTELACIÓN DE PALAS — el contorno de
 *  palas.png (arte NUEVO del dueño: logo CRAZY PING PONG macizo) reducido
 *  a 34 polilíneas que traza un bolígrafo. Mismo EFECTO que la r45, otra
 *  imagen: el arte macizo pide CONTORNO (marching squares sobre el canal
 *  alfa suavizado + Douglas-Peucker 1,6 px — gen_trazo_palas_r47.py), no
 *  el esqueleto de la silueta lineal de la r45. Coordenadas normalizadas:
 *  x −0.5..0.5, y abajo→arriba positivo. La consume montaConstelacion()
 *  (mismo fichero) sin cambios: el estado del bolígrafo es idéntico.
 *  ===================================================================== */
const ARCANO_PALAS_TRAZO = [[[-0.4262,-0.4043],[-0.3838,-0.3917],[-0.3721,-0.3857],[-0.3619,-0.3740],[-0.3571,-0.3555],[-0.3545,-0.3533],[-0.3340,-0.3744],[-0.3252,-0.3774],[-0.3135,-0.3774],[-0.2207,-0.3527],[-0.2041,-0.3454],[-0.1875,-0.3463],[-0.1602,-0.3394],[-0.1406,-0.3283],[-0.1221,-0.3371],[-0.1084,-0.3397],[-0.0830,-0.3371],[-0.0547,-0.3237],[-0.0371,-0.3075],[-0.0192,-0.3262],[-0.0010,-0.3295],[0.0430,-0.3215],[0.0566,-0.3160],[0.0680,-0.3047],[0.0717,-0.2969],[0.0735,-0.2842],[0.0762,-0.2828],[0.1074,-0.3071],[0.1338,-0.3152],[0.1611,-0.3123],[0.1875,-0.2994],[0.2041,-0.3070],[0.2178,-0.3073],[0.2559,-0.3009],[0.2744,-0.2896],[0.2930,-0.2971],[0.3242,-0.2905],[0.3359,-0.2855],[0.3672,-0.2982],[0.4053,-0.2983],[0.4229,-0.2932],[0.4492,-0.2779],[0.4669,-0.2588],[0.4786,-0.2363],[0.4868,-0.2070],[0.4869,-0.1748],[0.4829,-0.1602],[0.4716,-0.1426],[0.4752,-0.1221],[0.4634,-0.0986],[0.4424,-0.0848],[0.4092,-0.0783],[0.3770,-0.0837],[0.3467,-0.0989],[0.3249,-0.0781],[0.3318,-0.0107],[0.3799,0.0654],[0.4089,0.1172],[0.4105,0.1289],[0.4076,0.1396],[0.4028,0.1475],[0.3936,0.1547],[0.3848,0.1577],[0.3721,0.1578],[0.2988,0.1486],[0.2869,0.1416],[0.2705,0.1152],[0.2666,0.1124],[0.2520,0.1336],[0.2393,0.1420],[0.2285,0.1433],[0.1895,0.1346],[0.1777,0.1394],[0.1641,0.1395],[0.0996,0.1252],[0.0156,0.0971],[0.0107,0.0976],[0.0000,0.1091],[-0.0107,0.1137],[-0.0234,0.1135],[-0.0703,0.1017],[-0.0869,0.0935],[-0.0996,0.0699],[-0.1250,0.0852],[-0.1562,0.0911],[-0.1748,0.0903],[-0.1992,0.0851],[-0.2197,0.0784],[-0.2529,0.0622],[-0.2734,0.0745],[-0.2741,0.0781],[-0.2705,0.0830],[-0.2479,0.1055],[-0.2314,0.1151],[-0.2168,0.1193],[-0.1973,0.1193],[-0.1523,0.1101],[-0.1152,0.1101],[-0.0752,0.1181],[-0.0312,0.1366],[0.0098,0.1634],[0.0483,0.1992],[0.0713,0.2290],[0.0910,0.2656],[0.0988,0.2891],[0.1030,0.3135],[0.1002,0.3506],[0.0909,0.3789],[0.0833,0.3926],[0.0723,0.4079],[0.0586,0.4214],[0.0420,0.4327],[0.0215,0.4416],[-0.0225,0.4496],[-0.0674,0.4456],[-0.1172,0.4311],[-0.1582,0.4112],[-0.2008,0.3828],[-0.2285,0.3583],[-0.2566,0.3271],[-0.2747,0.2998],[-0.2933,0.2588],[-0.3000,0.2275],[-0.2976,0.1895],[-0.3014,0.1729],[-0.3066,0.1624],[-0.3174,0.1483],[-0.3934,0.0723],[-0.4021,0.0547],[-0.4254,0.0352],[-0.4404,0.0187],[-0.4619,-0.0122],[-0.4760,-0.0420],[-0.4827,-0.0635],[-0.4867,-0.0898],[-0.4840,-0.1211],[-0.4708,-0.1572],[-0.4491,-0.1875],[-0.4678,-0.2072],[-0.4735,-0.2236],[-0.4672,-0.3711],[-0.4623,-0.3857],[-0.4531,-0.3970],[-0.4385,-0.4045],[-0.4268,-0.4046]],[[-0.4316,-0.4122],[-0.4463,-0.4099],[-0.4582,-0.4023],[-0.4686,-0.3896],[-0.4741,-0.3750],[-0.4806,-0.2188],[-0.4763,-0.2061],[-0.4595,-0.1865],[-0.4802,-0.1562],[-0.4922,-0.1172],[-0.4923,-0.0742],[-0.4881,-0.0547],[-0.4787,-0.0283],[-0.4635,0.0000],[-0.4455,0.0244],[-0.4297,0.0415],[-0.4092,0.0587],[-0.3984,0.0782],[-0.3389,0.1365],[-0.3125,0.1670],[-0.3055,0.1855],[-0.3068,0.2334],[-0.2975,0.2695],[-0.2790,0.3076],[-0.2500,0.3475],[-0.2070,0.3875],[-0.1529,0.4229],[-0.1094,0.4421],[-0.0547,0.4552],[-0.0156,0.4564],[0.0283,0.4471],[0.0596,0.4298],[0.0723,0.4189],[0.0886,0.3984],[0.1004,0.3750],[0.1072,0.3535],[0.1098,0.3379],[0.1099,0.3115],[0.1032,0.2773],[0.0886,0.2432],[0.0652,0.2080],[0.0381,0.1783],[0.0059,0.1515],[-0.0391,0.1243],[-0.0811,0.1086],[-0.1113,0.1033],[-0.1562,0.1033],[-0.2012,0.1122],[-0.2197,0.1109],[-0.2412,0.1012],[-0.2631,0.0781],[-0.2520,0.0713],[-0.2080,0.0905],[-0.1670,0.0986],[-0.1504,0.0986],[-0.1289,0.0944],[-0.1025,0.0810],[-0.0926,0.0977],[-0.0811,0.1062],[-0.0322,0.1193],[-0.0176,0.1218],[-0.0059,0.1203],[0.0049,0.1150],[0.0156,0.1053],[0.0918,0.1307],[0.1680,0.1478],[0.1904,0.1427],[0.2246,0.1504],[0.2373,0.1504],[0.2539,0.1426],[0.2666,0.1254],[0.2809,0.1465],[0.2940,0.1553],[0.3662,0.1646],[0.3867,0.1646],[0.3965,0.1619],[0.4072,0.1541],[0.4131,0.1453],[0.4173,0.1338],[0.4171,0.1182],[0.4092,0.0996],[0.3389,-0.0139],[0.3331,-0.0742],[0.3486,-0.0891],[0.3662,-0.0794],[0.3828,-0.0741],[0.4199,-0.0713],[0.4395,-0.0755],[0.4555,-0.0830],[0.4719,-0.0977],[0.4817,-0.1182],[0.4802,-0.1416],[0.4910,-0.1602],[0.4951,-0.1875],[0.4912,-0.2227],[0.4838,-0.2441],[0.4709,-0.2656],[0.4589,-0.2793],[0.4365,-0.2947],[0.4082,-0.3051],[0.3721,-0.3066],[0.3535,-0.3024],[0.3359,-0.2938],[0.3232,-0.2988],[0.2979,-0.3039],[0.2842,-0.3027],[0.2754,-0.2990],[0.2593,-0.3076],[0.2207,-0.3142],[0.2021,-0.3140],[0.1875,-0.3082],[0.1592,-0.3206],[0.1309,-0.3220],[0.1074,-0.3154],[0.0801,-0.2969],[0.0731,-0.3105],[0.0596,-0.3230],[0.0459,-0.3283],[0.0117,-0.3350],[-0.0107,-0.3364],[-0.0186,-0.3347],[-0.0283,-0.3291],[-0.0381,-0.3193],[-0.0539,-0.3320],[-0.0801,-0.3439],[-0.0938,-0.3468],[-0.1123,-0.3467],[-0.1396,-0.3379],[-0.1582,-0.3467],[-0.1914,-0.3545],[-0.2031,-0.3533],[-0.2217,-0.3608],[-0.3174,-0.3857],[-0.3369,-0.3815],[-0.3516,-0.3695],[-0.3592,-0.3838],[-0.3711,-0.3943],[-0.4186,-0.4102],[-0.4311,-0.4121]],[[-0.3770,-0.1729],[-0.4004,-0.1702],[-0.4170,-0.1648],[-0.4336,-0.1548],[-0.4448,-0.1436],[-0.4564,-0.1260],[-0.4636,-0.1064],[-0.4651,-0.0674],[-0.4597,-0.0439],[-0.4519,-0.0244],[-0.4288,0.0127],[-0.3926,0.0476],[-0.3604,0.0654],[-0.3281,0.0738],[-0.2979,0.0724],[-0.2765,0.0635],[-0.2578,0.0449],[-0.2217,0.0648],[-0.1875,0.0763],[-0.1729,0.0791],[-0.1455,0.0792],[-0.1240,0.0712],[-0.1131,0.0605],[-0.1071,0.0479],[-0.1053,0.0391],[-0.1070,0.0146],[-0.1129,-0.0029],[-0.1214,-0.0176],[-0.1494,-0.0479],[-0.1230,-0.0698],[-0.1176,-0.0566],[-0.0808,0.0781],[-0.0779,0.0859],[-0.0732,0.0890],[-0.0166,0.1036],[-0.0117,0.1019],[0.0391,-0.0338],[0.0921,0.0430],[0.0352,0.0243],[0.0303,0.0247],[0.0240,0.0732],[0.0241,0.0859],[0.0283,0.0900],[0.1064,0.1151],[0.1572,0.1270],[0.1719,0.1280],[0.1753,0.1211],[0.1787,0.1206],[0.2314,0.1318],[0.2354,0.1296],[0.2596,0.0732],[0.2627,0.0707],[0.2942,0.1270],[0.3027,0.1379],[0.3701,0.1466],[0.3809,0.1462],[0.3816,0.1406],[0.2947,0.0068],[0.2863,-0.0723],[0.2822,-0.0764],[0.2139,-0.0884],[0.2107,-0.0869],[0.2248,0.0039],[0.1758,0.1024],[0.1729,0.0605],[0.1186,-0.0205],[0.1865,-0.0043],[0.1851,-0.0586],[0.1836,-0.0713],[0.1807,-0.0741],[0.1221,-0.0848],[0.0635,-0.1001],[0.0575,-0.0996],[0.0566,-0.0908],[0.0537,-0.0901],[-0.0059,-0.1067],[-0.0098,-0.1036],[-0.0204,-0.0615],[-0.0254,-0.0613],[-0.0581,-0.0703],[-0.0667,-0.1084],[-0.0703,-0.1130],[-0.1094,-0.1175],[-0.1094,-0.1117],[-0.0994,-0.0967],[-0.1006,-0.0923],[-0.1543,-0.1378],[-0.2080,-0.0838],[-0.2104,-0.0908],[-0.2105,-0.1299],[-0.2129,-0.1336],[-0.2731,-0.1504],[-0.2756,-0.1475],[-0.2756,-0.1367],[-0.2741,-0.1289],[-0.2655,-0.1152],[-0.2676,-0.1088],[-0.2910,-0.1368],[-0.3193,-0.1570],[-0.3496,-0.1688],[-0.3762,-0.1729]],[[-0.0127,-0.2872],[-0.0166,-0.2867],[-0.0177,-0.2842],[-0.0176,-0.1328],[0.0186,-0.1181],[0.0518,-0.1143],[0.0654,-0.1171],[0.0771,-0.1230],[0.0876,-0.1338],[0.0947,-0.1515],[0.1085,-0.1299],[0.1230,-0.1182],[0.1416,-0.1118],[0.1582,-0.1117],[0.1689,-0.1145],[0.1811,-0.1221],[0.1924,-0.1348],[0.2012,-0.1525],[0.2023,-0.1133],[0.2412,-0.1040],[0.2458,-0.1074],[0.2705,-0.1511],[0.2726,-0.1016],[0.3174,-0.0935],[0.3223,-0.0946],[0.3238,-0.0986],[0.3200,-0.1514],[0.3213,-0.1626],[0.3303,-0.1387],[0.3407,-0.1230],[0.3584,-0.1067],[0.3750,-0.0973],[0.3975,-0.0908],[0.4150,-0.0908],[0.4340,-0.0967],[0.4489,-0.1084],[0.4491,-0.1123],[0.4238,-0.1474],[0.4199,-0.1478],[0.4033,-0.1407],[0.3926,-0.1422],[0.3770,-0.1535],[0.3682,-0.1709],[0.3669,-0.1816],[0.3721,-0.1970],[0.3809,-0.2034],[0.3916,-0.2036],[0.3994,-0.1993],[0.4007,-0.1953],[0.3828,-0.1975],[0.3782,-0.1943],[0.3818,-0.1602],[0.4463,-0.1493],[0.4530,-0.1504],[0.4548,-0.1816],[0.4469,-0.2119],[0.4365,-0.2276],[0.4170,-0.2440],[0.3867,-0.2533],[0.3672,-0.2520],[0.3545,-0.2478],[0.3428,-0.2402],[0.3325,-0.2295],[0.3226,-0.2109],[0.3193,-0.1984],[0.3176,-0.2080],[0.3186,-0.2412],[0.3162,-0.2451],[0.2793,-0.2517],[0.2500,-0.2072],[0.2496,-0.2549],[0.2031,-0.2638],[0.2004,-0.2598],[0.2031,-0.2002],[0.1940,-0.2285],[0.1823,-0.2471],[0.1738,-0.2553],[0.1514,-0.2676],[0.1270,-0.2687],[0.1046,-0.2588],[0.0967,-0.2509],[0.0878,-0.2363],[0.0824,-0.2148],[0.0910,-0.1973],[0.0947,-0.1747],[0.0877,-0.1934],[0.0752,-0.2109],[0.0586,-0.2241],[0.0312,-0.2357],[0.0312,-0.2762],[-0.0118,-0.2871]],[[-0.2734,-0.3206],[-0.2782,-0.3203],[-0.2796,-0.3174],[-0.2784,-0.2549],[-0.2806,-0.1816],[-0.2792,-0.1738],[-0.2725,-0.1701],[-0.2451,-0.1610],[-0.2393,-0.1612],[-0.2129,-0.2049],[-0.2116,-0.1553],[-0.1670,-0.1449],[-0.1638,-0.1514],[-0.1664,-0.1846],[-0.1650,-0.1968],[-0.1521,-0.1670],[-0.1328,-0.1453],[-0.1089,-0.1338],[-0.0830,-0.1325],[-0.0637,-0.1406],[-0.0570,-0.1475],[-0.0574,-0.1514],[-0.0781,-0.1863],[-0.0967,-0.1808],[-0.1113,-0.1879],[-0.1183,-0.1992],[-0.1222,-0.2119],[-0.1223,-0.2246],[-0.1195,-0.2344],[-0.1156,-0.2402],[-0.1084,-0.2438],[-0.0996,-0.2426],[-0.0929,-0.2354],[-0.0947,-0.2329],[-0.1094,-0.2365],[-0.1133,-0.2334],[-0.1135,-0.2051],[-0.1104,-0.2007],[-0.0576,-0.1871],[-0.0498,-0.1888],[-0.0471,-0.2197],[-0.0498,-0.2422],[-0.0588,-0.2646],[-0.0695,-0.2783],[-0.0889,-0.2907],[-0.1055,-0.2949],[-0.1162,-0.2950],[-0.1377,-0.2876],[-0.1485,-0.2793],[-0.1572,-0.2676],[-0.1670,-0.2444],[-0.1650,-0.2900],[-0.1670,-0.2940],[-0.2031,-0.3034],[-0.2334,-0.2605],[-0.2316,-0.3066],[-0.2402,-0.3113],[-0.2727,-0.3203]],[[-0.3650,-0.1641],[-0.3369,-0.1567],[-0.3117,-0.1436],[-0.2883,-0.1230],[-0.2753,-0.1055],[-0.3027,-0.0714],[-0.3154,-0.0859],[-0.3282,-0.0957],[-0.3535,-0.1055],[-0.3643,-0.1055],[-0.3750,-0.1020],[-0.3857,-0.0928],[-0.3896,-0.0857],[-0.3923,-0.0762],[-0.3908,-0.0518],[-0.3844,-0.0352],[-0.3721,-0.0158],[-0.3535,-0.0003],[-0.3320,0.0062],[-0.3174,0.0037],[-0.2998,-0.0073],[-0.2680,0.0420],[-0.2724,0.0508],[-0.2793,0.0562],[-0.3008,0.0656],[-0.3262,0.0670],[-0.3535,0.0601],[-0.3730,0.0510],[-0.3915,0.0391],[-0.4199,0.0119],[-0.4346,-0.0081],[-0.4448,-0.0273],[-0.4542,-0.0518],[-0.4582,-0.0703],[-0.4582,-0.0928],[-0.4554,-0.1074],[-0.4445,-0.1318],[-0.4353,-0.1436],[-0.4189,-0.1557],[-0.4033,-0.1619],[-0.3906,-0.1647],[-0.3652,-0.1641]],[[0.0682,-0.0908],[0.1768,-0.0663],[0.1797,-0.0132],[0.1074,-0.0341],[0.1033,-0.0322],[0.1663,0.0645],[0.1664,0.1191],[0.1533,0.1187],[0.0830,0.1006],[0.0312,0.0820],[0.0361,0.0330],[0.1015,0.0557],[0.1074,0.0568],[0.1093,0.0547],[0.0466,-0.0371],[0.0650,-0.0908],[0.0674,-0.0910]],[[-0.4414,-0.3624],[-0.4451,-0.3613],[-0.4467,-0.3574],[-0.4469,-0.2803],[-0.4500,-0.2129],[-0.4484,-0.2080],[-0.4092,-0.1885],[-0.3789,-0.1815],[-0.3623,-0.1832],[-0.3496,-0.1884],[-0.3428,-0.1934],[-0.3330,-0.2071],[-0.3312,-0.1836],[-0.2881,-0.1713],[-0.2830,-0.1758],[-0.2841,-0.3213],[-0.3281,-0.3347],[-0.3320,-0.3328],[-0.3327,-0.2754],[-0.3277,-0.2441],[-0.3291,-0.2341],[-0.3339,-0.2568],[-0.3468,-0.2783],[-0.3701,-0.2985],[-0.3965,-0.3096],[-0.3971,-0.3477],[-0.4405,-0.3623]],[[0.2279,-0.0781],[0.2793,-0.0684],[0.2874,0.0098],[0.3698,0.1377],[0.3060,0.1309],[0.2653,0.0576],[0.2617,0.0554],[0.2551,0.0645],[0.2295,0.1234],[0.1816,0.1136],[0.1910,0.0889],[0.2320,0.0059],[0.2190,-0.0742],[0.2197,-0.0787],[0.2275,-0.0783]],[[-0.2627,-0.1406],[-0.2178,-0.1272],[-0.2172,-0.0840],[-0.2148,-0.0706],[-0.2004,-0.0801],[-0.1543,-0.1284],[-0.1105,-0.0898],[-0.1553,-0.0536],[-0.1602,-0.0469],[-0.1347,-0.0225],[-0.1178,0.0049],[-0.1137,0.0176],[-0.1124,0.0342],[-0.1181,0.0547],[-0.1299,0.0659],[-0.1484,0.0721],[-0.1777,0.0708],[-0.2100,0.0617],[-0.2507,0.0400],[-0.2539,0.0244],[-0.2609,0.0107],[-0.2662,-0.0938],[-0.2587,-0.1055],[-0.2584,-0.1162],[-0.2674,-0.1338],[-0.2671,-0.1406],[-0.2637,-0.1410]],[[0.3824,-0.2461],[0.3984,-0.2436],[0.4111,-0.2387],[0.4316,-0.2215],[0.4453,-0.1943],[0.4480,-0.1631],[0.4466,-0.1582],[0.4424,-0.1574],[0.3887,-0.1666],[0.3863,-0.1729],[0.3863,-0.1885],[0.4092,-0.1869],[0.4119,-0.1885],[0.4119,-0.1924],[0.4051,-0.2041],[0.3983,-0.2090],[0.3844,-0.2119],[0.3721,-0.2070],[0.3652,-0.1999],[0.3600,-0.1836],[0.3613,-0.1680],[0.3685,-0.1523],[0.3781,-0.1416],[0.3955,-0.1337],[0.4072,-0.1337],[0.4209,-0.1383],[0.4401,-0.1113],[0.4307,-0.1030],[0.4121,-0.0979],[0.3936,-0.0991],[0.3799,-0.1032],[0.3595,-0.1152],[0.3414,-0.1348],[0.3279,-0.1680],[0.3265,-0.1934],[0.3310,-0.2109],[0.3438,-0.2314],[0.3643,-0.2435],[0.3818,-0.2463]],[[0.2150,-0.2549],[0.2428,-0.2480],[0.2432,-0.1850],[0.2497,-0.1904],[0.2822,-0.2439],[0.3100,-0.2393],[0.3105,-0.1914],[0.3169,-0.1035],[0.3105,-0.1018],[0.2791,-0.1074],[0.2798,-0.1709],[0.2773,-0.1751],[0.2707,-0.1689],[0.2393,-0.1123],[0.2109,-0.1177],[0.2086,-0.1201],[0.2085,-0.1475],[0.2121,-0.1895],[0.2073,-0.2529],[0.2090,-0.2555],[0.2148,-0.2549]],[[-0.0906,-0.1084],[-0.0740,-0.1055],[-0.0667,-0.0713],[-0.0625,-0.0634],[-0.0234,-0.0534],[-0.0176,-0.0526],[-0.0149,-0.0547],[-0.0029,-0.0972],[0.0488,-0.0830],[-0.0166,0.0947],[-0.0693,0.0823],[-0.0725,0.0791],[-0.1136,-0.0703],[-0.0940,-0.0869],[-0.0916,-0.0957],[-0.0962,-0.1074],[-0.0908,-0.1085]],[[-0.2700,-0.3115],[-0.2398,-0.3027],[-0.2393,-0.2392],[-0.2346,-0.2422],[-0.2012,-0.2943],[-0.1768,-0.2892],[-0.1733,-0.2861],[-0.1744,-0.2021],[-0.1724,-0.1543],[-0.2051,-0.1619],[-0.2039,-0.2246],[-0.2061,-0.2286],[-0.2118,-0.2236],[-0.2409,-0.1709],[-0.2461,-0.1692],[-0.2727,-0.1797],[-0.2728,-0.3086],[-0.2705,-0.3116]],[[-0.1080,-0.2871],[-0.0889,-0.2824],[-0.0716,-0.2695],[-0.0595,-0.2480],[-0.0553,-0.2314],[-0.0550,-0.2188],[-0.0552,-0.1982],[-0.0576,-0.1950],[-0.1025,-0.2056],[-0.1066,-0.2109],[-0.1064,-0.2272],[-0.0850,-0.2244],[-0.0835,-0.2305],[-0.0879,-0.2420],[-0.0947,-0.2485],[-0.1055,-0.2518],[-0.1162,-0.2490],[-0.1249,-0.2402],[-0.1290,-0.2285],[-0.1291,-0.2100],[-0.1210,-0.1885],[-0.1113,-0.1785],[-0.1016,-0.1741],[-0.0811,-0.1765],[-0.0653,-0.1494],[-0.0732,-0.1433],[-0.0859,-0.1393],[-0.1064,-0.1408],[-0.1246,-0.1484],[-0.1426,-0.1662],[-0.1557,-0.1924],[-0.1610,-0.2227],[-0.1570,-0.2500],[-0.1465,-0.2703],[-0.1318,-0.2824],[-0.1201,-0.2866],[-0.1084,-0.2872]],[[-0.2510,0.1132],[-0.2555,0.1143],[-0.2525,0.1201],[-0.2201,0.1533],[-0.2568,0.1826],[-0.3050,0.1387],[-0.3111,0.1387],[-0.2965,0.1611],[-0.2888,0.1807],[-0.2874,0.1924],[-0.2913,0.2217],[-0.2891,0.2380],[-0.2793,0.2332],[-0.1313,0.1211],[-0.1338,0.1178],[-0.1543,0.1189],[-0.2109,0.1278],[-0.2285,0.1237],[-0.2509,0.1133]],[[0.3154,0.2098],[0.2842,0.2110],[0.2627,0.2190],[0.2510,0.2268],[0.2391,0.2373],[0.2245,0.2578],[0.2159,0.2852],[0.2159,0.3105],[0.2200,0.3271],[0.2278,0.3438],[0.2351,0.3535],[0.2549,0.3719],[0.2832,0.3839],[0.3174,0.3851],[0.3457,0.3758],[0.3584,0.3673],[0.3767,0.3477],[0.3852,0.3320],[0.3899,0.3164],[0.3899,0.2793],[0.3771,0.2490],[0.3654,0.2344],[0.3506,0.2228],[0.3320,0.2139],[0.3162,0.2100]],[[0.3128,0.2168],[0.3391,0.2246],[0.3563,0.2363],[0.3696,0.2510],[0.3831,0.2822],[0.3845,0.3037],[0.3814,0.3193],[0.3755,0.3350],[0.3628,0.3535],[0.3379,0.3713],[0.3125,0.3784],[0.2930,0.3783],[0.2695,0.3715],[0.2461,0.3552],[0.2332,0.3379],[0.2255,0.3193],[0.2230,0.3066],[0.2243,0.2803],[0.2376,0.2510],[0.2572,0.2314],[0.2861,0.2183],[0.3125,0.2167]],[[-0.3544,-0.0977],[-0.3408,-0.0940],[-0.3252,-0.0846],[-0.3037,-0.0603],[-0.2734,-0.0936],[-0.2679,0.0127],[-0.2593,0.0322],[-0.2607,0.0380],[-0.2988,-0.0183],[-0.3027,-0.0182],[-0.3086,-0.0103],[-0.3193,-0.0035],[-0.3359,-0.0017],[-0.3564,-0.0117],[-0.3711,-0.0276],[-0.3829,-0.0508],[-0.3852,-0.0752],[-0.3803,-0.0879],[-0.3758,-0.0928],[-0.3672,-0.0971],[-0.3545,-0.0977]],[[-0.4379,-0.3535],[-0.4034,-0.3428],[-0.4034,-0.3047],[-0.3779,-0.2942],[-0.3596,-0.2812],[-0.3467,-0.2655],[-0.3394,-0.2500],[-0.3366,-0.2246],[-0.3450,-0.2021],[-0.3545,-0.1941],[-0.3643,-0.1900],[-0.3779,-0.1887],[-0.3926,-0.1912],[-0.4219,-0.2017],[-0.4426,-0.2139],[-0.4385,-0.3537]],[[-0.0071,-0.2783],[0.0246,-0.2705],[0.0245,-0.2295],[0.0469,-0.2219],[0.0668,-0.2090],[0.0794,-0.1924],[0.0874,-0.1689],[0.0874,-0.1582],[0.0832,-0.1416],[0.0783,-0.1338],[0.0693,-0.1267],[0.0576,-0.1225],[0.0439,-0.1212],[0.0049,-0.1304],[-0.0120,-0.1396],[-0.0106,-0.2764],[-0.0078,-0.2786]],[[-0.1520,0.1279],[-0.2825,0.2246],[-0.2806,0.1885],[-0.2836,0.1699],[-0.2615,0.1904],[-0.2568,0.1917],[-0.2100,0.1550],[-0.2106,0.1514],[-0.2285,0.1323],[-0.2002,0.1349],[-0.1631,0.1273],[-0.1523,0.1274]],[[0.1430,-0.2617],[0.1553,-0.2582],[0.1670,-0.2512],[0.1857,-0.2285],[0.1964,-0.1953],[0.1965,-0.1689],[0.1887,-0.1436],[0.1738,-0.1257],[0.1562,-0.1186],[0.1445,-0.1186],[0.1309,-0.1227],[0.1142,-0.1348],[0.1023,-0.1523],[0.1006,-0.1904],[0.0905,-0.2148],[0.0905,-0.2207],[0.1002,-0.2432],[0.1113,-0.2544],[0.1299,-0.2619],[0.1426,-0.2619]],[[-0.3227,-0.3252],[-0.2902,-0.3145],[-0.2901,-0.1826],[-0.2920,-0.1797],[-0.3242,-0.1888],[-0.3246,-0.2129],[-0.3208,-0.2354],[-0.3257,-0.2822],[-0.3258,-0.3232],[-0.3232,-0.3255]],[[-0.2129,-0.0381],[-0.2161,-0.0352],[-0.2145,0.0156],[-0.1865,0.0259],[-0.1748,0.0257],[-0.1669,0.0195],[-0.1650,0.0068],[-0.1680,-0.0029],[-0.1826,-0.0215],[-0.2123,-0.0381]],[[0.1455,-0.2220],[0.1309,-0.2200],[0.1240,-0.2128],[0.1200,-0.1992],[0.1212,-0.1826],[0.1242,-0.1748],[0.1298,-0.1660],[0.1387,-0.1598],[0.1465,-0.1582],[0.1553,-0.1621],[0.1612,-0.1709],[0.1642,-0.1836],[0.1631,-0.1992],[0.1589,-0.2109],[0.1522,-0.2188],[0.1464,-0.2217]],[[-0.0537,-0.0285],[-0.0578,-0.0283],[-0.0590,-0.0234],[-0.0439,0.0407],[-0.0410,0.0400],[-0.0383,0.0322],[-0.0250,-0.0195],[-0.0283,-0.0236],[-0.0532,-0.0283]],[[-0.3975,-0.2737],[-0.4037,-0.2725],[-0.4054,-0.2510],[-0.4054,-0.2334],[-0.4004,-0.2287],[-0.3809,-0.2261],[-0.3744,-0.2295],[-0.3699,-0.2393],[-0.3704,-0.2471],[-0.3776,-0.2607],[-0.3969,-0.2734]],[[-0.2043,-0.0264],[-0.1936,-0.0205],[-0.1788,-0.0068],[-0.1720,0.0098],[-0.1736,0.0166],[-0.1777,0.0189],[-0.2023,0.0137],[-0.2078,0.0088],[-0.2077,-0.0254],[-0.2051,-0.0267]],[[0.0273,-0.2003],[0.0240,-0.1973],[0.0240,-0.1602],[0.0254,-0.1574],[0.0332,-0.1558],[0.0449,-0.1559],[0.0508,-0.1591],[0.0540,-0.1641],[0.0547,-0.1719],[0.0531,-0.1807],[0.0469,-0.1899],[0.0283,-0.2002]],[[0.1439,-0.2148],[0.1542,-0.2031],[0.1573,-0.1865],[0.1519,-0.1689],[0.1475,-0.1665],[0.1406,-0.1668],[0.1342,-0.1719],[0.1297,-0.1807],[0.1282,-0.2021],[0.1338,-0.2133],[0.1436,-0.2150]],[[-0.0481,-0.0195],[-0.0332,-0.0156],[-0.0420,0.0157],[-0.0495,-0.0137],[-0.0488,-0.0197]],[[-0.3934,-0.2637],[-0.3850,-0.2578],[-0.3795,-0.2500],[-0.3783,-0.2373],[-0.3838,-0.2328],[-0.3965,-0.2351],[-0.3984,-0.2383],[-0.3971,-0.2627],[-0.3965,-0.2645],[-0.3936,-0.2638]],[[0.0325,-0.1904],[0.0420,-0.1844],[0.0473,-0.1738],[0.0449,-0.1643],[0.0342,-0.1630],[0.0308,-0.1660],[0.0322,-0.1905]]];

/** r45 · MONTA la constelación de palas: un plano tangente a la bóveda
 *  (15 × 11,25 m a 45 m del centro, SIEMPRE en el cielo) con su lienzo
 *  512×384 y el estado del bolígrafo de luz: espera → trazo (el contorno
 *  se dibuja poco a poco, naciendo en un punto) → sostén → fundido →
 *  espera (y vuelve a nacer en OTRO lugar al azar). El repintado del
 *  lienzo ocurre SÓLO durante el trazado; el sostén y el fundido son
 *  opacity del material (cero lienzo, cero subidas de textura). */
function montaConstelacion() {
  const cv = hallCanvas(512, 384);
  const tex = new THREE.CanvasTexture(cv);
  try { tex.colorSpace = THREE.SRGBColorSpace; } catch { /* */ }
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(15, 11.25),
    new THREE.MeshBasicMaterial({
      map: tex, transparent: true, opacity: 0, depthWrite: false,
      fog: false, blending: THREE.AdditiveBlending,
    }),
  );
  mesh.visible = false;
  mesh.renderOrder = 1;            // sobre la bóveda (opaca), bajo el resto
  // — los trazos a coordenadas DE LIENZO + longitudes acumuladas —
  const CX = 256, CY = 182, S = 330;      // centro y escala (px por unidad)
  const trazos = [];
  let total = 0;
  for (const s of ARCANO_PALAS_TRAZO) {
    const pts = [];
    const cum = [0];
    for (let i = 0; i < s.length; i++) {
      pts.push({ x: CX + s[i][0] * S, y: CY - s[i][1] * S });
      if (i) cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
    }
    trazos.push({ pts, cum, len: cum[cum.length - 1], ini: total });
    total += cum[cum.length - 1];
  }
  // — las TRES PASADAS de glow (la firma del búho: halo→cuerpo→alma) —
  mesh.userData.conste = {
    cv, tex, trazos, total,
    pasadas: [
      { lw: 3.4, col: 'rgba(56,140,255,0.32)', blur: 13 },
      { lw: 2.1, col: 'rgba(120,205,255,0.78)', blur: 5 },
      { lw: 1.0, col: 'rgba(226,246,255,0.5)', blur: 0 },
    ],
    estado: 'espera', t: 2.4, prog: 0, opMax: 0.62,
  };
  return mesh;
}

/** MONTA el espacio arcano. Devuelve el Group con userData.arcono = {
 *  motas, cometas, suelo, buho: {mesh, glints, hover}, panel: {mesh, cv,
 *  tex}, flechaL/R: {mesh, cv, tex}, pop (0..1 materialización) } — c12
 *  lo añade a la escena OCULTO y lo gobierna (r40: enterArcano lo PLANTA
 *  sobre los pies del anfitrión mirando hacia donde mira él — nunca más
 *  «la galería a la espalda»). Centro del grupo = los pies del jugador:
 *  el búho flota delante, la galería debajo, el cielo y el suelo
 *  infinito alrededor. TODA pieza con fog:false: la niebla de la cancha
 *  jamás alcanza la estancia infinita. */
export function montarArcano(base) {
  const g = new THREE.Group();
  const vbase = (typeof base === 'string' && base) ? base : 'assets/hall/';
  // — BÓVEDA CELESTE (esfera invertida; r40: azul oscuro LISO, sin imagen) —
  const bovCv = hallCanvas(1024, 512);
  pintaBoveda(bovCv);
  const bovTex = new THREE.CanvasTexture(bovCv);
  try { bovTex.colorSpace = THREE.SRGBColorSpace; } catch { /* */ }
  const boveda = new THREE.Mesh(
    new THREE.SphereGeometry(58, 40, 24),
    new THREE.MeshBasicMaterial({ map: bovTex, side: THREE.BackSide, fog: false }),
  );
  g.add(boveda);
  // — EL SUELO (r41): negro, con la matriz fina de losetas y rellenos
  //    azules que nacen y mueren completamente al azar —
  const suelo = montaSueloArcano();
  g.add(suelo);
  // — MOTAS azules que serpentean —
  const motas = montaMotas(240);
  g.add(motas);
  // — r45 · LA CONSTELACIÓN DE PALAS: el contorno del arte del dueño
  //    trazado a bolígrafo en el cielo (nace, se dibuja, se funde y
  //    reaparece en otro lugar al azar) —
  const conste = montaConstelacion();
  g.add(conste);
  // — COMETAS ocasionales (cabeza + halo alargado) —
  const headTex = spriteRadial(2, 'rgba(240,250,255,0.98)', 'rgba(130,210,255,0.6)', 'rgba(60,140,255,0)');
  const haloTex = spriteRadial(6, 'rgba(120,200,255,0.5)', 'rgba(70,150,255,0.22)', 'rgba(30,80,200,0)');
  const cometas = [];
  for (let i = 0; i < 3; i++) {
    const head = new THREE.Sprite(new THREE.SpriteMaterial({
      map: headTex, transparent: true, opacity: 0.95, fog: false,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: haloTex, transparent: true, opacity: 0.5, fog: false,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    head.scale.setScalar(0.5);
    halo.scale.set(3.4, 1.1, 1);
    head.visible = halo.visible = false;
    g.add(head); g.add(halo);
    cometas.push({ head, halo, on: false, t: 0, dur: 0, p: new THREE.Vector3(), q: new THREE.Vector3(), prox: 2 + i * 4 });
  }
  // — EL BÚHO presente (grande, flotando delante del anfitrión) —
  const buhoCv = hallCanvas(512, 342);
  drawArcanoBuho(buhoCv);
  const buhoTex = new THREE.CanvasTexture(buhoCv);
  try { buhoTex.colorSpace = THREE.SRGBColorSpace; buhoTex.anisotropy = 4; } catch { /* */ }
  const buhoMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.32, 0.88),
    new THREE.MeshBasicMaterial({ map: buhoTex, transparent: true, fog: false }));
  buhoMesh.position.set(0, 2.28, -2.55);
  g.add(buhoMesh);
  try {
    new THREE.TextureLoader().load(vbase + 'arcano.png', (t) => {
      try {
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 4;
        buhoMesh.material.map = t;
        buhoMesh.material.needsUpdate = true;
        buhoTex.dispose();
      } catch { /* seguimos con el vectorial */ }
    }, undefined, () => { /* */ });
  } catch { /* */ }
  const glintTex = spriteRadial(2, 'rgba(235,250,255,0.95)', 'rgba(120,210,255,0.55)', 'rgba(60,140,255,0)');
  const buhoGlints = [];
  for (const rel of [[0.452, 0.392], [0.557, 0.376]]) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glintTex, transparent: true, opacity: 0.35, fog: false,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    sp.scale.setScalar(0.115);
    sp.position.set((rel[0] - 0.5) * 1.32, (0.5 - rel[1]) * 0.88, 0.02);
    buhoMesh.add(sp);
    buhoGlints.push(sp);
  }
  // — r43 · EL LETRERO DE SALIDA: «Salir/Exit» sobre el búho cuando el
  //  anfitrión lo APUNTA — letras azules con el halo azulón, la misma
  //  estética del búho. El texto lo rellena c12 con el idioma vivo
  //  (drawArcanoSalir + T('arcono_salir')); updateArcanoFx lo funde con
  //  el hover y le da un leve ascenso al aparecer. —
  const salCv = hallCanvas(256, 96);
  drawArcanoSalir(salCv, 'Salir');
  const salTex = new THREE.CanvasTexture(salCv);
  try { salTex.colorSpace = THREE.SRGBColorSpace; salTex.anisotropy = 4; } catch { /* */ }
  const salMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.1725),
    new THREE.MeshBasicMaterial({
      map: salTex, transparent: true, opacity: 0,
      depthWrite: false, fog: false,
    }));
  salMesh.position.set(0, 2.95, -2.55);       // justo ENCIMA del búho
  salMesh.visible = false;
  g.add(salMesh);
  const salHalo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: spriteRadial(6, 'rgba(120,200,255,0.5)', 'rgba(73,182,255,0.22)', 'rgba(30,80,200,0)'),
    transparent: true, opacity: 0, fog: false, color: 0x49b6ff,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }));
  salHalo.scale.set(0.62, 0.30, 1);
  salHalo.position.set(0, 2.95, -2.56);
  salHalo.visible = false;
  g.add(salHalo);
  // — LA GALERÍA: panel + dos flechas con glow —
  // r41 · DOS lienzos: «cv» (la ficha COMPLETA que pinta c12) y «holo»
  // (el lienzo VIVO de la textura) — updateArcanoFx COMPONE el
  // holograma cv→holo mientras la ficha se materializa; condensada,
  // copia exacta y a dormir (el holograma es el nacimiento, no el aire).
  const panCv = hallCanvas(1024, 700);
  drawArcanoPanel(panCv, { titulo: '· · ·' });
  const panHolo = hallCanvas(1024, 700);
  panHolo.getContext('2d').drawImage(panCv, 0, 0);
  const panTex = new THREE.CanvasTexture(panHolo);
  try { panTex.colorSpace = THREE.SRGBColorSpace; panTex.anisotropy = 4; } catch { /* */ }
  const panMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.46, 1.0),
    new THREE.MeshBasicMaterial({ map: panTex, transparent: true, fog: false }));
  panMesh.position.set(0, 1.32, -2.35);
  g.add(panMesh);
  const flechas = {};
  for (const k of ['L', 'R']) {
    const cv = hallCanvas(128, 128);
    drawArcanoFlecha(cv, k);
    const tex = new THREE.CanvasTexture(cv);
    try { tex.colorSpace = THREE.SRGBColorSpace; } catch { /* */ }
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(0.20, 0.20),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, fog: false }));
    // r41 · INTERCAMBIADOS (petición del dueño: «las flechas están al
    // revés, intercambiar los iconos»): los GLIFOS se descruzan en
    // drawArcanoFlecha — en la IZQUIERDA vive el ‹ (retrocede) y en la
    // DERECHA el › (avanza); antes la izquierda mostraba › y la derecha ‹.
    mesh.position.set(k === 'L' ? -0.93 : 0.93, 1.32, -2.35);
    g.add(mesh);
    flechas[k] = { mesh, cv, tex, hover: false };
  }
  // — r45 · EL CANDADO FLOTANTE de los bloqueados: GRUPO propio DELANTE
  // del medallón, ahora en la ZONA SUPERIOR IZQUIERDA del icono (petición
  // literal del dueño: «colocándolos en la zona superior izquierda del
  // icono de superpoder») con SU IMAGEN (candado.png, silueta negra del
  // artista sobre transparencia — la misma carga perezosa del búho, con
  // el glifo vectorial de respaldo) y el MISMO HALO ROJO pulsante
  // (sprite aditivo que updateArcanoFx respira): la silueta negra recorta
  // contra el resplandor rojo y el bloqueo se lee vivo y claro. —
  const candCv = hallCanvas(128, 128);
  drawArcanoCandado(candCv);
  const candTex = new THREE.CanvasTexture(candCv);
  try { candTex.colorSpace = THREE.SRGBColorSpace; candTex.anisotropy = 4; } catch { /* */ }
  const candMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.16),
    new THREE.MeshBasicMaterial({ map: candTex, transparent: true, depthWrite: false, fog: false }));
  try {
    new THREE.TextureLoader().load(vbase + 'candado.png', (t) => {
      try {
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 4;
        candMesh.material.map = t;      // la IMAGEN del dueño manda
        candMesh.material.needsUpdate = true;
        candTex.dispose();              // el vectorial era el respaldo
      } catch { /* seguimos con el vectorial */ }
    }, undefined, () => { /* sin imagen: glifo vectorial de la casa */ });
  } catch { /* */ }
  const candHalo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: spriteRadial(4, 'rgba(255,150,120,0.92)', 'rgba(255,45,30,0.4)', 'rgba(255,0,0,0)'),
    transparent: true, opacity: 0.5, fog: false, color: 0xff4530,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }));
  candHalo.scale.setScalar(0.32);       // halo algo mayor: la silueta negra recorta contra él
  const candado = new THREE.Group();
  candado.add(candHalo);
  candado.add(candMesh);
  // r47 · EL CANDADO SE ADELANTA (petición del dueño: «debe estar un poco
  // por encima del plano del icono, pues a veces se ve y otras no»): el
  // grupo pasa de z −2,28 a −2,20 (15 cm delante del panel −2,35) y los
  // dos hijos llevan renderOrder FIJO (halo 6 · candado 7 — tras panel y
  // constelación): el sort de transparentes ya no puede tragárselo — se
  // ve SIEMPRE, en cualquier ángulo y re-entrada.
  candHalo.renderOrder = 6;
  candMesh.renderOrder = 7;
  // r45 · zona SUPERIOR IZQUIERDA del medallón del icono (centro del
  // icono en el lienzo 1024×700: x 152, y 236, r 96 → 3D x −0.512,
  // y 1.483, radio 0.137; el candado se apoya en el borde, a −45°)
  candado.position.set(-0.612, 1.585, -2.20);   // r47 · delante del panel, esquina sup-izq
  candado.visible = false;
  g.add(candado);
  g.userData.arcono = {
    motas, cometas, suelo, buho: { mesh: buhoMesh, glints: buhoGlints, hover: false },
    panel: { mesh: panMesh, cv: panCv, tex: panTex, holo: panHolo }, flechas,
    candado: { grupo: candado, halo: candHalo }, pop: 1, holoSem: 0,
    conste,   // r45 · la constelación de palas de la bóveda
    // r43 · el letrero de salida («Salir/Exit» sobre el búho al apuntarlo)
    salir: { mesh: salMesh, halo: salHalo, cv: salCv, tex: salTex, op: 0 },
  };
  return g;
}

/** ANIMA el espacio arcano (sólo se llama con la estancia encendida):
 *  motas que serpentean, cometas ocasionales con su halo, el búho que
 *  flota con sus ojos en HALO azul↔rojo (r41), las losetas del suelo
 *  naciendo y muriendo AL AZAR (r41), el candado flotante con su halo
 *  rojo pulsante (r41) y la MATERIALIZACIÓN HOLOGRÁFICA del panel (r41:
 *  bandas que viajan, disolución, barrido y parpadeo de encendido). */
export function updateArcanoFx(g, dt, now) {
  const A = g.userData && g.userData.arcono;
  if (!A) return;
  // — motas: serpenteo suave (posición base + dos senos por punto) —
  const pos = A.motas.geometry.attributes.position;
  const { base, fase, n } = A.motas.userData;
  for (let i = 0; i < n; i++) {
    const f = fase[i];
    pos.array[i * 3] = base[i * 3] + Math.sin(now * 0.35 + f) * 0.55;
    pos.array[i * 3 + 1] = base[i * 3 + 1] + Math.sin(now * 0.5 + f * 1.7) * 0.4;
    pos.array[i * 3 + 2] = base[i * 3 + 2] + Math.cos(now * 0.28 + f * 0.9) * 0.55;
  }
  pos.needsUpdate = true;
  // — r43 · SUELO: DESTELLOS que dibujan la trama fina — corredores que
  //  nacen en un borde del suelo, recorren UNA línea de la retícula
  //  (fila en X o columna en Z — cruces de 90°, ambos sentidos) y dejan
  //  tras de sí la ESTELA = la propia línea, que aguanta ~5 s y se
  //  desvanece. Las celdas que el destello atraviesa pueden encender su
  //  RELLENO azul (la misma envolvente nacer→aguantar→morir de la r41).
  //  Repintado: clear + los trazos y rellenos vivos (~100 ops máx en
  //  512²: el mismo orden de coste que la capa de rellenos de la r41).
  const S = A.suelo && A.suelo.userData;
  if (S) {
    // — 1 · nace un destello (temporizador propio, tope ~9 vivos) —
    S.prox -= dt;
    if (S.prox <= 0 && S.trazos.length < 9) {
      S.prox = 0.30 + Math.random() * 0.70;
      const ax = Math.random() < 0.5 ? 'x' : 'z';      // 90°: filas y columnas
      const dir = Math.random() < 0.5 ? 1 : -1;        // ambos sentidos
      const ln = (Math.random() * (S.N + 1)) | 0;      // línea de la retícula (0..N)
      S.trazos.push({
        ax, ln, dir,
        head: dir > 0 ? 0 : S.N,          // parte de UN fondo («partiendo de
        desde: dir > 0 ? 0 : S.N,         //  un fondo y llegando al otro»)
        vel: 2.4 + Math.random() * 3.6,   // losetas/s (1,5 m por loseta)
        t: 0, col: S.mezcla(),
        ultima: -1,                       // última celda cruzada (rellenos)
      });
    }
    // — 2 · repintado del lienzo: clear + rellenos + trazos vivos —
    const fx = S.tCtx, pw = S.paso, L = S.N;
    fx.clearRect(0, 0, 512, 512);
    // — rellenos: celdas azules de la banda del dueño (nacen→aguantan→
    //   mueren; una celda ya encendida no se re-enciende) —
    for (let k = S.lit.length - 1; k >= 0; k--) {
      const q = S.lit[k];
      q.t += dt;
      const fin = q.tIn + q.hold + q.tOut;
      if (q.t >= fin) { S.lit.splice(k, 1); continue; }
      const aV = q.t < q.tIn ? q.t / q.tIn
        : q.t < q.tIn + q.hold ? 1
        : 1 - (q.t - q.tIn - q.hold) / q.tOut;
      const dx = (q.i + 0.5) / L * 2 - 1, dy = (q.j + 0.5) / L * 2 - 1;
      const rr = Math.min(1, Math.sqrt(dx * dx + dy * dy) / 1.02);
      const al = q.alfa * aV * (1 - rr * rr);
      if (al <= 0.012) continue;
      fx.globalAlpha = al;
      fx.fillStyle = 'rgb(' + q.col[0] + ',' + q.col[1] + ',' + q.col[2] + ')';
      fx.fillRect(q.i * pw + 1.5, q.j * pw + 1.5, pw - 3, pw - 3);
    }
    fx.globalAlpha = 1;
    // — trazos: la ESTELA dibujada (origen → cabeza) + cabeza brillante —
    fx.lineCap = 'round';
    for (let k = S.trazos.length - 1; k >= 0; k--) {
      const q = S.trazos[k];
      q.t += dt;
      const corriendo = q.head !== (q.dir > 0 ? L : 0);
      if (corriendo) {
        q.head += q.vel * q.dir * dt;
        if (q.dir > 0) q.head = Math.min(L, q.head);
        else q.head = Math.max(0, q.head);
        // rellenos: la celda que acabo de cruzar puede encenderse
        const cel = Math.min(L - 1, Math.floor(q.head));
        if (cel !== q.ultima && S.lit.length < 70 && Math.random() < 0.20) {
          q.ultima = cel;
          S.lit.push({
            i: q.ax === 'x' ? cel : Math.max(0, q.ln - 1),
            j: q.ax === 'x' ? Math.max(0, q.ln - 1) : cel,
            t: 0, tIn: 0.3 + Math.random() * 0.5, hold: 1.2 + Math.random() * 2.4,
            tOut: 0.7 + Math.random() * 1.1,
            col: S.mezcla(), alfa: 0.38 + Math.random() * 0.34,
          });
        }
      }
      const vida = q.t;                          // desde el NACIMIENTO
      const dibujo = Math.abs(q.desde - q.head) / q.vel;   // s de trazado
      const resto = vida - dibujo;               // s desde que COMPLETÓ
      if (!corriendo && resto >= S.VIDA) { S.trazos.splice(k, 1); continue; }
      // viñeta del horizonte: hacia el borde del suelo se disuelve
      const cn = q.ln / L * 2 - 1;
      const fVi = 1 - Math.min(1, Math.abs(cn) / 1.02) ** 2;
      // alpha: 0,50 mientras corre y aguanta; fundido final de 0,9 s
      let al = 0.50 * fVi;
      if (!corriendo && resto > S.VIDA - 0.9) {
        al *= Math.max(0, (S.VIDA - resto) / 0.9);
      }
      if (al <= 0.012) continue;
      const hx = q.ax === 'x' ? q.head * pw : q.ln * pw;
      const hy = q.ax === 'x' ? q.ln * pw : q.head * pw;
      const ox = q.ax === 'x' ? q.desde * pw : q.ln * pw;
      const oy = q.ax === 'x' ? q.ln * pw : q.desde * pw;
      // la ESTELA = la línea fina de la trama (0,8 px ≈ 5 cm reales)
      fx.globalAlpha = al;
      fx.strokeStyle = 'rgba(' + q.col[0] + ',' + q.col[1] + ',' + q.col[2] + ',0.9)';
      fx.lineWidth = 0.8;
      fx.beginPath();
      fx.moveTo(ox, oy);
      fx.lineTo(hx, hy);
      fx.stroke();
      // la CABEZA: el destello que viaja (aditivo, blanco-azul)
      if (corriendo) {
        fx.globalCompositeOperation = 'lighter';
        fx.globalAlpha = Math.min(1, al * 2.1);
        fx.fillStyle = '#bfe0ff';
        fx.beginPath();
        fx.arc(hx, hy, 1.6, 0, Math.PI * 2);
        fx.fill();
        fx.globalCompositeOperation = 'source-over';
      }
    }
    fx.globalAlpha = 1;
    S.tex.needsUpdate = true;
  }
  // — cometas: cruce lejano cada tanto; el halo azul queda tras la cabeza —
  for (const c of A.cometas) {
    if (!c.on) {
      c.prox -= dt;
      if (c.prox <= 0) {
        c.on = true;
        c.t = 0;
        c.dur = 5.5 + Math.random() * 3.5;
        const lado = Math.random() < 0.5 ? -1 : 1;
        c.p.set(lado * 30, 7 + Math.random() * 9, -22 - Math.random() * 16);
        c.q.set(-lado * 60, -1.5 - Math.random() * 2, (Math.random() - 0.5) * 6);
        c.head.visible = c.halo.visible = true;
      }
      continue;
    }
    c.t += dt;
    const k = c.t / c.dur;
    if (k >= 1) {
      c.on = false;
      c.prox = 4 + Math.random() * 8;
      c.head.visible = c.halo.visible = false;
      continue;
    }
    c.head.position.set(c.p.x + c.q.x * k, c.p.y + c.q.y * k, c.p.z + c.q.z * k);
    c.halo.position.copy(c.head.position);
    c.halo.position.x -= Math.sign(c.q.x) * 0.9;   // el halo, tras la cabeza
    const fade = Math.sin(Math.min(1, k) * Math.PI);
    c.head.material.opacity = 0.95 * fade;
    c.halo.material.opacity = 0.5 * fade;
  }
  // — r45 · LA CONSTELACIÓN DE PALAS: un bolígrafo de luz traza en el
  //  cielo el contorno de palas.png (34 polilíneas r47 del arte NUEVO
  //  del dueño — logo CRAZY PING PONG macizo trazado a contorno; la r45
  //  encadenadas como pluma humana): nace en un punto, va perfilando las
  //  líneas con el glow del búho hasta completarlo, aguanta, se funde y
  //  unos segundos más tarde nace en OTRO lugar al azar de la bóveda —
  //  como una constelación, muy sutil. Lienzo vivo SÓLO durante el
  //  trazado; sostén y fundido viven de la opacity del material. —
  const CN = A.conste && A.conste.userData.conste;
  if (CN) {
    CN.t -= dt;
    if (CN.estado === 'espera') {
      if (CN.t <= 0) {
        // nace en OTRO lugar: azimut amplio alrededor del frente, altura
        // 18°..47°, escala y giro en plano al azar (constelación viva)
        const az = (Math.random() - 0.5) * 3.1;
        const el = 0.32 + Math.random() * 0.52;
        const rr = 45;
        A.conste.position.set(
          Math.sin(az) * Math.cos(el) * rr,
          Math.sin(el) * rr,
          -Math.cos(az) * Math.cos(el) * rr);
        A.conste.lookAt(0, 1.55, 0);
        A.conste.rotateZ((Math.random() - 0.5) * 1.0);
        A.conste.scale.setScalar(0.85 + Math.random() * 0.5);
        CN.cv.getContext('2d').clearRect(0, 0, 512, 384);
        CN.tex.needsUpdate = true;
        CN.estado = 'trazo';
        CN.prog = 0;
        A.conste.visible = true;
        A.conste.material.opacity = CN.opMax;
      }
    } else if (CN.estado === 'trazo') {
      CN.prog += dt * (CN.total / 7.2);   // el dibujo completo en ~7,2 s
      const cx = CN.cv.getContext('2d');
      cx.clearRect(0, 0, 512, 384);
      cx.lineCap = 'round';
      cx.lineJoin = 'round';
      let punta = null;
      for (const tr of CN.trazos) {
        if (tr.ini >= CN.prog) break;
        const frac = Math.min(1, (CN.prog - tr.ini) / tr.len);
        if (frac <= 0) break;
        // — hasta dónde llega la pluma EN ESTE trazo —
        const objetivo = frac * tr.len;
        let k = 1;
        while (k < tr.cum.length && tr.cum[k] < objetivo) k++;
        if (k >= tr.pts.length) k = tr.pts.length - 1;
        const l0 = tr.cum[k - 1], l1 = tr.cum[k];
        const fSeg = l1 > l0 ? (objetivo - l0) / (l1 - l0) : 0;
        const px = tr.pts[k - 1].x + (tr.pts[k].x - tr.pts[k - 1].x) * fSeg;
        const py = tr.pts[k - 1].y + (tr.pts[k].y - tr.pts[k - 1].y) * fSeg;
        // — el trazo VISIBLE con las tres pasadas del búho —
        for (const pa of CN.pasadas) {
          cx.shadowColor = pa.col;
          cx.shadowBlur = pa.blur;
          cx.strokeStyle = pa.col;
          cx.lineWidth = pa.lw;
          cx.beginPath();
          cx.moveTo(tr.pts[0].x, tr.pts[0].y);
          for (let i = 1; i < k; i++) cx.lineTo(tr.pts[i].x, tr.pts[i].y);
          cx.lineTo(px, py);
          cx.stroke();
        }
        cx.shadowBlur = 0;
        punta = { x: px, y: py };   // la pluma se queda en el trazo vivo
        if (frac < 1) break;
      }
      // — la punta del bolígrafo: chispa aditiva blanco-azul —
      if (punta) {
        cx.globalCompositeOperation = 'lighter';
        cx.shadowColor = 'rgba(150,215,255,0.95)';
        cx.shadowBlur = 9;
        cx.fillStyle = '#eaf6ff';
        cx.beginPath();
        cx.arc(punta.x, punta.y, 2.6, 0, Math.PI * 2);
        cx.fill();
        cx.shadowBlur = 0;
        cx.globalCompositeOperation = 'source-over';
      }
      CN.tex.needsUpdate = true;
      if (CN.prog >= CN.total) { CN.estado = 'sosten'; CN.t = 2.4; }
    } else if (CN.estado === 'sosten') {
      if (CN.t <= 0) { CN.estado = 'fundido'; CN.t = 2.3; }
    } else if (CN.estado === 'fundido') {
      A.conste.material.opacity = CN.opMax * Math.max(0, CN.t / 2.3);
      if (CN.t <= 0) {
        A.conste.visible = false;
        CN.cv.getContext('2d').clearRect(0, 0, 512, 384);
        CN.tex.needsUpdate = true;
        CN.estado = 'espera';
        // «unos segundos más tarde… cada 10 segundos o algo más»
        CN.t = 3.5 + Math.random() * 4.5;
      }
    }
  }
  // — búho: flote + yaw vivo + ojos latiendo (más presente que en el hall) —
  const B = A.buho;
  B.mesh.position.y = 2.28 + Math.sin(now * 0.7) * 0.05;
  B.mesh.rotation.y = Math.sin(now * 0.4) * 0.06;
  if (B.glints.length === 2) {
    // r41 · HALO EN LOS OJOS que OSCILA de AZUL a ROJO (y de vuelta —
    // petición del dueño): el color del destello viaja la banda azul
    // búho ↔ rojo bloqueo con un seno lento y el halo RESPIRA con la
    // misma fase (escala del sprite).
    const tO = 0.5 + 0.5 * Math.sin(now * 1.5);
    _arcoOjoT.copy(_ARCO_OJO_A).lerp(_ARCO_OJO_B, tO);
    B.glints[0].material.color.copy(_arcoOjoT);
    _arcoOjoT.copy(_ARCO_OJO_A).lerp(_ARCO_OJO_B, Math.min(1, tO + 0.07));
    B.glints[1].material.color.copy(_arcoOjoT);
    B.glints[0].material.opacity = 0.5 + Math.sin(now * 2.4) * 0.22;
    B.glints[1].material.opacity = 0.5 + Math.sin(now * 2.4 + 2.1) * 0.22;
    const scO = 0.115 + tO * 0.05;
    B.glints[0].scale.setScalar(scO);
    B.glints[1].scale.setScalar(scO * 1.03);
  }
  const tgtB = B.hover ? 1.1 : 1.0;
  const curB = B.mesh.scale.x || 1;
  B.mesh.scale.setScalar(curB + (tgtB - curB) * Math.min(1, dt * 10));
  // — r43 · EL LETRERO «Salir/Exit»: se funde con el hover del búho
  //  (aparece al apuntarlo, se retira al apartar la mano) con un leve
  //  ascenso al entrar — la misma respuesta viva que las flechas. —
  const SA = A.salir;
  if (SA) {
    SA.op += ((B.hover ? 1 : 0) - SA.op) * Math.min(1, dt * 9);
    if (SA.op < 0.015) {
      if (SA.mesh.visible) { SA.mesh.visible = false; SA.halo.visible = false; }
      SA.op = 0;
    } else {
      SA.mesh.visible = true;
      SA.halo.visible = true;
      SA.mesh.material.opacity = SA.op;
      SA.halo.material.opacity = 0.62 * SA.op;
      const sc = 0.94 + SA.op * 0.06;
      SA.mesh.scale.setScalar(sc);
      SA.mesh.position.y = 2.95 + SA.op * 0.045;
      SA.halo.position.y = SA.mesh.position.y;
    }
  }
  // — r41 · galería: MATERIALIZACIÓN HOLOGRÁFICA — la ficha se FORMA
  //  (bandas que viajan, disolución de motas, barrido de condensación,
  //  parpadeo de encendido y aberración que se cierra); al terminar,
  //  copia exacta y la textura duerme (coste cero en reposo). —
  if (A.pop < 1) {
    A.pop = Math.min(1, A.pop + dt * 0.92);
    A.holoSem++;
    const P = A.panel;
    arconoHoloFrame(P.holo.getContext('2d'), P.cv, A.pop, A.holoSem);
    P.tex.needsUpdate = true;
    if (A.pop >= 1) {
      const c2 = P.holo.getContext('2d');
      c2.clearRect(0, 0, P.holo.width, P.holo.height);
      c2.drawImage(P.cv, 0, 0);
      P.tex.needsUpdate = true;
    }
    const e = 1 + Math.sin(A.pop * Math.PI) * 0.045;   // leve respiración
    P.mesh.scale.setScalar((0.945 + A.pop * 0.055) * e);
  }
  // — r41 · candado flotante: HALO ROJO pulsante (bloqueo vivo y claro) —
  const CD = A.candado;
  if (CD && CD.grupo.visible) {
    const pC = 0.5 + 0.5 * Math.sin(now * 3.2);
    CD.halo.scale.setScalar(0.24 + pC * 0.13);
    CD.halo.material.opacity = 0.34 + pC * 0.5;
  }
  // — flechas: hover agranda, y el glow late suave —
  for (const k of ['L', 'R']) {
    const F = A.flechas[k];
    const tgt = F.hover ? 1.22 : 1.0;
    const cur = F.mesh.scale.x || 1;
    F.mesh.scale.setScalar(cur + (tgt - cur) * Math.min(1, dt * 12));
  }
}

export function createChampRoom(game) {
  let builtFor = null;        // activeId del set construido ('' = sala limpia)
  let set = null;             // { cfg, texs, disposables }
  let variantTint = 0xffffff; // teñido multiplicativo de la variante activa
  const loader = new THREE.TextureLoader();
  let maxAniso = 4;
  try { maxAniso = game.renderer.capabilities.getMaxAnisotropy(); } catch { /* */ }
  const WALL_MAP = ['left', 'right', 'back', 'front'];   // = orden de wallMats
  const KEYS = ['floor', 'ceil', 'left', 'right', 'back', 'front'];

  /* v3.6.29 · ARTE POR DEFECTO DEL PARTIDO (ronda 37, FASE 31) — el
   * escenario del PARTIDO (Match) viste SIEMPRE las seis caras con el
   * arte del artista (assets/partido/, dimensiones canónicas de
   * createRoom: frente/fondo 6,10×2,85 · laterales 7,90×2,85 · suelo y
   * techo 6,10×7,90 — mapeo 1:1 sin distorsión). PETICIÓN EXPRÉS del
   * dueño: las paredes IZQUIERDA y DERECHA comparten imagen
   * (izquierda.jpg — UNA sola carga, DOS materiales). El campeonato
   * activo con «room» propio GANA clave a clave; las claves que falte
   * visten el arte del partido. Carga a prueba de fallos: sin imagen
   * (file://), ese plano conserva su color del tema y el juego SIGUE. */
  const defaultTexs = {};
  const applyDefaultTex = (tex) => {
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = maxAniso;
    return tex;
  };
  for (const k2 of ['floor', 'ceil', 'back', 'front']) {
    const f = { floor: 'suelo', ceil: 'techo', back: 'fondo', front: 'frente' }[k2];
    loader.load('assets/partido/' + f + '.jpg', (tex) => {
      try { defaultTexs[k2] = applyDefaultTex(tex); } catch { /* */ }
    }, undefined, () => { /* file:// o arte ausente: color del tema */ });
  }
  // izquierda.jpg UNA SOLA carga para las DOS paredes laterales
  loader.load('assets/partido/izquierda.jpg', (tex) => {
    try {
      applyDefaultTex(tex);
      defaultTexs.left = tex;
      defaultTexs.right = tex;   // MISMA imagen en ambas laterales
    } catch { /* */ }
  }, undefined, () => { /* */ });

  /* r38 (v3.6.134) · EL ARTE DEL SALÓN DE LA PARTIDA — tercera fuente de
   * la cadena: campeonato → SALÓN DEL ANFITRIÓN → arte por defecto.
   * Petición del dueño: «las partidas se realizan en el hall que tenga
   * configurado el anfitrión, tanto para las modalidades contra la IA como
   * en el modo multijugador». Las salas de campeonato (las 5 traen room)
   * conservan SU identidad (champTex gana); fuera de campeonato la cancha
   * viste las 6 fichas del salón (mismos nombres/proporciones: la caja es
   * LA MISMA — patrón createHall). game.hallBasePartido() resuelve QUÉ
   * salón manda (local = el tuyo; online invitado = el del anfitrión
   * viajado en hp.hv/hallv); carga perezosa + a prueba de fallos: si una
   * ficha no llega, ese plano cae a la fuente siguiente y el juego SIGUE. */
  let hallSet = null;        // { base, texs, disposables }
  let hallBuiltFor = null;   // base construida ('' = sin salón → nada)
  const HALL_FICHAS = {
    floor: 'suelo.jpg', ceil: 'techo.jpg', left: 'izquierda.jpg',
    right: 'derecha.jpg', back: 'fondo.jpg', front: 'frente.jpg',
  };
  /** Construye (carga perezosa) el vestido del salón «base» ('' = quita). */
  function buildHallFor(base) {
    if (hallSet) {
      for (const d of hallSet.disposables) { try { d.dispose(); } catch { /* */ } }
      hallSet = null;
    }
    hallBuiltFor = base;
    if (!base) return;                        // sin salón: cadena sin él
    const mine = { base, texs: {}, disposables: [] };
    hallSet = mine;
    for (const key of KEYS) {
      loader.load(base + HALL_FICHAS[key], (tex) => {
        if (hallSet !== mine) { try { tex.dispose(); } catch { /* */ } return; }
        try {
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.anisotropy = maxAniso;
          mine.texs[key] = tex;
          mine.disposables.push(tex);
        } catch { /* el arte NUNCA rompe el juego */ }
      }, undefined, () => { /* file:// o arte ausente: fuente siguiente */ });
    }
  }

  const ud = () => (game.roomGroup ? game.roomGroup.userData : null);

  /** Quita mapas y colores forzados y re-aplica el tema del jugador. */
  function clearRoom() {
    const U = ud();
    if (U) {
      const mats = [];
      if (U.floorMat) mats.push(U.floorMat);
      if (U.ceilMat) mats.push(U.ceilMat);
      if (U.wallMats) mats.push(...U.wallMats);
      for (const m of mats) {
        if (m && m.map) { m.map = null; m.needsUpdate = true; }
      }
    }
    variantTint = 0xffffff;
    if (U) { try { game.applyTheme(game.theme); } catch { /* */ } }
  }

  function disposeSet() {
    clearRoom();
    if (set) for (const d of set.disposables) { try { d.dispose(); } catch { /* */ } }
    set = null;
  }

  /** Construye (con carga perezosa) el decorado del campeonato «id». */
  function buildFor(id) {
    disposeSet();
    builtFor = id;
    const mod = id ? game.champs.moduleIfLoaded(id) : null;
    const cfg = (mod && mod.room) ? mod.room : null;
    if (!cfg) return;                        // campeonato sin «room»: sala clásica
    const base = 'championships/' + id + '/';
    const mine = { cfg, texs: {}, disposables: [] };
    set = mine;
    for (const key of KEYS) {
      const file = cfg[key];
      if (!file) continue;
      loader.load(base + file, (tex) => {
        if (set !== mine) { try { tex.dispose(); } catch { /* */ } return; }  // set ya sustituido
        try {
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.anisotropy = maxAniso;
          mine.texs[key] = tex;
          mine.disposables.push(tex);
        } catch { /* el decorado NUNCA rompe el juego */ }
      }, undefined, () => { /* file:// o arte ausente: ese plano queda con su color */ });
    }
  }

  /** Mood por etapa (módulo): teñido multiplicativo + arte alternativo. */
  function useVariant(key) {
    let tint = 0xffffff;
    try {
      const v = (set && set.cfg && set.cfg.variants && set.cfg.variants[key]) || null;
      if (v && v.tint) tint = v.tint;
    } catch { /* */ }
    variantTint = tint;
  }

  /** Refuerzo por frame (barato e idempotente): mapas + blanco/tinte + */
  /** complementos de la sala clásica ocultos mientras haya arte. v3.6.29:
   *  el arte EFECTIVO por cara es el del campeonato activo (si trae) o el
   *  arte por defecto del partido — la cancha nunca vuelve a estar desnuda.
   *  r38: y ENTRE el campeonato y el por defecto, el SALÓN DEL ANFITRIÓN
   *  (la partida se disputa en su hall — fuera de campeonato). */
  function update() {
    const activeId = (game.champs && game.champs.activeId) || '';
    if (activeId !== builtFor) buildFor(activeId);
    const U = ud();
    if (!U) return;
    // r38 · el salón de la partida SOLO fuera de campeonato (la mesa
    // ocupada por un torneo manda: su decorado no se mezcla con el hall).
    let enSalon = false;
    try { enSalon = !(game.mesaOcupada && game.mesaOcupada()); } catch { /* */ }
    let hb = '';
    try {
      hb = (enSalon && typeof game.hallBasePartido === 'function')
        ? (game.hallBasePartido() || '') : '';
    } catch { /* */ }
    if (hb !== hallBuiltFor) buildHallFor(hb);
    const champTex = (k) => (set && set.texs[k]) || null;
    const hallTex = (k) => (hallSet && hallSet.texs[k]) || null;
    const eff = (k) => champTex(k) || hallTex(k) || defaultTexs[k] || null;
    const anyArt = KEYS.some(eff);
    if (anyArt) {
      const tint = variantTint;
      if (U.floorMat) {
        const t2 = eff('floor');
        if (t2 && U.floorMat.map !== t2) {
          U.floorMat.map = t2; U.floorMat.needsUpdate = true;
        }
        if (t2) U.floorMat.color.set(champTex('floor') ? tint : 0xffffff);
      }
      if (U.ceilMat) {
        const t2 = eff('ceil');
        if (t2 && U.ceilMat.map !== t2) {
          U.ceilMat.map = t2; U.ceilMat.needsUpdate = true;
        }
        if (t2) U.ceilMat.color.set(champTex('ceil') ? tint : 0xffffff);
      }
      const wm = U.wallMats || [];
      for (let i = 0; i < wm.length && i < 4; i++) {
        const m = wm[i];
        if (!m) continue;
        const t2 = eff(WALL_MAP[i]);
        if (t2 && m.map !== t2) { m.map = t2; m.needsUpdate = true; }
        if (t2) m.color.set(champTex(WALL_MAP[i]) ? tint : 0xffffff);
      }
      // complementos del núcleo que chocarían con el arte:
      if (U.grid) U.grid.visible = !eff('floor');
      if (U.panels) for (const p of U.panels) p.visible = !eff('ceil');
      if (U.strips) for (const s of U.strips) s.visible = !(eff('left') || eff('right'));
    } else {
      // sin NINGÚN arte (file:// sin assets): la sala clásica de siempre
      if (U.grid) U.grid.visible = true;
      if (U.panels) for (const p of U.panels) p.visible = true;
      if (U.strips) for (const s of U.strips) s.visible = true;
    }
  }

  return {
    /** Campeonato del decorado construido ('' = sala sin arte). */
    get builtFor() { return builtFor || ''; },
    /** Claves de arte ya cargadas del set activo (lectura en tests). */
    get loadedKeys() { return set ? Object.keys(set.texs) : []; },
    /** v3.6.29: claves del arte POR DEFECTO del partido ya cargadas. */
    get defaultKeys() { return Object.keys(defaultTexs); },
    useVariant,
    update,
  };
}

export function createBounceMarkers() {
  const pool = [];
  for (let i = 0; i < 4; i++) {
    const m = new THREE.Mesh(
      new THREE.RingGeometry(0.02, 0.036, 20),
      new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide,
      }),
    );
    m.rotation.x = -Math.PI / 2;
    m.userData.t = 1;
    m.visible = false;
    m.renderOrder = 3;
    pool.push(m);
  }
  return pool;
}

export function createScoreboard() {
  const group = new THREE.Group();
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;

  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(1.7, 0.85),
    new THREE.MeshBasicMaterial({ map: tex }),
  );
  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(1.76, 0.91, 0.04),
    new THREE.MeshStandardMaterial({ color: 0x101316, roughness: 0.6 }),
  );
  frame.position.z = -0.025;
  group.add(frame);
  group.add(panel);
  group.position.set(0, 1.95, DIMS.roomFrontZ + 0.9);

  let last = '';
  const update = (d) => {
    const key = d.mode === 'survival'
      ? `S|${d.rally}|${d.rallyes}|${d.best}|${d.server}|${d.message}|${d.oppLabel ?? ''}`
      : `${d.player}|${d.ai}|${d.server}|${d.message}|${d.gamesPlayer}|${d.gamesAi}|${d.bestOf}|${d.netPing ?? ''}|${d.netDeg ? 1 : 0}|${d.oppLabel ?? ''}`;
    if (key === last) return;
    last = key;

    ctx.fillStyle = '#101418';
    ctx.fillRect(0, 0, 1024, 512);
    ctx.strokeStyle = '#2a3138';
    ctx.lineWidth = 10;
    ctx.strokeRect(10, 10, 1004, 492);

    ctx.textAlign = 'center';

    if (d.mode === 'survival') {
      // ---------- MODO SUPERVIVENCIA ----------
      ctx.fillStyle = '#e8b45a';
      ctx.font = '700 40px system-ui, sans-serif';
      ctx.fillText(T('sb_surv'), 512, 78);

      ctx.fillStyle = '#f2f4f6';
      ctx.font = '800 210px system-ui, sans-serif';
      ctx.fillText(String(d.rally || 0), 512, 315);

      ctx.fillStyle = '#c8ced4';
      ctx.font = '600 44px system-ui, sans-serif';
      ctx.fillText(T('sb_rally_hits'), 512, 390);

      ctx.fillStyle = '#8b949c';
      ctx.font = '500 40px system-ui, sans-serif';
      ctx.fillText(T('sb_rallies', { r: d.rallyes || 0, b: d.best || 0 }), 512, 452);
      tex.needsUpdate = true;
      return;
    }

    // v2.34: en ARCADE el cabecero del marcador pasa a ser el campeonato
    ctx.fillStyle = '#8b949c';
    ctx.font = '600 34px system-ui, sans-serif';
    ctx.fillText(d.oppLabel === 'clown'
      ? T('arc_title').split('').join(' ')
      : 'P I N G   P O N G   X R', 512, 70);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#e8b45a';
    ctx.font = '700 52px system-ui, sans-serif';
    ctx.fillText(T('sb_you'), 150, 170);
    if (d.server === 'player') {
      ctx.beginPath();
      ctx.arc(118, 152, 13, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.textAlign = 'right';
    ctx.fillStyle = '#7fb069';
    ctx.font = '700 52px system-ui, sans-serif';
    // v2.27: RIVAL en online (antes decía CPU siempre); v2.34: CLOWN en arcade
    ctx.fillText(d.oppLabel === 'clown'
      ? T('sb_clown')
      : T(d.oppLabel === 'rival' ? 'sb_rival' : 'sb_cpu'), 874, 170);
    if (d.server === 'ai') {
      ctx.beginPath();
      ctx.arc(906, 152, 13, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.textAlign = 'center';
    ctx.fillStyle = '#f2f4f6';
    ctx.font = '800 190px system-ui, sans-serif';
    ctx.fillText(`${d.player} : ${d.ai}`, 512, 340);

    // v3.6.29 · MEJOR DE 3: la serie de JUEGOS vive en el marcador — pucks
    // dorados (ganados) y huecos (por jugar) a los lados de «MEJOR DE 3»
    if (d.bestOf > 1) {
      const mk = (cx0, on) => {
        ctx.beginPath();
        ctx.arc(cx0, 388, 11, 0, Math.PI * 2);
        if (on) { ctx.fillStyle = '#e8b45a'; ctx.fill(); }
        else { ctx.strokeStyle = '#5a646e'; ctx.lineWidth = 3; ctx.stroke(); }
      };
      ctx.fillStyle = '#8b949c';
      ctx.font = '600 30px system-ui, sans-serif';
      ctx.fillText(T('sb_bo', { n: d.bestOf }), 512, 399);
      for (let i = 0; i < d.bestOf; i++) mk(360 - i * 36, i < (d.gamesPlayer || 0));
      for (let i = 0; i < d.bestOf; i++) mk(664 + i * 36, i < (d.gamesAi || 0));
    }

    ctx.fillStyle = '#c8ced4';
    // v2.18: el mensaje se auto-ajusta (fuente menor) en vez de recortarse a
    // ciegas: en el visor los textos largos se salían del marco del panel.
    let msg = d.message || '';
    if (msg.length > 72) msg = msg.slice(0, 71) + '…';
    let msgFs = 40;
    ctx.font = `500 ${msgFs}px system-ui, sans-serif`;
    while (msgFs > 22 && ctx.measureText(msg).width > 920) {
      msgFs -= 2;
      ctx.font = `500 ${msgFs}px system-ui, sans-serif`;
    }
    ctx.fillText(msg, 512, 440);

    // r79 · v2 · ICONO DE PING (calidad de conexión visible, spec §11):
    // punto de color + ms en la esquina superior derecha del marcador
    if (typeof d.netPing === 'number' && d.netPing >= 0) {
      const col = d.netPing < 80 ? '#7fb069' : d.netPing < 150 ? '#e8b45a' : '#ff6b57';
      const txt = d.netPing + ' ms' + (d.netDeg ? ' ·' : '');
      ctx.textAlign = 'right';
      ctx.font = '700 30px system-ui, sans-serif';
      ctx.fillStyle = col;
      ctx.fillText(txt, 996, 66);
      ctx.textAlign = 'center';
    }

    tex.needsUpdate = true;
  };

  update({ player: 0, ai: 0, server: 'player', message: '', mode: 'match', rally: 0, rallyes: 0, best: 0 });
  return { group, update };
}

function roundRectPath(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

/* =====================================================================
 *  PANEL DE AJUSTE DE PALA (r83 · AJUSTES › PALA — modo propio en VR)
 *  Panel FRONTAL head-locked, un poco por encima de la línea de ojos y
 *  SIN tapar la pala que se ajusta (está en la mano, más abajo). Canvas
 *  768×512 con: cabecera + chip de estado (passthrough o réplica 3D),
 *  TABLA VIVA de los 6 grados de libertad (X/Y/Z × posición/giro) con
 *  barras centradas en cero y la celda del eje en uso iluminada, leyenda
 *  de controles y pie de salida. Solo se redibuja cuando cambian valores.
 *  La API es la de siempre: update({ name, off, act?, pst? }).
 * ===================================================================== */
export function createCalibPanel() {
  const W = 768, H = 512;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const g2 = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  const mat = new THREE.MeshBasicMaterial({
    map: tex, transparent: true, opacity: 0.96, side: THREE.DoubleSide, depthWrite: false,
  });
  const group = new THREE.Group();
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.4133), mat);
  plane.renderOrder = 30;
  group.add(plane);

  // barras centradas en cero (negativo a la izquierda, positivo a la derecha)
  const barra = (x, y, w, h, v, vMax, activa, col) => {
    g2.fillStyle = 'rgba(255,255,255,0.10)';
    roundRectPath(g2, x, y, w, h, 4);
    g2.fill();
    g2.fillStyle = 'rgba(255,255,255,0.30)';
    g2.fillRect(x + w / 2 - 1, y - 2, 2, h + 4);
    const f = Math.max(-1, Math.min(1, v / vMax));
    const bw = Math.max(2, Math.abs(f) * (w / 2 - 2));
    g2.fillStyle = activa ? col : 'rgba(158,177,196,0.85)';
    if (f >= 0) roundRectPath(g2, x + w / 2 + 1, y, bw, h, 3);
    else roundRectPath(g2, x + w / 2 - 1 - bw, y, bw, h, 3);
    g2.fill();
  };

  function update(d) {
    const o = d.off;
    const act = d.act || null;
    const deg = (r) => ((r * 180) / Math.PI).toFixed(1);
    const mm = (m) => Math.round(m * 1000);
    const COL = { x: '#ff8787', y: '#8ce99a', z: '#74c0fc' };
    const AX = [
      ['X', 'px', 'rx', COL.x],
      ['Y', 'py', 'ry', COL.y],
      ['Z', 'pz', 'rz', COL.z],
    ];

    g2.clearRect(0, 0, W, H);
    g2.fillStyle = 'rgba(11,15,22,0.94)';
    g2.strokeStyle = 'rgba(232,180,90,0.9)';
    g2.lineWidth = 4;
    roundRectPath(g2, 8, 8, W - 16, H - 16, 26);
    g2.fill();
    g2.stroke();

    // cabecera: título + chip del agarre con nombre
    g2.textAlign = 'left';
    g2.textBaseline = 'alphabetic';
    g2.fillStyle = '#e8b45a';
    g2.font = '900 44px system-ui, sans-serif';
    g2.fillText('AJUSTE DE PALA', 36, 62);
    g2.font = '700 22px system-ui, sans-serif';
    const nomTxt = 'Agarre: ' + (d.name || 'Natural');
    const nomW = Math.min(360, g2.measureText(nomTxt).width + 34);
    g2.fillStyle = 'rgba(232,180,90,0.14)';
    roundRectPath(g2, W - 36 - nomW, 30, nomW, 40, 20);
    g2.fill();
    g2.strokeStyle = 'rgba(232,180,90,0.55)';
    g2.lineWidth = 2.5;
    roundRectPath(g2, W - 36 - nomW, 30, nomW, 40, 20);
    g2.stroke();
    g2.fillStyle = '#ffd257';
    g2.fillText(nomTxt, W - 36 - nomW + 17, 57);

    // chip de estado: passthrough real o réplica 3D de los mandos
    const pst = !!d.pst;
    const stTxt = pst ? '◉ PASSTHROUGH · mandos reales a la vista'
                      : '◇ RÉPLICA 3D · mando de referencia';
    g2.fillStyle = pst ? 'rgba(103,223,140,0.16)' : 'rgba(116,192,252,0.16)';
    roundRectPath(g2, 36, 84, 470, 40, 20);
    g2.fill();
    g2.fillStyle = pst ? '#8ce99a' : '#a5d8ff';
    g2.font = '800 22px system-ui, sans-serif';
    g2.fillText(stTxt, 54, 111);

    // tabla viva de los 6 grados de libertad
    const ty = 158, rh = 62, bx = 120, bw = 268;
    g2.font = '700 21px ui-monospace, monospace';
    g2.fillStyle = '#75828f';
    g2.fillText('POSICIÓN', bx, ty - 14);
    g2.fillText('GIRO', bx + bw + 130, ty - 14);
    for (const [ax, pk, rk, col] of AX) {
      const y = ty + (ax === 'X' ? 0 : ax === 'Y' ? rh : rh * 2);
      const aP = !!(act && act[pk]);
      const aR = !!(act && act[rk]);
      // fila activa: banda suave del color del eje
      if (aP || aR) {
        g2.fillStyle = col.replace(')', ',0.10)').replace('rgb', 'rgba').replace('#', '');
        g2.fillStyle = 'rgba(255,255,255,0.05)';
        roundRectPath(g2, 28, y - 6, W - 56, 48, 12);
        g2.fill();
      }
      // insignia del eje
      g2.fillStyle = col;
      g2.beginPath();
      g2.arc(56, y + 16, 17, 0, Math.PI * 2);
      g2.fill();
      g2.fillStyle = '#10131a';
      g2.font = '900 21px system-ui, sans-serif';
      g2.textAlign = 'center';
      g2.fillText(ax, 56, y + 23);
      g2.textAlign = 'left';
      // posición (mm) + barra · giro (grados) + barra
      g2.font = '700 21px ui-monospace, monospace';
      g2.fillStyle = aP ? '#ffffff' : '#cfd8e0';
      g2.fillText(`${mm(o[pk])} mm`, 350, y + 23);
      g2.fillStyle = aR ? '#ffffff' : '#cfd8e0';
      g2.fillText(`${deg(o[rk])}°`, 608, y + 23);
      barra(bx, y + 8, bw, 16, o[pk], 0.35, aP, col);
      barra(bx + bw + 130, y + 8, bw, 16, o[rk], 1.2, aR, col);
    }

    // leyenda de controles (dos columnas compactas)
    const lines = [
      ['STICK D', 'girar X / Y'],
      ['STICK D pulsado', 'rodar · eje Z'],
      ['STICK I', 'mover X / Y'],
      ['STICK I pulsado', 'acercar · eje Z'],
      ['A', 'guardar agarre'],
      ['B', 'menú · cargar · salir'],
      ['X', 'agarre natural'],
      ['GATILLO', 'bola de práctica'],
    ];
    let ly = 386;
    for (let i = 0; i < lines.length; i++) {
      const colX = i < 4 ? 36 : 400;
      const yy = ly + (i % 4) * 30;
      g2.fillStyle = '#e8b45a';
      g2.font = '800 19px system-ui, sans-serif';
      g2.fillText(lines[i][0], colX, yy);
      g2.fillStyle = '#aeb9c5';
      g2.font = '600 19px system-ui, sans-serif';
      g2.fillText(lines[i][1], colX + 188, yy);
    }

    // pie: la salida es SIEMPRE limpia (el dueño: nada arrastrado al Hall)
    g2.textAlign = 'center';
    g2.fillStyle = 'rgba(255,255,255,0.55)';
    g2.font = '700 20px system-ui, sans-serif';
    g2.fillText('Y · salir al HALL      B · MENÚ (Volver al Hall)', W / 2, 496);
    g2.textAlign = 'left';
    tex.needsUpdate = true;
  }

  return { group, update };
}


/* =====================================================================
 *  FANFARRIA DE FIN DE PARTIDO · cartel 3D flotante sobre la red con el
 *  ARTE OFICIAL del juego (v2.26: imágenes ¡HAS GANADO! / ¡HAS PERDIDO!;
 *  v2.27: versión por idioma — castellano e inglés incrustados en base64)
 *  + chip con el marcador final y la revancha. Lluvia de confeti 3D cuando
 *  se gana. Se muestra en todo el estado 'over'. Si la imagen aún no está
 *  decodificada (primer instante) se dibuja un panel de respaldo con el
 *  mismo texto; al cargar se repinta sola.
 * ===================================================================== */
const POSTER_SRC = {
  es: { win: 'assets/externos/poster_es_win.webp', lose: 'assets/externos/poster_es_lose.webp' },
  en: { win: 'assets/externos/poster_en_win.webp', lose: 'assets/externos/poster_en_lose.webp' },
};
export function createFanfareBanner() {
  // v2.44: carteles CUADRADOS (1024x1024) — victoria/derrota (ES) y
  // victory/lost (EN), arte WebP con alfa incrustado por build
  const W = 1024, H = 1024;
  const group = new THREE.Group();
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1.18, 1.18),
    // FrontSide: de detrás se ve transparente (en la órbita de la demo) en
    // lugar del arte en espejo; en VR el jugador siempre está de frente.
    new THREE.MeshBasicMaterial({
      map: tex, transparent: true, side: THREE.FrontSide, depthWrite: false,
    }),
  );
  group.add(mesh);
  group.position.set(0, 1.86, DIMS.tableCenterZ);
  group.visible = false;
  group.renderOrder = 5;

  // v2.27: carteles por IDIOMA (carga diferida; cadena vacía = sin arte:
  // se usa el panel de respaldo dibujado en el canvas).
  const posters = {};
  let lastArgs = null;
  const ensurePoster = (lang, key) => {
    if (posters[key + ':' + lang] !== undefined) return;
    const url = (POSTER_SRC[lang] || POSTER_SRC.es)[key] || '';
    posters[key + ':' + lang] = null;         // marcado: en curso/sin arte
    if (!url) return;
    const img = new Image();
    img.onload = () => {
      posters[key + ':' + lang] = img;
      if (group.visible && lastArgs) draw(...lastArgs);   // repinta si está en pantalla
    };
    img.src = url;
  };

  function draw(win, pScore, aScore, stats) {
    lastArgs = [win, pScore, aScore, stats];
    const lang = (typeof TLang === 'function') ? TLang() : 'es';
    const key = win ? 'win' : 'lose';
    ensurePoster(lang, key);
    ctx.clearRect(0, 0, W, H);
    const img = posters[key + ':' + lang];
    if (img) {
      // cartel oficial a sangre completa (mismo aspecto: sin deformar ni recortar)
      ctx.drawImage(img, 0, 0, W, H);
    } else {
      // respaldo (imagen aún decodificando o arte ausente): panel con el mismo mensaje
      ctx.fillStyle = win ? 'rgba(43,26,4,0.94)' : 'rgba(12,16,22,0.94)';
      ctx.strokeStyle = win ? '#ffd35c' : '#ff5b4d';
      ctx.lineWidth = 14;
      roundRectPath(ctx, 14, 14, W - 28, H - 28, 40);
      ctx.fill();
      ctx.stroke();
      ctx.textAlign = 'center';
      ctx.shadowColor = win ? 'rgba(255,196,40,0.9)' : 'rgba(0,0,0,0.8)';
      ctx.shadowBlur = 26;
      ctx.fillStyle = win ? '#ffd35c' : '#ff6a5b';
      ctx.font = '900 128px system-ui, sans-serif';
      ctx.fillText(T(win ? 'fanf_win' : 'fanf_lose'), W / 2, H / 2 - 40);
      ctx.shadowBlur = 0;
      ctx.fillStyle = '#f2f4f6';
      ctx.font = '800 78px system-ui, sans-serif';
      ctx.fillText(`${pScore} - ${aScore}`, W / 2, H / 2 + 90);
    }

    // chip inferior con el marcador final y la revancha (legible sobre el arte)
    const txt = T('fanf_chip', { p: pScore, q: aScore });
    ctx.font = '800 44px system-ui, sans-serif';
    const tw = ctx.measureText(txt).width;
    const cw = tw + 56, ch = 72;
    const cx = W / 2, cy = H - 58;
    ctx.fillStyle = win ? 'rgba(12,20,34,0.82)' : 'rgba(8,10,16,0.82)';
    ctx.strokeStyle = win ? 'rgba(255,211,92,0.9)' : 'rgba(255,107,91,0.9)';
    ctx.lineWidth = 5;
    roundRectPath(ctx, cx - cw / 2, cy - ch / 2, cw, ch, 36);
    ctx.fill();
    ctx.stroke();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(txt, cx, cy + 2);
    ctx.textBaseline = 'alphabetic';

    // r95 · ESTADÍSTICAS DEL DUELO (petición del dueño: «al final de cada
    // duelo: velocidad máx. de bola, rally más largo, % precisión») — chip
    // delgado ENCIMA del marcador, mismo lenguaje visual. Con guard: si no
    // llegan stats (repintados viejos) no se pinta nada.
    if (stats && (stats.vmax > 0 || stats.rally > 0 || stats.prec > 0)) {
      const stTxt = T('fanf_stats', {
        v: (Math.round((stats.vmax || 0) * 10) / 10).toFixed(1),
        r: stats.rally || 0,
        p: stats.prec || 0,
      });
      ctx.font = '700 34px system-ui, sans-serif';
      const sw = ctx.measureText(stTxt).width;
      const scw = sw + 48, sch = 56;
      const scy = cy - ch / 2 - 44;
      ctx.fillStyle = 'rgba(8,12,20,0.72)';
      ctx.strokeStyle = win ? 'rgba(232,180,90,0.75)' : 'rgba(150,165,180,0.55)';
      ctx.lineWidth = 4;
      roundRectPath(ctx, cx - scw / 2, scy - sch / 2, scw, sch, 28);
      ctx.fill();
      ctx.stroke();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#e9edf2';
      ctx.fillText(stTxt, cx, scy + 1);
      ctx.textBaseline = 'alphabetic';

      // r97 · MAPA DE CALOR DEL PARTIDO (petición del dueño: «zonas donde
      // pierdes puntos»): mini-mesa 3×3 a la izquierda del chip de
      // estadísticas — cada celda se enciende ROJO según los puntos
      // perdidos en esa zona (corta/media/fondo × izq/centro/der). Con
      // guard: sólo con ≥3 puntos perdidos (menos no dice nada).
      if (stats.heat && stats.heat.g) {
        const hg = stats.heat.g;
        let tot = 0; for (let i = 0; i < 9; i++) tot += hg[i] | 0;
        if (tot >= 3) {
          let maxC = 1; for (let i = 0; i < 9; i++) maxC = Math.max(maxC, hg[i] | 0);
          const gx = cx - scw / 2 - 88, gy = scy - 26;
          ctx.fillStyle = 'rgba(8,12,20,0.72)';
          ctx.strokeStyle = win ? 'rgba(232,180,90,0.55)' : 'rgba(150,165,180,0.45)';
          ctx.lineWidth = 3;
          roundRectPath(ctx, gx, gy, 76, 56, 12);
          ctx.fill();
          ctx.stroke();
          for (let r = 0; r < 3; r++) {
            for (let cI = 0; cI < 3; cI++) {
              const v = hg[r * 3 + cI] | 0;
              const alfa = v > 0 ? (0.18 + 0.72 * (v / maxC)) : 0.05;
              ctx.fillStyle = v > 0
                ? 'rgba(255,82,70,' + alfa.toFixed(2) + ')'
                : 'rgba(255,255,255,0.05)';
              ctx.fillRect(gx + 6 + cI * 22, gy + 6 + r * 16, 20, 14);
            }
          }
          // red (línea superior) + etiqueta corta
          ctx.fillStyle = 'rgba(255,255,255,0.55)';
          ctx.fillRect(gx + 4, gy + 3, 68, 2);
          ctx.font = '600 13px system-ui, sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#93a3b5';
          ctx.fillText(T('heat_t'), gx + 38, gy + 68);
          ctx.textBaseline = 'alphabetic';
        }
      }
    }

    tex.needsUpdate = true;
  }

  // v2.27: al cambiar el idioma con el cartel en pantalla se repinta en el idioma nuevo
  function langChanged() {
    if (group.visible && lastArgs) draw(...lastArgs);
  }

  // canvas expuesto SOLO lectura (diagnóstico/verificación headless)
  return { group, draw, canvas, langChanged };
}

/** r115 · RETIRO DEL DUEÑO: el cartel de la REPETICIÓN del mejor
 *  intercambio (r61) se suprimió con todo el sistema de replay — el
 *  constructor propio del cartel ya no existe. */

export function createConfetti() {
  // v2.35: lluvia MUCHO más densa (120 -> 430) y repartida también sobre
  // tu campo, para que el confeti del Clown estorbe la visión y el golpeo.
  const N = 430;
  const pos = new Float32Array(N * 3);
  const col = new Float32Array(N * 3);
  const fall = new Float32Array(N);
  const sway = new Float32Array(N);
  const phase = new Float32Array(N);
  const palette = [
    [1.0, 0.83, 0.36], [1.0, 0.42, 0.34], [0.34, 0.78, 1.0],
    [0.48, 0.88, 0.48], [0.9, 0.48, 0.88], [1.0, 1.0, 1.0],
  ];
  const topY = 2.45;
  const floorY = 0.85;
  // v3.6.50 (r58) · CAZABLE por las palas CLON del SÚPER CLONACIÓN: las
  // partículas muertas por kill(i) dejan de caer y de RENACER hasta que
  // la ráfaga termina (reviven TODAS al apagarse — celebraciones limpias).
  // Contador de muertos = revive sin barrer con cierres (cero allocs).
  const dead = new Uint8Array(N);
  let nMuertos = 0;
  // banda z: media mesa rival + TODA tu zona (el jugador está en z>0)
  const zMin = DIMS.tableCenterZ - 1.0;
  const zSpan = 3.2;   // hasta z≈+0,6: delante de tu cara, estorba el golpeo
  const reset = (i, first) => {
    pos[i * 3] = (Math.random() * 2 - 1) * 1.05;
    pos[i * 3 + 1] = first ? floorY + Math.random() * (topY - floorY) : topY;
    pos[i * 3 + 2] = zMin + Math.random() * zSpan;
    fall[i] = 0.32 + Math.random() * 0.42;   // caída lenta: queda más tiempo
    sway[i] = 0.12 + Math.random() * 0.2;
    phase[i] = Math.random() * Math.PI * 2;
    const c = palette[(Math.random() * palette.length) | 0];
    col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
  };
  for (let i = 0; i < N; i++) reset(i, true);

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const points = new THREE.Points(geo, new THREE.PointsMaterial({
    size: 0.036, vertexColors: true, transparent: true, opacity: 0.95, depthWrite: false,
  }));
  points.visible = false;
  points.renderOrder = 6;

  let t = 0;
  const update = (dt, active) => {
    if (!active) {
      points.visible = false;
      if (nMuertos) { for (let i = 0; i < N; i++) dead[i] = 0; nMuertos = 0; }
      return;
    }
    points.visible = true;
    t += dt;
    for (let i = 0; i < N; i++) {
      if (dead[i]) continue;   // cazado por un clon: fuera hasta la próxima ráfaga
      pos[i * 3 + 1] -= fall[i] * dt;
      pos[i * 3] += Math.sin(t * 2.4 + phase[i]) * sway[i] * dt;
      pos[i * 3 + 2] += Math.cos(t * 1.8 + phase[i]) * sway[i] * dt * 0.6;
      if (pos[i * 3 + 1] < floorY) reset(i, false);
    }
    geo.attributes.position.needsUpdate = true;
  };

  /* v3.6.50 · kill(i): el clon atrapó este confeto — muere sin renacer.
   * pos/N expuestos (solo lectura) para el barrido de los clones. */
  const kill = (i) => {
    if (i >= 0 && i < N && !dead[i]) { dead[i] = 1; nMuertos++; }
  };

  return { points, update, kill, pos, N };
}

/* =====================================================================
 *  MULTIJUGADOR ONLINE (v2.19) · P2P WebRTC vía PeerJS (sin servidor propio)
 *  - El anfitrión crea una sala con código de 5 caracteres (id ppxr3-CODE).
 *  - El invitado introduce el código con un teclado dibujado en el menú.
 *  - Canal de datos: poses de pala (20 Hz), estado de la bola (el dueño la
 *    simula y la emite), eventos de física y estado del partido.
 *  - VOZ: llamada de medios WebRTC entre ambos (micrófono del navegador).
 *    v2.25: la LLAMA el INVITADO al ID de la sala (el anfitrión responde).
 *    Antes llamaba el anfitrión a su PROPIO id: bucle hacia sí mismo y el
 *    rival sin voz. El micrófono se pide al crear/unirse (gesto 2D del menú,
 *    fuera de VR): el cambio de ruta de audio de Android ocurre ANTES de la
 *    sesión inmersiva y el WebAudio del juego no se queda mudo.
 *  Autoridad: el ANFITRIÓN lleva las reglas y el marcador; el invitado
 *  recibe el estado (reglas sombra). Marco de coordenadas:
 *  · EMISIÓN en CRUDO (posiciones locales tal cual) y RECEPCIÓN con UNA
 *    rotación de 180° en Y alrededor del centro de la mesa: (x,z)->(-x,-3.2-z).
 *    v2.25: ANTES se transformaba al emitir Y también al recibir — doble
 *    espejo: el rival aparecía en TU mismo lado y las bolas eran fantasmas.
 *    La involución aplicada UNA vez es el cambio de marco correcto (ambos
 *    mundos son copias idénticas que se miran de frente).
 *  · SINCRONÍA POR PUNTO DE VISTA: el anfitrión etiqueta los datos desde SU
 *    perspectiva ('player'=anfitrión). En el invitado 'player' soy YO, así
 *    que applySync intercambia marcador y sacador, remapea las causas de los
 *    puntos y genera megafonía local (antes el invitado callaba y veía el
 *    marcador invertido).
 * ===================================================================== */
