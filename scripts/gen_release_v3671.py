#!/usr/bin/env python3
"""gen_release_v3671 — hereda scripts/release-v3670 → scripts/release-v3671
e inserta las NOTAS de la FASE 73 «CRAZY LINK v2» en build_zip.py.

Idempotente: si release-v3671 ya existe, se regenera desde cero.
Además retira el fragmento heredado de r76 (PUNTO SEGURO v3.6.67-r75)
que quedó pegado tras el bloque de notas de la FASE 72.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3670"
DEST = RAIZ / "scripts" / "release-v3671"

BZ = DEST / "build_zip.py"

# Bloque de notas FASE 72 (r78) + fragmento heredado r76 que salen enteros
BLOQUE_VIEJO_INI = ("    'Rama    : main · SDK6 (FASE 72 — EL NARRADOR HONESTO: la nota del\\n'")
BLOQUE_VIEJO_FIN = ("    '    profesor con datos, panel vivo dentro de bounds y captura).\\n\\n'")

# Bloque nuevo FASE 73 (r79)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 73 — CRAZY LINK v2: el multijugador deja\\n'
    'de ser cosmético — petición del dueño («Lo siguiente es trabajar el\\n'
    'modo multijugador… necesitamos hacerlo realista y no cosmético… un\\n'
    'modo multijugador perfecto para la modalidad de "Partida"») siguiendo\\n'
    'la spec «Netcode multijugador online — Ping Pong VR (WebXR)» v1.0)\\n\\n'
    'Novedades de esta versión (frente a V3.6.70-SDK6):\\n\\n'
    '  · SUBMENÚ MULTIJUGADOR CON DOS MODOS (estética común del juego):\\n'
    '    NORMAL · PARTIDA (1 vs 1 online, mejor de 3) y DUELOS LOCOS con\\n'
    '    la etiqueta PRÓXIMAMENTE y el CANDADO encima del nombre, como los\\n'
    '    campeonatos bloqueados (voz al intentar entrar incluida).\\n\\n'
    '  · TRANSPORTE BINARIO REAL (spec §2/§5): RTCPeerConnection propia con\\n'
    '    DOS canales — fast {ordered:false, maxRetransmits:0} tipo UDP a 60\\n'
    '    Hz (cabecera 21 B con eco NTP + pose 31 B de cabeza y dos manos +\\n'
    '    eventos) y reliable {ordered:true} para el control. Señalización\\n'
    '    SDP/ICE sobre la sala PeerJS; voz intacta. Degradación honesta al\\n'
    '    modo compatible 30 Hz si la subida falla.\\n\\n'
    '  · EL GOLPE PROPIO ES SAGRADO + AUTORIDAD POR MITAD DE MESA (spec\\n'
    '    §1/§7): la colisión, el sonido y la vibración de tu golpe se\\n'
    '    resuelven en TU visor sin esperar la red; quien tiene la bola en\\n'
    '    su mitad decide botes, fallos y puntos; traspaso exacto al cruzar\\n'
    '    la red, avance dt·0,6 (tope 120 ms), correcciones 2 cm/30 cm con\\n'
    '    absorción de 80 ms y autoridad provisional a los 300 ms.\\n\\n'
    '  · REGLAS Y MARCADOR SINCRONIZADOS (spec §9): POINT_CLAIM/POINT_ACK\\n'
    '    con identidad de rallye determinista, RESYNC_STATE del anfitrión\\n'
    '    como árbitro final, saque alterno calculado igual en ambos visores\\n'
    '    y LET determinista sin red.\\n\\n'
    '  · RELOJ COMPARTIDO Y AVATAR REAL (spec §4/§6): reloj del anfitrión\\n'
    '    con ancla gruesa + refinado NTP (mediana de las 4 muestras de\\n'
    '    menor RTT, suavizado 1 ms/s, sin saltos en rallye); el rival se\\n'
    '    reproduce con jitter buffer adaptativo (40-120 ms), extrapolación\\n'
    '    de 100 ms y atenuación si se congela; su pala se deriva de la mano\\n'
    '    con el agarre fijo y su visor aparece con la cabeza.\\n\\n'
    '  · PARTIDA SINCRONIZADA Y RESILIENTE (spec §3/§10/§11): HELLO de\\n'
    '    versiones, MATCH_START con cuenta atrás de 3 s en el reloj del\\n'
    '    anfitrión, pausa automática al quitar el visor, reinicio de ICE,\\n'
    '    pose degradada a 30 Hz con pérdida sostenida y PING de color en el\\n'
    '    marcador. Validación anti-trampa de cada golpe recibido (spec §12)\\n'
    '    y telemetría de red (net_match) para medirlo todo.\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3670 → v3671 / V3.6.70 → V3.6.71
    txt = txt.replace("V3.6.70-SDK6", "V3.6.71-SDK6")
    txt = txt.replace("3.6.70-SDK6", "3.6.71-SDK6")   # guards contra game_src
    txt = txt.replace("v3670-sdk6", "v3671-sdk6")
    txt = txt.replace("release-v3670", "release-v3671")
    txt = txt.replace("staging-v3670", "staging-v3671")
    txt = txt.replace('grep -c "3.6.70"', 'grep -c "3.6.71"')
    txt = txt.replace("menciones 3.6.70", "menciones 3.6.71")
    txt = txt.replace("no es el v3670", "no es el v3671")
    txt = txt.replace("n3670 = int", "n3671 = int")
    txt = txt.replace("{n3670}", "{n3671}")
    txt = txt.replace("if n3670 < 4:", "if n3671 < 4:")

    # 2 · notas: bloque FASE 72 (+ fragmento heredado r76) → bloque FASE 73
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 72 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + BLOQUE_NUEVO + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.71-SDK6'" in txt, "guard VERSION"
    assert "V3.6.71-SDK6" in txt, "badge"
    assert "FASE 73" in txt, "notas FASE 73"
    assert "FASE 72" not in txt, "quedan notas FASE 72"
    assert "v3.6.67-r75-baseline" not in txt, "fragmento r76 heredado"
    print("✓ release-v3671 creada (notas FASE 73, guards V3.6.71-SDK6)")


if __name__ == "__main__":
    main()
