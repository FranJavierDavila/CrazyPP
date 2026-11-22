#!/usr/bin/env python3
"""v3.3.0-NUC1 · Bump de VERSION + badge + bloque de cambios en game.html."""
import sys
from pathlib import Path

GH = Path('/home/z/my-project/public/game.html')
src = GH.read_text()

def reemplazo(antes, despues, etiqueta):
    global src
    n = src.count(antes)
    if n != 1:
        sys.exit(f'ERROR ancla {etiqueta!r}: {n} apariciones (esperaba 1)')
    src = src.replace(antes, despues, 1)
    print(f'  OK {etiqueta}')

# 1) bloque de cambios antes del bloque ORB2
bloque = """  /* v3.3.0-NUC1 · REACTOR DE ENERGÍA INESTABLE (etapa 2 del camino) — nueva
   * mecánica descrita por el dueño: el NÚCLEO DE GRAVEDAD (nucleo_gravedad_lp
   * .glb, GLB procedural del artista: NucleoGravedad_Principal + Halo) flota
   * tras el borde lejano (0 · 1,62 · −3,35) con ROTACIÓN CAÓTICA procedural
   * (3 ejes con senos desfasados; se calma al acertar) y lanza ESFERAS DE
   * PLASMA (una a la vez, arco balístico T 0,95-1,25 s al campo del jugador;
   * la bola real queda aparcada en HOLD). El jugador las GOLPEA con la pala
   * (bumper esfera-esfera r 0,045+0,085 + velocidad de pala ×0,85, anti-
   * rebote 250 ms, salida 2,7-7,2 m/s con arco mínimo) y las devuelve a
   * COMPUERTAS de energía (anillo + película aditiva pulsante): la
   * estabilización es el CRUCE REAL del plano de la compuerta dentro del
   * radio interior (segmento prev→pos con quaternion inverso). FASE A: 1
   * compuerta GRANDE (r 0,40) fija que rota por 4 spots (3 aciertos). FASE
   * B: 2 PEQUEÑAS (r 0,24) simultáneas, una MÓVIL con deriva sinusoidal
   * (5 aciertos). FALLO (mesa sin golpear, suelo, 2.º bote, pasada, parada,
   * tiempo): ALARMA (3 flashes rojos de sala + luz/halo rojo pulsante +
   * zumbido sawtooth + haptics en ambas manos) + MODIFIER DE GRAVEDAD de la
   * próxima esfera (PESADA ×1,45 naranja / LIGERA ×0,55 violeta, 75%) — el
   * acierto re-estabiliza la gravedad. EXPRESIONES DEL ASTRO: laughing al
   * fallar (se burla), surprised cada 3 aciertos encadenados, derrotado/
   * triunfante al cerrar; base focused con retorno programado propio
   * (_exprHold: el _exprUpdate del duelo no pisa en prueba). HUD propio
   * (tiempo · X/8 compuertas · estabilidad ●●○ · gravedad activa) + cartel
   * showInstrucciones con la skin 'estacion' y botón EMPEZAR + re-explicación
   * en reintento (regla v2.106). 2 min 30 s · 5 fallos. Fin por _finish →
   * _pruebaFin/_despuesDePrueba (patrón muro) + reenter propio en el export.
   * Regla Quest: pools en el constructor, GLB con pereza (fallback
   * procedural), CERO asignaciones por frame (vectores tmp reutilizados).
   */
"""
reemplazo("  /* v3.2.1-ORB2 · AJUSTE FINO DEL DECORADO DE LA ESTACIÓN ORBITAL (informe",
          bloque + "  /* v3.2.1-ORB2 · AJUSTE FINO DEL DECORADO DE LA ESTACIÓN ORBITAL (informe",
          'bloque NUC1')

# 2) VERSION
reemplazo("const VERSION = '3.2.1-ORB2';   // v3.2.1-ORB2 · ",
          "const VERSION = '3.3.0-NUC1';   // v3.3.0-NUC1 · REACTOR DE ENERGÍA INESTABLE (etapa 2: sustituye al MURO 1; ARKANOID II de la etapa 4 intacto) · ",
          'const VERSION')

# 3) badge estático
reemplazo('>V3.2.1-ORB2</span>', '>V3.3.0-NUC1</span>', 'badge')

GH.write_text(src)
print(f'game.html escrito: {len(src):,} B')
