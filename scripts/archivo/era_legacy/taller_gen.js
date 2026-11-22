/* ══════════ app2b · fábrica de assets y generador de PAQUETES REALES ══════════
   El Taller V3.0.3: el paquete ya no es una caja + un leeme — es la carpeta
   championships/<id> COMPLETA que el juego (ChampLoader) sabe cargar:
   manifest.json (contrato 1) + index.js (módulo plantilla) + assets/ reales
   (arte generado en canvas o aportado por ti) + championships.json + LEEME. */

const ID_TPL = "tpl-modulo";

/* ---------- utilidades de bytes ---------- */
function dataUrlABytes(dataUrl){
  const i = dataUrl.indexOf(",");
  const b64 = dataUrl.slice(i + 1);
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let j = 0; j < bin.length; j++) out[j] = bin.charCodeAt(j);
  return out;
}
function bytesABase64(bytes){
  let s = "";
  const CH = 0x8000;
  for (let i = 0; i < bytes.length; i += CH){
    s += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
  }
  return btoa(s);
}
function extDe(nombre, defecto){
  const m = /\.([a-z0-9]{2,5})$/i.exec(String(nombre || ""));
  return m ? m[1].toLowerCase() : defecto;
}
function cvBytes(cv, tipo, q){
  return new Promise((res) => cv.toBlob((b) => {
    const fr = new FileReader();
    fr.onload = () => res({ dataUrl: fr.result, bytes: dataUrlABytes(fr.result) });
    fr.readAsDataURL(b);
  }, tipo || "image/jpeg", q || 0.85));
}

/* ---------- paletas por estilo visual ---------- */
const ESTILO_PALETA = {
  pabellon:      { suelo:["#b98a4f","#7d5730"], techo:["#efe9dc","#d3cbb9"], pared:["#f3ecdd","#d9cdb4"], acento:"#c2410c", tipo:"parquet" },
  artico:        { suelo:["#dbeafe","#8fb9f2"], techo:["#f2f8ff","#d5e6fb"], pared:["#e3f2fe","#bcdffb"], acento:"#0369a1", tipo:"hielo" },
  atardecer:     { suelo:["#8a4b1c","#b4741f"], techo:["#fed7aa","#fb923c"], pared:["#ffedd5","#fdba74"], acento:"#9a3412", tipo:"atardecer" },
  neon:          { suelo:["#0b1220","#131c33"], techo:["#0f172a","#1e293b"], pared:["#101528","#2b2470"], acento:"#22d3ee", tipo:"neon" },
  personalizado: { suelo:["#8a7a68","#5f5548"], techo:["#efe9df","#d6cfc2"], pared:["#e8e1d4","#cfc7b8"], acento:"#f97316", tipo:"neutro" }
};
const ILU_TINT = { calida:["#ffedcc",0.10], fria:["#cfe3ff",0.14], neon:["#a5f3fc",0.10], atardecer:["#ffd9b0",0.12] };

function cvPlano(plano){
  const cv = document.createElement("canvas");
  cv.width = 1024; cv.height = 1024;
  return cv;
}
function pintaPlano(caja, plano){
  const p = ESTILO_PALETA[caja.ficha.estiloVisual] || ESTILO_PALETA.pabellon;
  const cv = cvPlano(plano);
  const c = cv.getContext("2d");
  const grupo = plano === "floor" ? "suelo" : plano === "ceil" ? "techo" : "pared";
  const g = c.createLinearGradient(0, 0, 0, 1024);
  g.addColorStop(0, p[grupo][0]); g.addColorStop(1, p[grupo][1]);
  c.fillStyle = g; c.fillRect(0, 0, 1024, 1024);

  if (plano === "floor"){
    if (p.tipo === "parquet" || p.tipo === "neutro"){
      for (let y = 0; y < 1024; y += 64){
        c.fillStyle = (y / 64) % 2 ? "rgba(0,0,0,.10)" : "rgba(255,255,255,.06)";
        c.fillRect(0, y, 1024, 64);
        c.strokeStyle = "rgba(0,0,0,.16)"; c.lineWidth = 2;
        for (let x = ((y / 64) % 2) * 120; x < 1024; x += 240){
          c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 64); c.stroke();
        }
      }
    } else if (p.tipo === "neon"){
      c.strokeStyle = "rgba(34,211,238,.5)"; c.lineWidth = 4;
      for (let k = 0; k <= 8; k++){
        c.beginPath(); c.moveTo(k * 128, 0); c.lineTo(k * 128, 1024); c.stroke();
        c.beginPath(); c.moveTo(0, k * 128); c.lineTo(1024, k * 128); c.stroke();
      }
    } else if (p.tipo === "hielo"){
      c.strokeStyle = "rgba(255,255,255,.5)"; c.lineWidth = 3;
      for (let k = 0; k < 26; k++){
        const x = Math.random() * 1024, y = Math.random() * 1024;
        c.beginPath(); c.moveTo(x, y);
        c.lineTo(x + (Math.random() - .5) * 260, y + (Math.random() - .5) * 260); c.stroke();
      }
    } else if (p.tipo === "atardecer"){
      for (let k = 0; k < 7; k++){
        c.fillStyle = "rgba(255,237,160," + (0.10 + (k % 3) * 0.05) + ")";
        c.fillRect(0, k * 150, 1024, 70);
      }
    }
  } else if (plano === "ceil"){
    for (let fy = 0; fy < 2; fy++) for (let fx = 0; fx < 3; fx++){
      const cx = 170 + fx * 342, cy = 300 + fy * 420;
      c.fillStyle = "rgba(255,255,255,.85)";
      c.beginPath(); c.ellipse(cx, cy, 120, 74, 0, 0, Math.PI * 2); c.fill();
      c.fillStyle = "rgba(253,224,71,.5)";
      c.beginPath(); c.ellipse(cx, cy, 84, 48, 0, 0, Math.PI * 2); c.fill();
    }
  } else {
    // paredes: ventanal grande + zócalo + acento
    c.fillStyle = "rgba(0,0,0,.18)"; c.fillRect(0, 880, 1024, 144);
    const vent = (x, w, h, y) => {
      c.fillStyle = p.tipo === "neon" ? "rgba(34,211,238,.14)" : "rgba(255,255,255,.55)";
      c.beginPath(); c.roundRect(x, y, w, h, 26); c.fill();
      c.strokeStyle = p.acento; c.lineWidth = 10; c.stroke();
    };
    if (plano === "back" || plano === "front"){
      vent(90, 360, 430, 170); vent(574, 360, 430, 170);
    } else {
      vent(120, 784, 470, 200);
    }
    if (plano === "back"){
      c.fillStyle = "rgba(0,0,0,.30)";
      c.font = "800 84px 'Baloo 2', sans-serif"; c.textAlign = "center";
      c.fillText(String(caja.ficha.nombre || "CRAZY").toUpperCase().slice(0, 18), 512, 760);
    }
    if (p.tipo === "neon"){
      c.strokeStyle = "rgba(34,211,238,.6)"; c.lineWidth = 6;
      for (let k = 0; k < 5; k++){
        c.beginPath(); c.moveTo(0, 140 + k * 40); c.lineTo(1024, 140 + k * 40); c.stroke();
      }
    }
  }
  const [tint, alpha] = ILU_TINT[caja.sala.iluminacion] || ILU_TINT.calida;
  c.globalAlpha = alpha; c.fillStyle = tint; c.fillRect(0, 0, 1024, 1024); c.globalAlpha = 1;
  return cvBytes(cv, "image/jpeg", 0.80);
}

/* ---------- rival generado (troquel) ---------- */
function cvRival(caja, estado){
  const W = 512, H = 1024;
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const p = ESTILO_PALETA[caja.ficha.estiloVisual] || ESTILO_PALETA.pabellon;
  const acc = p.acento;
  // cuerpo
  c.fillStyle = "#e2e8f0"; c.strokeStyle = "#334155"; c.lineWidth = 8;
  c.beginPath(); c.roundRect(136, 330, 240, 420, 60); c.fill(); c.stroke();
  // cabeza
  c.fillStyle = "#f1f5f9";
  c.beginPath(); c.roundRect(146, 130, 220, 200, 74); c.fill(); c.stroke();
  // ojos según estado
  const ojo = (x) => {
    c.fillStyle = "#0f172a";
    if (estado === "derrotado"){
      c.lineWidth = 10; c.strokeStyle = "#0f172a";
      c.beginPath(); c.moveTo(x - 20, 200); c.lineTo(x + 20, 240); c.stroke();
      c.beginPath(); c.moveTo(x + 20, 200); c.lineTo(x - 20, 240); c.stroke();
    } else {
      c.beginPath(); c.arc(x, 220, 22, 0, Math.PI * 2); c.fill();
      c.fillStyle = "#fff";
      c.beginPath(); c.arc(x + 7, 212, 7, 0, Math.PI * 2); c.fill();
    }
  };
  ojo(216); ojo(296);
  // boca
  c.lineWidth = 10; c.strokeStyle = "#0f172a";
  c.beginPath();
  if (estado === "triunfante") c.arc(256, 280, 30, 0, Math.PI);
  else if (estado === "derrotado") c.arc(256, 306, 30, Math.PI, 0);
  else if (estado === "duelo") { c.moveTo(226, 292); c.lineTo(286, 292); }
  else c.arc(256, 276, 26, Math.PI * 0.15, Math.PI * 0.85);
  c.stroke();
  // panel con el nombre
  c.fillStyle = acc;
  c.beginPath(); c.roundRect(176, 430, 160, 120, 22); c.fill();
  c.fillStyle = "#fff"; c.textAlign = "center";
  c.font = "800 40px 'Baloo 2', sans-serif";
  const nom = String(caja.rival.nombre || "RIVAL").toUpperCase().slice(0, 8);
  c.fillText(nom, 256, 502);
  // brazos
  c.strokeStyle = "#334155"; c.lineWidth = 14;
  const alza = (estado === "triunfante");
  c.beginPath(); c.moveTo(136, 380); c.lineTo(alza ? 56 : 76, alza ? 250 : 520); c.stroke();
  c.beginPath(); c.moveTo(376, 380); c.lineTo(alza ? 456 : 436, alza ? 250 : 520); c.stroke();
  // piernas
  c.beginPath(); c.moveTo(196, 750); c.lineTo(196, 880); c.stroke();
  c.beginPath(); c.moveTo(316, 750); c.lineTo(316, 880); c.stroke();
  if (estado && estado !== "idle"){
    c.fillStyle = "rgba(15,23,42,.72)";
    c.beginPath(); c.roundRect(96, 918, 320, 66, 20); c.fill();
    c.fillStyle = "#fde047"; c.font = "700 36px 'Nunito Sans', sans-serif";
    c.fillText(estado.toUpperCase(), 256, 962);
  }
  return cvBytes(cv, "image/png", 0.9);
}
async function cvRivalDesdeBase(caja, estado){
  // el arte lo aportó el dueño: mismo arte + banda del estado
  const m = materialGuardado(caja, "rival");
  if (!m || !m.dataUrl) return cvRival(caja, estado);
  try {
    const img = await new Promise((res, rej) => {
      const im = new Image();
      im.onload = () => res(im); im.onerror = rej;
      im.src = m.dataUrl;
    });
    const W = 512, H = 1024;
    const cv = document.createElement("canvas"); cv.width = W; cv.height = H;
    const c = cv.getContext("2d");
    c.drawImage(img, 0, 0, W, H);
    const tintes = { idle: null, duelo: "rgba(251,113,36,.16)", derrotado: "rgba(59,130,246,.22)", triunfante: "rgba(250,204,21,.20)" };
    const t = tintes[estado];
    if (t){ c.fillStyle = t; c.fillRect(0, 0, W, H); }
    if (estado === "derrotado" || estado === "triunfante"){
      c.fillStyle = "rgba(15,23,42,.72)";
      c.beginPath(); c.roundRect(96, 918, 320, 66, 20); c.fill();
      c.fillStyle = estado === "derrotado" ? "#93c5fd" : "#fde047";
      c.font = "700 36px 'Nunito Sans', sans-serif"; c.textAlign = "center";
      c.fillText(estado.toUpperCase(), 256, 962);
    }
    return cvBytes(cv, "image/png", 0.9);
  } catch (e) {
    return cvRival(caja, estado);
  }
}

/* ---------- troqueles + insignia + iconos ---------- */
function cvTroquel(caja, n){
  const W = 512, H = 640;
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const p = ESTILO_PALETA[caja.ficha.estiloVisual] || ESTILO_PALETA.pabellon;
  c.strokeStyle = "#78350f"; c.lineWidth = 10;
  if (n === 1){
    // cartel colgante
    c.beginPath(); c.moveTo(60, 0); c.lineTo(150, 90); c.moveTo(452, 0); c.lineTo(362, 90); c.stroke();
    c.fillStyle = "#f5e6c8";
    c.beginPath(); c.roundRect(60, 90, 392, 250, 24); c.fill(); c.stroke();
    c.fillStyle = p.acento; c.font = "800 56px 'Baloo 2', sans-serif"; c.textAlign = "center";
    c.fillText(String(caja.ficha.nombre || "CRAZY").toUpperCase().slice(0, 12), 256, 200);
    c.fillStyle = "#78350f"; c.font = "600 34px 'Nunito Sans', sans-serif";
    c.fillText("campeonato", 256, 262);
  } else {
    // rosetón estrella
    c.fillStyle = p.acento;
    c.beginPath();
    for (let k = 0; k < 10; k++){
      const a = -Math.PI / 2 + k * Math.PI / 5;
      const r = k % 2 ? 120 : 240;
      const x = 256 + Math.cos(a) * r, y = 320 + Math.sin(a) * r;
      k ? c.lineTo(x, y) : c.moveTo(x, y);
    }
    c.closePath(); c.fill(); c.stroke();
    c.fillStyle = "#fff"; c.font = "800 120px 'Baloo 2', sans-serif"; c.textAlign = "center";
    c.fillText(String(caja.rival.nombre || "VS").slice(0, 1).toUpperCase(), 256, 368);
  }
  // pie de apoyo
  c.fillStyle = "#9a7448";
  c.fillRect(216, 560, 80, 80);
  return cvBytes(cv, "image/png", 0.9);
}
function cvInsignia(caja){
  const cv = document.createElement("canvas"); cv.width = 512; cv.height = 512;
  const c = cv.getContext("2d");
  c.strokeStyle = "#166534"; c.lineWidth = 16;
  c.beginPath(); c.arc(256, 256, 190, Math.PI * 0.15, Math.PI * 0.85, false); c.stroke();
  c.beginPath(); c.arc(256, 256, 190, Math.PI * 1.15, Math.PI * 1.85, false); c.stroke();
  c.fillStyle = "#f59e0b";
  c.beginPath();
  for (let k = 0; k < 10; k++){
    const a = -Math.PI / 2 + k * Math.PI / 5;
    const r = k % 2 ? 70 : 160;
    const x = 256 + Math.cos(a) * r, y = 256 + Math.sin(a) * r;
    k ? c.lineTo(x, y) : c.moveTo(x, y);
  }
  c.closePath(); c.fill();
  c.fillStyle = "#78350f"; c.textAlign = "center";
  c.font = "800 54px 'Baloo 2', sans-serif";
  c.fillText("★", 256, 282);
  return cvBytes(cv, "image/png", 0.9);
}
function cvIconoPoder(kind, nombre){
  const mapa = {
    confeti: ["#fde68a", "#f59e0b"], mareo: ["#c7d2fe", "#4f46e5"],
    globos: ["#fecdd3", "#e11d48"], orbe: ["#a5f3fc", "#0891b2"], arena: ["#fde68a", "#b45309"]
  };
  const [c1, c2] = mapa[kind] || ["#e2e8f0", "#475569"];
  const cv = document.createElement("canvas"); cv.width = 256; cv.height = 256;
  const c = cv.getContext("2d");
  const g = c.createRadialGradient(128, 112, 16, 128, 128, 120);
  g.addColorStop(0, c1); g.addColorStop(1, c2);
  c.beginPath(); c.arc(128, 128, 116, 0, Math.PI * 2); c.fillStyle = g; c.fill();
  c.lineWidth = 10; c.strokeStyle = "rgba(255,255,255,.9)"; c.stroke();
  c.fillStyle = "#fff"; c.textAlign = "center";
  c.font = "800 64px 'Baloo 2', sans-serif";
  c.fillText(String(nombre || kind).slice(0, 1).toUpperCase(), 128, 152);
  return cvBytes(cv, "image/png", 0.9);
}

/* ---------- música procedural (WAV 16-bit vía OfflineAudioContext) ---------- */
async function generaBso(caja){
  const mood = caja.sala.musica;
  const sr = 22050, dur = 12;
  const OC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
  if (!OC) throw new Error("OfflineAudioContext no disponible");
  const ctx = new OC(1, sr * dur, sr);
  const master = ctx.createGain(); master.gain.value = 0.55;
  const filtro = ctx.createBiquadFilter(); filtro.type = "lowpass";
  filtro.frequency.value = mood === "artica" ? 900 : (mood === "neon" ? 2400 : 1500);
  filtro.connect(master); master.connect(ctx.destination);
  const acordes = {
    pabellon: [220, 277.2, 329.6], espacial: [174.6, 261.6, 349.2],
    artica: [196, 246.9, 293.7], neon: [261.6, 329.6, 392]
  }[mood] || [220, 277.2, 329.6];
  acordes.forEach((f, i) => {
    const o = ctx.createOscillator();
    o.type = mood === "neon" ? "sawtooth" : "sine";
    o.frequency.value = f;
    const g = ctx.createGain(); g.gain.value = 0.05 / (i + 1);
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.1 + i * 0.07;
    const lg = ctx.createGain(); lg.gain.value = 0.02 / (i + 1);
    lfo.connect(lg); lg.connect(g.gain); lfo.start();
    o.connect(g); g.connect(filtro);
    o.start(); o.stop(dur);
  });
  if (mood === "artica"){
    const buf = ctx.createBuffer(1, sr * dur, sr);
    const d = buf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource(); src.buffer = buf;
    const bp = ctx.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 520; bp.Q.value = 0.8;
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.17;
    const lg = ctx.createGain(); lg.gain.value = 260;
    lfo.connect(lg); lg.connect(bp.frequency); lfo.start();
    const g = ctx.createGain(); g.gain.value = 0.14;
    src.connect(bp); bp.connect(g); g.connect(master);
    src.start();
  }
  if (mood === "neon"){
    for (let k = 0; k < 18; k++){
      const o = ctx.createOscillator();
      o.type = "triangle";
      o.frequency.value = acordes[k % 3] * 2;
      const g = ctx.createGain();
      const t0 = k * 0.62;
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(0.05, t0 + 0.05);
      g.gain.linearRampToValueAtTime(0, t0 + 0.5);
      o.connect(g); g.connect(filtro);
      o.start(t0); o.stop(t0 + 0.55);
    }
  }
  const buf = await ctx.startRendering();
  const n = buf.length;
  const out = new ArrayBuffer(44 + n * 2);
  const dv = new DataView(out);
  const wstr = (off, s) => { for (let i = 0; i < s.length; i++) dv.setUint8(off + i, s.charCodeAt(i)); };
  wstr(0, "RIFF"); dv.setUint32(4, 36 + n * 2, true); wstr(8, "WAVE");
  wstr(12, "fmt "); dv.setUint32(16, 16, true); dv.setUint16(20, 1, true);
  dv.setUint16(22, 1, true); dv.setUint32(24, sr, true);
  dv.setUint32(28, sr * 2, true); dv.setUint16(32, 2, true); dv.setUint16(34, 16, true);
  wstr(36, "data"); dv.setUint32(40, n * 2, true);
  const ch = buf.getChannelData(0);
  for (let i = 0; i < n; i++){
    const v = Math.max(-1, Math.min(1, ch[i]));
    dv.setInt16(44 + i * 2, v < 0 ? v * 0x8000 : v * 0x7fff, true);
  }
  const bytes = new Uint8Array(out);
  return { bytes, dataUrl: "data:audio/wav;base64," + bytesABase64(bytes) };
}

/* ---------- manifest (contrato 1) ---------- */
function construirManifest(caja, id, definitivo, fn){
  const retos = (caja.retos || []).map((r, i) => ({
    nombre: r.nombre || ("Prueba " + (i + 1)), tipo: r.tipo || "objetivos",
    objetivo: Math.max(1, Number(r.objetivo) || 5),
    puntos: Math.max(1, Number(r.puntos) || 1),
    premio: r.premio || ""
  }));
  const per = {
    agresividad: Math.max(1, Math.min(5, Number(caja.rival.agresividad) || 3)),
    precision: Math.max(1, Math.min(5, Number(caja.rival.precision) || 3)),
    constancia: Math.max(1, Math.min(5, Number(caja.rival.constancia) || 3)),
    caracter: caja.rival.caracter || "frio",
    celebracion: caja.rival.celebracion || "",
    cerebro: caja.rival.cerebroBase || "partido"
  };
  if (per.cerebro === "agresivo") per.agresividad = Math.min(5, per.agresividad + 1);
  if (per.cerebro === "defensivo") per.agresividad = Math.max(1, per.agresividad - 1);
  const powers = (caja.superpoderes || []).map((s, i) => {
    const rally = (s.activacion || "rally") === "rally";
    const p = {
      kind: s.efecto, name: s.nombre || "Superpoder",
      icon: "assets/power_" + i + ".png",
      cooldown: Math.max(4, Number(s.recarga) || 18),
      duration: Math.max(1, Number(s.duracion) || 5),
      warn: 2, activacion: s.activacion || "rally"
    };
    if (rally) p.chance = Math.max(0.05, Math.min(1, (Number(s.chance) || 35) / 100));
    else p.cadaCuantos = Math.max(1, Number(s.cadaCuantos) || 3);
    return p;
  });
  const stages = [];
  retos.forEach((r, i) => {
    stages.push({ id: "duelo" + (i + 1), name: "Duelo " + (i + 1), kind: "duelo" });
    stages.push({ id: "prueba" + (i + 1), name: r.nombre, kind: "objetos",
      rules: { modo: r.tipo, objetivo: r.objetivo, puntos: r.puntos, premio: r.premio } });
  });
  stages.push({ id: "final", name: "DUELO FINAL", kind: "duelo" });
  const music = caja.sala.musica === "ninguna" ? null
    : (caja.sala.musica === "propia" ? fn("sala-musica", "bso.wav") : "assets/bso.wav");
  const man = {
    id,
    version: 1,
    contract: 1,
    estado: definitivo ? "publicado" : "listo",
    title: { es: String(caja.ficha.nombre || id).slice(0, 40) },
    description: { es: String(caja.ficha.historia || "").slice(0, 400) },
    rival: {
      id: id + "_rival",
      name: caja.rival.nombre || "RIVAL",
      kind: "stock",
      states: ["idle", "duelo", "derrotado", "triunfante"],
      oppLabel: "rival",
      personalidad: per
    },
    storage: "pp_champ_" + id + "_*",
    assets: "Taller V3.0.3: rival + estados (idle/duelo/derrotado/triunfante), sala_*.jpg (6 planos), decor1/2.png, power_*.png, insignia.png" + (music ? ", bso" : ""),
    audio: { music, musicVolume: 0.18 },
    powers,
    stages,
    decor: {
      pieces: [
        { file: fn("decor1", "decor1.png"), h: 1.15, x: -2.5, z: -2.45, sway: 0.45 },
        { file: fn("decor2", "decor2.png"), h: 0.85, x: 2.15, z: -2.45, sway: 0.3 }
      ]
    },
    room: {
      floor: fn("sala-floor", "sala_floor.jpg"), ceil: fn("sala-ceil", "sala_ceil.jpg"),
      back: fn("sala-back", "sala_back.jpg"), front: fn("sala-front", "sala_front.jpg"),
      left: fn("sala-left", "sala_left.jpg"), right: fn("sala-right", "sala_right.jpg")
    },
    trophy: { name: { es: "Insignia " + caja.ficha.nombre, en: caja.ficha.nombre + " badge" } },
    taller: {
      editor: "V3.0.3",
      dificultad: caja.ficha.dificultad || "media",
      retos,
      generado: new Date().toISOString()
    },
    notes: ["v1 · Campeonato creado con El Taller V3.0.3: manifest, módulo y assets generados automáticamente."]
  };
  if (!music) delete man.audio;
  return man;
}

/* ---------- LEEME real ---------- */
function leemePaquete(caja, definitivo, id){
  return "CRAZY PING PONG · EL TALLER V3.0.3\n" +
(definitivo ? "PAQUETE DEFINITIVO" : "PAQUETE DE PRUEBAS") + " — campeonato «" + caja.ficha.nombre + "» (etiqueta: " + id + ")\n" +
"Generado el " + new Date().toLocaleString("es-ES") + "\n" +
"\n" +
"QUÉ CONTIENE (la carpeta REAL del campeonato)\n" +
"  championships/" + id + "/manifest.json ..... el carné del campeonato (contrato 1 del juego)\n" +
"  championships/" + id + "/index.js .......... el módulo: sala, duelos, superpoderes y pruebas\n" +
"  championships/" + id + "/assets/ ........... todo el arte y la música (generado por el Taller y/o aportado por ti)\n" +
"  championships/championships.json ........... el índice de campeonatos CON LA LÍNEA NUEVA AÑADIDA\n" +
"\n" +
"CÓMO SE MONTA EN EL JUEGO (5 minutos)\n" +
"1. Descomprime este zip.\n" +
"2. Copia la carpeta championships/ completa DENTRO de la carpeta del juego,\n" +
"   al lado del index.html del juego (se fusiona con la que ya hay: tu\n" +
"   campeonato se AÑADE; los demás no se tocan). Si lo haces a mano, añade\n" +
"   también la línea «" + id + "» al archivo championships/championships.json.\n" +
"3. Sube el juego a tu alojamiento (Netlify Drop u otro) o ábrelo en local.\n" +
"4. PRUEBA SIN PUBLICAR: abre el juego terminando la dirección en\n" +
"   ?champ=" + id + "   (ejemplo: https://tu-direccion/?champ=" + id + ")\n" +
"   — el campeonato arranca aunque venga en estado «listo» (en pruebas).\n" +
"5. PUBLICAR PARA TODOS: cambia \"estado\": \"listo\" → \"publicado\" en\n" +
"   championships/" + id + "/manifest.json (o genera el PAQUETE DEFINITIVO,\n" +
"   que ya sale publicado) y vuelve a subir el juego. Aparecerá en el menú\n" +
"   CAMPEONATOS con su nombre.\n" +
"\n" +
"QUÉ HACE DENTRO DEL JUEGO\n" +
"· Sala propia con el arte, la luz, los troqueles y la música decididos.\n" +
"· Camino de etapas: un duelo y una prueba por cada reto, y DUELO FINAL.\n" +
"· Superpoderes reales del motor: confeti, mareo, globos, orbe, arena.\n" +
"· Progreso guardado (pp_champ_" + id + "_…), insignia ¡CONSEGUIDO! al vencer el final.\n" +
"· Mapa del camino en la pared: apunta con la pala y aprieta el gatillo.\n" +
"\n" +
"LA LISTA DE COMPROBACIÓN (la prueba del algodón)\n" +
"1. El campeonato arranca (?champ=" + id + " o el menú si está publicado).\n" +
"2. La sala se ve y suena como la definiste.\n" +
"3. El rival está en su sitio y sus superpoderes entran en los duelos.\n" +
"4. Las pruebas de habilidad se juegan, puntúan y dan su premio.\n" +
"5. Se gana el DUELO FINAL y sale la insignia ¡CONSEGUIDO!.\n" +
"6. Los cuatro campeonatos del juego siguen intactos.\n" +
"\n" +
"LA REGLA DE ORO\n" +
"Tu campeonato vive en SU carpeta: nada de lo que hay aquí toca a La Locura,\n" +
"Magia, el Salvaje Oeste ni Estación Orbital. Y publicar no es para siempre:\n" +
"cambiando el estado vuelve a pruebas o se desactiva sin dramas.\n";
}

/* ---------- el generador del paquete ---------- */
async function construirPaquete(caja, definitivo){
  const id = slug(caja.etiqueta);
  if (!/^[a-z0-9_-]{2,24}$/.test(id)) throw new Error("la etiqueta «" + id + "» no es válida como carpeta");
  const files = [];
  const add = (nombre, contenido) => files.push({ nombre, contenido });
  const fn = (clave, defecto) => {
    const m = materialGuardado(caja, clave);
    return "assets/" + ((m && m.nombre) ? m.nombre : defecto);
  };

  /* --- assets: lo aportado viaja tal cual; lo demás se genera AHORA --- */
  const baseRival = materialGuardado(caja, "rival");
  const mkRival = async () => {
    if (baseRival && baseRival.dataUrl) return { bytes: dataUrlABytes(baseRival.dataUrl), nombre: baseRival.nombre || "rival.png" };
    const r = await cvRival(caja, null);
    return { bytes: r.bytes, nombre: "rival.png" };
  };
  const riv = await mkRival();
  add("championships/" + id + "/assets/" + riv.nombre, riv.bytes);

  for (const st of ["idle", "duelo", "derrotado", "triunfante"]){
    const m = materialGuardado(caja, "rival-" + st);
    if (m && m.dataUrl){
      add("championships/" + id + "/assets/" + (m.nombre || (st + ".png")), dataUrlABytes(m.dataUrl));
    } else {
      const r = await cvRivalDesdeBase(caja, st);
      add("championships/" + id + "/assets/" + st + ".png", r.bytes);
    }
  }

  const planos = [["sala-floor", "floor", "sala_floor.jpg"], ["sala-ceil", "ceil", "sala_ceil.jpg"],
    ["sala-back", "back", "sala_back.jpg"], ["sala-front", "front", "sala_front.jpg"],
    ["sala-left", "left", "sala_left.jpg"], ["sala-right", "right", "sala_right.jpg"]];
  for (const [clave, plano, def] of planos){
    const m = materialGuardado(caja, clave);
    if (m && m.dataUrl){
      add("championships/" + id + "/assets/" + (m.nombre || def), dataUrlABytes(m.dataUrl));
    } else {
      const r = await pintaPlano(caja, plano);
      add("championships/" + id + "/assets/" + def, r.bytes);
    }
  }

  for (const [clave, n, def] of [["decor1", 1, "decor1.png"], ["decor2", 2, "decor2.png"]]){
    const m = materialGuardado(caja, clave);
    if (m && m.dataUrl){
      add("championships/" + id + "/assets/" + (m.nombre || def), dataUrlABytes(m.dataUrl));
    } else {
      const r = await cvTroquel(caja, n);
      add("championships/" + id + "/assets/" + def, r.bytes);
    }
  }

  { // insignia
    const m = materialGuardado(caja, "insignia");
    const r = (m && m.dataUrl) ? { bytes: dataUrlABytes(m.dataUrl) } : await cvInsignia(caja);
    add("championships/" + id + "/assets/insignia.png", r.bytes);
  }
  (caja.superpoderes || []).forEach((s, i) => {
    const m = materialGuardado(caja, "sp-" + i);
    if (m && m.dataUrl) add("championships/" + id + "/assets/power_" + i + ".png", dataUrlABytes(m.dataUrl));
  });
  for (let i = 0; i < (caja.superpoderes || []).length; i++){
    const s = caja.superpoderes[i];
    const m = materialGuardado(caja, "sp-" + i);
    if (m && m.dataUrl) continue;
    const r = await cvIconoPoder(s.efecto, s.nombre);
    add("championships/" + id + "/assets/power_" + i + ".png", r.bytes);
  }

  /* --- música --- */
  if (caja.sala.musica !== "ninguna"){
    const m = materialGuardado(caja, "sala-musica");
    if (caja.sala.musica === "propia"){
      if (!m || !m.dataUrl) throw new Error("la música propia no está en la caja");
      add("championships/" + id + "/assets/" + (m.nombre || "bso.wav"), dataUrlABytes(m.dataUrl));
    } else if (m && m.dataUrl){
      add("championships/" + id + "/assets/" + (m.nombre || "bso.wav"), dataUrlABytes(m.dataUrl));
    } else {
      const r = await generaBso(caja);
      add("championships/" + id + "/assets/bso.wav", r.bytes);
    }
  }

  /* --- manifest + módulo + índice + leeme --- */
  const man = construirManifest(caja, id, definitivo, fn);
  add("championships/" + id + "/manifest.json", JSON.stringify(man, null, 1));
  const tpl = document.getElementById(ID_TPL);
  if (!tpl) throw new Error("falta la plantilla del módulo (tpl-modulo)");
  add("championships/" + id + "/index.js", String(tpl.textContent));

  const idx = {
    version: 1,
    generado: new Date().toISOString() + " · El Taller V3.0.3",
    note: "Indice de campeonatos externos (carpetas autocontenidas). Para añadir uno nuevo: carpeta championships/<id>/ con manifest.json + index.js + assets/ y su linea en «championships». El nucleo lo descubre solo; ?champ=<id> previsualiza sin publicar. En file:// se ignora en silencio.",
    championships: [{ id: "locura", eager: true }, "magia", "oeste", "estacion_orbital", id]
  };
  add("championships/championships.json", JSON.stringify(idx, null, 1));
  add("LEEME.txt", leemePaquete(caja, definitivo, id));

  return { files, id, man };
}

/* ---------- vistas previas REALES (fase 4): pinta y guarda en la caja ---------- */
async function generarVistasPrevias(caja){
  let n = 0;
  const guarda = (clave, dataUrl, nombre, nota) => {
    resolverMaterial(caja, clave, "generado", dataUrl, nombre, nota || "Pintado por el Taller");
    n++;
  };
  const rivBase = materialGuardado(caja, "rival");
  if (!(rivBase && rivBase.dataUrl)){
    const riv = await cvRival(caja, null);
    guarda("rival", riv.dataUrl, "rival.png");
  }
  for (const st of ["idle", "duelo", "derrotado", "triunfante"]){
    if (materialGuardado(caja, "rival-" + st) && materialGuardado(caja, "rival-" + st).dataUrl) continue;
    const r = await cvRivalDesdeBase(caja, st);
    guarda("rival-" + st, r.dataUrl, st + ".png");
  }
  for (const [clave, plano, def] of [["sala-floor", "floor", "sala_floor.jpg"], ["sala-ceil", "ceil", "sala_ceil.jpg"],
    ["sala-back", "back", "sala_back.jpg"], ["sala-front", "front", "sala_front.jpg"],
    ["sala-left", "left", "sala_left.jpg"], ["sala-right", "right", "sala_right.jpg"]]){
    const m = materialGuardado(caja, clave);
    if (m && m.dataUrl) continue;
    const r = await pintaPlano(caja, plano);
    guarda(clave, r.dataUrl, def);
  }
  for (const [clave, num, def] of [["decor1", 1, "decor1.png"], ["decor2", 2, "decor2.png"]]){
    const m = materialGuardado(caja, clave);
    if (m && m.dataUrl) continue;
    const r = await cvTroquel(caja, num);
    guarda(clave, r.dataUrl, def);
  }
  {
    const m = materialGuardado(caja, "insignia");
    if (!(m && m.dataUrl)){
      const r = await cvInsignia(caja);
      guarda("insignia", r.dataUrl, "insignia.png");
    }
  }
  for (let i = 0; i < (caja.superpoderes || []).length; i++){
    const s = caja.superpoderes[i];
    const m = materialGuardado(caja, "sp-" + i);
    if (m && m.dataUrl) continue;
    const r = await cvIconoPoder(s.efecto, s.nombre);
    guarda("sp-" + i, r.dataUrl, "power_" + i + ".png");
  }
  if (caja.sala.musica !== "ninguna" && caja.sala.musica !== "propia"){
    const m = materialGuardado(caja, "sala-musica");
    if (!(m && m.dataUrl)){
      const r = await generaBso(caja);
      guarda("sala-musica", r.dataUrl, "bso.wav", "Compuesta por el Taller (WAV)");
    }
  }
  return n;
}

/* ---------- descarga real ---------- */
async function descargarPaquete(definitivo){
  const caja = actual;
  if (!caja) return;
  const enviar = async (ok) => {
    if (!ok) return;
    try {
      toast("🏗️ Construyendo el paquete real…");
      const paq = await construirPaquete(caja, definitivo);
      const nombreZip = (definitivo ? "campeonato-publicado-" : "campeonato-pruebas-") + paq.id + ".zip";
      const zip = zipDeArchivos(paq.files);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(zip);
      a.download = nombreZip;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      anotarEnDiario(caja.id, "Generó el paquete REAL " + (definitivo ? "DEFINITIVO (publicado)" : "de pruebas (listo)") + ": " + paq.files.length + " archivos.");
      guardarActual(true);
      toast("📦 " + nombreZip + " descargado (" + paq.files.length + " archivos)", "ok");
    } catch (e) {
      toast("No se pudo construir el paquete: " + (e && e.message ? e.message : e), "err");
    }
  };
  if (definitivo){
    const check = caja.checklist || [];
    const sin = 6 - check.filter(Boolean).length;
    const si = await preguntar("🏟️ Paquete definitivo",
      sin > 0
        ? "Ojo: tu lista de comprobación tiene " + sin + " punto" + (sin === 1 ? "" : "s") + " sin marcar. El paquete saldrá con «estado: publicado» (aparecerá en el menú del juego en cuanto lo montes). ¿Generar igualmente?"
        : "Tu lista de comprobación está completa. El paquete saldrá con «estado: publicado»: en cuanto copies la carpeta al juego aparecerá en el menú CAMPEONATOS. ¿Generar?",
      [{ texto: "Cancelar", valor: false }, { texto: "Sí, generar", valor: true, tipo: "primario" }]);
    await enviar(si);
  } else {
    const si = await preguntar("🔬 Paquete de pruebas",
      "Genera la carpeta championships/" + slug(caja.etiqueta) + " COMPLETA (manifest + módulo + arte + música + índice) con «estado: listo». La pruebas montándola en el juego y abriendo ?champ=" + slug(caja.etiqueta) + ". ¿Generar?",
      [{ texto: "Cancelar", valor: false }, { texto: "Sí, generar", valor: true, tipo: "primario" }]);
    await enviar(si);
  }
}
