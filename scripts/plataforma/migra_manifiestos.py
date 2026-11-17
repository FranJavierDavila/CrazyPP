"""Fase D · Migra los 3 manifiestos existentes al esquema normalizado v2.125.

IDEMPOTENTE: re-ejecutar no duplica nada. Añade SOLO los campos que faltan
(contract, estado, description, powers[], stages[], audio) sin tocar los
bloques legacy (cfg/level/notes) ni el index.js de cada módulo. Los powers y
stages se documentan con los kinds del SISTEMA COMÚN real.
"""
import json
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project/public/championships')

MIGRACION = {
    'locura': {
        'contract': 1,
        'estado': 'publicado',
        'description': {
            'es': 'Enféntate del PAYASO LOCO en su carpa de circo: cinco etapas de '
                  'ping pong caótico con confeti, bola roja fantasma, bolas dobles, '
                  'globos que marean y el arkanoid del circo. Gana el trofeo de La Locura.',
            'en': 'Face the CRAZY CLOWN in his circus tent: five chaotic ping pong '
                  'stages with confetti, ghost red ball, double balls, dizzy balloons '
                  'and the circus arkanoid. Win the Mad Cup.',
        },
        'powers': [
            {'kind': 'confeti', 'name': 'Confeti caótico', 'chance': 0.30, 'duration': 8},
            {'kind': 'bola', 'name': 'Bola roja loca', 'chance': 0.30},
            {'kind': 'split', 'name': 'Bola doble', 'chance': 0.25},
            {'kind': 'mareo', 'name': 'Mareo total', 'chance': 0.22, 'duration': 6},
            {'kind': 'globos', 'name': 'Globos', 'chance': 0.25},
        ],
        'stages': [
            {'id': 'etapa1', 'name': 'Duelo inicial', 'kind': 'duelo'},
            {'id': 'etapa2', 'name': 'Arkanoid del circo', 'kind': 'arkanoid'},
            {'id': 'etapa3', 'name': 'Duelo caliente', 'kind': 'duelo'},
            {'id': 'etapa4', 'name': 'Arkanoid II', 'kind': 'arkanoid'},
            {'id': 'etapa5', 'name': 'Jefe final', 'kind': 'duelo'},
        ],
        'audio': {'music': 'assets/bso.ogg', 'musicVolume': 0.18},
    },
    'magia': {
        'contract': 1,
        'estado': 'publicado',
        'description': {
            'es': 'Duelo de ping pong contra el MAGO ARCANO en su laboratorio de '
                  'alquimista: orbe mágico con poderes (fantasmas, portales, fuego), '
                  'cinco etapas y el trofeo del Hechicero.',
            'en': 'Ping pong duel against the ARCANE WIZARD in his alchemist lab: '
                  'magic orb with powers (ghosts, portals, fire), five stages and '
                  'the Sorcerer trophy.',
        },
        'powers': [
            {'kind': 'orbe', 'name': 'Orbe mágico', 'chance': 0.30},
        ],
        'stages': [
            {'id': 'etapa1', 'name': 'Duelo inicial', 'kind': 'duelo'},
            {'id': 'etapa2', 'name': 'Orbe arkanoid', 'kind': 'objetos'},
            {'id': 'etapa3', 'name': 'Duelo caliente', 'kind': 'duelo'},
            {'id': 'etapa4', 'name': 'Orbe II', 'kind': 'objetos'},
            {'id': 'etapa5', 'name': 'Jefe final', 'kind': 'duelo'},
        ],
        'audio': {'music': 'assets/bso.mp3', 'musicVolume': 0.18},
    },
    'oeste': {
        'contract': 1,
        'estado': 'publicado',
        'description': {
            'es': 'Confróntate con el FORAJIDO en el Salvaje Oeste: duelo de ping '
                  'pong con revólver y dinamita, asedio al escondite, asalto al tren '
                  'y superpoderes de arena y estampida. El trofeo: la estrella del sheriff.',
            'en': 'Face the OUTLAW in the Wild West: ping pong duel with revolver and '
                  'dynamite, hideout siege, train heist and sandstorm/stampede super '
                  'powers. The trophy: the sheriff star.',
        },
        'powers': [
            {'kind': 'disparo', 'name': 'Disparo certero', 'chance': 0.30, 'warn': 2.5},
            {'kind': 'dinamita', 'name': 'Dinamita', 'chance': 0.30, 'warn': 3},
            {'kind': 'arena', 'name': 'Tormenta de arena', 'chance': 0.28, 'duration': 8},
            {'kind': 'estampida', 'name': 'Estampida', 'chance': 0.25, 'duration': 6.5},
        ],
        'stages': [
            {'id': 'duelo', 'name': 'Duelo al mediodía', 'kind': 'duelo'},
            {'id': 'asedio', 'name': 'Asedio al escondite', 'kind': 'objetos'},
            {'id': 'tren', 'name': 'Asalto al tren', 'kind': 'tren'},
        ],
        'audio': {'music': 'assets/bso.mp3', 'musicVolume': 0.18,
                  'sounds': {'vagon': 'assets/vagon.mp3'}},
    },
}


def main():
    for cid, campos in MIGRACION.items():
        mf = RAIZ / cid / 'manifest.json'
        m = json.loads(mf.read_text(encoding='utf-8'))
        nuevos = []
        for k, v in campos.items():
            if k not in m:
                m[k] = v
                nuevos.append(k)
        # notas: changelog estructurado (conserva las note_v* legacy)
        m.setdefault('notes', [])
        marca = 'migrado al esquema v2.125 (contract 1) — sin cambios de comportamiento'
        if marca not in m['notes']:
            m['notes'].append(f'{time.strftime("%Y-%m-%d")}: {marca}')
        mf.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n',
                      encoding='utf-8')
        print(f'✓ {cid}: +{", ".join(nuevos) if nuevos else "nada (ya migrado)"}')


if __name__ == '__main__':
    main()
