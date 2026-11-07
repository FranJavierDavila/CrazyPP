/* ══════════ Crazy Ping Pong · Editor de campeonatos · V2.124 ══════════
   app1 · datos, almacenamiento, plantillas, navegación, diario, modales */
"use strict";

/* ---------- constantes compartidas ---------- */
const VERSION_EDITOR = "V2.124";
const CLAVE_ALMACEN  = "pp_editor_proyectos_v1";
const CLAVE_DIARIO   = "pp_editor_diario_v1";
const CLAVE_ULTIMO   = "pp_editor_ultimo_v1";

const ESTADOS = [
  { id:"borrador",     nombre:"Borrador",         emoji:"✏️" },
  { id:"preparacion",  nombre:"En preparación",   emoji:"🧰" },
  { id:"validacion",   nombre:"En validación",    emoji:"🕵️" },
  { id:"listo",        nombre:"Listo para probar",emoji:"✅" },
  { id:"publicado",    nombre:"Publicado",        emoji:"🏆" },
  { id:"desactivado",  nombre:"Desactivado",      emoji:"🌙" }
];
const INFO_ESTADO = {
  borrador:    "El campeonato se está creando o retocando en el Taller. Solo tú lo ves: para los jugadores todavía no existe.",
  preparacion: "Se completan las piezas que faltaban para terminar la caja.",
  validacion:  "La revisión automática lo examina de arriba abajo. Si encuentra fallos, lo devuelve con la lista completa.",
  listo:       "Ha pasado el examen y baja al Laboratorio: genera el paquete de pruebas y juega con el casco puesto.",
  publicado:   "Aparece en el menú del juego final para todos los jugadores. Sigue siendo reversible.",
  desactivado: "Retirado del menú sin borrar nada: la caja se conserva íntegra y puede volver a publicarse."
};
const ETIQUETAS_RESERVADAS = ["partido","entrenamiento","supervivencia","crazy"];

const EFECTOS_CONOCIDOS = ["fantasma","escudo","lenta"]; // ya inventados por el sistema
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
];
const ESTILOS_VISUALES = [
  { id:"pabellon", nombre:"Pabellón clásico", emoji:"🏟️" },
  { id:"artico",   nombre:"Ártico", emoji:"🧊" },
  { id:"atardecer",nombre:"Atardecer", emoji:"🌅" },
  { id:"neon",     nombre:"Neón", emoji:"🌆" },
  { id:"personalizado", nombre:"Personalizado", emoji:"🎨" }
];
const ILUMINACIONES = [
  { id:"calida",    nombre:"Cálida (luz de tarde)" },
  { id:"fria",      nombre:"Fría (luz de luna)" },
  { id:"neon",      nombre:"Neón (colores vivos)" },
  { id:"atardecer", nombre:"Atardecer (naranja suave)" }
];
const MUSICA_SALA = [
  { id:"ninguna",  nombre:"Sin música" },
  { id:"pabellon", nombre:"Murmullo de pabellón" },
  { id:"espacial", nombre:"Ambiente espacial" },
  { id:"artica",   nombre:"Viento ártico" },
  { id:"neon",     nombre:"Sintetizador neón" },
  { id:"propia",   nombre:"Mi propia música (aportada)" }
];
const CARACTERES = [
  { id:"frio",      nombre:"Frío y calculador" },
  { id:"arriesgado",nombre:"Arriesgado" },
  { id:"bromista",  nombre:"Bromista" },
  { id:"robotico",  nombre:"Robótico" },
  { id:"tranquilo", nombre:"Tranquilo" }
];
const CEREBROS = [
  { id:"partido",       nombre:"El cerebro de Partido" },
  { id:"entrenamiento", nombre:"El cerebro de Entrenamiento" },
  { id:"supervivencia", nombre:"El cerebro de Supervivencia" }
];

/* ---------- utilidades ---------- */
const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
  .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
const slug = (s) => String(s||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"")
  .replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,40) || "campeonato";
const ahora = () => new Date().toISOString();
const fechaBonita = (iso) => {
  try{
    return new Date(iso).toLocaleString("es-ES",{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"});
  }catch(_){ return iso || ""; }
};

function toast(msg, tipo){
  const t = document.createElement("div");
  t.className = "toast" + (tipo ? " " + tipo : "");
  t.textContent = msg;
  $("#toasts").appendChild(t);
  setTimeout(()=>{ t.style.opacity = "0"; t.style.transition = "opacity .3s"; }, 2400);
  setTimeout(()=> t.remove(), 2800);
}

/* ---------- modal de confirmación (promesa) ---------- */
let _resolverModal = null;
function preguntar(titulo, texto, botones){
  $("#modal-tit").textContent = titulo;
  $("#modal-txt").textContent = texto;
  const cont = $("#modal-botones");
  cont.innerHTML = "";
  botones.forEach(b=>{
    const btn = document.createElement("button");
    btn.className = "btn" + (b.tipo ? " " + b.tipo : "");
    btn.textContent = b.texto;
    btn.addEventListener("click", ()=>{ cerrarModal(); _resolverModal && _resolverModal(b.valor); });
    cont.appendChild(btn);
  });
  $("#modal-fondo").classList.add("abierto");
  return new Promise(res=>{ _resolverModal = res; });
}
function cerrarModal(){ $("#modal-fondo").classList.remove("abierto"); }

/* ---------- almacenamiento ---------- */
function cargarProyectos(){
  try{ return JSON.parse(localStorage.getItem(CLAVE_ALMACEN) || "[]"); }
  catch(_){ return []; }
}
function guardarProyectos(lista){
  localStorage.setItem(CLAVE_ALMACEN, JSON.stringify(lista));
}
function cargarDiario(){
  try{ return JSON.parse(localStorage.getItem(CLAVE_DIARIO) || "[]"); }
  catch(_){ return []; }
}
function anotarEnDiario(proyId, que){
  const diario = cargarDiario();
  diario.unshift({ id:proyId, cuando:ahora(), que });
  localStorage.setItem(CLAVE_DIARIO, JSON.stringify(diario.slice(0,400)));
}
function diarioDe(proyId){
  return cargarDiario().filter(e => !proyId || e.id === proyId);
}

/* ---------- fábrica de la caja ---------- */
function cajaNueva(nombre){
  return {
    schema: "crazy-pingpong-campeonato",
    version: "1.0",
    id: "ppc_" + Date.now().toString(36) + Math.random().toString(36).slice(2,7),
    etiqueta: "",
    ficha: {
      nombre: nombre || "",
      historia: "",
      estiloVisual: "pabellon",
      dificultad: "media"
    },
    rival: {
      nombre: "",
      caracter: "frio",
      cerebroBase: "partido",
      agresividad: 3,
      precision: 3,
      constancia: 3,
      celebracion: ""
    },
    superpoderes: [],
    materiales: [],
    retos: [],
    sala: {
      decoracion: "",
      iluminacion: "calida",
      musica: "pabellon",
      musicaPropia: null,   // {nombre, dataUrl}
      transicion: ""
    },
    estado: "borrador",
    creado: ahora(),
    modificado: ahora(),
    validacion: null   // {cuando, resultado, fallos:[...]}
  };
}

/* plantillas: copia limpia de los campeonatos de siempre (el original jamás se toca) */
function cajaDesdePlantilla(tipo, nombre){
  const c = cajaNueva(nombre);
  if(tipo === "cero") return c;
  c.ficha.nombre = nombre;
  c.ficha.historia = "";
  if(tipo === "partido"){
    c.ficha.historia = "Un partido de tenis de mesa de los de siempre: gana quien llegue antes a 11 puntos con ventaja de 2.";
    c.ficha.estiloVisual = "pabellon";
    c.ficha.dificultad = "media";
    c.rival = { nombre:"RIVAL", caracter:"frio", cerebroBase:"partido", agresividad:3, precision:3, constancia:3, celebracion:"Levanta la pala al ganar el punto." };
    c.sala = { decoracion:"Pista clásica de pabellón con suelo de parquet", iluminacion:"calida", musica:"pabellon", musicaPropia:null, transicion:"Entrada directa a la pista" };
  }else if(tipo === "entrenamiento"){
    c.ficha.historia = "Zona de práctica tranquila para afinar el golpeo sin presión de marcador.";
    c.ficha.estiloVisual = "pabellon";
    c.ficha.dificultad = "facil";
    c.rival = { nombre:"COMPAÑERO", caracter:"tranquilo", cerebroBase:"entrenamiento", agresividad:2, precision:2, constancia:4, celebracion:"Da un golpecito en la mesa." };
    c.retos = [ { nombre:"Calentamiento de brazos", tipo:"puntos", objetivo:5, puntos:1, premio:"Estrella de bronce" } ];
    c.sala = { decoracion:"Media pista con cesta de bolas", iluminacion:"calida", musica:"ninguna", musicaPropia:null, transicion:"Entrada directa a la pista" };
  }else if(tipo === "supervivencia"){
    c.ficha.historia = "Aguanta la lluvia de bolas el mayor tiempo posible: cada bola devuelta suma, un fallo lo cambia todo.";
    c.ficha.estiloVisual = "neon";
    c.ficha.dificultad = "dificil";
    c.rival = { nombre:"LANZADOR", caracter:"arriesgado", cerebroBase:"supervivencia", agresividad:5, precision:4, constancia:5, celebracion:"Silba burlón cuando fallas." };
    c.retos = [ { nombre:"Aguanta la lluvia", tipo:"lluvia", objetivo:20, puntos:1, premio:"Escudo dorado" } ];
    c.sala = { decoracion:"Pista de neón con suelo reflectante", iluminacion:"neon", musica:"neon", musicaPropia:null, transicion:"Luces que se encienden en cadena" };
  }
  return c;
}

/* ---------- estado de la app ---------- */
let proyectos = cargarProyectos();   // [{caja}]
let actual = null;                   // caja en edición
let faseActual = 1;
let guardadoTimer = null;

function proyectosIdx(){ const m = new Map(); proyectos.forEach(p=>m.set(p.caja.id, p)); return m; }

function guardarActual(silencioso){
  if(!actual) return;
  actual.modificado = ahora();
  const idx = proyectosIdx();
  const i = proyectos.findIndex(p => p.caja.id === actual.id);
  if(i >= 0) proyectos[i] = { caja: actual }; else proyectos.push({ caja: actual });
  guardarProyectos(proyectos);
  const pg = $("#punto-guardado");
  if(pg) pg.textContent = "💾 Guardado " + new Date().toLocaleTimeString("es-ES",{hour:"2-digit",minute:"2-digit",second:"2-digit"});
  if(!silencioso) toast("Guardado", "ok");
}

/* autosave con retardo suave */
function programarGuardado(){
  clearTimeout(guardadoTimer);
  guardadoTimer = setTimeout(()=> guardarActual(true), 900);
}

/* ---------- navegación entre pantallas ---------- */
function irAPantalla(id){
  $$(".pantalla").forEach(s => s.classList.toggle("visible", s.id === id));
  window.scrollTo({top:0, behavior:"smooth"});
}

/* ---------- pantalla inicio ---------- */
function pintarInicio(){
  const cont = $("#lista-proys");
  if(!proyectos.length){
    cont.innerHTML = `<div class="vacio">Todavía no hay campeonatos en tu taller.<br>
      Pulsa <b>＋ Crear campeonato nuevo</b> y el asistente te guiará paso a paso.</div>`;
    return;
  }
  cont.innerHTML = proyectos.map(p=>{
    const c = p.caja;
    const est = ESTADOS.find(e=>e.id===c.estado) || ESTADOS[0];
    return `<div class="proy">
      <div class="proy-top">
        <div class="proy-emoji">${est.emoji}</div>
        <div style="min-width:0">
          <h3>${esc(c.ficha.nombre || "(sin nombre)")}</h3>
          <div class="meta">etiqueta: ${esc(c.etiqueta || "—")} · modificado ${esc(fechaBonita(c.modificado))}</div>
        </div>
      </div>
      <div><span class="pildora p-${est.id}">${est.emoji} ${est.nombre}</span></div>
      <div class="acciones">
        <button class="btn primario btn-mini" data-abrir="${esc(c.id)}">Abrir en el Taller</button>
        <button class="btn fantasma btn-mini" data-duplicar="${esc(c.id)}">Duplicar</button>
        <button class="btn fantasma btn-mini" data-exportar="${esc(c.id)}">📤 Descargar caja</button>
        <button class="btn fantasma btn-mini" data-borrar="${esc(c.id)}">🗑️</button>
      </div>
    </div>`;
  }).join("");

  cont.querySelectorAll("[data-abrir]").forEach(b=>b.addEventListener("click",()=>{
    abrirProyecto(b.dataset.abrir);
  }));
  cont.querySelectorAll("[data-duplicar]").forEach(b=>b.addEventListener("click",async ()=>{
    const p = proyectosIdx().get(b.dataset.duplicar); if(!p) return;
    const copia = JSON.parse(JSON.stringify(p.caja));
    copia.id = "ppc_" + Date.now().toString(36) + Math.random().toString(36).slice(2,7);
    copia.ficha.nombre = (copia.ficha.nombre || "Campeonato") + " (copia)";
    copia.etiqueta = slug(copia.ficha.nombre);
    copia.estado = "borrador"; copia.validacion = null; copia.creado = ahora(); copia.modificado = ahora();
    proyectos.push({ caja: copia }); guardarProyectos(proyectos);
    anotarEnDiario(copia.id, "Se creó una copia del campeonato.");
    pintarInicio(); toast("Copia creada", "ok");
  }));
  cont.querySelectorAll("[data-exportar]").forEach(b=>b.addEventListener("click",()=>{
    const p = proyectosIdx().get(b.dataset.exportar); if(!p) return;
    descargarJSON(p.caja);
  }));
  cont.querySelectorAll("[data-borrar]").forEach(b=>b.addEventListener("click",async ()=>{
    const p = proyectosIdx().get(b.dataset.borrar); if(!p) return;
    const si = await preguntar("¿Eliminar esta caja?",
      "La caja «" + (p.caja.ficha.nombre || "sin nombre") + "» se borrará de este editor. Esto no toca para nada el juego publicado ni los campeonatos de siempre.",
      [ {texto:"Cancelar", valor:false}, {texto:"Sí, eliminar", valor:true, tipo:"primario"} ]);
    if(!si) return;
    proyectos = proyectos.filter(x => x.caja.id !== p.caja.id);
    guardarProyectos(proyectos);
    pintarInicio(); toast("Caja eliminada");
  }));
}

/* ---------- crear / abrir ---------- */
function nuevoDesdePlantilla(tipo){
  const nombres = { cero:"Mi campeonato", partido:"Campeonato Partido (copia)", entrenamiento:"Campeonato Entrenamiento (copia)", supervivencia:"Campeonato Supervivencia (copia)" };
  actual = cajaDesdePlantilla(tipo, nombres[tipo] || "Mi campeonato");
  actual.etiqueta = slug(actual.ficha.nombre);
  proyectos.push({ caja: actual }); guardarProyectos(proyectos);
  anotarEnDiario(actual.id, tipo === "cero"
    ? "Nació el campeonato: se empezó de cero."
    : "Nació el campeonato: se copió como plantilla limpia («" + tipo + "»). El original no se tocó.");
  faseActual = 1;
  abrirProyecto(actual.id, true);
  toast("Campeonato creado. ¡Adelante con la fase 1!", "ok");
}

function abrirProyecto(id, yaEnEditor){
  const p = proyectosIdx().get(id); if(!p) return;
  actual = p.caja;
  // saneo: claves basura de versiones antiguas
  delete actual.sp; delete actual.reto;
  localStorage.setItem(CLAVE_ULTIMO, id);
  faseActual = 1;
  pintarEditor();
  irAPantalla("screen-editor");
}

/* ---------- importar / exportar JSON de la caja ---------- */
function descargarJSON(caja){
  const blob = new Blob([JSON.stringify(caja, null, 2)], {type:"application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "caja-" + (caja.etiqueta || "campeonato") + ".json";
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
  toast("Caja descargada (copia de seguridad)", "ok");
}
function importarJSON(archivo){
  const lector = new FileReader();
  lector.onload = () => {
    try{
      const caja = JSON.parse(lector.result);
      if(!caja || caja.schema !== "crazy-pingpong-campeonato" || !caja.ficha){
        throw new Error("no-es-caja");
      }
      // si ya existe la misma id → nueva id para no pisar
      if(proyectosIdx().has(caja.id)){
        caja.id = "ppc_" + Date.now().toString(36) + Math.random().toString(36).slice(2,7);
        caja.ficha.nombre += " (importada)";
      }
      caja.modificado = ahora();
      proyectos.push({ caja }); guardarProyectos(proyectos);
      anotarEnDiario(caja.id, "Se importó la caja desde un archivo.");
      pintarInicio(); toast("Caja importada: " + caja.ficha.nombre, "ok");
    }catch(_){
      toast("Ese archivo no parece una caja de campeonato de Crazy Ping Pong", "err");
    }
  };
  lector.readAsText(archivo);
}
