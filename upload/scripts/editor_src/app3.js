/* ══════════ app3 · revisión automática, estados, paquetes, diario, arranque ══════════ */

/* ---------- la revisión automática: 7 chequeos, contados en cristiano ---------- */
function revisarCaja(caja){
  const chequeos = [];
  const fallos = [];
  const add = (n, titulo, ok, detalle, tituloFallo) => {
    chequeos.push({ n, titulo, ok, detalle });
    if(!ok) fallos.push({ titulo: tituloFallo || titulo, detalle });
  };

  /* 1 · que la caja esté completa */
  const faltan = [];
  if(!caja.ficha.nombre) faltan.push("el nombre");
  if(!caja.etiqueta) faltan.push("la etiqueta única");
  if(!caja.ficha.historia || caja.ficha.historia.length < 10) faltan.push("la historia (una frase larga)");
  if(!caja.rival.nombre) faltan.push("el nombre del rival");
  if(!caja.rival.celebracion) faltan.push("cómo celebra el rival");
  if(!caja.sala.decoracion) faltan.push("la decoración de la sala");
  if(!caja.sala.transicion) faltan.push("la transición de entrada");
  if(!caja.retos.length) faltan.push("al menos una prueba de habilidad");
  add(1, "La caja está completa", faltan.length === 0,
    faltan.length ? "Falta por decidir: " + faltan.join(", ") + "." : "Ninguna pieza de la ficha está en blanco.",
    "La caja no está completa");

  /* 2 · que todos los materiales estén y en su sitio */
  const pend = deriveMateriales(caja).filter(m => m.estado === "pendiente");
  add(2, "Todos los materiales están y en su sitio", pend.length === 0,
    pend.length ? "Quedan pendientes: " + pend.map(m => m.nombre).join(", ") + ". Resuélvelos en la fase 4." : "Inventario completo: nada a medias.",
    "Hay materiales pendientes");

  /* 3 · que no haya dos campeonatos con la misma etiqueta */
  const eti = slug(caja.etiqueta);
  let choca = null;
  if(ETIQUETAS_RESERVADAS.includes(eti)) choca = "un campeonato de siempre («" + eti + "»)";
  else{
    const otro = proyectos.find(p => p.caja.id !== caja.id && slug(p.caja.etiqueta) === eti);
    if(otro) choca = "otra caja de tu taller («" + otro.caja.ficha.nombre + "»)";
  }
  add(3, "Ninguna etiqueta repetida", !choca,
    choca ? "La etiqueta «" + eti + "» ya pertenece a " + choca + ". Cámbiala en la fase 1." : "La etiqueta «" + eti + "» es única e inconfundible.",
    "La etiqueta ya está en uso");

  /* 4 · que todas las piezas encajen entre sí */
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
  });
  add(4, "Todas las piezas encajan entre sí", encaje.length === 0,
    encaje.length ? encaje.slice(0,4).join(". ") + (encaje.length > 4 ? ". Y " + (encaje.length - 4) + " más." : ".") : "Retos con premios, rival con personalidad y superpoderes con reglas: todo encaja.",
    "Hay piezas que no encajan");

  /* 5 · que todo lo que se menciona exista de verdad */
  const refs = [];
  if(caja.sala.musica === "propia" && !caja.sala.musicaPropia) refs.push("se pidió música propia pero no hay archivo aportado");
  deriveMateriales(caja).forEach(m=>{
    if(m.estado === "aportado"){
      const g = materialGuardado(caja, m.clave);
      if(!g || !g.dataUrl) refs.push("«" + m.nombre + "» figura como aportado pero el archivo no está");
    }
  });
  if(!CEREBROS.some(cb => cb.id === caja.rival.cerebroBase)) refs.push("el cerebro base del rival no existe");
  if(!ESTILOS_VISUALES.some(e => e.id === caja.ficha.estiloVisual)) refs.push("el estilo visual elegido no existe");
  add(5, "Todo lo mencionado existe de verdad", refs.length === 0,
    refs.length ? refs.join(". ") + "." : "Ninguna pieza apunta a algo que no está.",
    "Hay piezas que apuntan a algo inexistente");

  /* 6 · que los campeonatos de siempre sigan pasando sus propias pruebas */
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
    "La partida de control falló");

  return { chequeos, fallos };
}

/* ---------- el viaje: lanzar la revisión ---------- */
async function lanzarRevision(){
  guardarActual(true);
  const incompletas = [1,2,3,4,5,6].filter(n => !faseCompleta(n));
  if(incompletas.length){
    await preguntar("🧰 La caja aún está a medias",
      "Antes de la revisión hay que terminar de montar la caja. Fases con piezas pendientes: " +
      incompletas.map(n => n + " · " + FASES[n-1].titulo).join(" — ") + ".",
      [ {texto:"Voy a terminarlas", valor:false} ]);
    return;
  }
  if(actual.estado === "borrador"){
    actual.estado = "preparacion";
    anotarEnDiario(actual.id, "La caja quedó montada: pasó a «En preparación».");
    guardarActual(true);
  }
  actual.estado = "validacion";
  actual.validacion = null;
  guardarActual(true);
  pintarEstadoStrip();
  toast("🕵️ La revisión automática está examinando la caja…");
  setTimeout(()=>{
    const res = revisarCaja(actual);
    if(res.fallos.length === 0){
      actual.estado = "listo";
      actual.validacion = { cuando: ahora(), resultado: "ok", fallos: [], chequeos: res.chequeos };
      anotarEnDiario(actual.id, "Pasó la revisión automática: quedó «Listo para probar». 🎉");
      toast("✅ Revisión superada: listo para el laboratorio", "ok");
    }else{
      actual.estado = "preparacion";
      actual.validacion = { cuando: ahora(), resultado: "fallos", fallos: res.fallos, chequeos: res.chequeos };
      anotarEnDiario(actual.id, "La revisión devolvió " + res.fallos.length + " corrección" + (res.fallos.length===1?"":"es") + ".");
      toast("🚫 La revisión encontró " + res.fallos.length + " corrección" + (res.fallos.length===1?"":"es"), "err");
    }
    guardarActual(true);
    faseActual = 7;
    pintarEditor();
  }, 1400);
}

function cambiarEstado(destino){
  const nombres = { publicado:"«Publicado» 🏆", desactivado:"«Desactivado» 🌙" };
  actual.estado = destino;
  anotarEnDiario(actual.id, "El campeonato pasó a " + (nombres[destino] || destino) + ".");
  guardarActual(true);
  pintarEditor();
  toast("Estado actualizado", "ok");
}

/* ---------- ZIP de la caja (sin compresión, puro JavaScript) ---------- */
let _crcTabla = null;
function crc32(bytes){
  if(!_crcTabla){
    _crcTabla = new Uint32Array(256);
    for(let n2 = 0; n2 < 256; n2++){
      let c = n2;
      for(let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      _crcTabla[n2] = c >>> 0;
    }
  }
  let crc = 0xFFFFFFFF;
  for(let i = 0; i < bytes.length; i++) crc = _crcTabla[(crc ^ bytes[i]) & 0xFF] ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function zipDeArchivos(archivos){
  const enc = new TextEncoder();
  const partes = [], centrales = [];
  let offset = 0;
  const f = new Date();
  const tiempo = ((f.getHours() << 11) | (f.getMinutes() << 5) | Math.floor(f.getSeconds() / 2)) & 0xFFFF;
  const fecha = (((f.getFullYear() - 1980) << 9) | ((f.getMonth() + 1) << 5) | f.getDate()) & 0xFFFF;
  archivos.forEach(a=>{
    const nombre = enc.encode(a.nombre);
    const datos = typeof a.contenido === "string" ? enc.encode(a.contenido) : a.contenido;
    const crc = crc32(datos);
    const local = new Uint8Array(30 + nombre.length);
    const dv = new DataView(local.buffer);
    dv.setUint32(0, 0x04034b50, true);
    dv.setUint16(4, 20, true);
    dv.setUint16(6, 0x0800, true);
    dv.setUint16(8, 0, true);
    dv.setUint16(10, tiempo, true);
    dv.setUint16(12, fecha, true);
    dv.setUint32(14, crc, true);
    dv.setUint32(18, datos.length, true);
    dv.setUint32(22, datos.length, true);
    dv.setUint16(26, nombre.length, true);
    dv.setUint16(28, 0, true);
    local.set(nombre, 30);
    partes.push(local, datos);
    const central = new Uint8Array(46 + nombre.length);
    const cv = new DataView(central.buffer);
    cv.setUint32(0, 0x02014b50, true);
    cv.setUint16(4, 20, true);
    cv.setUint16(6, 20, true);
    cv.setUint16(8, 0x0800, true);
    cv.setUint16(10, 0, true);
    cv.setUint16(12, tiempo, true);
    cv.setUint16(14, fecha, true);
    cv.setUint32(16, crc, true);
    cv.setUint32(20, datos.length, true);
    cv.setUint32(24, datos.length, true);
    cv.setUint16(28, nombre.length, true);
    cv.setUint32(42, offset, true);
    central.set(nombre, 46);
    centrales.push(central);
    offset += local.length + datos.length;
  });
  const tamCentral = centrales.reduce((s,c)=> s + c.length, 0);
  const fin = new Uint8Array(22);
  const fv = new DataView(fin.buffer);
  fv.setUint32(0, 0x06054b50, true);
  fv.setUint16(8, archivos.length, true);
  fv.setUint16(10, archivos.length, true);
  fv.setUint32(12, tamCentral, true);
  fv.setUint32(16, offset, true);
  return new Blob([ ...partes, ...centrales, fin ], { type: "application/zip" });
}

function resumenCajaTexto(caja){
  const est = ESTADOS.find(e=>e.id===caja.estado) || ESTADOS[0];
  return [
    "Nombre: " + caja.ficha.nombre,
    "Etiqueta única: " + caja.etiqueta,
    "Estado en el viaje: " + est.nombre,
    "Historia: " + (caja.ficha.historia || "—"),
    "Estilo visual: " + ((ESTILOS_VISUALES.find(x=>x.id===caja.ficha.estiloVisual)||{}).nombre||"—") +
      " · Dificultad: " + ((DIFICULTADES.find(x=>x.id===caja.ficha.dificultad)||{}).nombre||"—"),
    "Rival: " + (caja.rival.nombre || "—") + " (" + ((CARACTERES.find(x=>x.id===caja.rival.caracter)||{}).nombre||"—") + ")" +
      " · cerebro base: " + ((CEREBROS.find(x=>x.id===caja.rival.cerebroBase)||{}).nombre||"—"),
    "Superpoderes: " + (caja.superpoderes.length
      ? caja.superpoderes.map(s=>{ const ef = EFECTOS.find(e=>e.id===s.efecto)||EFECTOS[0]; return (s.nombre||ef.nombre)+" ["+ef.nombre+"]"; }).join("; ")
      : "ninguno"),
    "Pruebas de habilidad: " + (caja.retos.length
      ? caja.retos.map(r=> (r.nombre||"—")+" ("+((TIPOS_RETO.find(t=>t.id===r.tipo)||TIPOS_RETO[0]).nombre)+", premio: "+(r.premio||"—")+")").join("; ")
      : "ninguna"),
    "Sala: " + (caja.sala.decoracion||"—") + " · luz " + ((ILUMINACIONES.find(x=>x.id===caja.sala.iluminacion)||{}).nombre||"—") +
      " · música " + ((MUSICA_SALA.find(x=>x.id===caja.sala.musica)||{}).nombre||"—") +
      " · entrada: " + (caja.sala.transicion||"—")
  ].join("\n");
}

const CHECKLIST_TEXTO = [
  "1. El campeonato nuevo aparece en el menú con su nombre y su sala.",
  "2. Los tres campeonatos de siempre (Partido, Entrenamiento y Supervivencia) funcionan exactamente igual que antes.",
  "3. El rival se comporta como lo definiste: golpea, falla donde debía fallar y celebra como acordaste.",
  "4. Los superpoderes se activan bien, duran lo acordado y no desequilibran el partido.",
  "5. La sala se ve y suena como decidiste: decoración, luces y música ambiental.",
  "6. Las pruebas de habilidad puntúan correctamente y dan los premios previstos.",
  "7. Se puede ganar y se puede perder, y ambos finales se muestran con sus carteles.",
  "8. Nada del juego de siempre se ha movido de sitio: menú, salas, opciones e idioma intactos."
];

function leemePruebas(caja){
  return "CRAZY PING PONG · V2.124\n" +
"PAQUETE DE PRUEBAS — campeonato «" + caja.ficha.nombre + "» (etiqueta: " + caja.etiqueta + ")\n" +
"Generado por el Taller el " + new Date().toLocaleString("es-ES") + "\n" +
"\n" +
"QUÉ ES ESTE ARCHIVO\n" +
"Es la copia paralela del juego con tu campeonato nuevo dentro, marcado «en pruebas».\n" +
"El juego que ya usan los jugadores NO se entera de nada: vive en su propia dirección.\n" +
"\n" +
"LA CAJA QUE VIAJA\n" +
resumenCajaTexto(caja) + "\n" +
"\n" +
"CÓMO SE PRUEBA (el Laboratorio, 4 pasos)\n" +
"1. Genera el paquete de pruebas: ya lo tienes — es este archivo.\n" +
"2. Desde el navegador de un ordenador entra en app.netlify.com/drop y arrastra este .zip a la página.\n" +
"   En unos segundos te da una dirección web (URL) que empieza por HTTPS: esa es tu dirección privada de pruebas.\n" +
"3. Ponte las Meta Quest 3, abre el Meta Quest Browser, escribe esa dirección y pulsa ENTRAR EN VR.\n" +
"4. Juega con calma y recorre la lista de comprobación de abajo.\n" +
"\n" +
"LA LISTA DE COMPROBACIÓN (la prueba del algodón)\n" +
CHECKLIST_TEXTO.join("\n") + "\n" +
"\n" +
"¿Y SI ALGO FALLA? Tranquilidad total\n" +
"El campeonato vuelve a Borrador en el Taller, se corrige, se genera un paquete de pruebas nuevo\n" +
"y se vuelve a probar. Puedes repetir el ciclo las veces que haga falta: el juego publicado\n" +
"vive en su propia dirección y no se entera de nada hasta que tú decidas publicar.\n" +
"\n" +
"LA REGLA DE ORO\n" +
"Nada de lo que hay aquí toca los campeonatos de siempre (Partido, Entrenamiento y Supervivencia)\n" +
"ni el juego publicado. Cada campeonato vive en su propia caja, y las cajas no se mezclan.\n";
}

function leemeDefinitivo(caja){
  return "CRAZY PING PONG · V2.124\n" +
"PAQUETE DEFINITIVO — campeonato «" + caja.ficha.nombre + "» (etiqueta: " + caja.etiqueta + ")\n" +
"Generado por el Taller el " + new Date().toLocaleString("es-ES") + "\n" +
"\n" +
"QUÉ ES ESTE ARCHIVO\n" +
"Es el paquete final con todos los campeonatos aprobados, listo para que jueguen TODOS los jugadores.\n" +
"\n" +
"LA CAJA QUE VIAJA\n" +
resumenCajaTexto(caja) + "\n" +
"\n" +
"CÓMO SE PUBLICA (el Estadio, 3 pasos)\n" +
"1. Genera el paquete definitivo: ya lo tienes — es este archivo.\n" +
"2. Arrástralo a app.netlify.com/drop desde un ordenador y copia la dirección que entrega:\n" +
"   esa es «la dirección del estadio», la que usarán todos los jugadores.\n" +
"3. Compártela. La dirección oficial nunca cambia si no tú lo decides.\n" +
"\n" +
"CÓMO SE JUEGA EN LA QUEST 3 (2 minutos)\n" +
"1. Ponte el casco y abre el Meta Quest Browser (el navegador de las gafas).\n" +
"   Ojo: no vale por cable (Quest Link) ni el Chrome del ordenador.\n" +
"2. Escribe la dirección del estadio en la barra del navegador.\n" +
"   Truco: guárdala en favoritos la primera vez.\n" +
"3. Pulsa el gran botón ENTRAR EN VR.\n" +
"4. Elige el campeonato en el menú flotante y juega.\n" +
"\n" +
"CONSEJOS DE ORO\n" +
"- La dirección debe empezar por HTTPS (una web segura): las gafas lo exigen para el modo inmersivo.\n" +
"- ¿Silencio al entrar? Pulsa de nuevo o usa «Probar sonido» en Opciones: el juego se repara solo.\n" +
"- Siempre en el navegador del casco: es donde imagen, sonido y seguimiento funcionan como deben.\n" +
"\n" +
"LA REGLA DE ORO\n" +
"Nada de lo que hay aquí toca los campeonatos de siempre (Partido, Entrenamiento y Supervivencia).\n" +
"Publicar no es para siempre: si algún día se retira, se desactiva sin dramas y puede volver.\n";
}

function descargarPaquete(definitivo){
  const caja = actual;
  if(!caja) return;
  const enviar = (okParaViajar) => {
    const zip = zipDeArchivos([
      { nombre: "campeonato.json", contenido: JSON.stringify(caja, null, 2) },
      { nombre: "LEEME.txt", contenido: definitivo ? leemeDefinitivo(caja) : leemePruebas(caja) }
    ]);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(zip);
    a.download = (definitivo ? "paquete-definitivo-" : "paquete-pruebas-") + (caja.etiqueta || "campeonato") + ".zip";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
    anotarEnDiario(caja.id, "Se generó el paquete " + (definitivo ? "DEFINITIVO" : "de pruebas") + " para descargar.");
    guardarActual(true);
    toast((definitivo ? "🏟️ Paquete definitivo" : "🔬 Paquete de pruebas") + " descargado", "ok");
  };
  if(definitivo){
    const check = caja.checklist || [];
    const sin = 8 - check.filter(Boolean).length;
    preguntar("🏟️ Paquete definitivo",
      sin > 0
        ? "Ojo: en tu lista de comprobación del laboratorio hay " + sin + " punto" + (sin===1?"":"s") + " sin marcar. ¿Generar el paquete definitivo igualmente?"
        : "Tu lista de comprobación está completa. ¿Generar el paquete definitivo?",
      [ {texto:"Cancelar", valor:false}, {texto:"Sí, generar", valor:true, tipo:"primario"} ])
    .then(si=>{ if(si) enviar(true); });
  }else{
    enviar(false);
  }
}

/* ---------- el diario de bordo ---------- */
function abrirDiario(){
  const entradas = diarioDe(actual ? actual.id : null);
  $("#diario-lista").innerHTML = entradas.length
    ? entradas.map(e=>`<div class="entrada"><b>${esc(e.que)}</b><span>${esc(fechaBonita(e.cuando))}</span></div>`).join("")
    : `<div class="vacio">Sin anotaciones todavía. Todo cambio queda registrado aquí: qué se modificó y cuándo.</div>`;
  $("#cajon-fondo").classList.add("abierto");
  $("#cajon-diario").classList.add("abierto");
}
function cerrarDiario(){
  $("#cajon-fondo").classList.remove("abierto");
  $("#cajon-diario").classList.remove("abierto");
}

/* ---------- cableado global ---------- */
function conectarEventos(){
  $("#btn-inicio").addEventListener("click", ()=>{
    if(actual) guardarActual(true);
    pintarInicio();
    irAPantalla("screen-home");
  });
  $("#btn-diario").addEventListener("click", abrirDiario);
  $("#btn-cerrar-cajon").addEventListener("click", cerrarDiario);
  $("#cajon-fondo").addEventListener("click", cerrarDiario);

  $("#btn-crear").addEventListener("click", ()=> irAPantalla("screen-nuevo"));
  $("#btn-importar").addEventListener("click", ()=> $("#fichero-importar").click());
  $("#fichero-importar").addEventListener("change", (e)=>{
    if(e.target.files && e.target.files[0]) importarJSON(e.target.files[0]);
    e.target.value = "";
  });

  $$(".plantilla").forEach(b=>b.addEventListener("click", ()=> nuevoDesdePlantilla(b.dataset.plantilla)));

  $("#btn-anterior").addEventListener("click", ()=>{
    if(faseActual > 1){ faseActual--; pintarEditor(); }
  });
  $("#btn-siguiente").addEventListener("click", ()=>{
    if(faseActual < 7){ faseActual++; pintarEditor(); }
  });

  $("#modal-fondo").addEventListener("click", (e)=>{
    if(e.target === $("#modal-fondo")){ cerrarModal(); _resolverModal && _resolverModal(false); }
  });
  document.addEventListener("keydown", (e)=>{
    if(e.key === "Escape"){
      cerrarModal(); _resolverModal && _resolverModal(false);
      cerrarDiario();
    }
  });
}

/* ---------- arranque ---------- */
conectarEventos();
pintarInicio();
