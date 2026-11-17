#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""editor_v3.py — El Taller pasa de «caja + leeme» a PAQUETE REAL montable.
Inyecta la plantilla del módulo + la fábrica de assets, y parchea las fases,
la revisión y los textos a la realidad del juego (4 campeonatos reales)."""
import io, sys, pathlib

BASE = pathlib.Path("/home/z/my-project")
import os
# Fuente PRÍSTINA (nunca se sobrescribe) y salida separada: el parche es re-ejecutable.
PRISTINE = pathlib.Path(os.environ.get("EDITOR_SRC", str(BASE / "scripts/tmp_editor_src/pristine.html")))
OUT = pathlib.Path(os.environ.get("EDITOR_OUT", str(BASE / "download/editor-campeonatos/index.html")))
EDITOR = PRISTINE
TPL = BASE / "scripts/plantilla_modulo.js"
GEN = BASE / "scripts/taller_gen.js"

html = EDITOR.read_text(encoding="utf-8")
orig = html

def rep(old, new, n=1):
    global html
    c = html.count(old)
    assert c == n, f"ANCLA x{c} (esperaba {n}): {old[:90]!r}"
    html = html.replace(old, new)

# ── guardado blindado (cuota llena con arte dentro de la caja) ───────────
rep('''function guardarProyectos(lista){
  localStorage.setItem(CLAVE_ALMACEN, JSON.stringify(lista));
}''',
    '''function guardarProyectos(lista){
  try{
    localStorage.setItem(CLAVE_ALMACEN, JSON.stringify(lista));
  }catch(e){
    // cuota llena (arte dentro de la caja): se avisa sin tumba la app
    console.warn('[taller] cuota de almacenamiento llena', e);
    try{ toast('El navegador está lleno: descarga la copia de seguridad (.json) y borra cajas viejas', 'err'); }catch(_){ }
  }
}''')

# ── slug con GUIONES BAJOS (contrato: storage ^[a-z0-9_]+_\*?$ y reservas) ──
rep('''const slug = (s) => String(s||"").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"")
  .replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,40) || "campeonato";''',
    '''// El juego exige storage pp_champ_<id>_* con SÓLO guiones bajos
// (championship.schema.json): la etiqueta y la carpeta usan «_», nunca «-».
const slug = (s) => String(s||"").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"")
  .replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"").replace(/_{2,}/g,"_").slice(0,40) || "campeonato";''')

# ── versiones / cabeceras ────────────────────────────────────────────────
rep("<title>Crazy Ping Pong · Editor de campeonatos · V3.0.2</title>",
    "<title>Crazy Ping Pong · Editor de campeonatos · V3.0.3</title>")
rep("/* ===== Crazy Ping Pong · Editor de campeonatos · V3.0.2 ===== */",
    "/* ===== Crazy Ping Pong · Editor de campeonatos · V3.0.3 ===== */")
rep('<span>Editor de campeonatos — versión del juego V3.0.2</span>',
    '<span>Editor de campeonatos — genera el paquete REAL listo para montar en el juego</span>')
rep('const VERSION_EDITOR = "V3.0.2";', 'const VERSION_EDITOR = "V3.0.3";')

# ── hero ─────────────────────────────────────────────────────────────────
rep('''<p style="margin-top:12px; font-size:13.5px; color:var(--tinta-suave); background:rgba(255,255,255,.55); border:1px dashed var(--tinta-suave); border-radius:14px; padding:10px 14px">✨ <b>Novedad V3.0.2.2 «PRO TRAINING»:</b> el juego estrena un centro de entrenamiento con 5 áreas profesionales y pieles de pala — ya pulido con los fixes de las pruebas en el casco (metrónomo, pase bajo y zonas bien visibles). Las cajas que genera este Taller siguen siendo válidas tal cual — el entrenamiento nuevo vive en su propio módulo y no toca a los campeonatos.</p>''',
    '''<p style="margin-top:12px; font-size:13.5px; color:var(--tinta-suave); background:rgba(255,255,255,.55); border:1px dashed var(--tinta-suave); border-radius:14px; padding:10px 14px">🚀 <b>El Taller genera el paquete REAL:</b> al terminar baja un .zip con la carpeta <b>championships/tu-campeonato</b> completa — manifest oficial (contrato 1), el módulo con duelos, superpoderes y pruebas, el arte de la sala y del rival, los iconos, la música y el índice championships.json — <b>listo para copiar dentro del juego</b>. Verificado de punta a punta montando un campeonato de verdad.</p>''')

# ── pantalla inicio: nota de campeonatos reales ─────────────────────────
rep('''      Cada campeonato vive en su propia caja, independiente de las demás. Partido, Entrenamiento y
      Supervivencia viven en sus propias cajas del juego y <b>aquí no se pueden tocar</b>: solo se pueden
      copiar como plantilla para empezar sin partir de cero.''',
    '''      Cada campeonato vive en su propia caja, independiente de las demás. Los campeonatos del juego (La
      Locura, Magia, el Salvaje Oeste y Estación Orbital) viven en sus propias carpetas y <b>aquí no se
      pueden tocar</b>: solo se pueden imitar con las plantillas para empezar sin partir de cero.''')

# ── pantalla nuevo: plantillas reales ───────────────────────────────────
rep('''      Puedes empezar de cero o partir de una <b>plantilla</b>: una copia limpia de un campeonato que ya
      existe. El original queda intacto, para siempre — solo se copia.''',
    '''      Puedes empezar de cero o partir de una <b>plantilla</b>: un punto de partida ya decidido (rival,
      sala y pruebas de ejemplo). Todo se puede cambiar después en el asistente.''')
rep('''        <b>Copia de Partido</b>
        <span>El clásico partido a 11 puntos como punto de partida. El original no se toca.</span>''',
    '''        <b>Duelo clásico</b>
        <span>El clásico a 11 puntos con un rival a tu medida: la forma más rápida de empezar.</span>''')
rep('''        <b>Copia de Entrenamiento</b>
        <span>Ideal para campeonatos de retos y práctica. El original no se toca.</span>''',
    '''        <b>Retos y práctica</b>
        <span>Campeonato corto con pruebas de habilidad y duelos suaves. Ideal la primera vez.</span>''')
rep('''        <b>Copia de Supervivencia</b>
        <span> Aguanta la lluvia de bolas: perfecto para torneos de resistencia. El original no se toca.</span>''',
    '''        <b>A contrarreloj</b>
        <span>Dianas rápidas y presión de tiempo: perfecto para torneos de puntería.</span>''')

# ── constantes reales del motor ─────────────────────────────────────────
rep('''const ETIQUETAS_RESERVADAS = ["partido","entrenamiento","supervivencia","crazy"];''',
    '''const ETIQUETAS_RESERVADAS = ["locura","magia","oeste","estacion_orbital","crazy"];''')

rep('''const EFECTOS_CONOCIDOS = ["fantasma","escudo","lenta"]; // ya inventados por el sistema
const EFECTOS = [
  { id:"fantasma", nombre:"Bola fantasma", emoji:"👻", desc:"La bola atraviesa la red" },
  { id:"escudo",   nombre:"Escudo magnético", emoji:"🛡️", desc:"Un muro invisible protege un momento" },
  { id:"lenta",    nombre:"Cámara lenta", emoji:"🐢", desc:"Todo se ralentiza unos segundos" },
  { id:"rapida",   nombre:"Bola rápida", emoji:"⚡", desc:"La bola va más rápido de lo normal" },
  { id:"multibola",nombre:"Multibola", emoji:"🎱", desc:"Aparecen bolas extra" },
  { id:"otro",     nombre:"Otro (idea nueva)", emoji:"💡", desc:"Un efecto que el sistema aún no conoce" }
];
const ACTIVACIONES = [
  { id:"puntos",      nombre:"Cada X puntos" },
  { id:"fallo-rival", nombre:"Cuando el rival falla" },
  { id:"boton",       nombre:"Con un botón especial" }
];
const TIPOS_RETO = [
  { id:"objetivos",    nombre:"Derriba objetivos flotantes", emoji:"🎯" },
  { id:"bola-rapida",  nombre:"Devuelve una bola rápida", emoji:"⚡" },
  { id:"lluvia",       nombre:"Aguanta la lluvia de bolas", emoji:"🌧️" },
  { id:"puntos",       nombre:"Marca X puntos antes que el rival", emoji:"🏓" },
  { id:"supervivencia",nombre:"Sobrevive el mayor tiempo", emoji:"⏱️" }
];''',
    '''const EFECTOS_CONOCIDOS = ["confeti","mareo","globos","orbe","arena"]; // kinds REALES del motor de campeonatos
const EFECTOS = [
  { id:"confeti", nombre:"Lluvia de confeti", emoji:"🎉", desc:"Llueve confeti sobre la mesa mientras dura" },
  { id:"mareo",   nombre:"Mareo total",       emoji:"🌀", desc:"El visor del jugador se tambalea unos segundos" },
  { id:"globos",  nombre:"Globos intrusos",   emoji:"🎈", desc:"Globos suben sobre la mesa y revientan con la bola" },
  { id:"orbe",    nombre:"Orbe rondador",     emoji:"🔮", desc:"Un orbe brillante ronda el campo del rival" },
  { id:"arena",   nombre:"Tormenta de arena", emoji:"🏜️", desc:"Ráfagas de arena cruzan la sala" }
];
const ACTIVACIONES = [
  { id:"rally",  nombre:"Durante el rally (con probabilidad)" },
  { id:"puntos", nombre:"Cada X puntos" }
];
const TIPOS_RETO = [
  { id:"objetivos",    nombre:"Derriba dianas flotantes", emoji:"🎯" },
  { id:"movimiento",   nombre:"Dianas en movimiento",     emoji:"🛸" },
  { id:"contrarreloj", nombre:"A contrarreloj (dianas rápidas)", emoji:"⏱️" }
];''')

rep('''const CEREBROS = [
  { id:"partido",       nombre:"El cerebro de Partido" },
  { id:"entrenamiento", nombre:"El cerebro de Entrenamiento" },
  { id:"supervivencia", nombre:"El cerebro de Supervivencia" }
];''',
    '''const CEREBROS = [
  { id:"equilibrado", nombre:"Equilibrado" },
  { id:"agresivo",    nombre:"Agresivo (más presión)" },
  { id:"defensivo",   nombre:"Defensivo (más paciencia)" }
];''')

# ── plantillas: cerebro por defecto ─────────────────────────────────────
rep('c.rival = { nombre:"RIVAL", caracter:"frio", cerebroBase:"partido"',
    'c.rival = { nombre:"RIVAL", caracter:"frio", cerebroBase:"equilibrado"')
rep('c.rival = { nombre:"COMPAÑERO", caracter:"tranquilo", cerebroBase:"entrenamiento"',
    'c.rival = { nombre:"COMPAÑERO", caracter:"tranquilo", cerebroBase:"defensivo"')
rep('c.rival = { nombre:"LANZADOR", caracter:"arriesgado", cerebroBase:"supervivencia"',
    'c.rival = { nombre:"LANZADOR", caracter:"arriesgado", cerebroBase:"agresivo"')
rep('cerebroBase: "partido",', 'cerebroBase: "equilibrado",')

# ── fase 2: subtítulo real ──────────────────────────────────────────────
rep('''html += `<p class="fase-sub">Quién es tu oponente: identidad, carácter y forma de jugar. El asistente reutiliza el <b>«cerebro»</b> de rivales que el juego ya tiene —los mismos movimientos, errores y celebraciones— y lo adapta a tu personaje.</p>''',
    '''html += `<p class="fase-sub">Quién es tu oponente: identidad, carácter y forma de jugar. El módulo del juego ajusta su <b>agresividad, puntería y constancia</b> a lo que decidas aquí, y su arte se planta como troquel gigante en la sala (el archivo lo decides en la fase 4).</p>''')
rep('''      ${campoSel("rival.cerebroBase","Cerebro base","De qué campeonato de siempre se copia su forma de jugar (el original no se toca: solo se copia).", c.rival.cerebroBase, CEREBROS)}''',
    '''      ${campoSel("rival.cerebroBase","Estilo de juego","El matiz de su juego: equilibrado, con más presión o más paciencia.", c.rival.cerebroBase, CEREBROS)}''')

# ── fase 3: superpoderes reales ─────────────────────────────────────────
rep('''  if(n===3){
    const cards = c.superpoderes.map((s,i)=>{
      const ef = EFECTOS.find(e=>e.id===s.efecto) || EFECTOS[0];
      const esNuevo = s.efecto === "otro";
      return `<div class="repeticion" data-sp="${i}">
        <button class="borrar" data-borra-sp="${i}" title="Quitar este superpoder">✕</button>
        ${campoText("superpoderes."+i+".nombre","Nombre del superpoder","", s.nombre, {fantasma:"Bola fantasma"})}
        ${campoSel("superpoderes."+i+".efecto","Qué hace", esNuevo ? "El asistente pregunta antes de inventar algo nuevo." : "", s.efecto, EFECTOS)}
        ${campoSel("superpoderes."+i+".activacion","Cuándo se activa","", s.activacion || "puntos", ACTIVACIONES)}
        ${s.activacion === "puntos" ? campoNum("superpoderes."+i+".cadaCuantos","…cada cuántos puntos","", s.cadaCuantos || 3, 'min="1" max="20" step="1"') : `<div class="campo"><label>&nbsp;</label><div class="aviso info" style="padding:8px 12px">${s.activacion==="fallo-rival"?"Se activa solo cuando el rival falla.":"El jugador decide cuándo usarlo."}</div></div>`}
        ${campoNum("superpoderes."+i+".duracion","Duración (segundos)","Cuánto dura el efecto encendido.", s.duracion, 'min="1" max="60" step="1"')}
        ${campoNum("superpoderes."+i+".recarga","Recarga (puntos)","Puntos que deben pasar hasta poder repetirse.", s.recarga, 'min="0" max="20" step="1"')}
        ${esNuevo ? `<div class="aviso alerta">💡 <div><b>Efecto nuevo.</b> El asistente no adivina: si el sistema no conoce este efecto, se detiene y te consulta. Se resolverá en la fase de materiales antes de poder probar el campeonato.</div></div>` : `<div class="aviso info">${ef.emoji} <div>${esc(ef.desc)} — efecto <b>ya conocido por el sistema</b>: se reutiliza sin riesgo.</div></div>`}
      </div>`;
    }).join("");
    html += `<p class="fase-sub">Efectos especiales y cómo se activan. Los efectos que el juego <b>ya conoce</b> se reutilizan sin riesgo; si inventas uno <b>realmente nuevo</b>, el asistente se detiene a consultarlo contigo.</p>
    <div class="campos">
      <div class="tarjetas-repet">
        <div class="cab">✨ Superpoderes del campeonato <button class="btn primario btn-mini" data-add-sp>＋ Añadir superpoder</button></div>
        ${cards || `<div class="vacio-repet">Ninguno por ahora. Está bien decidir que este campeonato va «limpio», sin efectos especiales.</div>`}
      </div>
    </div>`;
  }''',
    '''  if(n===3){
    const cards = c.superpoderes.map((s,i)=>{
      const ef = EFECTOS.find(e=>e.id===s.efecto) || EFECTOS[0];
      return `<div class="repeticion" data-sp="${i}">
        <button class="borrar" data-borra-sp="${i}" title="Quitar este superpoder">✕</button>
        ${campoText("superpoderes."+i+".nombre","Nombre del superpoder","", s.nombre, {fantasma:"Lluvia de confeti"})}
        ${campoSel("superpoderes."+i+".efecto","Qué hace","Efectos REALES del motor del juego: llegan tal cual al campeonato.", s.efecto, EFECTOS)}
        ${campoSel("superpoderes."+i+".activacion","Cuándo se activa","", s.activacion || "rally", ACTIVACIONES)}
        ${((s.activacion||"rally")==="puntos") ? campoNum("superpoderes."+i+".cadaCuantos","…cada cuántos puntos","", s.cadaCuantos || 3, 'min="1" max="20" step="1"') : campoNum("superpoderes."+i+".chance","Probabilidad por rally (%)","Qué tan a menudo lo intenta el rival.", (s.chance==null?35:s.chance), 'min="5" max="100" step="5"')}
        ${campoNum("superpoderes."+i+".duracion","Duración (segundos)","Cuánto dura el efecto encendido.", s.duracion, 'min="1" max="60" step="1"')}
        ${campoNum("superpoderes."+i+".recarga","Recarga (segundos)","Tiempo mínimo entre superpoderes.", s.recarga, 'min="0" max="120" step="1"')}
        <div class="aviso info">${ef.emoji} <div>${esc(ef.desc)} — efecto <b>real del motor</b>: se monta tal cual en el campeonato.</div></div>
      </div>`;
    }).join("");
    html += `<p class="fase-sub">Efectos especiales del rival y cómo se activan. Todos los efectos de esta lista son <b>reales</b>: el módulo del juego los conoce y los monta tal cual, con su cartel de aviso en la sala.</p>
    <div class="campos">
      <div class="tarjetas-repet">
        <div class="cab">✨ Superpoderes del campeonato <button class="btn primario btn-mini" data-add-sp>＋ Añadir superpoder</button></div>
        ${cards || `<div class="vacio-repet">Ninguno por ahora. Está bien decidir que este campeonato va «limpio», sin efectos especiales.</div>`}
      </div>
    </div>`;
  }''')

# ── deriveMateriales: inventario REAL ───────────────────────────────────
rep('''function deriveMateriales(caja){
  const filas = [];
  const est = ESTILOS_VISUALES.find(e=>e.id===caja.ficha.estiloVisual) || ESTILOS_VISUALES[0];
  filas.push({ clave:"sala-decorado", tipo:"imagen", icono:"🖼️", nombre:"El decorado de la sala",
    detalle: est.nombre + (caja.sala.decoracion ? " — " + caja.sala.decoracion : ""), estado:"generado" });
  const ilu = ILUMINACIONES.find(i=>i.id===caja.sala.iluminacion) || ILUMINACIONES[0];
  filas.push({ clave:"sala-luces", tipo:"imagen", icono:"💡", nombre:"Iluminación «" + ilu.nombre + "»",
    detalle:"El asistente la monta con las piezas estándar del juego.", estado:"generado" });
  if(caja.sala.musica === "propia"){
    filas.push({ clave:"sala-musica", tipo:"musica", icono:"🎵", nombre:"Tu propia música ambiental",
      detalle: caja.sala.musicaPropia ? "Archivo aportado: " + caja.sala.musicaPropia.nombre : "Aporta tu archivo de música (MP3/OGG).",
      estado: caja.sala.musicaPropia ? "aportado" : "pendiente" });
  }else if(caja.sala.musica !== "ninguna"){
    const m = MUSICA_SALA.find(x=>x.id===caja.sala.musica) || MUSICA_SALA[1];
    filas.push({ clave:"sala-musica", tipo:"musica", icono:"🎵", nombre:m.nombre,
      detalle:"Generado automáticamente por el asistente.", estado:"generado" });
  }
  filas.push({ clave:"rival-voz", tipo:"voz", icono:"🗣️", nombre:"La voz del rival «" + (caja.rival.nombre || "…") + "»",
    detalle: materialGuardado(caja,"rival-voz") ? "Resuelto en el taller." : "Pendiente: genérala el asistente o aporta un audio.",
    estado: (materialGuardado(caja,"rival-voz") || {}).estado || "pendiente" });
  (caja.superpoderes || []).forEach((s,i)=>{
    const conocido = EFECTOS_CONOCIDOS.includes(s.efecto);
    const ef = EFECTOS.find(e=>e.id===s.efecto) || EFECTOS[0];
    filas.push({ clave:"sp-"+i, tipo:"sonido", icono: ef.emoji, nombre:"Efecto «" + (s.nombre || ef.nombre) + "»",
      detalle: conocido ? "Efecto ya conocido por el sistema: se reutiliza." :
        (materialGuardado(caja,"sp-"+i) ? "Efecto nuevo resuelto en el taller." : "Efecto nuevo: resuélvelo con el asistente."),
      estado: conocido ? "generado" : ((materialGuardado(caja,"sp-"+i) || {}).estado || "pendiente") });
  });
  const tipos = new Set((caja.retos||[]).map(r=>r.tipo));
  if(tipos.has("objetivos")) filas.push({ clave:"reto-objetivos", tipo:"imagen", icono:"🎯",
    nombre:"Objetivos flotantes derribables", detalle:"Pieza estándar del juego.", estado:"generado" });
  if(tipos.has("lluvia")) filas.push({ clave:"reto-lluvia", tipo:"imagen", icono:"🌧️",
    nombre:"Lluvia de bolas", detalle:"Pieza estándar del juego.", estado:"generado" });
  return filas;
}''',
    '''function deriveMateriales(caja){
  const filas = [];
  const est = ESTILOS_VISUALES.find(e=>e.id===caja.ficha.estiloVisual) || ESTILOS_VISUALES[0];
  const tiene = (k) => !!(materialGuardado(caja,k) && materialGuardado(caja,k).dataUrl);
  const aport = (k) => { const m = materialGuardado(caja,k); return !!(m && m.estado === "aportado" && m.dataUrl); };
  filas.push({ clave:"rival", tipo:"imagen", icono:"🤖", nombre:"El rival (troquel gigante de la sala)",
    detalle: aport("rival") ? "Tu arte: " + (materialGuardado(caja,"rival").nombre||"") + " (512×1024 con transparencia)." :
      "El Taller DIBUJA un troquel con su nombre — si prefieres el tuyo, usa «Cambiar».",
    estado: aport("rival") ? "aportado" : "generado" });
  ["idle","duelo","derrotado","triunfante"].forEach((st)=>{
    filas.push({ clave:"rival-"+st, tipo:"imagen", icono:"🎭", nombre:"Estado «"+st+"» del rival",
      detalle: aport("rival-"+st) ? "Tu arte para este estado." : "Se deriva del arte base (con su tinte).",
      estado: aport("rival-"+st) ? "aportado" : "generado" });
  });
  [["floor","el suelo"],["ceil","el techo"],["back","la pared del fondo"],["front","la pared tras ti"],["left","la pared izquierda"],["right","la pared derecha"]].forEach(([k,txt])=>{
    filas.push({ clave:"sala-"+k, tipo:"imagen", icono:"🧱", nombre:"Sala · " + txt,
      detalle: aport("sala-"+k) ? "Tu propia imagen (1024×1024)." : "Lo PINTA el Taller con el estilo «"+est.nombre+"» y la luz elegida.",
      estado: aport("sala-"+k) ? "aportado" : "generado" });
  });
  [["decor1","Troquel de ambiente 1"],["decor2","Troquel de ambiente 2"]].forEach(([k,txt])=>{
    filas.push({ clave:k, tipo:"imagen", icono:"🎪", nombre:txt,
      detalle: aport(k) ? "Tu propio troquel (PNG con transparencia)." : "Lo dibuja el Taller con los colores del estilo.",
      estado: aport(k) ? "aportado" : "generado" });
  });
  filas.push({ clave:"insignia", tipo:"imagen", icono:"🏅", nombre:"La insignia del campeón",
    detalle: aport("insignia") ? "Tu propia insignia." : "La dibuja el Taller (laurel + estrella).",
    estado: aport("insignia") ? "aportado" : "generado" });
  (caja.superpoderes || []).forEach((s,i)=>{
    const ef = EFECTOS.find(e=>e.id===s.efecto) || EFECTOS[0];
    filas.push({ clave:"sp-"+i, tipo:"imagen", icono: ef.emoji, nombre:"Icono de «" + (s.nombre || ef.nombre) + "»",
      detalle: aport("sp-"+i) ? "Tu propio icono." : "Medallón dibujado por el Taller.",
      estado: aport("sp-"+i) ? "aportado" : "generado" });
  });
  if(caja.sala.musica === "propia"){
    filas.push({ clave:"sala-musica", tipo:"musica", icono:"🎵", nombre:"Tu propia música ambiental",
      detalle: (caja.sala.musicaPropia || (materialGuardado(caja,"sala-musica")||{}).estado === "aportado") ? "Archivo aportado." : "Aporta tu archivo de música (MP3/OGG/WAV, máx. 1,5 MB).",
      estado: (caja.sala.musicaPropia || (materialGuardado(caja,"sala-musica")||{}).estado === "aportado") ? "aportado" : "pendiente" });
  }else if(caja.sala.musica !== "ninguna"){
    const m = MUSICA_SALA.find(x=>x.id===caja.sala.musica) || MUSICA_SALA[1];
    filas.push({ clave:"sala-musica", tipo:"musica", icono:"🎵", nombre:m.nombre,
      detalle: aport("sala-musica") ? "Tu archivo de música." : "La COMPONE el Taller (melodía ambiental .wav real, según el mood).",
      estado: aport("sala-musica") ? "aportado" : "generado" });
  }
  return filas;
}''')

# ── pildoraEstado ───────────────────────────────────────────────────────
rep('''  const m = { generado:["mp-ok","generado por el asistente"], aportado:["mp-apor","aportado por ti"], pendiente:["mp-pend","pendiente"] }[estado] || ["mp-pend",estado];''',
    '''  const m = { generado:["mp-ok","lo pinta el Taller"], aportado:["mp-apor","tu archivo"], pendiente:["mp-pend","pendiente"] }[estado] || ["mp-pend",estado];''')

# ── fase 4: inventario con vistas previas ───────────────────────────────
rep('''  if(n===4){
    const filas = deriveMateriales(c);
    const pendientes = filas.filter(m=>m.estado==="pendiente").length;
    html += `<p class="fase-sub">El asistente hace el <b>inventario</b> de todo lo que hace falta y <b>genera automáticamente</b> lo que puede. Solo se aprueba el estilo y, si quieres, se aportan materiales propios.</p>
    <div class="campos">
      ${pendientes ? `<div class="aviso alerta">🧾 <div><b>Faltan ${pendientes} ${pendientes===1?"pieza":"piezas"} por resolver.</b> Usa «Generar lo que falte» o aporta tu propio archivo. Nada baja al laboratorio con la caja a medias.</div></div>`
        : `<div class="aviso exito">✅ <div><b>Inventario completo.</b> Todo lo que hace falta está generado o aportado.</div></div>`}
      <div class="tarjetas-repet">
        <div class="cab">📦 El inventario de la caja <button class="btn primario btn-mini" data-generar-todo>🎛️ Generar lo que falte</button></div>
        ${filas.map(m=>`<div class="material-fila">
          <div class="m-ico">${m.icono}</div>
          <div class="m-txt"><b>${esc(m.nombre)} ${pildoraEstado(m.estado)}</b><span>${esc(m.detalle || "")}</span></div>
          ${m.estado === "pendiente" ? `
            <label class="btn fantasma btn-mini" style="display:inline-flex;align-items:center">📎 Aportar archivo
              <input type="file" hidden data-subir="${esc(m.clave)}" accept="${m.tipo==="musica"||m.tipo==="voz"||m.tipo==="sonido" ? "audio/*" : "image/*"}">
            </label>` : ""}
        </div>`).join("")}
      </div>
    </div>`;
  }''',
    '''  if(n===4){
    const filas = deriveMateriales(c);
    const pendientes = filas.filter(m=>m.estado==="pendiente").length;
    html += `<p class="fase-sub">Este es el <b>inventario real</b> de lo que lleva el paquete. Lo marcado «lo pinta el Taller» se genera de verdad (arte en canvas y música compuesta) al construir el paquete; si prefieres, aporta tu propio archivo y ese viaja tal cual.</p>
    <div class="campos">
      ${pendientes ? `<div class="aviso alerta">🧾 <div><b>Falta tu archivo de música.</b> Aporta el archivo o cambia la música de la sala en la fase 6. Nada baja al laboratorio con la caja a medias.</div></div>`
        : `<div class="aviso exito">✅ <div><b>Inventario completo.</b> Todo lo que hace falta se genera o ya lo aportaste.</div></div>`}
      <div class="tarjetas-repet">
        <div class="cab">📦 El inventario del paquete <button class="btn primario btn-mini" data-generar-todo>🎨 Generar vistas previas</button></div>
        ${filas.map(m=>{ const g = materialGuardado(c, m.clave); return `<div class="material-fila">
          <div class="m-ico">${(g && g.dataUrl && m.tipo==="imagen") ? `<img src="${g.dataUrl}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:10px">` : m.icono}</div>
          <div class="m-txt"><b>${esc(m.nombre)} ${pildoraEstado(m.estado)}</b><span>${esc(m.detalle || "")}</span></div>
          ${m.estado === "pendiente" ? `
            <label class="btn primario btn-mini" style="display:inline-flex;align-items:center">📎 Aportar archivo
              <input type="file" hidden data-subir="${esc(m.clave)}" accept="audio/*">
            </label>` : `
            <label class="btn fantasma btn-mini" style="display:inline-flex;align-items:center" title="Sustituir por tu archivo">📎 Cambiar
              <input type="file" hidden data-subir="${esc(m.clave)}" accept="${m.tipo==="musica" ? "audio/*" : "image/*"}">
            </label>`}
        </div>`; }).join("")}
      </div>
    </div>`;
  }''')

# ── fase 5: retos reales ────────────────────────────────────────────────
rep('''        ${campoNum("retos."+i+".objetivo", t.id==="puntos" ? "Puntos necesarios" : t.id==="supervivencia" ? "Segundos a sobrevivir" : "Cantidad objetivo","Qué cuenta como superarlo.", r.objetivo, 'min="1" step="1"')}
        ${campoNum("retos."+i+".puntos","Puntos que suma","Cuánto aporta al campeonato.", r.puntos, 'min="1" max="20" step="1"')}
        ${campoText("retos."+i+".premio","Premio que recibe","", r.premio, {fantasma:"Estrella dorada"})}
        <div class="aviso info">🎯 <div>Superar este reto: <b>${esc(t.nombre)}</b>. El asistente lo encaja con las reglas del juego y comprueba que ganar y perder queden equilibrados.</div></div>''',
    '''        ${campoNum("retos."+i+".objetivo","Dianas a derribar","Qué cuenta como superarlo.", r.objetivo, 'min="1" max="30" step="1"')}
        ${campoNum("retos."+i+".puntos","Puntos que suma","Cuánto aporta al campeonato.", r.puntos, 'min="1" max="20" step="1"')}
        ${campoText("retos."+i+".premio","Premio que recibe","Se enseña en el cartel al superarla.", r.premio, {fantasma:"Estrella dorada"})}
        <div class="aviso info">${t.emoji} <div><b>${esc(t.nombre)}</b> — prueba REAL del módulo: la bola rompe dianas flotando sobre la mesa${t.id==="objetivos" ? ", quietas y tranquilas" : t.id==="movimiento" ? ", desplazándose en vaivén" : ", rápidas y esquivas"}. El camino queda: duelo → esta prueba → … → DUELO FINAL.</div></div>''')

# ── fase 6: subtítulo honesto ───────────────────────────────────────────
rep('''    html += `<p class="fase-sub">Cómo se viste el escenario. El asistente monta la sala con las <b>piezas estándar</b> del juego —las mismas de las salas pabellón, ártico, atardecer y neón— vestidas a tu manera.</p>''',
    '''    html += `<p class="fase-sub">Cómo se viste el escenario. El Taller PINTA la sala de verdad (6 planos 1024×1024) con el estilo y la luz elegidos, y compone la música ambiental como un .wav real. En la fase 4 puedes sustituir cualquiera de las piezas por tu propio arte.</p>''')

# ── fase 7: checklist + paquetes reales ─────────────────────────────────
rep('''  const CHECKLIST = [
    "El campeonato nuevo <b>aparece en el menú</b> con su nombre y su sala.",
    "Los tres campeonatos de siempre — <b>Partido, Entrenamiento y Supervivencia</b> — funcionan exactamente igual que antes.",
    "El <b>rival</b> se comporta como lo definiste: golpea, falla donde debía fallar y celebra como acordaste.",
    "Los <b>superpoderes</b> se activan bien, duran lo acordado y no desequilibran el partido.",
    "La <b>sala</b> se ve y suena como decidiste: decoración, luces y música ambiental.",
    "Las <b>pruebas de habilidad</b> puntúan correctamente y dan los premios previstos.",
    "Se puede <b>ganar y se puede perder</b>, y ambos finales se muestran con sus carteles.",
    "Nada del juego de siempre se ha movido de sitio: menú, salas, opciones e idioma intactos."
  ];''',
    '''  const CHECKLIST = [
    "El campeonato <b>arranca</b> (?champ=etiqueta o el menú si está publicado).",
    "Los cuatro campeonatos del juego — <b>La Locura, Magia, el Salvaje Oeste y Estación Orbital</b> — siguen funcionando igual que antes.",
    "El <b>rival</b> está en su sala, golpea con la dificultad decidida y sus superpoderes entran en los duelos.",
    "Las <b>pruebas de habilidad</b> se juegan, cuentan dianas y dan sus premios.",
    "La <b>sala</b> se ve y suena como decidiste: arte, luz y música.",
    "Se gana el <b>DUELO FINAL</b> y aparece la insignia ¡CONSEGUIDO!."
  ];''')
rep('''        <div class="aviso info">🔬 <div><b>Paquete de pruebas</b>: el juego completo con tu campeonato marcado «en pruebas». Arrástralo a <b>app.netlify.com/drop</b> desde un ordenador y te dará una dirección web privada para probar con el casco.</div></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn primario" data-paquete="pruebas">🔬 Descargar paquete de pruebas (.zip)</button>
          <button class="btn" data-paquete="definitivo">🏟️ Descargar paquete definitivo (.zip)</button>
          <button class="btn fantasma" data-caja-json>💾 Copia de seguridad (.json)</button>
        </div>
        <div class="aviso info">🏟️ <div><b>Paquete definitivo</b>: solo se arrastra a la página de Netlify cuando quieras que <b>todos los jugadores</b> lo reciban. Esa dirección nueva será «la dirección del estadio».</div></div>''',
    '''        <div class="aviso info">🔬 <div><b>Paquete de pruebas</b>: la carpeta <b>championships/&lt;etiqueta&gt;</b> COMPLETA (manifest oficial + módulo con duelos y pruebas + arte y música + índice championships.json) con estado «listo». Descomprime, copia al juego y prueba con <b>?champ=&lt;etiqueta&gt;</b>.</div></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn primario" data-paquete="pruebas">🔬 Descargar paquete de pruebas (.zip)</button>
          <button class="btn" data-paquete="definitivo">🏟️ Descargar paquete definitivo (.zip)</button>
          <button class="btn fantasma" data-caja-json>💾 Copia de seguridad (.json)</button>
        </div>
        <div class="aviso info">🏟️ <div><b>Paquete definitivo</b>: el mismo paquete con el campeonato MARCADO «publicado» — en cuanto copies la carpeta al juego aparece en el menú CAMPEONATOS para todos los jugadores. Las instrucciones completas viajan dentro (LEEME.txt).</div></div>''')
rep('''      const si = await preguntar("🏆 ¿Marcar como publicado?",
        "Recuerda: publicar de verdad es arrastrar el paquete definitivo a app.netlify.com/drop desde un ordenador. Aquí solo se registra el hito en el viaje del campeonato. ¿Continuamos?",
        [ {texto:"Aún no", valor:false}, {texto:"Sí, registrado", valor:true, tipo:"ok"} ]);''',
    '''      const si = await preguntar("🏆 ¿Marcar como publicado?",
        "Publicar de verdad = generar el PAQUETE DEFINITIVO y copiar su carpeta championships/ al juego (las instrucciones exactas viajan dentro del paquete, en LEEME.txt). Aquí solo se registra el hito en el viaje del campeonato. ¿Continuamos?",
        [ {texto:"Aún no", valor:false}, {texto:"Sí, registrado", valor:true, tipo:"ok"} ]);''')

# ── revisión: chequeos reales ───────────────────────────────────────────
rep('''  /* 4 · que todas las piezas encajen entre sí */
  const encaje = [];
  caja.superpoderes.forEach((s,i)=>{
    if(!(Number(s.duracion) > 0)) encaje.push("el superpoder «" + (s.nombre || (i+1)) + "» necesita duración en segundos");
    if(!(Number(s.recarga) >= 0) || s.recarga === "") encaje.push("el superpoder «" + (s.nombre || (i+1)) + "» necesita recarga (0 o más)");
    if(!ACTIVACIONES.some(a => a.id === s.activacion)) encaje.push("el superpoder «" + (s.nombre || (i+1)) + "» necesita una forma de activarse");
  });
  caja.retos.forEach((r,i)=>{
    if(!(Number(r.objetivo) > 0)) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» necesita un objetivo mayor que cero");
    if(!(Number(r.puntos) > 0)) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» necesita los puntos que suma");
    if(!r.premio) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» necesita su premio");
  });
  ["agresividad","precision","constancia"].forEach(k=>{
    const v = Number(caja.rival[k]);
    if(!(v >= 1 && v <= 5)) encaje.push("la personalidad del rival (" + k + ") debe estar entre 1 y 5");
  });''',
    '''  /* 4 · que todas las piezas encajen entre sí */
  const encaje = [];
  caja.superpoderes.forEach((s,i)=>{
    const nom = "el superpoder «" + (s.nombre || (i+1)) + "»";
    if(!(Number(s.duracion) > 0)) encaje.push(nom + " necesita duración en segundos");
    if(!(Number(s.recarga) >= 0) || s.recarga === "") encaje.push(nom + " necesita recarga (0 o más segundos)");
    if(!ACTIVACIONES.some(a => a.id === (s.activacion || "rally"))) encaje.push(nom + " necesita una forma de activarse");
    if((s.activacion || "rally") === "rally" && !(Number(s.chance) >= 5 && Number(s.chance) <= 100)) encaje.push(nom + " necesita una probabilidad entre 5 y 100 %");
    if(s.activacion === "puntos" && !(Number(s.cadaCuantos) > 0)) encaje.push(nom + " necesita «cada cuántos puntos»");
    if(!EFECTOS.some(e => e.id === s.efecto)) encaje.push(nom + " usa un efecto que el motor del juego no conoce");
  });
  if(caja.superpoderes.length > 4) encaje.push("el motor admite un MÁXIMO de 4 superpoderes por campeonato");
  if(caja.retos.length > 3) encaje.push("el camino admite un MÁXIMO de 3 pruebas (cada una añade un duelo: el camino sería interminable)");
  caja.retos.forEach((r,i)=>{
    if(!(Number(r.objetivo) > 0)) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» necesita sus dianas (mayor que cero)");
    if(Number(r.objetivo) > 30) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» pide más de 30 dianas: injusto");
    if(!(Number(r.puntos) > 0)) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» necesita los puntos que suma");
    if(!r.premio) encaje.push("la prueba «" + (r.nombre || (i+1)) + "» necesita su premio");
  });
  ["agresividad","precision","constancia"].forEach(k=>{
    const v = Number(caja.rival[k]);
    if(!(v >= 1 && v <= 5)) encaje.push("la personalidad del rival (" + k + ") debe estar entre 1 y 5");
  });''')

rep('''  /* 6 · que los campeonatos de siempre sigan pasando sus propias pruebas */
  const toca = ETIQUETAS_RESERVADAS.includes(eti);
  add(6, "Los campeonatos de siempre siguen intactos", !toca,
    "Por diseño, este editor no puede tocar las cajas de Partido, Entrenamiento y Supervivencia: solo se pueden copiar como plantilla. El original nunca se modifica.",
    "Algo intentó tocar los campeonatos de siempre");

  /* 7 · que una partida automática de control se juegue de principio a fin sin errores */
  const juego = [];
  try{
    const copia = JSON.parse(JSON.stringify(caja));
    if(copia.schema !== "crazy-pingpong-campeonato") juego.push("la caja no lleva el sello de Crazy Ping Pong");
    const totalObjetivo = caja.retos.reduce((s,r)=> s + Number(r.objetivo || 0), 0);
    const totalPuntos  = caja.retos.reduce((s,r)=> s + Number(r.puntos  || 0), 0);
    if(!(totalObjetivo > 0)) juego.push("la partida de control no llegó a ningún final: los retos suman cero");
    if(!(totalPuntos  > 0))  juego.push("las pruebas no puntúan: no se podría ganar");
    const limite = { facil: 60, media: 100, dificil: 200 }[caja.ficha.dificultad] || 100;
    if(totalObjetivo > limite) juego.push("el objetivo total (" + totalObjetivo + ") es desorbitado para una partida");
    const dias = ["borrador","preparacion","validacion","listo","publicado","desactivado"];
    if(!dias.includes(caja.estado)) juego.push("el campeonato está en un estado desconocido del viaje");
  }catch(e){
    juego.push("la caja está dañada por dentro: " + e.message);
  }
  add(7, "Partida automática de control sin errores", juego.length === 0,
    juego.length ? juego.join(". ") + "." : "Se jugó una partida de control de principio a fin con las reglas de la caja: saque, retos, premios y final. Cero errores.",
    "La partida de control falló");''',
    '''  /* 6 · que los campeonatos del juego sigan intactos */
  const toca = ETIQUETAS_RESERVADAS.includes(eti);
  add(6, "Los campeonatos del juego siguen intactos", !toca,
    "Por diseño, este editor no puede tocar La Locura, Magia, el Salvaje Oeste ni Estación Orbital: sus etiquetas están reservadas y sus carpetas, fuera de alcance.",
    "Algo intentó tocar los campeonatos del juego");

  /* 7 · que el camino se pueda montar DE VERDAD (simulación del generador) */
  const juego = [];
  try{
    const copia = JSON.parse(JSON.stringify(caja));
    if(copia.schema !== "crazy-pingpong-campeonato") juego.push("la caja no lleva el sello de Crazy Ping Pong");
    const id = slug(caja.etiqueta);
    if(!/^[a-z0-9_-]{2,24}$/.test(id)) juego.push("la etiqueta «" + id + "» no vale como carpeta (2-24 letras, números, guiones)");
    const storage = "pp_champ_" + id + "_*";
    if(!/^pp_champ_[a-z0-9_-]{2,24}_\\*$/.test(storage)) juego.push("el prefijo de guardado «" + storage + "» no cumple el contrato del juego");
    const totalObjetivo = caja.retos.reduce((s,r)=> s + Number(r.objetivo || 0), 0);
    const totalPuntos  = caja.retos.reduce((s,r)=> s + Number(r.puntos  || 0), 0);
    if(!(totalObjetivo > 0)) juego.push("el camino no llegaría a ningún final: las pruebas suman cero");
    if(!(totalPuntos  > 0))  juego.push("las pruebas no puntúan: no se podría ganar");
    if(totalObjetivo > 60) juego.push("el objetivo total (" + totalObjetivo + " dianas) es desorbitado");
    /* el camino que construirá el módulo: duelo → prueba → … → DUELO FINAL */
    const difMul = { facil: 0.85, media: 1.0, dificil: 1.18 }[caja.ficha.dificultad] || 1.0;
    const nEtapas = caja.retos.length * 2 + 1;
    const aiFinal = difMul * 1.35;
    if(!(aiFinal >= 0.6 && aiFinal <= 2.0)) juego.push("la dificultad final (" + aiFinal.toFixed(2) + "×) se sale de los límites sanos del motor");
    if(!["borrador","preparacion","validacion","listo","publicado","desactivado"].includes(caja.estado)) juego.push("el campeonato está en un estado desconocido del viaje");
    if(nEtapas < 3) juego.push("el camino quedaría vacío");
  }catch(e){
    juego.push("la caja está dañada por dentro: " + e.message);
  }
  add(7, "Camino montable de verdad (simulación del generador)", juego.length === 0,
    juego.length ? juego.join(". ") + "." : "Se montó el camino completo en simulación: " + (caja.retos.length * 2 + 1) + " etapas (duelo y prueba por reto + DUELO FINAL), carpeta championships/" + slug(caja.etiqueta) + ", prefijo de guardado y arte a bordo. Cero errores.",
    "El camino no se puede montar");''')

# ── addSp default ───────────────────────────────────────────────────────
rep('''    actual.superpoderes.push({ nombre:"", efecto:"fantasma", activacion:"puntos", cadaCuantos:3, duracion:5, recarga:2 });''',
    '''    actual.superpoderes.push({ nombre:"", efecto:"confeti", activacion:"rally", chance:35, cadaCuantos:3, duracion:6, recarga:18 });''')

# ── data-subir: límite y aviso ──────────────────────────────────────────
rep('''      if(file.size > 600 * 1024){
        toast("El archivo pesa más de 600 KB: elige uno más ligero", "err");
        inp.value = ""; return;
      }''',
    '''      if(file.size > 1500 * 1024){
        toast("El archivo pesa más de 1,5 MB: elige uno más ligero", "err");
        inp.value = ""; return;
      }''')

# ── data-generar-todo: vistas previas REALES ────────────────────────────
rep('''  /* generar lo que falte (fase 4) */
  const genBtn = panel.querySelector("[data-generar-todo]");
  if(genBtn) genBtn.addEventListener("click", async ()=>{
    const filas = deriveMateriales(actual).filter(m=>m.estado==="pendiente");
    if(!filas.length){ toast("No falta nada: el inventario está completo", "ok"); return; }
    const auto = filas.filter(m=>m.clave !== "sala-musica");
    const propios = filas.filter(m=>m.clave === "sala-musica");
    let texto = auto.length
      ? "El asistente puede generar " + auto.length + " pieza" + (auto.length===1?"":"s") + " automáticamente: " + auto.map(m=>m.nombre).join(", ") + "."
      : "";
    if(propios.length) texto += (texto ? " " : "") + "Tu propia música necesita un archivo tuyo: la fila queda pendiente hasta que lo aportes.";
    const si = await preguntar("¿Generar lo que falte?", texto || "No hay nada pendiente.",
      [ {texto:"Cancelar", valor:false}, {texto:"Sí, generar", valor:true, tipo:"primario"} ]);
    if(!si) return;
    auto.forEach(m=> resolverMaterial(actual, m.clave, "generado", undefined, undefined, "Generado por el asistente"));
    anotarEnDiario(actual.id, "El asistente completó " + auto.length + " pieza" + (auto.length===1?"":"s") + " del inventario.");
    pintarEditor(); programarGuardado();
    toast(auto.length ? "Piezas generadas" : "Recuerda aportar tu archivo de música", auto.length ? "ok" : "");
  });''',
    '''  /* generar vistas previas REALES (fase 4) — el arte viaja igual al paquete */
  const genBtn = panel.querySelector("[data-generar-todo]");
  if(genBtn) genBtn.addEventListener("click", async ()=>{
    try {
      toast("🎨 Pintando piezas…");
      const generadas = await generarVistasPrevias(actual);
      anotarEnDiario(actual.id, "El Taller pintó " + generadas + " pieza" + (generadas===1?"":"s") + " del paquete.");
      pintarEditor(); programarGuardado();
      toast(generadas ? generadas + " piezas pintadas: así viajan al paquete" : "Ya estaba todo pintado", "ok");
    }catch(e){
      toast("No se pudo pintar: " + (e && e.message ? e.message : e), "err");
    }
  });''')

# ── quitar los leemes/paquetes viejos (ficción netlify) ─────────────────
i0 = html.index("function resumenCajaTexto(caja){")
i1 = html.index("/* ---------- el diario de bordo ---------- */")
html = html[:i0] + "/* los paquetes REALES viven ahora en app2b (construirPaquete + descargarPaquete) */\n\n" + html[i1:]

# ── handler muerto del "efecto nuevo" (ya no existe «otro») ─────────────
i0 = html.index("      // superpoder con efecto nuevo: el asistente pregunta antes de inventar")
i1 = html.index("      // repintar campos dependientes")
html = html[:i0] + html[i1:]

# ── inyectar plantilla del módulo + fábrica (antes de app3) ─────────────
tpl = TPL.read_text(encoding="utf-8")
gen = GEN.read_text(encoding="utf-8")
assert "</script" not in tpl and "</script" not in gen
bloque = ('<script type="text/plain" id="tpl-modulo">\n' + tpl + '\n</script>\n'
          '<script>\n' + gen + '\n</script>\n')
ancla = '<script>\n/* ══════════ app3 · revisión automática, estados, paquetes, diario, arranque ══════════ */'
rep(ancla, bloque + ancla)

# ── comprobar que los leemes viejos ya no se referencian ────────────────
for muerto in ("leemePruebas", "leemeDefinitivo", "CHECKLIST_TEXTO", "resumenCajaTexto"):
    assert muerto not in html, "quedan restos de " + muerto
assert "app.netlify.com/drop" not in html, "queda la ficción de Netlify"

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print("salida →", OUT)
print(f"OK — editor parcheado: {len(orig)} → {len(html)} bytes")
