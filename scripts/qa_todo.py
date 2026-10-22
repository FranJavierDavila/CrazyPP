#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · QA TOTAL (un comando, toda la cadena).
Encadena TODAS las capas de verificación del proyecto, de la más rápida a la
más lenta, y saca el marcador global. Descubre los QA de la versión actual
por nombre (qa_sup1_vNNN.py → el más alto), así que no hay que tocarlo en
cada release.

Capas:
  A. qa_version.py        — cadena de versión única (23 checks)
  B. test_fisica.mjs      — determinismo de la física (11 escenarios)
  C. qa_manifiestos.py    — schema + assets de los 5 campeonatos (29)
  D. qa_rendimiento.py    — presupuesto (tamaños/física/boot, 14)
  E. qa_sup1_vNNN.py      — el juego EN VIVO con el orbital cargado (~150)
  F. qa_imp2_vNNN.py      — reactor de impulso (~66)
  G. qa_escudo_vNNN.py    — escudo de pala (~54)
  H. qa_descargas_vNNN.py — hub + 4 ZIPs byte-exactos (~208)
  I. smoke_sdkN.py        — SDK + 5 módulos en cadena
  J. qa_telemetria.py     — telemetría anónima: catálogo, receptor, E2E (41)
  K. qa_hub_hints.py      — (POST-DEPLOY, --produccion) hints del hub en
                            producción contra el estado real del dueño (11)
  L. qa_champion_listo.py — (POST-DEPLOY, --produccion) estado champion de
                            los 5 campeonatos en producción (13)

Uso:
  python3 scripts/qa_todo.py                # TODO (A-J, pre-deploy)
  python3 scripts/qa_todo.py --rapido       # solo A-D (sin Playwright pesado)
  python3 scripts/qa_todo.py --produccion   # A-J + K/L contra PRODUCCIÓN
                                            # (tras el deploy: K/L exigen
                                            # que pages sirva la versión
                                            # de la FUENTE DE VERDAD)
Salida: marcador global. Exit 1 si CUALQUIER capa falla."""
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'
TIMEOUT = {  # segundos por capa
    'qa_version.py': 120, 'test_fisica.mjs': 90, 'qa_manifiestos.py': 60,
    'qa_rendimiento.py': 300,
}

def ultimo(pat):
    cand = sorted(SCR.glob(pat))
    return cand[-1].name if cand else None

CAPAS = [
    ('A · versión única', 'qa_version.py'),
    ('B · física determinista', 'test_fisica.mjs'),
    ('C · manifiestos', 'qa_manifiestos.py'),
    ('D · presupuesto', 'qa_rendimiento.py'),
    ('E · juego en vivo (sup1)', ultimo('qa_sup1_v*.py')),
    ('F · reactor de impulso', 'qa_imp2_v351.py'),
    ('G · escudo de pala', 'qa_escudo_v350.py'),
    ('H · hub + ZIPs', ultimo('qa_descargas_v*.py')),
    ('I · smoke del SDK', ultimo('smoke_sdk*.py')),
    ('J · telemetría', 'qa_telemetria.py'),
    ('T · zonas entrenamiento', 'qa_train_zonas_v3619.py'),
    ('U · ayudas entrenamiento', 'qa_train_ayudas_v3621.py'),
    ('V · sonido del tren', 'qa_tren_audio_v3626.py'),
    ('W · salon del artista', 'qa_hall_salon_v3628.py'),
    ('X · sala del partido + mejor de 3', 'qa_partido_sala_v3629.py'),
    ('Y · hall sin pala ni bola', 'qa_hall_sin_pala_v3630.py'),
    ('Z · menú campeonatos + intro', 'qa_menu_intro_v3631.py'),
    # AC (qa_mega_norma_v3634) RETIRADA: verificaba la norma v3.6.34 (una
    # carga por rally, icono canvas, gatillo cualquiera). La sustituye AD
    # (v3635): SUPERPODER DE PALA con CARGAS ×3 — cada 11 golpes del rally
    # = +1 (tope ×3, distinto sustituye), icono DEL DUEÑO anclado al mango
    # con etiqueta ×N, voz TTS embebida y gatillo del mando LIBRE.
    # AD (qa_mega_cargas_v3635) y AE (qa_poderes_matriz_v3636) RETIRADAS:
    # la sustituye AF (v3637): SÚPER IMÁN (3.er poder, spec completa del
    # dueño: campo 8 s al punto dulce, topes 0,45/0,12/3/0,35/0,15, consumo
    # por impacto asistido, máx. 3) + flechas de la matriz como sprites
    # PROPIOS (disco+oro+pulso) + SÚPER EFECTO notorio (halo rojo en la
    # bola, anillo de bote, rival con error ×2 y piernas ×0,85) + toda la
    # norma de la matriz con 3 poderes y las 6 voces nativas.
    ('AF · superpoder imán (v3637)', 'qa_poderes_iman_v3637.py'),
    # AG (v3638): INMEDIATEZ del gatillo (redibujo diferido + textura
    # persistente + PRECALIENTE repartido) + halo HIJO de la bola (cero
    # desfase) + flechas EN EL PLANO del icono (anclaje mundo + lateral de
    # cámara, tangenciales) + LOD 50 % en juego / 100 % mirando el mango.
    ('AG · poderes inmediatez+LOD (v3638)', 'qa_poderes_v3638.py'),
    # AH (v3639): PARTIDA NUEVA = PALA LIMPIA (reporte del dueño: los
    # poderes sin gastar de una partida previa PERMANECÍAN) — hook único
    # rules.onMatchStart avisado por el árbitro en CADA startMatch (menú,
    # revancha por gatillo y de menú, cambio de modo, online, calibración
    # y reinicio automático del estado 'over') → _megaNormReset completo:
    # matriz, icono ×N, FX de los tres poderes, flechas, halo, marcas de
    # bola y escalas LOD. Idempotente y sin dispose doble.
    ('AH · partida nueva pala limpia (v3639)', 'qa_poderes_reset_v3639.py'),
    # AI (v3640): EL PODER ACTIVO SE VE EN LA PALA (petición del dueño:
    # «que el usuario sepa el tipo de poder que tiene activo, sin que
    # moleste») — el icono del mango NO desaparece al activar: pasa a modo
    # ACTIVO con ANILLO DE TIEMPO que se vacía (oro/cian/azul = firma del
    # canto), PARPADEA los últimos 2 s y al terminar vuelve al inventario.
    # Un solo icono (FASE 38), redibujo diferido+ahorrado (r46), el
    # indicador duerme en CADA _megaNormReset (FASE 41).
    ('AI · poder activo se ve en pala (v3640)', 'qa_poderes_activo_v3640.py'),
    # AJ (v3641): SÚPER PORTAL, 4.º PODER DE PALA (spec completa del dueño:
    # portal que traslada la bola tras cada golpe VÁLIDO — 8 s / 3 golpes,
    # desviación lateral 0,25–0,70 m, vertical 0–0,15 m, conserva 90–100 %
    # de la rapidez, antirrebote 0,25 s, salida legal con bote jugable por
    # el solver existente, swap ATÓMICO: la bola jamás cruza la red
    # físicamente, cero colisiones fantasma, árbitro y física intactos) +
    # penalización honesta a la IA rival (c06: predicción muerta al cruzar
    # el portal, error ×1,6, piernas ×0,75, +10 % de fallo; la marca se
    # limpia al devolver). Icono del dueño + voces ES/EN embebidos.
    # AJ (v3641) RETIRADA: verificaba el portal de r49 (swap inmediato +
    # muerte de predicción por frame — el dueño demostró en el Quest que la
    # IA dejaba de devolver). La sustituye AK (v3642).
    # AK (v3642): EL PORTAL SE ENTIENDE Y LA IA RESPONDE (informe del dueño
    # tras V3.6.41): tránsito EXPLÍCITO en 3 fases (portal de ENTRADA con
    # portals.png al 50 % en la zona de impacto + halo → la bola viaja
    # OCULTA 1 s con la física congelada → el MISMO portal se abre SOBRE la
    # mesa rival y la bola sale por su CENTRO con bote jugable del solver),
    # IA penalizada en % con FLANCO único (nunca anulada; la marca muere
    # con la ventana y con el punto), icono del dueño RECORTADO con alfa
    # (verificación PIL) y voz ES nativa Piper (la de r49 estaba corrupta),
    # ANTI-LAG (precaliente de 13 piezas al empezar la partida: cantos,
    # icono, imagen del portal y 4 voces) y PASSTHROUGH en AJUSTES (en VR,
    # por defecto OFF, cambio de modo en vivo con re-entrada automática).
    ('AK · portal se entiende + IA responde (v3642)', 'qa_portal_v3642.py'),
    # AL (v3643): SUPERPODERES QUE SE VEN Y SE OYEN (informe del dueño tras
    # V3.6.42): Súper EFECTO exagerado (brush ×3, Magnus ×2,2, bote ×2,4,
    # tope ×3, halo +35 %) · Súper IMÁN con radio 0,75 m, RESCATE real
    # (bolas escapadas atraídas al punto dulce) y 3 FLECHAS cian bola→pala
    # · Súper PORTAL con 3 GOLPES GARANTIZADOS por activación (el gasto
    # por golpe mataba la ventana con sorteo ×1 — «con uno solo me
    # desaparece»; vigilante de matriz retirado) · CUENTA SONORA 3·2·1
    # uniforme en los cuatro poderes (sin mirar el icono) · PASSTHROUGH EN
    # CALIENTE (sesión siempre immersive-ar; _pstAplicar canjea fondo/sala
    # al vuelo — el conmutador ya NO sale a la web).
    ('AL · superpoderes se ven y se oyen (v3643)', 'qa_superpoderes_v3643.py'),
    # r52 (v3644): el informe del dueño tras probar V3.6.43 en el Quest —
    # «el Super iman no hace nada… en el Super efecto tampoco noto nada,
    # además de que la marca del bote va desfasada. El sonido de alerta de
    # que se está agotando no suena o no se percibe» → IMÁN con campo
    # continuo en la pala + flechas ×1,8 ANCLADAS (la r51 las construyó
    # pero nadie las llamaba) + física 0,95/6,5/0,80 y rescate 7,5/1,05 ·
    # EFECTO con halo 0,21 + estela roja + anillo de bote mayor · MARCA DEL
    # BOTE clavada a la bola visual · BLIPS 988/1319 a gain 0,42 con
    # háptica 3·2·1 · y el LADRILLO BOMBA del ARKANOID 2 (etapa 4 de La
    # Locura): negro con bomba.webp, sustituye a un azul (≥1 vez/partida
    # garantizada), salta cada 4 s, espera sin azules, DETONA radio
    # 2 filas × 2 columnas (bola o láser) y no vuelve en la partida.
    ('AM · imán/efecto se notan + bomba (v3644)', 'qa_bomba_v3644.py'),
]

# Capas POST-DEPLOY (--produccion): cargan game.html de PRODUCCIÓN y exigen
# que pages sirva la versión de la FUENTE DE VERDAD (src/game/VERSION.json).
CAPAS_PRODUCCION = [
    ('K · hints del hub (prod)', 'qa_hub_hints.py'),
    ('L · champion listo (prod)', 'qa_champion_listo.py'),
]

def main():
    rapido = '--rapido' in sys.argv
    produccion = '--produccion' in sys.argv
    capas = CAPAS + (CAPAS_PRODUCCION if produccion else [])
    filas = []
    fallos_total = 0
    t_global = time.monotonic()
    for nombre, script in capas:
        if not script or not (SCR / script).exists():
            filas.append((nombre, 'AUSENTE', '-', script or '(no encontrado)'))
            fallos_total += 1
            continue
        if rapido and script.startswith('qa_sup1'):
            break
        cmd = ['node', '--no-warnings', str(SCR / script)] if script.endswith('.mjs') \
            else [sys.executable, str(SCR / script)]
        t0 = time.monotonic()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=TIMEOUT.get(script, 600))
            dur = time.monotonic() - t0
            salida = r.stdout + r.stderr
            if script.endswith('.mjs'):
                # test_fisica: 'RESULTADO: N escenarios · 0 desviaciones'
                linea = next((l for l in salida.splitlines() if l.startswith('RESULTADO')), '')
                desv = '0 desviaciones' in linea and r.returncode == 0
                estado = 'OK' if desv else 'FALLO'
                resumen = linea.replace('RESULTADO: ', '').strip()
            else:
                linea = next((l for l in salida.splitlines()
                              if 'RESULTADO' in l.upper()), '')
                limpio = linea.replace('RESULTADO:', '').replace('RESULTADO', '').strip()
                n_fallos = 0
                for trozo in limpio.replace('OK ·', '·').split('·'):
                    t = trozo.strip().lower()
                    for pref in ('fallos', 'fallo', 'desviaciones'):
                        if t.startswith(pref):
                            try:
                                n_fallos = int(t.split()[0])
                            except (ValueError, IndexError):
                                n_fallos = 9999
                estado = 'OK' if (r.returncode == 0 and n_fallos == 0) else 'FALLO'
                resumen = f'{limpio} ({dur:.0f} s)'
        except subprocess.TimeoutExpired:
            dur = time.monotonic() - t0
            estado, resumen = 'TIMEOUT', f'>{dur:.0f} s'
        if estado != 'OK':
            fallos_total += 1
        filas.append((nombre, estado, resumen, script))

    print('=' * 72)
    print('CRAZY PING PONG · QA TOTAL')
    print('=' * 72)
    for nombre, estado, resumen, script in filas:
        marca = '✓' if estado == 'OK' else ('·' if estado == 'OMITIDA' else '✗')
        print(f'  {marca} {nombre:28s} [{estado:7s}] {resumen}  ({script})')
    print('=' * 72)
    print(f'  TIEMPO TOTAL: {time.monotonic() - t_global:.0f} s · '
          f'CAPAS EN FALLO: {fallos_total}')
    sys.exit(1 if fallos_total else 0)

if __name__ == '__main__':
    main()
