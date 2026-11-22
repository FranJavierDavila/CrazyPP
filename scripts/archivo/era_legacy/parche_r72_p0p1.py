#!/usr/bin/env python3
# r72 · Parches P0 (congelamiento Ranking Mundial) + P1 (fuera kofi de Ajustes)
# Aplica reemplazos byte-exacto sobre public/game.html con verificación de conteo.
import sys

PATH = '/home/z/my-project/upload/public/game.html'
s = open(PATH, encoding='utf-8').read()
orig_len = len(s)

EDITS = []

# ── P0-1 · drawMenuRankIni: el reloj DENTRO del dibujo (bucle infinito) ──
old1 = """    // r70 · WORLDRANK fresco al aterrizar (silencioso, como r67)
    WORLDRANK.load(true).then(() => {
      if (this.menuOpen && this.menuPage === 'rankini') this.drawMenu();
    }).catch(() => { /* nunca rompe */ });
  }"""
new1 = """    // r72 · FIX CONGELAMIENTO (informe del dueño: «al pulsar Ranking Mundial
    // se queda congelado»): el reloj vivía DENTRO del dibujo y su .then()
    // redibujaba ESTA MISMA página, que volvía a disparar el load(true) —
    // ciclo GET+redibujo sin fin que en la Quest saturaba el navegador
    // (juego congelado). Ahora UNA sola revalidación por aterrizaje:
    // _rankiniFresh se arma al ENTRAR en la página (page:/wrl:open) y el
    // dibujo jamás vuelve a disparar la petición.
    if (!this._rankiniFresh) {
      this._rankiniFresh = true;
      WORLDRANK.load(true).then(() => {
        if (this.menuOpen && this.menuPage === 'rankini') this.drawMenu();
      }).catch(() => { /* nunca rompe */ });
    }
  }"""
EDITS.append(('P0-1 bucle drawMenuRankIni', old1, new1, 1))

# ── P0-2 · wrl:open: re-armar la guarda + fuera el load(true) muerto ──
old2 = """        if (arg === 'open') {
          this.menuPage = 'rankini';
          WORLDRANK.load(true).then(() => {
            if (this.menuOpen && this.menuPage === 'rank') this.drawMenu();
          }).catch(() => { /* nunca rompe */ });
        } else if (arg === 'tab') {"""
new2 = """        if (arg === 'open') {
          this.menuPage = 'rankini';
          // r72 · re-arma el reloj único de aterrizaje (fuera el load(true)
          // muerto que miraba 'rank': el refresco lo hace el propio landing,
          // UNA sola vez, con su guarda anti-bucle).
          this._rankiniFresh = false;
        } else if (arg === 'tab') {"""
EDITS.append(('P0-2 wrl:open', old2, new2, 1))

# ── P0-3 · case 'page': re-armar la guarda al entrar por la rejilla ──
old3 = """          this.menuPage = arg;
          this._resetArm = false;"""
new3 = """          this.menuPage = arg;
          this._resetArm = false;
          if (arg === 'rankini') this._rankiniFresh = false;   // r72 · reloj único de aterrizaje"""
EDITS.append(('P0-3 case page', old3, new3, 1))

# ── P1 · fuera la tarjeta kofi de la rejilla de AJUSTES ──
old4 = """        { id: 'page:optsPala', icono: 'partido', etiquetaKey: 'cat_pala',
          gradiente: ['#ec407a', '#ad1457'] },
        { id: 'kofi', icono: 'apoyar', etiquetaKey: 'btn_kofi',
          gradiente: ['#ffd25e', '#e8a80e'] },
      ] },"""
new4 = """        { id: 'page:optsPala', icono: 'partido', etiquetaKey: 'cat_pala',
          gradiente: ['#ec407a', '#ad1457'] },
        // r72 · FUERA «Apoyar el proyecto (Ko-fi)» de AJUSTES (petición del
        // dueño): la tarjeta se retira de la rejilla; el canal kofi de la
        // portada web (dock/footlink) no se toca.
      ] },"""
EDITS.append(('P1 kofi fuera de Ajustes', old4, new4, 1))

fail = False
for name, old, new, expect in EDITS:
    n = s.count(old)
    print(f'[{name}] ocurrencias old={n} (esperadas {expect})')
    if n != expect:
        print('  !! FALLO: conteo inesperado, NO se aplica')
        fail = True
        continue
    s = s.replace(old, new)
    print(f'  OK · delta {len(new)-len(old):+d} B')

if fail:
    print('RESULTADO: PARCIAL — revisar')
    sys.exit(1)

open(PATH, 'w', encoding='utf-8').write(s)
print(f'TAMAÑO: {orig_len} → {len(s)} B (delta {len(s)-orig_len:+d})')

# Verificación post-parche
s2 = open(PATH, encoding='utf-8').read()
checks = [
    ('_rankiniFresh guarda', s2.count('this._rankiniFresh')),
    ('load(true).then rankini sin guarda (debe ser 0)', s2.count("WORLDRANK.load(true).then(() => {\n      if (this.menuOpen && this.menuPage === 'rankini') this.drawMenu();")),
    ('tarjeta kofi en ajustes (debe ser 0)', s2.count("{ id: 'kofi', icono: 'apoyar', etiquetaKey: 'btn_kofi',")),
    ("load muerto 'rank' en wrl:open (debe ser 0)", s2.count("if (this.menuOpen && this.menuPage === 'rank') this.drawMenu();\n          }).catch(() => { /* nunca rompe */ });\n        } else if (arg === 'tab')")),
]
for name, v in checks:
    print(f'CHECK {name}: {v}')
