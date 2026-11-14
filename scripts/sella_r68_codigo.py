#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r68_codigo.py — FASE 162 · r68 · CIRUGÍA DE c12 (EL ARCO).
Todas las ediciones con ancla asertada (count==1 salvo needsUpdate==N).
Piezas: buildMenu (3 panelas + lienzo virtual) · pin ON por defecto ·
anchorMenu en la cabeza · _menuTexSube (troceado virtual→3 texturas) ·
rayo por panela · drawMenu (concha + legado 0,911) · drawMenuHeader→concha ·
drawMenuConcha (nuevo) · _menuRejilla (nuevo) · helpers caramelo como
métodos · drawMenuVestibulo v2 (héroe, sin dock, salir en TU CASA) ·
rejilla de AJUSTES en drawMenuOpts · prompts caramelo (salida/hall) ·
dedup de botones atrás legados · import CONFIG_SECCIONES."""
import re
import sys
from pathlib import Path

F = Path('/home/z/my-project/upload/src/game/core/c12_pingponggame.js')
t0 = F.read_text(encoding='utf-8')
t = t0
n_ok = 0


def edit(nombre, ancla, nuevo, esperados=1):
    global t, n_ok
    k = t.count(ancla)
    if k != esperados:
        sys.exit(f'ABORTA {nombre}: count={k} (esperaba {esperados})')
    t = t.replace(ancla, nuevo)
    n_ok += 1


# ---------------------------------------------------------------- E1 · import
edit('import CONFIG_SECCIONES',
     'CONFIG_DIFICULTAD, CONFIG_MENU, CONFIG_MENUS, CONFIG_TORNEOS, DIMS,',
     'CONFIG_DIFICULTAD, CONFIG_MENU, CONFIG_MENUS, CONFIG_SECCIONES, '
     'CONFIG_TORNEOS, DIMS,')

# ------------------------------------------------- E2 · buildMenu: el arco
E2_ANCLA = """    this.menuCanvas = document.createElement('canvas');
    // r67 · FASE 161 · EL VESTÍBULO: el lienzo pasa a PANORÁMICO 2560×1440
    // (16:9) para componer los TRES paneles + dock de la página principal;
    // las páginas legadas 1024×1536 se pintan escaladas y centradas (ver
    // drawMenu). A ~1,08 m: ~1600 texel/m horizontal (antes ~1138) — MÁS
    // nitidez, mismo presupuesto de repintado (sin mips, como r105).
    this.menuCanvas.width = 2560;
    this.menuCanvas.height = 1440;"""
E2_NUEVO = """    /* r68 · FASE 162 · EL ARCO (petición del dueño: «el menú debe ocupar
     * prácticamente toda la pantalla… los 3 bloques equidistantes como si
     * de una pantalla curva se tratase… por defecto aparecerá anclado en el
     * centro (chincheta pulsada) a una distancia que permita su lectura
     * cómoda»): TRES panelas físicas — centro 0,98 m a 1,15 m, lados 0,74 m
     * a 1,25 m, yaw ±36° — alimentadas por UN LIENZO VIRTUAL
     * (CONFIG_MENUS.lienzo 3696×1400) que drawMenu pinta entero y
     * _menuTexSube() trocea a las tres texturas. El rayo lee la panela
     * tocada y suma su offset → coordenadas VIRTUALES (los rects viven
     * ahí). ~1500 texel/m a 1,15 m — nítido sin mips (r105). Cobertura
     * angular ≈105°: pantalla casi completa, centros equidistantes. */
    this._menuPanelas = [];
    this._menuPanelaDe = {};
    this.menuCanvas = document.createElement('canvas');   // LIENZO VIRTUAL
    this.menuCanvas.width = CONFIG_MENUS.lienzo.ancho;
    this.menuCanvas.height = CONFIG_MENUS.lienzo.alto;"""
edit('buildMenu lienzo virtual', E2_ANCLA, E2_NUEVO)

E2B_ANCLA = """    this.menuTex = new THREE.CanvasTexture(this.menuCanvas);
    this.menuTex.colorSpace = THREE.SRGBColorSpace;"""
E2B_NUEVO = """    this.menuTex = null;   // r68 · la textura «central» se crea en el bucle
    for (const pa of CONFIG_MENUS.arco.panelas) {
      const cv = document.createElement('canvas');
      cv.width = pa.w;
      cv.height = CONFIG_MENUS.lienzo.alto;
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      // sin mips (r105): magnificación pura a ~1,15 m
      tex.generateMipmaps = false;
      tex.minFilter = THREE.LinearFilter;
      tex.anisotropy = 1;
      const mesh = new THREE.Mesh(
        new THREE.PlaneGeometry(pa.anchoM, pa.altoM),
        new THREE.MeshBasicMaterial({
          map: tex, transparent: true, depthTest: false }),
      );
      // r68 · posición en el arco (el grupo vive EN LA CABEZA — ver
      // anchorMenu): centro al frente, lados abiertos en yaw a su dist,
      // cada panela GIRADA hacia el jugador (pantalla curva real).
      const yaw = (pa.yaw * Math.PI) / 180;
      mesh.position.set(-Math.sin(yaw) * pa.dist,
        CONFIG_MENUS.arco.yCentro, -Math.cos(yaw) * pa.dist);
      mesh.rotation.y = -yaw;
      mesh.renderOrder = 9998;   // r73 · EL MENÚ MANDA (bajo la chapa 9999)
      mesh.userData.panela = pa;
      mesh.userData.cv = cv;
      mesh.userData.tex = tex;
      this.menuGroup.add(mesh);
      this._menuPanelas.push(mesh);
      this._menuPanelaDe[pa.id] = mesh;
      if (pa.id === 'C') { this.menuTex = tex; this.menuMesh = mesh; }
    }
    if (!this.menuTex) throw new Error('arco sin panela C');"""
edit('buildMenu tres panelas', E2B_ANCLA, E2B_NUEVO)

E2C_ANCLA = """    // r105 · RENDIMIENTO: el panel vive a ~1 m del jugador — MAGNIFICACIÓN
    // pura (el visor pide MÁS píxeles de los que tiene la textura 1024×1536),
    // así que los mips no aportan nitidez y CADA repintado del canvas pagaba
    // su generación (~12 niveles en GPU) encima del upload de 6 MB. Sin mips
    // el repintado es más barato y el aspecto a 1 m es IDÉNTICO (mip 0 +
    // bilineal era lo que ya se usaba en magnificación con mips activos).
    this.menuTex.generateMipmaps = false;
    this.menuTex.minFilter = THREE.LinearFilter;
    this.menuTex.anisotropy = 1;   // sin mips el anisotrópico no aplica (era 8)
    // r67 · plano panorámico 1,60×0,90 m (16:9, misma área visible que la
    // referencia del dueño): los 3 paneles en arco caben en el FOV a 1,08 m.
    // El mapeo del rayo (uv→px y cursor) se lee VIVO de canvas/geometry —
    // ya no puede desincronizarse (fin del FIX DERIVA r105 por literales).
    this.menuMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1.60, 0.90),
      new THREE.MeshBasicMaterial({ map: this.menuTex, transparent: true, depthTest: false }),
    );
    // r73 · EL MENÚ MANDA: el panel del menú es la ventana que manda donde
    // sea que se despliegue — se pinta POR ENCIMA de cualquier otra ventana
    // (instrucciones 9994/9995, mapa del oeste 9990..9996, telón 65..70,
    // conseguido 60). Sólo la chapa del MODO DEPURACIÓN (9999) comparte
    // cielo, y es una marca de agua, no una ventana. Al estar el grupo
    // oculto el orden no afecta a nada más.
    this.menuMesh.renderOrder = 9998;   // antes 990 (bajo instrucciones/mapa)
    this.menuGroup.add(this.menuMesh);"""
edit('buildMenu malla única fuera', E2C_ANCLA, '')

# ------------------------------------------------------------ E3 · pin ON
E3_ANCLA = """    /* r113 · LA CHINCHETA DEL MENÚ (petición del dueño): icono de chincheta
     * SIEMPRE visible en el CENTRO SUPERIOR del panel. POR DEFECTO OFF (el
     * menú se comporta como siempre: anclaje delante de la cara + flotación
     * de 1,8 s y fijo). Al pulsarla el menú queda ANCLADO al punto del
     * espacio donde estaba en ese instante (anchorMenu deja de reposicionar
     * — ni flotación ni re-anclajes al reabrir). Pulso de nuevo = soltar:
     * el panel vuelve a anclarse delante de la cabeza. Estado en memoria
     * (cada sesión arranca con la chincheta OFF, tal cual pidió el dueño). */
    this.menuPin = false;             // r113: OFF por defecto (petición expresa)"""
E3_NUEVO = """    /* r113 · LA CHINCHETA DEL MENÚ. r68 · FASE 162 · ON POR DEFECTO
     * (petición del dueño: «por defecto el menú aparecerá anclado en el
     * centro (chincheta pulsada) a una distancia que permita su lectura
     * cómoda, incluso los textos más pequeños»): cada APERTURA ancla el
     * arco EN LA CABEZA (anchorMenu) y el pin lo deja FIJO sin flotación.
     * Soltarla devuelve el modo flotante r113 (sigue a la cabeza 1,8 s). */
    this.menuPin = true;              // r68: ON por defecto (petición expresa)"""
edit('pin ON por defecto', E3_ANCLA, E3_NUEVO)

E3B_ANCLA = """    // r67 · el pin cuelga sobre el borde SUPERIOR del plano panorámico
    // (alto 0,90 → 0,45 + 0,032 de pie = 0,482; antes 0,707 con 1,35)
    this._menuPinMesh.position.set(0, 0.482, 0.006);"""
E3B_NUEVO = """    // r68 · el pin cabalga el borde superior de la PANELA CENTRAL del arco
    this._menuPinMesh.position.set(0,
      CONFIG_MENUS.arco.yCentro + 0.475 + 0.032,
      -(CONFIG_MENUS.arco.panelas[1].dist - 0.006));"""
edit('pin en la panela central', E3B_ANCLA, E3B_NUEVO)

# --------------------------------------------- E4 · _menuTexSube + anchorMenu
E4_ANCLA = """  anchorMenu() {
    if (this.menuPin) { this._menuAnchorUntil = 0; return; }
    this.camera.getWorldPosition(muHead);
    this.camera.getWorldQuaternion(muQ);
    muDir.set(0, 0, -1).applyQuaternion(muQ);
    muDir.y = 0;
    if (muDir.lengthSq() < 1e-6) muDir.set(0, 0, -1);
    muDir.normalize();
    this.menuGroup.position.copy(muHead).addScaledVector(muDir, 1.08);
    // r104 · panel 1,35 m de alto: el centro baja 7 cm para repartir la
    // altura nueva (arriba 27°· abajo 36° aprox.) sin perder la cabecera
    this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.12);
    this.menuGroup.lookAt(muHead);
    this._menuAnchorUntil = performance.now() / 1000 + 1.8;
    // r114 · la ancla se FIRMA: estancia donde nace + z del rig de ese
    // momento. updateMenu vigila la firma — si el jugador viaja de escena
    // o el rig se teletransporta, el ancla vieja se invalida sola.
    this._menuAnchorEst = this._menuEstancia();
    this._menuAnchorRigZ = this.rig ? this.rig.position.z : 0;
  }"""
E4_NUEVO = """  /** r68 · FASE 162 · trocea el lienzo virtual a las TRES texturas del
   * arco. drawMenu pinta UNA vez en el virtual; aquí viaja cada rodaja a
   * su panela (L/C/R). Los «needsUpdate» del drawMenu delegan AQUÍ. */
  _menuTexSube() {
    const li = CONFIG_MENUS.lienzo;
    for (const mesh of this._menuPanelas) {
      const pa = mesh.userData.panela;
      const cv = mesh.userData.cv;
      const c2 = cv.getContext('2d');
      c2.setTransform(1, 0, 0, 1, 0, 0);
      c2.clearRect(0, 0, pa.w, li.alto);
      c2.drawImage(this.menuCanvas, pa.x, 0, pa.w, li.alto,
        0, 0, pa.w, li.alto);
      mesh.userData.tex.needsUpdate = true;
    }
  }

  /** r68 · anchorMenu reescrito para EL ARCO: el grupo vive EN LA CABEZA
   * (posición + yaw de la vista, sin pitch/roll) y las panelas cuelgan del
   * arco CONFIG_MENUS — centros a 1,15/1,25 m, cada una mirando al jugador
   * (pantalla curva equidistante). Con chincheta (r68: por defecto) el
   * arco queda FIJO (sin flotación); sin chincheta, flotación r113 de
   * 1,8 s. La firma r114 (estancia + rig z) se conserva intacta. */
  anchorMenu() {
    this.camera.getWorldPosition(muHead);
    this.camera.getWorldQuaternion(muQ);
    muDir.set(0, 0, -1).applyQuaternion(muQ);
    muDir.y = 0;
    if (muDir.lengthSq() < 1e-6) muDir.set(0, 0, -1);
    muDir.normalize();
    // r68 · el ORIGEN del grupo es la cabeza: el arco se despliega delante
    this.menuGroup.position.copy(muHead);
    this.menuGroup.lookAt(muHead.x + muDir.x, muHead.y, muHead.z + muDir.z);
    if (this.menuPin) this._menuAnchorUntil = 0;   // fijo: sin flotación
    else this._menuAnchorUntil = performance.now() / 1000 + 1.8;
    this._menuAnchorEst = this._menuEstancia();
    this._menuAnchorRigZ = this.rig ? this.rig.position.z : 0;
  }"""
edit('anchorMenu en la cabeza + texSube', E4_ANCLA, E4_NUEVO)

# ------------------------------------------------- E5 · reapertura honesta
E5_ANCLA = """      // r114 · reapertura HONESTA: si el ancla clavada quedó lejos de la
      // cabeza (el jugador caminó con la chincheta puesta), se suelta y el
      // menú nace SIEMPRE delante — nunca «no lo veo» al pulsar B.
      if (this.menuPin) {
        this.camera.getWorldPosition(muHead);
        if (this.menuGroup.position.distanceTo(muHead) > 2.5) {
          this.menuPin = false;
          this._menuPinDraw();
        }
      }
      this.anchorMenu();          // v2.28: DELANTE del jugador, no en la muñeca"""
E5_NUEVO = """      // r68 · cada apertura nace EN LA CABEZA y CON LA CHINCHETA PUESTA
      // (petición del dueño): el arco aparece centrado, equidistante y fijo.
      // La honestidad r114 sigue garantizada: el ancla se re-firma aquí
      // (estancia + rig z) y el heal r114 re-ancla si la escena viaja.
      this.menuPin = true;
      this._menuPinDraw();
      this.anchorMenu();          // r68: el arco nace en la cabeza"""
edit('toggleMenu: pin + ancla en cabeza', E5_ANCLA, E5_NUEVO)

E5B_ANCLA = """    // r114 · el prompt B nace SIEMPRE delante: si el ancla clavada quedó
    // lejos de la cabeza (otro escenario o el jugador caminó), se suelta.
    if (this.menuPin) {
      this.camera.getWorldPosition(muHead);
      if (this.menuGroup.position.distanceTo(muHead) > 2.5 ||
          this._menuEstancia() !== this._menuAnchorEst) {
        this.menuPin = false;
        this._menuPinDraw();
      }
    }
    this.anchorMenu();"""
E5B_NUEVO = """    // r68 · el prompt B también nace en la cabeza con la chincheta puesta
    this.menuPin = true;
    this._menuPinDraw();
    this.anchorMenu();"""
edit('openHallAsk: pin + ancla', E5B_ANCLA, E5B_NUEVO)

# ----------------------------------------------------------- E6 · raycast
E6_ANCLA = """        const hit = (this.menuOpen && !this._arconoOn)
          ? (muRaycaster.intersectObject(this.menuMesh, false)[0] || null)
          : null;"""
E6_NUEVO = """        // r68 · el rayo prueba las TRES panelas del arco
        const hit = (this.menuOpen && !this._arconoOn)
          ? (muRaycaster.intersectObjects(this._menuPanelas, false)[0] || null)
          : null;"""
edit('rayo a las tres panelas', E6_ANCLA, E6_NUEVO)

E6B_ANCLA = """          // r67 · px/py se leen VIVOS de las dimensiones del canvas
          // (2560×1440) — ya no hay literales que desincronizar.
          const px = hit.uv.x * this.menuCanvas.width;
          const py = (1 - hit.uv.y) * this.menuCanvas.height;"""
E6B_NUEVO = """          // r68 · px/py VIRTUALES: la panela tocada aporta su offset —
          // los rects de TODAS las páginas viven en el lienzo virtual.
          const paHit = hit.object.userData.panela;
          const px = paHit.x + hit.uv.x * paHit.w;
          const py = (1 - hit.uv.y) * CONFIG_MENUS.lienzo.alto;"""
edit('px/py virtuales por panela', E6B_ANCLA, E6B_NUEVO)

E6C_ANCLA = """          // r67 · dimensiones leídas VIVAS de geometry.parameters (1.60×0.90)
          // — el FIX DERIVA r105 se vuelve estructural: impossible que el
          // cursor y el plano diverjan (mismo objeto THREE del que nace uv).
          dot.visible = true;
          const gp = this.menuMesh.geometry.parameters;
          dot.position.set((hit.uv.x - 0.5) * gp.width,
            (hit.uv.y - 0.5) * gp.height, 0.004);"""
E6C_NUEVO = """          // r68 · el cursor vive en la panela tocada: local→grupo (la
          // panela está yaweada y desplazada en el arco — pantalla curva).
          dot.visible = true;
          dot.position.set((hit.uv.x - 0.5) * paHit.anchoM,
            (hit.uv.y - 0.5) * paHit.altoM, 0.004)
            .applyQuaternion(hit.object.quaternion)
            .add(hit.object.position);"""
edit('cursor en la panela', E6C_ANCLA, E6C_NUEVO)

# ------------------------------------------------------- E7 · drawMenu top
E7_ANCLA = """    const W = 2560, H = 1440;"""
E7_NUEVO = """    const W = CONFIG_MENUS.lienzo.ancho, H = CONFIG_MENUS.lienzo.alto;"""
edit('drawMenu W/H desde CONFIG', E7_ANCLA, E7_NUEVO)

E7B_ANCLA = """    const LEG = this.menuPage !== 'main';
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.clearRect(0, 0, W, H);
    if (LEG) {
      this._menuMap = { s: 0.9375, dx: 800, dy: 0 };
      c.setTransform(0.9375, 0, 0, 0.9375, 800, 0);
      // tarjeta (sólo legado: el Vestíbulo compone sus propios paneles)
      rr(8, 8, 1024 - 16, 1536 - 16, 36);
      c.fillStyle = 'rgba(10,13,20,0.95)';
      c.fill();
      c.strokeStyle = 'rgba(232,180,90,0.6)';
      c.lineWidth = 4;
      c.stroke();
    } else {
      this._menuMap = null;
    }"""
E7B_NUEVO = """    const LEG = this.menuPage !== 'main';
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.clearRect(0, 0, W, H);
    this._menuConchaPintada = false;
    if (LEG) {
      // r68 · CONCHA de secciones (cristal en las TRES panelas + título +
      // atrás, de CONFIG_SECCIONES) y luego el contenido legado 1024×1536
      // centrado (escala 0,911) sobre una placa serena. Los rects de todos
      // los painters se mapean (btn + _mapRect — misma cuenta).
      const S68 = H / 1536, DX68 = (W - 1024 * S68) / 2;
      this._menuMap = { s: S68, dx: DX68, dy: 0 };
      this.drawMenuConcha(rects);
      c.setTransform(S68, 0, 0, S68, DX68, 0);
      rr(8, 200, 1024 - 16, 1536 - 208, 30);
      c.fillStyle = 'rgba(8,12,24,0.72)';
      c.fill();
      c.strokeStyle = 'rgba(232,180,90,0.35)';
      c.lineWidth = 3;
      c.stroke();
    } else {
      this._menuMap = null;
    }"""
edit('drawMenu concha + legado 0,911', E7B_ANCLA, E7B_NUEVO)

# --------------------------------------------- E8 · helpers como métodos
E8_ANCLA = """  /* ================== r67 · FASE 161 · EL VESTÍBULO ===================="""
E8_NUEVO = """  /* ============ r68 · FASE 162 · HELPERS CARAMERO (métodos) ============
   *  Los mismos helpers del Vestíbulo r67, ahora compartidos por la
   *  concha de secciones, las rejillas y los prompts: icono (decode+cache
   *  de ICONOS_MENUS), RR (roundRect), candy (botón caramelo) y medallón. */
  _vestIcono(nombre) {
    if (!this._menuIconos) this._menuIconos = {};
    const ent = ICONOS_MENUS.iconos[nombre];
    if (!ent) return null;
    let im = this._menuIconos[nombre];
    if (!im) {
      im = new Image();
      im.src = ent.src;
      this._menuIconos[nombre] = im;
    }
    return (im.complete && im.naturalWidth) ? im : null;
  }

  _vestRR(c, x, y, w, h, r) {
    if (c.roundRect) { c.beginPath(); c.roundRect(x, y, w, h, r); }
    else { c.beginPath(); c.rect(x, y, w, h); }
  }

  _vestCandy(c, x, y, w, h, grad, r) {
    const g = c.createLinearGradient(0, y, 0, y + h);
    g.addColorStop(0, grad[0]);
    g.addColorStop(1, grad[1]);
    c.save();
    c.shadowColor = 'rgba(0,0,0,0.45)';
    c.shadowBlur = 14;
    c.shadowOffsetY = 5;
    this._vestRR(c, x, y, w, h, r);
    c.fillStyle = g;
    c.fill();
    c.restore();
    this._vestRR(c, x, y, w, h, r);
    c.strokeStyle = 'rgba(6,12,26,0.85)';
    c.lineWidth = 4;
    c.stroke();
    this._vestRR(c, x + 4, y + 4, w - 8, h - 8, Math.max(6, r - 4));
    c.strokeStyle = 'rgba(255,255,255,0.30)';
    c.lineWidth = 2;
    c.stroke();
    c.save();
    this._vestRR(c, x + 4, y + 4, w - 8, h * 0.46, Math.max(6, r - 2));
    c.clip();
    const sg = c.createLinearGradient(0, y, 0, y + h * 0.55);
    sg.addColorStop(0, 'rgba(255,255,255,0.32)');
    sg.addColorStop(1, 'rgba(255,255,255,0.02)');
    c.fillStyle = sg;
    c.fillRect(x, y, w, h * 0.58);
    c.restore();
  }

  _vestMedallion(c, cx, cy, r, nombre) {
    c.beginPath();
    c.arc(cx, cy, r, 0, Math.PI * 2);
    c.fillStyle = 'rgba(10,16,34,0.92)';
    c.fill();
    c.lineWidth = 4;
    c.strokeStyle = 'rgba(255,255,255,0.85)';
    c.stroke();
    const im = this._vestIcono(nombre);
    if (im) {
      const esc = (ICONOS_MENUS.iconos[nombre].escala || 1) *
        (r * 1.52) / 256;
      const dw = im.naturalWidth * esc, dh = im.naturalHeight * esc;
      c.drawImage(im, cx - dw / 2, cy - dh / 2, dw, dh);
    }
  }

  /** r68 · LA CONCHA DE SECCIONES (CONFIG_SECCIONES.shell): cristal
   *  continuo en las TRES panelas del arco con marco cian por panela,
   *  botón ATRÁS con icono (panela L), título con medallón (panela C),
   *  palas de idioma y sello (panela R). Los painters legados siguen
   *  llamando drawMenuHeader: llamada idempotente (bandera por frame). */
  drawMenuConcha(rects) {
    const c = this.menuCanvas.getContext('2d');
    const CM = CONFIG_MENUS, CS = CONFIG_SECCIONES;
    const li = CM.lienzo;
    this._menuConchaPintada = true;
    const sh = CS.shell[this.menuPage] ||
      { tituloKey: '', icono: 'vestibulo', volver: 'page:main' };
    // cristal de fondo continuo
    const g = c.createLinearGradient(0, 0, 0, li.alto);
    g.addColorStop(0, 'rgba(20,34,72,0.97)');
    g.addColorStop(1, 'rgba(7,11,24,0.98)');
    c.fillStyle = g;
    c.fillRect(0, 0, li.ancho, li.alto);
    // marco cian por panela (las 3 pantallas del arco)
    for (const pa of CM.arco.panelas) {
      this._vestRR(c, pa.x + 4, 4, pa.w - 8, li.alto - 8, 26);
      c.strokeStyle = 'rgba(90,190,255,0.7)';
      c.lineWidth = 3;
      c.stroke();
      this._vestRR(c, pa.x + 10, 10, pa.w - 20, li.alto - 20, 22);
      c.strokeStyle = 'rgba(255,255,255,0.12)';
      c.lineWidth = 2;
      c.stroke();
    }
    // ATRÁS (panela L, arriba a la izquierda) — id del dato (volver)
    {
      const bx = 44, by = 44, bw = 300, bh = 88;
      const hovered = this.menuHover.includes(rects.length);
      this._vestCandy(c, bx, by, bw, bh,
        hovered ? ['#3a76d8', '#1d3f8f'] : ['#22335e', '#131e3c'], 26);
      this._vestMedallion(c, bx + 56, by + bh / 2, 32, 'atras');
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillStyle = '#ffffff';
      c.font = '800 34px system-ui, sans-serif';
      c.fillText(T('page_back'), bx + 104, by + bh / 2 + 1);
      rects.push({ x: bx - 6, y: by - 4, w: bw + 12, h: bh + 8,
        id: sh.volver });
    }
    // TÍTULO con medallón (panela C)
    {
      const pC = CM.arco.panelas[1];
      const tx = pC.x + 44;
      this._vestMedallion(c, tx + 52, 92, 52, sh.icono);
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillStyle = '#ffffff';
      c.font = '900 58px system-ui, sans-serif';
      let tit = sh.tituloKey ? T(sh.tituloKey) : '';
      while (tit.length > 2 && c.measureText(tit).width > pC.w - 200) {
        tit = tit.slice(0, -1);
      }
      c.fillText(tit, tx + 128, 94);
    }
    // palas de idioma (panela R, arriba a la derecha) + sello
    {
      const pR = CM.arco.panelas[2];
      this._langPaddle(rects, 'es', pR.x + pR.w - 306, 36);
      this._langPaddle(rects, 'en', pR.x + pR.w - 162, 36);
      c.textAlign = 'right';
      c.textBaseline = 'alphabetic';
      c.fillStyle = '#ffd257';
      c.font = '800 22px system-ui, sans-serif';
      c.fillText('V' + (typeof window !== 'undefined' && window.__PP_VERSION
        ? window.__PP_VERSION : ''), pR.x + pR.w - 24, 216);
    }
  }

  /** r68 · REJILLA data-driven (CONFIG_SECCIONES.rejillas): tarjetas-icono
   *  en dos columnas sobre las panelas C y R. subs = {idSinPage: texto}
   *  para los subtítulos vivos. Cero texto de más, iconos explicativos. */
  _menuRejilla(rects, nombre, subs) {
    const c = this.menuCanvas.getContext('2d');
    const rej = CONFIG_SECCIONES.rejillas[nombre];
    if (!rej) return;
    const CM = CONFIG_MENUS;
    const cols = rej.columnas.map((id) => CM.arco.panelas.find(
      (p) => p.id === id)).filter(Boolean);
    const porCol = Math.ceil(rej.tarjetas.length / cols.length);
    cols.forEach((pa, ci) => {
      const inner = pa.id === 'C' ? 80 : 44;
      const gx = pa.x + inner, gw = pa.w - inner * 2;
      const items = rej.tarjetas.slice(ci * porCol, (ci + 1) * porCol);
      const n = items.length;
      const hAuto = n > 0
        ? Math.min(rej.h, Math.floor((1252 - rej.y - (n - 1) * rej.gap) / n))
        : rej.h;
      items.forEach((t, i) => {
        const y = rej.y + i * (hAuto + rej.gap);
        const hovered = this.menuHover.includes(rects.length);
        this._vestCandy(c, gx, y, gw, hAuto, t.gradiente, 26);
        const ir = 44, icx = gx + 30 + ir, icy = y + hAuto / 2;
        this._vestMedallion(c, icx, icy, ir, t.icono);
        const tx = icx + ir + 24, maxw = gx + gw - tx - 28;
        c.textAlign = 'left';
        c.textBaseline = 'alphabetic';
        c.fillStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.97)';
        let f1 = 42;
        c.font = `800 ${f1}px system-ui, sans-serif`;
        let lab = T(t.etiquetaKey);
        while (c.measureText(lab).width > maxw && f1 > 22) {
          f1 -= 2;
          c.font = `800 ${f1}px system-ui, sans-serif`;
        }
        c.fillText(lab, tx, y + hAuto * 0.42);
        const sub = subs && subs[t.id.replace('page:', '')];
        if (sub) {
          let f2 = 23;
          c.font = `600 ${f2}px system-ui, sans-serif`;
          let sub2 = String(sub);
          while (c.measureText(sub2).width > maxw && f2 > 14) {
            f2 -= 2;
            c.font = `600 ${f2}px system-ui, sans-serif`;
          }
          while (c.measureText(sub2).width > maxw && sub2.length > 2) {
            sub2 = sub2.slice(0, -1);
          }
          if (sub2 !== String(sub)) sub2 += '\u2026';
          c.fillStyle = 'rgba(228,240,255,0.92)';
          c.fillText(sub2, tx, y + hAuto * 0.74);
        }
        if (hovered) {
          this._vestRR(c, gx, y, gw, hAuto, 26);
          c.strokeStyle = '#ffffff';
          c.lineWidth = 4;
          c.stroke();
        }
        rects.push({ x: gx - 6, y: y - 4, w: gw + 12, h: hAuto + 8,
          id: t.id });
      });
    });
  }

  /* ================== r67 · FASE 161 · EL VESTÍBULO ===================="""
edit('helpers + concha + rejilla', E8_ANCLA, E8_NUEVO)

F.write_text(t, encoding='utf-8')
print(f'PARTE 1 OK: {n_ok} ediciones aplicadas')
