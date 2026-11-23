#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G6 (auditoría r120 · ola 3 · r129) · ASSETS COMPARTIDOS para campeonatos.

El informe midió 7,32 MB de ficheros byte-idénticos repetidos en
public/championships: pistol.glb ×3 (2,87 MB cada una), el cartel de
superpoder ×3, reloj.png ×2, bso.wav ×2, risas_forajido.mp3 duplicado
dentro de oeste… En Pages se sirven TODAS las copias; los ZIP las llevan
todas. Arreglo del informe: los compartidos van a /assets/championships/
(enlace relativo ../../assets/championships/… desde cada módulo) y los
ZIP siguen autocontenidos (build_zip.py copia public/assets entero).

Alcance decidido (informe + criterio de riesgo):
  · pistol.glb (locura/magia/estacion) → compartido — 5,9 MB ahorrados.
  · cartel superpoder (locura/magia/oeste/estacion superpower.png) → compartido.
  · reloj.png (magia/oeste) → compartido.
  · bso.wav de halloween → FUERA (huérfano provisional «del valle», el
    manifest lo dice: su música es melodia.mp3 y nadie carga bso.wav;
    valle_neon conserva su copia — retired, no se toca).
  · risas_forajido.mp3 (oeste, byte-idéntico a risas.mp3 en su MISMA
    carpeta) → referencias a risas.mp3, fichero fuera.
  · NO se toca: _plantilla (convención autocontenida para terceros),
    valle_neon (retirado), los dobles internos de estacion
    (victory/triunfante · duelo/focused — estados de expresión del
    rival, semántica enredada por 166 KB de ahorro).
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
CH = RAIZ / 'public/championships'
COMPARTIDO = RAIZ / 'public/assets/championships'

informe = []


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def borrar_si_igual(quedarse, borrar):
    """Borra `borrar` sólo si su md5 == el de `quedarse` (nunca pierde bytes)."""
    a, b = md5(quedarse), md5(borrar)
    if a != b:
        sys.exit(f'ABORTA G6: {borrar.name} de {borrar.parent.name} difiere de la copia que queda')
    Path(borrar).unlink()
    informe.append(f'  · fuera: championships/{borrar.parent.name}/assets/{borrar.name} '
                   f'({Path(borrar).stat().st_size if Path(borrar).exists() else "×"} B — copia de '
                   f'{quedarse.parent.name}/{quedarse.name})')


def sustituir(rel, viejo, nuevo, etiqueta):
    p = CH / rel if not rel.startswith('assets/') else RAIZ / rel
    if not str(p).startswith(str(RAIZ)):
        p = RAIZ / rel
    t = Path(p).read_text(encoding='utf-8')
    n = t.count(viejo)
    if n != 1:
        sys.exit(f'ABORTA G6 [{etiqueta}]: ancla {n} veces (esperaba 1)')
    Path(p).write_text(t.replace(viejo, nuevo, 1), encoding='utf-8', newline='\n')
    informe.append(f'  · {etiqueta}')


def main():
    COMPARTIDO.mkdir(parents=True, exist_ok=True)

    # ── 1 · pistol.glb (el mismo GLB en los 3 campeonatos) ──
    pistol = COMPARTIDO / 'pistol.glb'
    if not pistol.exists():
        shutil.copy2(CH / 'locura/assets/pistol.glb', pistol)
    for mod in ('locura', 'magia', 'estacion_orbital'):
        borrar_si_igual(pistol, CH / f'{mod}/assets/pistol.glb')
    informe.append(f'  · compartido: assets/championships/pistol.glb ({pistol.stat().st_size} B)')

    # ── 2 · cartel de superpoder (superpoder.webp ≡ superpower.png) ──
    banner = COMPARTIDO / 'superpoder.webp'
    if not banner.exists():
        shutil.copy2(CH / 'oeste/assets/superpoder.webp', banner)
    for mod, nombre in (('oeste', 'superpoder.webp'), ('locura', 'superpoder.webp'),
                        ('estacion_orbital', 'superpower.png')):
        borrar_si_igual(banner, CH / f'{mod}/assets/{nombre}')
    informe.append(f'  · compartido: assets/championships/superpoder.webp ({banner.stat().st_size} B)')

    # ── 3 · reloj.png (magia/oeste) ──
    reloj = COMPARTIDO / 'reloj.png'
    if not reloj.exists():
        shutil.copy2(CH / 'oeste/assets/reloj.png', reloj)
    for mod in ('oeste', 'magia'):
        borrar_si_igual(reloj, CH / f'{mod}/assets/reloj.png')
    informe.append(f'  · compartido: assets/championships/reloj.png ({reloj.stat().st_size} B)')

    # ── 4 · bso.wav de halloween: huérfano provisional (del valle) ──
    h = CH / 'halloween'
    idx = (h / 'index.js').read_text(encoding='utf-8')
    if "bso.wav" in idx:
        sys.exit('ABORTA G6: halloween/index.js SÍ menciona bso.wav — revisar antes de borrar')
    (h / 'assets/bso.wav').unlink()
    informe.append('  · fuera: championships/halloween/assets/bso.wav (huérfano provisional, '
                   'la música es melodia.mp3 · el manifest lo documenta)')

    # ── 5 · risas_forajido.mp3 = risas.mp3 dentro de oeste ──
    o = CH / 'oeste'
    if md5(o / 'assets/risas_forajido.mp3') != md5(o / 'assets/risas.mp3'):
        sys.exit('ABORTA G6: risas_forajido.mp3 difiere de risas.mp3')
    (o / 'assets/risas_forajido.mp3').unlink()
    informe.append('  · fuera: championships/oeste/assets/risas_forajido.mp3 (= risas.mp3)')

    # ── 6 · reescrituras de call-sites (paths module-relative ../../) ──
    R = "'../../assets/championships/"
    sustituir('locura/index.js',
              "powerBannerUrl: A('superpoder.webp'),",
              f"powerBannerUrl: new URL({R}superpoder.webp', import.meta.url).href,",
              'locura: powerBannerUrl → compartido')
    sustituir('locura/index.js',
              "GUN_ART_URL = A('pistol.glb');",
              f"GUN_ART_URL = new URL({R}pistol.glb', import.meta.url).href;",
              'locura: pistol.glb → compartido')
    sustituir('locura/manifest.json',
              '"powerBanner": "superpoder.webp",',
              f'"powerBanner": "{R[1:-1]}/superpoder.webp",',
              'locura manifest: powerBanner (campo documental, sin consumidor)')
    sustituir('magia/index.js',
              "powerUrl: A('superpoder.webp'),",
              f"powerUrl: new URL({R}superpoder.webp', import.meta.url).href,",
              'magia: powerUrl → compartido')
    sustituir('magia/index.js',
              "relojUrl: A('reloj.png'),",
              f"relojUrl: new URL({R}reloj.png', import.meta.url).href,",
              'magia: relojUrl → compartido')
    sustituir('magia/index.js',
              "gunUrl: A('pistol.glb'),",
              f"gunUrl: new URL({R}pistol.glb', import.meta.url).href,",
              'magia: gunUrl → compartido')
    sustituir('oeste/index.js',
              "url: () => new URL('./assets/superpoder.webp', import.meta.url).href,",
              f"url: () => new URL({R}superpoder.webp', import.meta.url).href,",
              'oeste: cartel superpoder → compartido')
    sustituir('oeste/index.js',
              "ri.src = new URL('./assets/reloj.png', import.meta.url).href;",
              f"ri.src = new URL({R}reloj.png', import.meta.url).href;",
              'oeste: reloj de la oleada → compartido')
    t = (o / 'index.js').read_text(encoding='utf-8')
    n_risas = t.count('risas_forajido.mp3')
    if n_risas < 3:
        sys.exit(f'ABORTA G6: oeste solo tiene {n_risas} refs a risas_forajido.mp3')
    (o / 'index.js').write_text(t.replace('risas_forajido.mp3', 'risas.mp3'), encoding='utf-8', newline='\n')
    informe.append(f'  · oeste: {n_risas} refs risas_forajido.mp3 → risas.mp3')
    sustituir('estacion_orbital/index.js',
              "new URL('./assets/pistol.glb', import.meta.url).href",
              f"new URL({R}pistol.glb', import.meta.url).href",
              'estacion: pistol.glb del artista → compartido')
    sustituir('estacion_orbital/index.js',
              "url: () => this.ctrl._A('superpower.png'),",
              f"url: () => new URL({R}superpoder.webp', import.meta.url).href,",
              'estacion: cartel superpoder → compartido')

    # ── 7 · build_zip.py: contrato de assets actualizado (G6) ──
    bz = RAIZ / 'scripts/release-v36209/build_zip.py'
    t = bz.read_text(encoding='utf-8')
    viejo = "'pistol.glb', 'mapa.png', 'superpower.png', 'angry.webp',"
    if viejo in t:
        t = t.replace(viejo, "'mapa.png', 'angry.webp',", 1)
        t = t.replace(
            "if (PUB / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png').stat().st_size != 409356:",
            """# G6 (r129): pistol.glb y superpower.png son ahora COMPARTIDOS
# (assets/championships/): byte-exactos ahí, una sola copia en Pages.
for _sh, _sz in (('pistol.glb', 2942640), ('superpoder.webp', 75178), ('reloj.png', 28607)):
    _p = PUB / 'assets/championships' / _sh
    if not _p.exists() or _p.stat().st_size != _sz:
        sys.exit(f'FALLO: asset compartido {_sh} ausente o no byte-exacto (G6)')
if (PUB / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png').stat().st_size != 409356:""",
            1)
    # ligera: assets/championships también fuera (sin campeonatos no sirven)
    viejo_l = "shutil.rmtree(champ_bak)\nshutil.move(str(tmp_champ), str(champ_bak))   # staging queda íntegro otra vez"
    if viejo_l in t and "staging-assets-champs-bak" not in t:
        t = t.replace(
            """print('· Comprimiendo paquete LIGERA (sin campeonatos, ~11 MB)...')""",
            """print('· Comprimiendo paquete LIGERA (sin campeonatos, ~11 MB)...')
# G6 (r129): los assets COMPARTIDOS de campeonatos tampoco viajan en la
# ligera (el juego base nunca los pide; vuelven con el COMPLETO).
sh_ac = STAGE / 'assets' / 'championships'
tmp_ac = RAIZ / 'scripts' / 'staging-assets-champs-bak'
if tmp_ac.exists():
    shutil.rmtree(tmp_ac)
if sh_ac.exists():
    shutil.move(str(sh_ac), str(tmp_ac))""",
            1)
        t = t.replace(viejo_l, viejo_l + """
if tmp_ac.exists():
    shutil.move(str(tmp_ac), str(sh_ac))""", 1)
    # VERSION.txt: hashes de los compartidos
    ancla_v = """    'championships/sdk/champ_sdk.js':
        sha256(STAGE / 'championships/sdk/champ_sdk.js'),"""
    if ancla_v in t and 'assets/championships/pistol.glb' not in t:
        t = t.replace(ancla_v, ancla_v + """
    'assets/championships/pistol.glb':
        sha256(STAGE / 'assets/championships/pistol.glb'),
    'assets/championships/superpoder.webp':
        sha256(STAGE / 'assets/championships/superpoder.webp'),
    'assets/championships/reloj.png':
        sha256(STAGE / 'assets/championships/reloj.png'),""", 1)
    bz.write_text(t, encoding='utf-8', newline='\n')
    informe.append('  · build_zip.py: lista orbital −pistol/−superpower · guardia de compartidos · '
                   'ligera sin assets/championships · VERSION.txt con hashes G6')

    print('== INFORME G6 ==')
    print('\n'.join(informe))


if __name__ == '__main__':
    main()
