# -*- coding: utf-8 -*-
"""Genera qa_vestibulo_r81.py a partir del r80: regresión íntegra + FASE 177
«MENÚS EN ESCENA» (agujas estáticas FX + checks vivos de cascada/pulso/flash/salida)."""
import pathlib

SRC = pathlib.Path('/home/z/my-project/scripts/qa_vestibulo_r80.py')
DST = pathlib.Path('/home/z/my-project/scripts/qa_vestibulo_r81.py')
t = SRC.read_text(encoding='utf-8')

REEM = [
 ("\"\"\"qa_vestibulo_r80.py — QA de la FASE 176 «MENUS QUE RESPIRAN» · r80 · V3.6.171-SDK6.",
  "\"\"\"qa_vestibulo_r81.py — QA de la FASE 177 «MENÚS EN ESCENA» · r81 · V3.6.172-SDK6.\n\nFASE 177 (el dueño: «el menú al pulsar B, fijo y sin seguimiento de la vista, con\nlas animaciones y efectos de la competencia»): el arco ENTRA EN ESCENA con\ncascada C→L/R (+70 ms) y rebote easeOutBack + fundido; SALE encogiendo y\ndesvaneciendo; cada PULSACIÓN respira (pulso 1→1.03→1 + flash blanco en la\nfila + haptic fuerte); el FOCO tickea (osc + haptic) al cambiar de fila.\nEl ancla fija r69/r114 queda INTACTA (el FX nunca recoloca el grupo).\nRegresión ÍNTEGRA r80 (FASE 176) incluida."),
 ("/home/z/my-project/download/r80_capturas", "/home/z/my-project/download/r81_capturas"),
 ("chk('3.6.171-SDK6' in game, 'game.html sello 3.6.171-SDK6 (FASE 174 «MENÚS EN PROFUNDIDAD»)')",
  "chk('3.6.172-SDK6' in game, 'game.html sello 3.6.172-SDK6 (FASE 177 «MENÚS EN ESCENA»)')"),
 ("chk('3.6.171-SDK6' in vjson and 'MENUS QUE RESPIRAN' in vjson,\n        'VERSION.json sella 3.6.171 + FASE 176')",
  "chk('3.6.172-SDK6' in vjson and 'MENUS EN ESCENA' in vjson,\n        'VERSION.json sella 3.6.172 + FASE 177')"),
 ("chk(\"crazypp-v3.6.171-SDK6\" in swjs, 'sw.js CACHE sella v3.6.171 (purga de cachés viejas)')",
  "chk(\"crazypp-v3.6.172-SDK6\" in swjs, 'sw.js CACHE sella v3.6.172 (purga de cachés viejas)')"),
 ("chk('V3.6.171-SDK6' in hub, 'hub /descargas sella V3.6.171-SDK6')",
  "chk('V3.6.172-SDK6' in hub, 'hub /descargas sella V3.6.172-SDK6')"),
]

AGUJAS = """
    # ---- F177 · agujas estáticas MENÚS EN ESCENA (r81) ----
    chk(game.count("menuFxInicia('in')") == 6,
        '6 aperturas EN ESCENA (toggle, hallask, train, opts, optsPala, HUB)')
    chk(game.count("menuFxInicia('out')") == 2,
        '2 salidas EN ESCENA (toggle B/close + academia)')
    chk(game.count("menuFxInicia('pulse')") == 1,
        'pulsación viva: menuClick dispara el pulso del arco')
    chk('this.menuFxTick();   // r81' in game,
        'menuFxTick en el bucle (vida del arco, con o sin menú)')
    chk('_menuFxCascada' in game and 'eOB' in game,
        'cascada C→L/R con rebote easeOutBack')
    chk('FLASH de pulsación' in game and '_menuFlashRepinta' in game,
        'flash de fila horneado en _menuTexSube')
    chk('FOCO VIVO' in game,
        'foco vivo: tick + haptic al ganar el foco una fila')
    chk('this.menuGroup.visible = this.menuOpen;' not in game,
        'toggleMenu ya no muestra/esconde al instante (el FX manda)')
"""

VIVOS = """
  // — F177 · MENUS EN ESCENA: cascada, pulso, flash y salida (r81) —
  {
    // 1 · ENTRADA: C nace pequeña y rebota; L/R van 70 ms detrás; el ancla
    //     fija NO se mueve (el FX sólo escala panelas y opacidad)
    G.menuPage = 'main'; G.menuOpen = true;
    const posFx0 = JSON.stringify(G.menuGroup.position.toArray());
    G.menuFxInicia('in');
    const sC0 = G._menuPanelaDe.C.scale.x;
    const sL0 = G._menuPanelaDe.L.scale.x;
    await dorme(30);
    const sC30 = G._menuPanelaDe.C.scale.x;
    const sL30 = G._menuPanelaDe.L.scale.x;
    const op30 = G._menuPanelaDe.C.material.opacity;
    await dorme(430);
    const sCfin = G._menuPanelaDe.C.scale.x;
    const opCfin = G._menuPanelaDe.C.material.opacity;
    out.fxInNace = sC0 < 0.95 && sL0 < 0.95 && G.menuGroup.visible;
    out.fxInCascada = sC30 > sL30 + 0.02 && op30 < 1;
    out.fxInAsienta = Math.abs(sCfin - 1) < 0.01 && opCfin === 1 &&
      G._menuFxCascada === null;
    out.fxInAnclaIntacta = JSON.stringify(
      G.menuGroup.position.toArray()) === posFx0;
    // 2 · PULSO de pulsación: el arco respira y vuelve exactamente a 1
    G.menuFxInicia('pulse');
    await dorme(40);
    const sPulso = G.menuGroup.scale.x;
    await dorme(220);
    out.fxPulso = sPulso > 1.005 &&
      Math.abs(G.menuGroup.scale.x - 1) < 0.001;
    // 3 · FLASH: menuClick lo deja puesto y decae solo (≤170 ms)
    G.drawMenu(); await dorme(20);
    const idsF177 = (G.menuRects || []).map((r) => String(r.id));
    const iFx = idsF177.findIndex((i) => i.indexOf('page:') === 0);
    if (iFx >= 0) {
      G.menuClick(iFx, 0);   // deja flash + pulso (y navega a esa página)
      out.fxFlashWired = !!G._menuFlash;
      G.menuPage = 'main'; G.menuOpen = true; G.drawMenu();
    } else { out.fxFlashWired = false; }
    await dorme(260);
    out.fxFlashDecae = !G._menuFlash;
    // 4 · SALIDA: encoge + funde (150 ms), esconde y RESTAURA (ancla igual)
    const posFx1 = JSON.stringify(G.menuGroup.position.toArray());
    G.menuFxInicia('out');
    const visFx0 = G.menuGroup.visible;
    await dorme(260);
    out.fxOut = visFx0 && G.menuGroup.visible === false &&
      Math.abs(G._menuPanelaDe.C.scale.x - 1) < 0.001 &&
      G._menuPanelaDe.C.material.opacity === 1 &&
      JSON.stringify(G.menuGroup.position.toArray()) === posFx1;
    // estado limpio para el resto del QA: menú principal delante y asentado
    G.menuFxInicia('in');
    await dorme(430);
    G.menuPage = 'main'; G.drawMenu();
  }
"""

CHKS = """    # — F177 · MENÚS EN ESCENA —
    chk(out.get('fxInNace'), 'entrada FX: las panelas nacen pequeñas y visibles')
    chk(out.get('fxInCascada'), 'cascada C→L/R: el centro va por delante (+70 ms)')
    chk(out.get('fxInAsienta'), 'la cascada asienta en escala 1 · opacidad 1')
    chk(out.get('fxInAnclaIntacta'), 'el FX no recoloca el ancla fija (posición intacta)')
    chk(out.get('fxPulso'), 'pulso de pulsación: el arco respira 1→1.03→1')
    chk(out.get('fxFlashWired'), 'menuClick deja el flash de fila')
    chk(out.get('fxFlashDecae'), 'el flash decae solo (≤170 ms)')
    chk(out.get('fxOut'), 'salida FX: encoge, funde, esconde y restaura (ancla intacta)')
"""

for viejo, nuevo in REEM:
    n = t.count(viejo)
    assert n == 1, 'anclaje no único (%d): %r' % (n, viejo[:80])
    t = t.replace(viejo, nuevo)

ancla_ag = "    # ---- F172 · agujas estáticas del piso 72 ----"
assert t.count(ancla_ag) == 1
t = t.replace(ancla_ag, AGUJAS + "\n" + ancla_ag)

ancla_js = "  // — F169 · landing MULTI en tres zonas —"
assert t.count(ancla_js) == 1
t = t.replace(ancla_js, VIVOS + "\n" + ancla_js)

anala_chk = "    chk(out.get('imagenPrimero'), 'en el piso regala IMAGEN (fovea) antes que la tasa')"
assert t.count(anala_chk) == 1
t = t.replace(anala_chk, anala_chk + "\n" + CHKS)

DST.write_text(t, encoding='utf-8')
print('escrito', DST, len(t), 'bytes')
