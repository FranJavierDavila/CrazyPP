/* ══════════ app2 · el asistente: las 7 fases del Taller ══════════ */

const FASES = [
  { n:1, emoji:"📋", titulo:"La ficha del campeonato", corto:"Ficha" },
  { n:2, emoji:"🤖", titulo:"El rival", corto:"Rival" },
  { n:3, emoji:"✨", titulo:"Los superpoderes", corto:"Superpoderes" },
  { n:4, emoji:"📦", titulo:"Los materiales", corto:"Materiales" },
  { n:5, emoji:"🎯", titulo:"Las pruebas de habilidad", corto:"Pruebas" },
  { n:6, emoji:"🪄", titulo:"La sala", corto:"Sala" },
  { n:7, emoji:"🧾", titulo:"Montaje final y revisión", corto:"Montaje" }
];

const DIFICULTADES = [
  { id:"facil",   nombre:"Fácil",   emoji:"🌤️" },
  { id:"media",   nombre:"Media",   emoji:"⛅" },
  { id:"dificil", nombre:"Difícil", emoji:"🌩️" }
];

function deepGet(obj, ruta){
  return ruta.split(".").reduce((o,k)=> (o == null ? o : o[k]), obj);
}
function deepSet(obj, ruta, valor){
  const partes = ruta.split(".");
  let o = obj;
  for(let i=0;i<partes.length-1;i++){
    if(o[partes[i]] == null) o[partes[i]] = {};
    o = o[partes[i]];
  }
  o[partes[partes.length-1]] = valor;
}

/* ---------- inventario de materiales (se deriva de lo decidido) ---------- */
function materialGuardado(caja, clave){
  return (caja.materiales || []).find(m => m.clave === clave) || null;
}
function deriveMateriales(caja){
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
}
function resolverMaterial(caja, clave, estado, dataUrl, nombre, nota){
  let m = materialGuardado(caja, clave);
  if(!m){ m = { clave }; caja.materiales.push(m); }
  m.estado = estado; m.cuando = ahora();
  if(dataUrl !== undefined) m.dataUrl = dataUrl;
  if(nombre !== undefined) m.nombre = nombre;
  if(nota !== undefined) m.nota = nota;
}

/* ---------- completitud por fase (para el stepper) ---------- */
function faseCompleta(n){
  if(!actual) return false;
  const c = actual;
  switch(n){
    case 1: return !!(c.ficha.nombre && c.etiqueta && c.ficha.historia && c.ficha.historia.length >= 10);
    case 2: return !!(c.rival.nombre && c.rival.celebracion);
    case 3: return c.superpoderes.every(s => s.nombre && Number(s.duracion) > 0);
    case 4: return deriveMateriales(c).every(m => m.estado !== "pendiente");
    case 5: return c.retos.length >= 1 && c.retos.every(r => r.nombre && Number(r.objetivo) > 0 && r.premio);
    case 6: return !!(c.sala.decoracion && c.sala.transicion);
    case 7: return !!(c.validacion && c.validacion.resultado === "ok");
  }
  return false;
}

function pintarStepper(){
  $("#stepper").innerHTML = FASES.map(f=>{
    const cls = f.n === faseActual ? "actual" : (faseCompleta(f.n) ? "hecho" : "");
    const marca = f.n === faseActual ? f.n : (faseCompleta(f.n) ? "✓" : f.n);
    return `<button class="paso ${cls}" data-ir="${f.n}">
      <span class="num">${marca}</span> ${f.emoji} ${f.n} · ${esc(f.corto)}</button>`;
  }).join("");
  $$("#stepper [data-ir]").forEach(b=>b.addEventListener("click",()=>{
    faseActual = Number(b.dataset.ir); pintarEditor();
  }));
}

function pintarEstadoStrip(){
  const est = ESTADOS.find(e=>e.id===actual.estado) || ESTADOS[0];
  $("#estado-strip").innerHTML =
    ESTADOS.map(e=>`<span class="pildora p-${e.id} ${e.id===est.id?"activa":""}" title="${esc(INFO_ESTADO[e.id])}">${e.emoji} ${e.nombre}</span>`)
      .join(`<span class="flecha">→</span>`) +
    `<span style="flex:1"></span><span style="font-size:12.5px;color:var(--tinta-suave);max-width:340px">${esc(INFO_ESTADO[est.id])}</span>`;
}

function pintarEditor(){
  if(!actual) return;
  pintarEstadoStrip();
  pintarStepper();
  pintarFase(faseActual);
}

/* ---------- piezas de formulario ---------- */
function campoText(ruta, etiqueta, ayuda, valor, extra){
  extra = extra || {};
  return `<div class="campo ${extra.entera ? "entera" : ""}">
    <label>${etiqueta}${ayuda ? `<span class="ayuda">${ayuda}</span>` : ""}</label>
    <input type="text" data-ruta="${ruta}" value="${esc(valor ?? "")}" placeholder="${esc(extra.fantasma || "")}">
  </div>`;
}
function campoNum(ruta, etiqueta, ayuda, valor, attrs){
  return `<div class="campo">
    <label>${etiqueta}${ayuda ? `<span class="ayuda">${ayuda}</span>` : ""}</label>
    <input type="number" data-ruta="${ruta}" value="${esc(valor ?? "")}" ${attrs || ""}>
  </div>`;
}
function campoSel(ruta, etiqueta, ayuda, valor, opciones){
  return `<div class="campo">
    <label>${etiqueta}${ayuda ? `<span class="ayuda">${ayuda}</span>` : ""}</label>
    <select data-ruta="${ruta}">
      ${opciones.map(o=>`<option value="${esc(o.id)}" ${o.id===valor?"selected":""}>${o.emoji ? o.emoji + " " : ""}${esc(o.nombre)}</option>`).join("")}
    </select>
  </div>`;
}
function campoArea(ruta, etiqueta, ayuda, valor, fantasma){
  return `<div class="campo entera">
    <label>${etiqueta}${ayuda ? `<span class="ayuda">${ayuda}</span>` : ""}</label>
    <textarea data-ruta="${ruta}" placeholder="${esc(fantasma || "")}">${esc(valor ?? "")}</textarea>
  </div>`;
}
function rangoHTML(ruta, etiqueta, ayuda, valor, bajo, alto){
  valor = Number(valor || 3);
  return `<div class="campo">
    <label>${etiqueta}${ayuda ? `<span class="ayuda">${ayuda}</span>` : ""}</label>
    <div class="rango" data-rango="${ruta}">
      <input type="range" min="1" max="5" step="1" value="${valor}" data-ruta="${ruta}">
    </div>
    <div class="burbujas"><span>${esc(bajo)}</span><span>${esc(alto)}</span></div>
  </div>`;
}
function pildoraEstado(estado){
  const m = { generado:["mp-ok","generado por el asistente"], aportado:["mp-apor","aportado por ti"], pendiente:["mp-pend","pendiente"] }[estado] || ["mp-pend",estado];
  return `<span class="mini-pild ${m[0]}">${m[1]}</span>`;
}

/* ---------- render de cada fase ---------- */
function pintarFase(n){
  const c = actual;
  const f = FASES[n-1];
  let html = `<div class="fase-tit"><span class="fnum">Fase ${f.n} de 7</span><h2>${f.emoji} ${esc(f.titulo)}</h2></div>`;

  if(n===1){
    html += `<p class="fase-sub">Tú decides el nombre, la historia y la ambientación, el estilo visual y la dificultad general. El asistente le pone una <b>etiqueta única de identificación</b> (su carné, inconfundible).</p>
    <div class="campos">
      ${campoText("ficha.nombre","Nombre del campeonato","Cómo aparecerá en el menú del juego.", c.ficha.nombre, {fantasma:"Campeonato Órbita Cero"})}
      ${campoText("etiqueta","Etiqueta única","El asistente la propone a partir del nombre. Sin espacios ni acentos; no puede coincidir con los campeonatos de siempre.", c.etiqueta, {fantasma:"orbita-cero"})}
      ${campoArea("ficha.historia","La historia y la ambientación","Cuéntala con tus palabras: ¿dónde jugamos y por qué? (mínimo una frase)", c.ficha.historia, "Una estación espacial abandonada donde la bola flota…")}
      ${campoSel("ficha.estiloVisual","Estilo visual","Viste el mundo del campeonato con una de las salas que el juego ya conoce.", c.ficha.estiloVisual, ESTILOS_VISUALES)}
      ${campoSel("ficha.dificultad","Dificultad general","Cuánta exigencia tendrá el campeonato en conjunto.", c.ficha.dificultad, DIFICULTADES)}
    </div>`;
  }

  if(n===2){
    html += `<p class="fase-sub">Quién es tu oponente: identidad, carácter y forma de jugar. El asistente reutiliza el <b>«cerebro»</b> de rivales que el juego ya tiene —los mismos movimientos, errores y celebraciones— y lo adapta a tu personaje.</p>
    <div class="campos">
      ${campoText("rival.nombre","Nombre del rival","", c.rival.nombre, {fantasma:"COSMOS el robot"})}
      ${campoSel("rival.caracter","Carácter","Cómo se comporta fuera del juego.", c.rival.caracter, CARACTERES)}
      ${campoSel("rival.cerebroBase","Cerebro base","De qué campeonato de siempre se copia su forma de jugar (el original no se toca: solo se copia).", c.rival.cerebroBase, CEREBROS)}
      ${campoText("rival.celebracion","Cómo celebra los puntos","Un gesto o frase que le salga al ganar.", c.rival.celebracion, {fantasma:"Enciende sus luces azules"})}
      ${rangoHTML("rival.agresividad","Agresividad","¿Se lanza a golpes arriesgados?", c.rival.agresividad, "Tranquilo","Temerario")}
      ${rangoHTML("rival.precision","Precisión lejos de la mesa","¿Acierta desde lejos?", c.rival.precision, "Fallón","Francotirador")}
      ${rangoHTML("rival.constancia","Constancia","¿Cuántas bolas seguidas aguanta sin fallar?", c.rival.constancia, "Tropezona","Muralla")}
    </div>`;
  }

  if(n===3){
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
  }

  if(n===4){
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
  }

  if(n===5){
    const cards = c.retos.map((r,i)=>{
      const t = TIPOS_RETO.find(x=>x.id===r.tipo) || TIPOS_RETO[0];
      return `<div class="repeticion" data-reto="${i}">
        <button class="borrar" data-borra-reto="${i}" title="Quitar esta prueba">✕</button>
        ${campoText("retos."+i+".nombre","Nombre del reto","", r.nombre, {fantasma:"Derriba los cristales"})}
        ${campoSel("retos."+i+".tipo","Qué tipo de prueba","", r.tipo || "objetivos", TIPOS_RETO)}
        ${campoNum("retos."+i+".objetivo", t.id==="puntos" ? "Puntos necesarios" : t.id==="supervivencia" ? "Segundos a sobrevivir" : "Cantidad objetivo","Qué cuenta como superarlo.", r.objetivo, 'min="1" step="1"')}
        ${campoNum("retos."+i+".puntos","Puntos que suma","Cuánto aporta al campeonato.", r.puntos, 'min="1" max="20" step="1"')}
        ${campoText("retos."+i+".premio","Premio que recibe","", r.premio, {fantasma:"Estrella dorada"})}
        <div class="aviso info">🎯 <div>Superar este reto: <b>${esc(t.nombre)}</b>. El asistente lo encaja con las reglas del juego y comprueba que ganar y perder queden equilibrados.</div></div>
      </div>`;
    }).join("");
    html += `<p class="fase-sub">Qué retos hay que superar, qué cuenta como acierto y qué premios se reciben. Con al menos <b>una prueba</b> el campeonato tiene chicha; con tres o cuatro tiene vida.</p>
    <div class="campos">
      <div class="tarjetas-repet">
        <div class="cab">🎯 Pruebas de habilidad <button class="btn primario btn-mini" data-add-reto>＋ Añadir prueba</button></div>
        ${cards || `<div class="vacio-repet">Ninguna prueba todavía. Añade al menos una para que el campeonato se pueda ganar.</div>`}
      </div>
    </div>`;
  }

  if(n===6){
    html += `<p class="fase-sub">Cómo se viste el escenario. El asistente monta la sala con las <b>piezas estándar</b> del juego —las mismas de las salas pabellón, ártico, atardecer y neón— vestidas a tu manera.</p>
    <div class="campos">
      ${campoText("sala.decoracion","Decoración","Qué se ve alrededor de la pista.", c.sala.decoracion, {fantasma:"Ventana a las estrellas y paneles metálicos"})}
      ${campoSel("sala.iluminacion","Iluminación","El carácter de la luz.", c.sala.iluminacion, ILUMINACIONES)}
      ${campoSel("sala.musica","Música ambiental","El hilo sonoro de la sala.", c.sala.musica, MUSICA_SALA)}
      ${c.sala.musica === "propia" ? `<div class="campo">
        <label>Tu archivo de música<span class="ayuda">MP3 u OGG, máximo 600 KB. Se guarda dentro de la caja.</span></label>
        ${c.sala.musicaPropia
          ? `<div class="material-fila"><div class="m-ico">🎵</div><div class="m-txt"><b>${esc(c.sala.musicaPropia.nombre)} ${pildoraEstado("aportado")}</b><span>Puedes sustituirla si quieres.</span></div>
             <label class="btn fantasma btn-mini" style="display:inline-flex;align-items:center">Cambiar
               <input type="file" hidden data-subir="sala-musica" accept="audio/*"></label></div>`
          : `<label class="btn primario btn-mini" style="display:inline-flex;align-items:center">📎 Elegir archivo
               <input type="file" hidden data-subir="sala-musica" accept="audio/*"></label>`}
      </div>` : ""}
      ${campoText("sala.transicion","Transición de entrada","Cómo entra el jugador a la sala (luces, cortina, teletransporte…).", c.sala.transicion, {fantasma:"Las luces se encienden en cadena"})}
    </div>`;
  }

  if(n===7){
    html += pintarFase7();
  }

  $("#panel-fase").innerHTML = html;
  enlazarFase(n);
}

function pintarFase7(){
  const c = actual;
  const est = ESTADOS.find(e=>e.id===c.estado) || ESTADOS[0];
  const sp = c.superpoderes.length
    ? c.superpoderes.map(s=>{ const ef = EFECTOS.find(e=>e.id===s.efecto)||EFECTOS[0]; return esc(s.nombre||ef.nombre)+" ("+ef.nombre.toLowerCase()+")"; }).join(" · ")
    : "Ninguno (campeonato «limpio»)";
  const retos = c.retos.length
    ? c.retos.map(r=>esc(r.nombre)+" — "+ (TIPOS_RETO.find(t=>t.id===r.tipo)||TIPOS_RETO[0]).nombre.toLowerCase()).join("<br>")
    : "Ninguna todavía";
  const mats = deriveMateriales(c);
  const pend = mats.filter(m=>m.estado==="pendiente").length;

  const CHECKLIST = [
    "El campeonato nuevo <b>aparece en el menú</b> con su nombre y su sala.",
    "Los tres campeonatos de siempre — <b>Partido, Entrenamiento y Supervivencia</b> — funcionan exactamente igual que antes.",
    "El <b>rival</b> se comporta como lo definiste: golpea, falla donde debía fallar y celebra como acordaste.",
    "Los <b>superpoderes</b> se activan bien, duran lo acordado y no desequilibran el partido.",
    "La <b>sala</b> se ve y suena como decidiste: decoración, luces y música ambiental.",
    "Las <b>pruebas de habilidad</b> puntúan correctamente y dan los premios previstos.",
    "Se puede <b>ganar y se puede perder</b>, y ambos finales se muestran con sus carteles.",
    "Nada del juego de siempre se ha movido de sitio: menú, salas, opciones e idioma intactos."
  ];
  const checklist = (c.checklist || CHECKLIST.map(()=>false));

  let acciones = "";
  if(["borrador","preparacion"].includes(c.estado)){
    acciones = `<button class="btn primario" data-lanzar-revision>🕵️ Lanzar la revisión automática</button>`;
  }
  let exportar = "";
  if(["listo","publicado","desactivado"].includes(c.estado)){
    exportar = `
      <div class="tarjetas-repet" style="margin-top:14px">
        <div class="cab">📤 Paquetes listos para viajar</div>
        <div class="aviso info">🔬 <div><b>Paquete de pruebas</b>: el juego completo con tu campeonato marcado «en pruebas». Arrástralo a <b>app.netlify.com/drop</b> desde un ordenador y te dará una dirección web privada para probar con el casco.</div></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn primario" data-paquete="pruebas">🔬 Descargar paquete de pruebas (.zip)</button>
          <button class="btn" data-paquete="definitivo">🏟️ Descargar paquete definitivo (.zip)</button>
          <button class="btn fantasma" data-caja-json>💾 Copia de seguridad (.json)</button>
        </div>
        <div class="aviso info">🏟️ <div><b>Paquete definitivo</b>: solo se arrastra a la página de Netlify cuando quieras que <b>todos los jugadores</b> lo reciban. Esa dirección nueva será «la dirección del estadio».</div></div>
      </div>`;
  }

  let publicar = "";
  if(c.estado === "listo"){
    publicar = `<button class="btn ok" data-estado="publicado">🏆 Marcar como publicado</button>`;
  }else if(c.estado === "publicado"){
    publicar = `<button class="btn" data-estado="desactivado">🌙 Desactivar (jubilación reversible)</button>`;
  }else if(c.estado === "desactivado"){
    publicar = `<button class="btn ok" data-estado="publicado">♻️ Volver a publicar</button>`;
  }

  let revision = "";
  if(c.validacion && Array.isArray(c.validacion.chequeos) && c.validacion.chequeos.length){
    const fecha = esc(fechaBonita(c.validacion.cuando));
    revision = `<div class="tarjetas-repet" style="margin-top:14px">
      <div class="cab">🕵️ La revisión automática, punto por punto <span style="margin-left:auto;font-weight:600;color:var(--tinta-suave);font-size:12.5px">${fecha}</span></div>
      ${c.validacion.chequeos.map(ch=>`<div class="check ${ch.ok?"pass":"fall"}">
        <span class="c-ico">${ch.ok?"✓":"!"}</span>
        <div><b>${esc(ch.n)} · ${esc(ch.titulo)}</b><span class="det">${esc(ch.detalle)}</span></div>
      </div>`).join("")}
    </div>`;
  }

  let fallos = "";
  if(c.validacion && c.validacion.resultado === "fallos" && c.validacion.fallos.length){
    fallos = `<div class="aviso error" style="margin-top:14px">🚫 <div><b>La revisión devolvió correcciones.</b> Corrígelo en su fase, vuelve aquí y repite la revisión. Puedes repetir el ciclo <b>las veces que haga falta</b>: el juego publicado no se entera de nada.</div></div>`;
  }

  return `<p class="fase-sub">El asistente junta todo en la <b>caja del campeonato</b>, crea su lista de material, lo registra y lanza la <b>revisión automática</b>: un control de calidad que examina la caja entera en segundos.</p>
  <div class="resumen">
    <div class="bloque"><h4>📋 Ficha</h4>
      <p><b>${esc(c.ficha.nombre || "—")}</b> · etiqueta <b>${esc(c.etiqueta || "—")}</b></p>
      <p>${esc((c.ficha.historia || "Sin historia todavía").slice(0,160))}${(c.ficha.historia||"").length>160?"…":""}</p>
      <p>${esc((ESTILOS_VISUALES.find(x=>x.id===c.ficha.estiloVisual)||{}).nombre||"")} · dificultad ${(DIFICULTADES.find(x=>x.id===c.ficha.dificultad)||{}).nombre||""}</p></div>
    <div class="bloque"><h4>🤖 Rival</h4>
      <p><b>${esc(c.rival.nombre || "—")}</b> · ${(CARACTERES.find(x=>x.id===c.rival.caracter)||{}).nombre||""}</p>
      <p>Cerebro base: ${esc((CEREBROS.find(x=>x.id===c.rival.cerebroBase)||{}).nombre||"")}</p>
      <p>Celebra: ${esc(c.rival.celebracion || "—")}</p></div>
    <div class="bloque"><h4>✨ Superpoderes</h4><p>${sp}</p></div>
    <div class="bloque"><h4>📦 Materiales</h4>
      <p>${mats.length} piezas en el inventario · ${pend ? "<b style='color:var(--warn)'>" + pend + " pendiente" + (pend===1?"":"s") + "</b>" : "todo resuelto"}</p></div>
    <div class="bloque"><h4>🎯 Pruebas de habilidad</h4><p>${retos}</p></div>
    <div class="bloque"><h4>🪄 Sala</h4>
      <p>${esc(c.sala.decoracion || "—")}</p>
      <p>${esc((ILUMINACIONES.find(x=>x.id===c.sala.iluminacion)||{}).nombre||"")} · ${esc((MUSICA_SALA.find(x=>x.id===c.sala.musica)||{}).nombre||"")}</p>
      <p>Entrada: ${esc(c.sala.transicion || "—")}</p></div>
  </div>

  <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:18px 0 4px">
    ${acciones}
    ${publicar}
    <span class="pildora p-${est.id}">${est.emoji} ${est.nombre}</span>
  </div>
  ${fallos}
  ${revision}
  ${exportar}

  ${["listo","publicado","desactivado"].includes(c.estado) ? `
  <div class="tarjetas-repet" style="margin-top:14px">
    <div class="cab">📋 La lista de comprobación del laboratorio (la prueba del algodón)</div>
    ${CHECKLIST.map((t,i)=>`<label class="item"><input type="checkbox" data-check="${i}" ${checklist[i]?"checked":""}><span>${t}</span></label>`).join("")}
    <div class="aviso info">☑️ <div>Márcalos con el casco puesto en la copia de pruebas. Si todos pasan, el campeonato está preparado para publicarse.</div></div>
  </div>` : ""}`;
}

/* ---------- edición: enlazado de eventos de la fase ---------- */
function enlazarFase(n){
  const panel = $("#panel-fase");

  panel.querySelectorAll("[data-ruta]").forEach(el=>{
    const handler = () => {
      let v = el.value;
      if(el.type === "number" || el.type === "range") v = v === "" ? "" : Number(v);
      const ruta = el.dataset.ruta;

      // auto-etiqueta: si el nombre cambia y la etiqueta era la derivada del nombre anterior, se actualiza
      if(ruta === "ficha.nombre"){
        const anterior = slug(deepGet(actual, "ficha.nombre"));
        deepSet(actual, ruta, v);
        if(!actual.etiqueta || actual.etiqueta === anterior) actual.etiqueta = slug(v);
        const et = panel.querySelector('[data-ruta="etiqueta"]');
        if(et){ et.value = actual.etiqueta; }
      }else{
        deepSet(actual, ruta, v);
      }

      // superpoder con efecto nuevo: el asistente pregunta antes de inventar
      if(ruta && /^superpoderes\.\d+\.efecto$/.test(ruta) && v === "otro"){
        preguntar("¿Un efecto realmente nuevo?",
          "El sistema ya conoce algunos efectos y los reutiliza sin riesgo. Este que propones sería nuevo: el asistente se detiene y te consulta antes de inventar por su cuenta. ¿Lo dejamos como idea nueva para resolverlo en materiales?",
          [ {texto:"Mejor uso uno conocido", valor:false}, {texto:"Sí, idea nueva", valor:true, tipo:"primario"} ])
        .then(sigue=>{
          if(!sigue){
            deepSet(actual, ruta, "fantasma");
            const sel = panel.querySelector(`[data-ruta="${ruta}"]`);
            if(sel) sel.value = "fantasma";
          }
          pintarEditor(); programarGuardado();
        });
      }

      // repintar campos dependientes (cadaCuantos / música propia)
      if((ruta && (/^superpoderes\.\d+\.activacion$/.test(ruta) || /^retos\.\d+\.tipo$/.test(ruta))) || ruta === "sala.musica"){
        const scroll = window.scrollY;
        pintarEditor(); window.scrollTo(0, scroll);
      }

      if(el.type === "range"){
        programarGuardado();
      }else{
        programarGuardado();
      }
      // marcas del stepper en vivo (barato)
      pintarStepper();
    };
    if(el.tagName === "SELECT"){ el.addEventListener("change", handler); }
    else{ el.addEventListener("input", handler); }
  });

  /* botones de añadir / quitar */
  const addSp = panel.querySelector("[data-add-sp]");
  if(addSp) addSp.addEventListener("click",()=>{
    actual.superpoderes.push({ nombre:"", efecto:"fantasma", activacion:"puntos", cadaCuantos:3, duracion:5, recarga:2 });
    anotarEnDiario(actual.id, "Añadió un superpoder al campeonato.");
    pintarEditor(); programarGuardado();
  });
  panel.querySelectorAll("[data-borra-sp]").forEach(b=>b.addEventListener("click",()=>{
    actual.superpoderes.splice(Number(b.dataset.borraSp),1);
    anotarEnDiario(actual.id, "Quitó un superpoder.");
    pintarEditor(); programarGuardado();
  }));

  const addReto = panel.querySelector("[data-add-reto]");
  if(addReto) addReto.addEventListener("click",()=>{
    actual.retos.push({ nombre:"", tipo:"objetivos", objetivo:5, puntos:1, premio:"" });
    anotarEnDiario(actual.id, "Añadió una prueba de habilidad.");
    pintarEditor(); programarGuardado();
  });
  panel.querySelectorAll("[data-borra-reto]").forEach(b=>b.addEventListener("click",()=>{
    actual.retos.splice(Number(b.dataset.borraReto),1);
    anotarEnDiario(actual.id, "Quitó una prueba de habilidad.");
    pintarEditor(); programarGuardado();
  }));

  /* generar lo que falte (fase 4) */
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
  });

  /* aportar archivos (fase 4 y 6) */
  panel.querySelectorAll("[data-subir]").forEach(inp=>{
    inp.addEventListener("change", ()=>{
      const file = inp.files && inp.files[0];
      if(!file) return;
      if(file.size > 600 * 1024){
        toast("El archivo pesa más de 600 KB: elige uno más ligero", "err");
        inp.value = ""; return;
      }
      const lector = new FileReader();
      lector.onload = ()=>{
        const clave = inp.dataset.subir;
        if(clave === "sala-musica"){
          actual.sala.musicaPropia = { nombre: file.name, dataUrl: lector.result };
        }
        resolverMaterial(actual, clave, "aportado", lector.result, file.name, "Aportado por ti");
        anotarEnDiario(actual.id, "Aportó el archivo «" + file.name + "» a la caja.");
        pintarEditor(); programarGuardado();
        toast("Archivo guardado dentro de la caja", "ok");
      };
      lector.readAsDataURL(file);
    });
  });

  /* checklist del laboratorio (fase 7) */
  panel.querySelectorAll("[data-check]").forEach(ch=>{
    ch.addEventListener("change", ()=>{
      if(!Array.isArray(actual.checklist)) actual.checklist = [false,false,false,false,false,false,false,false];
      actual.checklist[Number(ch.dataset.check)] = ch.checked;
      programarGuardado();
    });
  });

  /* lanzar la revisión automática */
  const rev = panel.querySelector("[data-lanzar-revision]");
  if(rev) rev.addEventListener("click", lanzarRevision);

  /* descargar paquetes */
  panel.querySelectorAll("[data-paquete]").forEach(b=>b.addEventListener("click",()=>{
    descargarPaquete(b.dataset.paquete === "definitivo");
  }));
  const cj = panel.querySelector("[data-caja-json]");
  if(cj) cj.addEventListener("click",()=> descargarJSON(actual));

  /* publicar / desactivar / reactivar */
  panel.querySelectorAll("[data-estado]").forEach(b=>b.addEventListener("click",async ()=>{
    const destino = b.dataset.estado;
    if(destino === "publicado"){
      const si = await preguntar("🏆 ¿Marcar como publicado?",
        "Recuerda: publicar de verdad es arrastrar el paquete definitivo a app.netlify.com/drop desde un ordenador. Aquí solo se registra el hito en el viaje del campeonato. ¿Continuamos?",
        [ {texto:"Aún no", valor:false}, {texto:"Sí, registrado", valor:true, tipo:"ok"} ]);
      if(!si) return;
    }
    cambiarEstado(destino);
  }));
}
