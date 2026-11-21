#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r109 · SUPER CRIPTONITA — LA VOZ Y EL CANDADO (petición del dueño).

Cuatro cambios asertados en src/game/core/c12_pingponggame.js:

  1. VOCES (audio que faltaba «en el juego y en la sala Arcano, en
     castellano e inglés y con la entonación propia de cada lugar»):
     banco ES/EN Piper de la casa (davefx/lessac + loudnorm, receta
     r44/r50) embebido como las voces de concesión. La entonación propia
     de cada lugar ya vive en la arquitectura: en el JUEGO la voz ágil
     del selector (r58) / concesión (_megaVoz) y en la sala ARCANO la
     voz SOLEMNE del oráculo (r47: cinta ×0,82 + paso-bajo + sala
     ceremonial) sobre el MISMO banco — cero bytes duplicados.
  2. La entrada de 'cripto' en PODERES_PALA recibe voz/vozEn — con eso
     el selector (_vozSelFuente), la concesión (_poderVoz) y el Arcano
     (_vozSelSolemne) la nombran solos, data-driven como los otros 15.
  3. CANDADO HONESTO: revierte la apertura de fábrica de la r108
     (migración incluida: retira 'cripto' del almacenamiento del dueño)
     y arregla el fallback del catch. El candado del registro vuelve a
     mandar; se abre por la vía de siempre (coronación al azar).
  4. REGLA DEL ADMINISTRADOR: FORO3D (ppDebugMode de la casa, c00 —
     window.__PP_DEBUG) juega con TODO desbloqueado.

El build legítimo lo hace después bump_version.py (sello 3.6.207-SDK6).
"""
import base64
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
VOC = RAIZ / 'scripts' / 'r109_voces'


def die(msg):
    sys.exit('FALLO r109: ' + msg)


txt = C12.read_text(encoding='utf-8')


def reemplazar(viejo, nuevo, etiqueta):
    global txt
    n = txt.count(viejo)
    if n != 1:
        die(f'{etiqueta}: esperaba exactamente 1 aparición del ancla, hay {n}')
    txt = txt.replace(viejo, nuevo)
    print(f'· {etiqueta}: OK')


# ── 0. los mp3 de la voz (generados por r109_gen_voces.sh) ──────────
mp3_es = VOC / 'voz_cripto_es.mp3'
mp3_en = VOC / 'voz_cripto_en.mp3'
if not mp3_es.exists() or not mp3_en.exists():
    die('faltan scripts/r109_voces/voz_cripto_{es,en}.mp3 (ejecuta r109_gen_voces.sh)')
b64_es = base64.b64encode(mp3_es.read_bytes()).decode('ascii')
b64_en = base64.b64encode(mp3_en.read_bytes()).decode('ascii')

# ── 1. las dos consts de voz, junto al resto del banco (antes del registro) ──
BLOQUE_VOZ = (
    "// r109 · SUPER CRIPTONITA — LA VOZ (petición del dueño: «el Superpoder\n"
    "// de criptonita le falta el audio tanto en el juego como en la sala\n"
    "// Arcano; en ambos lugares en castellano e inglés y con la entonación\n"
    "// propia de cada lugar»). Banco ES/EN Piper de la casa (davefx/lessac +\n"
    "// loudnorm, receta r44/r50), embebido como las voces de concesión. La\n"
    "// entonación propia de cada lugar YA vive en la arquitectura: en el JUEGO\n"
    "// la nombra la voz ágil del selector (r58) / concesión (_megaVoz); en la\n"
    "// sala ARCANO la voz SOLEMNE del oráculo (r47: cinta lenta ×0,82 +\n"
    "// paso-bajo 2,8 kHz + sala ceremonial) sobre este mismo banco.\n"
    "const VOZ_PODER_CRIPTO = 'data:audio/mpeg;base64," + b64_es + "';\n"
    "const VOZ_PODER_CRIPTO_EN = 'data:audio/mpeg;base64," + b64_en + "';\n"
    "\n"
    "const PODERES_PALA = ["
)
reemplazar('const PODERES_PALA = [', BLOQUE_VOZ, '1. consts VOZ_PODER_CRIPTO/_EN')

# ── 2. la entrada del registro recibe su voz (data-driven como los demás) ──
ENTRY_VIEJO = (
    "  { id: 'cripto', dur: ARCANO_CFG.ventanas.cripto, nombre: () => T('poder_cripto'),\n"
    "    png: PNG_PODER_CRIPTO },"
)
ENTRY_NUEVO = (
    "  { id: 'cripto', dur: ARCANO_CFG.ventanas.cripto, nombre: () => T('poder_cripto'),\n"
    "    voz: VOZ_PODER_CRIPTO, vozEn: VOZ_PODER_CRIPTO_EN, png: PNG_PODER_CRIPTO },"
)
reemplazar(ENTRY_VIEJO, ENTRY_NUEVO, '2. entry cripto con voz/vozEn')

# ── 3. el selector la nombra (patrón r33: reutiliza su voz de concesión) ──
SEL_VIEJO = (
    "    // FASE 160 · la BOLA LOCA reutiliza su voz de concesión (patrón r33)\n"
    "    else if (id === 'bolaloca') par = [VOZ_PODER_BOLALOCA, VOZ_PODER_BOLALOCA_EN];\n"
    "    return par ? (en ? par[1] : par[0]) : null;"
)
SEL_NUEVO = (
    "    // FASE 160 · la BOLA LOCA reutiliza su voz de concesión (patrón r33)\n"
    "    else if (id === 'bolaloca') par = [VOZ_PODER_BOLALOCA, VOZ_PODER_BOLALOCA_EN];\n"
    "    // r109 · SUPER CRIPTONITA reutiliza su voz de concesión (patrón\n"
    "    // r33/r58): voz ágil en el juego, voz solemne del oráculo en Arcano.\n"
    "    else if (id === 'cripto') par = [VOZ_PODER_CRIPTO, VOZ_PODER_CRIPTO_EN];\n"
    "    return par ? (en ? par[1] : par[0]) : null;"
)
reemplazar(SEL_VIEJO, SEL_NUEVO, '3. caso cripto en _vozSelFuente')

# ── 4. candado honesto + regla del administrador ──
UNLOCK_VIEJO = (
    "      // r108 · SUPER CRIPTONITA nace DESBLOQUEADO (el dueño lo pide y\n"
    "      // lo juega desde el primer día, mismo trato que la Bola Loca).\n"
    "      if (ok.indexOf('cripto') >= 0 && lista.indexOf('cripto') < 0) {\n"
    "        lista.unshift('cripto');\n"
    "        try {\n"
    "          localStorage.setItem('pp_poderes_v1', JSON.stringify(lista));\n"
    "        } catch { /* la sesión la lleva en memoria */ }\n"
    "      }\n"
    "      return lista;\n"
    "    } catch { return ['bolaloca', 'cripto']; }"
)
UNLOCK_NUEVO = (
    "      // r109 · REGLA DEL ADMINISTRADOR (petición del dueño): el usuario\n"
    "      // FORO3D — el ppDebugMode de la casa (c00) — juega con TODO\n"
    "      // desbloqueado; el resto del mundo respeta los candados.\n"
    "      try {\n"
    "        if (typeof window !== 'undefined' && window.__PP_DEBUG) return ok.slice();\n"
    "      } catch { /* sin window: vía normal */ }\n"
    "      // r109 · SUPER CRIPTONITA vuelve al CANDADO (orden del dueño: «el\n"
    "      // Superpoder debe aparecer bloqueado»): se abre por la vía de\n"
    "      // siempre — la coronación de un campeonato libera uno AL AZAR entre\n"
    "      // los que sigan cerrados. La r108 la sembró abierto EN EL\n"
    "      // ALMACENAMIENTO: se retira UNA vez para que el candado sea\n"
    "      // honesto. La BOLA LOCA conserva su siembra de serie (regla FASE\n"
    "      // 160 del dueño, arriba).\n"
    "      const iCripto = lista.indexOf('cripto');\n"
    "      if (iCripto >= 0) {\n"
    "        lista.splice(iCripto, 1);\n"
    "        try {\n"
    "          localStorage.setItem('pp_poderes_v1', JSON.stringify(lista));\n"
    "        } catch { /* la sesión la lleva en memoria */ }\n"
    "      }\n"
    "      return lista;\n"
    "    } catch { return ['bolaloca']; }"
)
reemplazar(UNLOCK_VIEJO, UNLOCK_NUEVO, '4. candado honesto + regla FORO3D')

C12.write_text(txt, encoding='utf-8')
print(f'✓ c12 escrito ({len(txt):,} caracteres)')

# ── verificación post-parche ──
chk = [
    ('const VOZ_PODER_CRIPTO = ', 1),
    ('const VOZ_PODER_CRIPTO_EN = ', 1),
    ('voz: VOZ_PODER_CRIPTO, vozEn: VOZ_PODER_CRIPTO_EN', 1),
    ("else if (id === 'cripto') par = [VOZ_PODER_CRIPTO, VOZ_PODER_CRIPTO_EN];", 1),
    ("return ['bolaloca'];", 1),
    ('window.__PP_DEBUG) return ok.slice()', 1),
    ('lista.splice(iCripto, 1)', 1),
    ('nace DESBLOQUEADO', 0),
    ("return ['bolaloca', 'cripto']", 0),
]
for patron, esperado in chk:
    n = txt.count(patron)
    estado = 'OK' if n == esperado else 'FALLO'
    print(f'  [{estado}] {patron[:52]!r} → {n} (esperaba {esperado})')
    if n != esperado:
        die(f'verificación post-parche fallida: {patron!r}')
print('✓ verificación post-parche completa')
