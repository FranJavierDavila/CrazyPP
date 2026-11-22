#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3.0.2: RELEASE (cabecera + ADDENDUM), page.tsx y README al día del re-sello."""

NEW = 'd4df330b407914125131c3b38e0275c455251b2d31b168bcab3f85deb1c27515'
OLD = 'dd86d7344118f2f2ac61d7988607750096c07c7a361c160bb23e2a3ed06f74e1'

RELEASES = [
    '/home/z/my-project/download/RELEASE-V3.0.txt',
    '/home/z/my-project/public/descargas/RELEASE-V3.0.txt',
]
REL_EDITS = [
    ("RELEASE CONGELADO — CRAZY PING PONG V3.0.1 «PRO TRAINING»",
     "RELEASE CONGELADO — CRAZY PING PONG V3.0.2 «PRO TRAINING»"),
    ("Fecha de sellado: 14/10/2026 · V3.0.1 re-sellada el 14/10/2026 (fixes de la prueba en el casco)",
     "Fecha de sellado: 14/10/2026 · V3.0.2 (fixes del entrenamiento, misma fecha)"),
    ("   (copia ESPEJO con nombre inequívoco para vencer cachés: crazypp-v3.0.1.zip,",
     "   (copia ESPEJO con nombre inequívoco para vencer cachés: crazypp-v3.0.2.zip,"),
    ("     (V2.141 íntegra + módulo PRO TRAINING + fixes del casco V3.0.1)",
     "     (V2.141 íntegra + módulo PRO TRAINING + fixes del casco V3.0.1 + fixes de entrenamiento V3.0.2)"),
    ("   - SHA256: " + OLD, "   - SHA256: " + NEW),
    ("la portada 2D muestra «V3.0.1» en el pie (junto a Ko-fi) y TODAS las\n   páginas del menú VR llevan el sello dorado «V3.0.1» bajo las palas de\n   idioma. Si ves V3.0 (o nada), es la build antigua o una descarga cacheada.",
     "la portada 2D muestra «V3.0.2» en el pie (junto a Ko-fi) y TODAS las\n   páginas del menú VR llevan el sello dorado «V3.0.2» bajo las palas de\n   idioma. Si ves V3.0.1 o V3.0, es una build anterior o descarga cacheada."),
    ("  V3.0    100,71 MB (+56 KB de módulo sobre V2.141) ·\n  V3.0.1  100,70 MB (index 6.209.803 B — fixes del casco, ver ADDENDUM)\n",
     "  V3.0    100,71 MB (+56 KB de módulo sobre V2.141) ·\n  V3.0.1  100,70 MB (index 6.209.803 B — fixes del casco, ADDENDUM 1) ·\n  V3.0.2  100,71 MB (index 6.216.089 B — fixes de entrenamiento, ADDENDUM 2)\n"),
]

ADDENDUM_2 = """

═══════════════════════════════════════════════════════════════════
ADDENDUM 2 · V3.0.2 — FIXES DEL ENTRENAMIENTO (14/10/2026)
═══════════════════════════════════════════════════════════════════
Segunda prueba en el casco. Reporte del dueño: metrónomo con errores
(la bola desaparece y reaparece al sacar la máquina), PASE BAJO con la
máquina mandando SIEMPRE a la red, zonas casi invisibles. Auditoría
completa de las 9 pruebas + 4 causas raíz corregidas:

1) METRÓNOMO — el rally NUNCA contaba y la bola «desaparecía»
   Doble causa. (a) El juez no tenía rama t5a: st.rally jamás se
   incrementaba — contador clavado a 0, sin puntos ni hitos.
   (b) El beat sustituía la bola CADA 1,65 s aunque estuviera EN VUELO:
   la devolución del jugador se desvanecía a mitad de trayectoria y
   reaparecía en la máquina (lo que el dueño vio como desaparecer/
   aparecer). FIX: rama t5a en el juez (rally++, +1 punto, hitos
   30/50/100 con bonus, cerrado por aiTouched para no contar rebotes
   extra de la misma bola) y el beat SÓLO sustituye cuando la bola
   anterior está asentada (muerta, ya botó en campo rival o pasó de
   largo). Si el beat vence sin devolución, el rally CIERRA antes de
   alimentar. Verificado a 240 Hz: 0 robos en vuelo, feeds con ritmo,
   rally contando 3→8 con devoluciones simuladas.

2) PASE BAJO (t2a) — la máquina sacaba SIEMPRE a la red
   El feed multiplicaba ×1.08 la velocidad RESUELTA del saque (despeje
   justo sobre la cinta: netTop + radio + 6 mm) — el 8 % aplanaba el
   arco y la bola se estrellaba. FIX: todos los feeds con máquina usan
   el saque legal estándar sin multiplicar. Verificado a 240 Hz en los
   6 modos con máquina: 3 feeds por modo cruzando sobre la cinta
   (y ≥ 0,952) y CERO eventos de red.

3) SAQUE CORTO DOBLE BOTE (t4a) — el juez no miraba la zona
   Contaba DOS botes rivales en CUALQUIER sitio; la zona pintada (51 cm
   junto a la red) era decorativa. FIX: cada bote debe caer DENTRO del
   rect pintado (mismas cotas overlay/juez). Verificado: fuera →
   «LARGO», dentro×2 → acierto.

4) SAQUE LARGO (t4b) — fallo con etiqueta invertida
   No llegar a la franja de fondo decía «LARGO»; ahora «CORTA».

5) ZONAS MÁS VISIBLES (petición explícita)
   Parrilla de MESA MARCADA: trazos ×1,7 más gruesos y al 92 %;
   centro prohibido rojo al 55 % con borde; OBJETIVO dorado al 85 %
   con doble filete; bandas JUNTO A LA LÍNEA al 80 % con borde a 9 px;
   zonas de saque al 82-85 % con borde a 10 px. Colocación y dimensiones
   REVISADAS numéricamente: el overlay mapea 1:1 la mitad rival
   (512 px = 1,525 × 1,37 m) y las cotas del juez coinciden con las
   pintadas en TODOS los modos.

6) ROBUSTEZ — startMode resetea la sesión COMPLETA
   live/phase/aiTouched/deadT/cross quedaban sucios del modo anterior.
   Y el catch del tick ahora puede registrar su error
   (window.__PP_TRAIN_DEBUG = true) para depurar sin romper el bucle.

QA V3.0.2: node --check OK · física conducida a 240 Hz con render en
no-op (entorno headless <10 fps): 6 modos con despeje verificado +
metrónomo end-to-end (0 robos · 5 feeds/14 s · rally 3→8) + jueces
t4a/t4b/t5a por ruta real · 0 pageerrors · stopMode restaura el
partido. NUEVO HASH: """ + NEW + """
Espejo descargable: crazypp-v3.0.2.zip (mismos bytes).
"""

PAGE = '/home/z/my-project/src/app/descargas/page.tsx'
PAGE_EDITS = [
    ("Juego final — Crazy Ping Pong V3.0.1 «PRO TRAINING»",
     "Juego final — Crazy Ping Pong V3.0.2 «PRO TRAINING»"),
    ("BUILD ACTUAL (re-sellada tras la prueba en el casco): PRO TRAINING completo + 3 fixes V3.0.1 — marcas y trayectoria ya NO se desfasan de la bola al recentrar, iconos de efecto pegados a las caras reales de la pala y cinta de agarre sobre el mango. Comprueba el sello dorado «V3.0.1» en el menú VR (bajo las palas de idioma) o en el pie de la portada. Listo para arrastrar a Netlify Drop y abrir en el Meta Quest Browser.",
     "BUILD ACTUAL: fixes del casco V3.0.1 + fixes de entrenamiento V3.0.2 — metrónomo que ya cuenta el rally y no roba la bola en vuelo, PASE BAJO sin saques a la red, zona del doble bote exigida de verdad y zonas MÁS VISIBLES. Comprueba el sello dorado «V3.0.2» en el menú VR (bajo las palas de idioma) o en el pie de la portada. Listo para arrastrar a Netlify Drop y abrir en el Meta Quest Browser."),
    ("100,7 MB · ZIP · V3.0.1 sellada · SHA256 dd86d734…",
     "100,7 MB · ZIP · V3.0.2 sellada · SHA256 d4df330b…"),
    ('href: "/descargas/crazypp-v3.0.1.zip",', 'href: "/descargas/crazypp-v3.0.2.zip",'),
    ("BUILD ACTUAL (re-sellada tras la prueba en el casco): PRO TRAINING completo + 3 fixes V3.0.1 — marcas y trayectoria ya NO se desfasan",
     "BUILD ACTUAL: fixes del casco V3.0.1 + fixes de entrenamiento V3.0.2 — metrónomo que ya cuenta el rally y no roba la bola en vuelo, PASE BAJO sin saques a la red, zona del doble bote exigida de verdad y zonas MÁS VISIBLES"),
    ("V3.0.1 «PRO TRAINING»\n            </strong>{\" \"}\n            — re-sellada tras la prueba en el casco con los 3 fixes del\n            entrenamiento.",
     "V3.0.2 «PRO TRAINING»\n            </strong>{\" \"}\n            — fixes del casco (V3.0.1) + fixes del entrenamiento\n            (V3.0.2): metrónomo, PASE BAJO, jueces y zonas visibles."),
    ("Crazy Ping Pong V3.0.1 «PRO TRAINING» · WebXR · Netlify Drop · Meta",
     "Crazy Ping Pong V3.0.2 «PRO TRAINING» · WebXR · Netlify Drop · Meta"),
    ("Hash SHA256 de la build V3.0.1 (dd86d734…), válido para crazypp-v3.zip y crazypp-v3.0.1.zip (mismos bytes).",
     "Hash SHA256 de la build V3.0.2 (d4df330b…), válido para crazypp-v3.zip y crazypp-v3.0.2.zip (mismos bytes)."),
    ("Notas oficiales selladas: qué añade el PRO TRAINING, el ADDENDUM V3.0.1 con la causa raíz y el fix de los 3 defectos vistos en el casco, la verificación realizada e historial de tamaños.",
     "Notas oficiales selladas: qué añade el PRO TRAINING, el ADDENDUM 1 (V3.0.1, fixes del casco) y el ADDENDUM 2 (V3.0.2, metrónomo + PASE BAJO + jueces + zonas visibles) con su verificación a 240 Hz e historial de tamaños."),
]

READMES = ['/home/z/my-project/download/README.md', '/home/z/my-project/public/descargas/README.md']
README_EDITS = [
    ("Videojuego de tenis de mesa en WebXR. La versión actual, la **V3.0.1\n«PRO TRAINING»**",
     "Videojuego de tenis de mesa en WebXR. La versión actual, la **V3.0.2\n«PRO TRAINING»**"),
    ("> **V3.0.1** = la V3.0 re-sellada tras la primera prueba en el casco, con los\n> 3 fixes del entrenamiento (desfase bola↔marcas al recentrar, iconos de\n> efecto pegados a las caras reales de la pala y cinta de agarre sobre el\n> mango real). La build se verifica EN PANTALLA: sello dorado «V3.0.1» en el\n> menú VR y en el pie de la portada 2D.",
     "> **V3.0.2** = la V3.0 con los fixes del casco (V3.0.1: desfase bola↔marcas\n> al recentrar, iconos en las caras reales de la pala, cinta sobre el mango)\n> MÁS los fixes del entrenamiento (V3.0.2: metrónomo que cuenta el rally y\n> no roba la bola en vuelo, PASE BAJO sin saques a la red, zona del doble\n> bote exigida, zonas más visibles). La build se verifica EN PANTALLA: sello\n> dorado «V3.0.2» en el menú VR y en el pie de la portada 2D."),
    ("## 📦 Descargas del proyecto (versión definitiva V3.0.1 «PRO TRAINING»)",
     "## 📦 Descargas del proyecto (versión definitiva V3.0.2 «PRO TRAINING»)"),
    ("| `crazypp-v3.0.1.zip` | **El juego final (V3.0.1)**",
     "| `crazypp-v3.0.2.zip` | **El juego final (V3.0.2)**"),
    ("Hash SHA256 de la build V3.0.1 (dd86d734…)",
     "Hash SHA256 de la build V3.0.2 (d4df330b…)"),
    ("**LA VERSIÓN ACTUAL ES LA V3.0.1** (base V2.141, recuperada y auditada; la\nV3.0.1 añade los 3 fixes de la primera prueba en el casco).",
     "**LA VERSIÓN ACTUAL ES LA V3.0.2** (base V2.141, recuperada y auditada; la\nV3.0.1 añade los 3 fixes del casco y la V3.0.2 los fixes del entrenamiento)."),
]

def apply(path, edits):
    with open(path, encoding='utf-8') as f:
        txt = f.read()
    n = 0
    for old, new in edits:
        c = txt.count(old)
        if c == 1:
            txt = txt.replace(old, new); n += 1
        elif c == 0 and txt.count(new) >= 1:
            pass   # ya aplicado en una ejecución anterior
        else:
            raise AssertionError(f'ancla no única ({c}) en {path}: {old[:70]!r}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    print('OK', path, f'({n} edits aplicadas)')

for p in RELEASES:
    apply(p, REL_EDITS)
    # addendum al final
    with open(p, encoding='utf-8') as f:
        txt = f.read()
    assert 'ADDENDUM 2 — FIXES DEL ENTRENAMIENTO' not in txt
    with open(p, 'a', encoding='utf-8') as f:
        f.write(ADDENDUM_2)
    print('OK addendum', p)
for p in READMES:
    apply(p, README_EDITS)
apply(PAGE, PAGE_EDITS)
