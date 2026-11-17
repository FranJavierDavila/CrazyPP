#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""README del proyecto → V3.0: título, tabla de descargas y secciones de novedades."""
import io

P = '/home/z/my-project/download/README.md'
s = io.open(P, encoding='utf-8').read()

# ── 1) Título ──────────────────────────────────────────────────────────────
old_tit = "# 🏓 CRAZY PING PONG v2 — Meta Quest 3"
new_tit = "# 🏓 CRAZY PING PONG v3 «PRO TRAINING» — Meta Quest 3"
assert s.count(old_tit) == 1
s = s.replace(old_tit, new_tit)

# ── 2) Intro ──────────────────────────────────────────────────────────────
old_intro = """Videojuego de tenis de mesa en WebXR, en **un único archivo HTML**
(`pingpong-quest3-v2/index.html`, con la pala 3D, la librería PeerJS, los
DOS bancos de voz (castellano e inglés), los carteles de victoria/derrota
en ambos idiomas, la portada animada y la música incrustados — no necesita
más archivos)."""
new_intro = """Videojuego de tenis de mesa en WebXR. La versión actual, la **V3.0
«PRO TRAINING»**, conserva todo el espíritu de un solo `index.html` (pala 3D,
PeerJS, los DOS bancos de voz castellano/inglés, carteles, portada y música
incrustados) y añade el **centro de entrenamiento PRO TRAINING** además de
**4 campeonatos con arte propio** (La Locura · Magia · Salvaje Oeste ·
Estación Orbital) que viajan dentro del mismo zip."""
assert s.count(old_intro) == 1
s = s.replace(old_intro, new_intro)

# ── 3) Tabla de descargas ─────────────────────────────────────────────────
old_tab = """## 📦 Descargas del proyecto (versión definitiva V2.124)

| Archivo | Qué es | Cómo se usa |
|---|---|---|
| `pingpong-quest3-v2.zip` | **El juego final (V2.124)**, un solo `index.html` + `assets/pala.glb` | Arrastrar a [app.netlify.com/drop](https://app.netlify.com/drop) → abrir la URL en el Meta Quest Browser → **ENTRAR EN VR** |
| `editor-campeonatos.zip` | **El Taller**: editor de campeonatos (asistente de 7 fases) | Arrastrar a Netlify Drop (o abrir `index.html` con doble clic) → crear campeonatos → descargar el paquete de pruebas |
| `editor-campeonatos/index.html` | El mismo editor, suelto | Doble clic y listo; funciona sin internet |
| `guia-campeonatos-crazy-pingpong.pdf` | **Guía maquetada sin tecnicismos** (14 páginas) | Para leer/imprimir: cómo se crean, prueban y publican los campeonatos |
| `guia-campeonatos-crazy-pingpong.html` | La misma guía en HTML autónomo | Se abre en cualquier navegador, fuentes incluidas |
| `editor-captura-*.png` | Capturas del editor (inicio, fase 1, fase 7) | Vista rápida de la herramienta |"""
new_tab = """## 📦 Descargas del proyecto (versión definitiva V3.0 «PRO TRAINING»)

| Archivo | Qué es | Cómo se usa |
|---|---|---|
| `crazypp-v3.zip` | **El juego final (V3.0)** — `index.html` (6,2 MB) + `assets/intro.mp4` + 4 campeonatos con arte propio. SHA256 sellado en `SHA256SUMS-V3.0.txt` | Arrastrar a [app.netlify.com/drop](https://app.netlify.com/drop) → abrir la URL en el Meta Quest Browser → **ENTRAR EN VR** |
| `RELEASE-V3.0.txt` | **Notas oficiales de la V3.0** selladas: contenido, qué añade, verificación e historial de tamaños | Leer antes de publicar |
| `SHA256SUMS-V3.0.txt` | Hash SHA256 del zip oficial | Verificar con `sha256sum -c SHA256SUMS-V3.0.txt` |
| `editor-campeonatos.zip` | **El Taller**: editor de campeonatos (asistente de 7 fases), actualizado a V3.0 | Arrastrar a Netlify Drop (o abrir `index.html` con doble clic) → crear campeonatos → descargar el paquete de pruebas |
| `guia-campeonatos-crazy-pingpong.pdf` | **Guía maquetada sin tecnicismos** (14 páginas, V3.0) | Para leer/imprimir: cómo se crean, prueban y publican los campeonatos |
| `guia-campeonatos-crazy-pingpong.html` | La misma guía en HTML autónomo (V3.0) | Se abre en cualquier navegador, fuentes incluidas |
| `pingpong-quest3-v2.zip` | Archivo histórico **V2.124** (5,3 MB, sin campeonatos con arte) | Legado; la V3.0 lo sustituye por completo |"""
assert s.count(old_tab) == 1
s = s.replace(old_tab, new_tab)

# ── 4) Novedades V3.0 + resumen V2.125→V2.141 antes de v2.31 ──────────────
ancla = "## Novedades v2.31 — rescate definitivo del audio en VR"
assert s.count(ancla) == 1
bloque = """## Novedades V3.0 — «PRO TRAINING», el centro de alto rendimiento

**LA VERSIÓN ACTUAL ES LA V3.0** (base V2.141, recuperada y auditada). El botón
ENTRENAR abre ahora el HUB **PRO TRAINING**, un menú artístico en VR con:

- **Subapartado 0 — Posición de la pala**: el panel de ajuste de agarre de
  siempre, ahora plegado dentro del hub como primer subapartado.
- **5 áreas profesionales con 2 modos cada una**:
  1. *Dirección*: MESA MARCADA (6 zonas, objetivo dorado rotativo, centro
     prohibido) y JUNTO A LA LÍNEA (bandas de 10/12 cm).
  2. *Altura*: PASE BAJO (cinta naranja a 17 cm sobre la red) y GLOBO
     DEFENSIVO (aro a 1,50 m).
  3. *Efecto*: LEER EL CORTADO (máquina con backspin REAL) y BLOQUEAR EL
     TOPSPIN (velocidad variable).
  4. *Saque*: SAQUE CORTO DOBLE BOTE y SAQUE LARGO AL FONDO (últimos 15 cm).
  5. *Ritmo*: METRÓNOMO con hitos a 30/50/100 golpes.
- **Feedback técnico** (solo en entrenamiento): marcas de bote, línea de tiro
  real, flecha de efecto y panel flotante con racha/meta/puntos.
- **Progreso y recompensas**: puntos por acierto → perfil persistente con
  niveles Novato→Leyenda → **5 pieles de pala desbloqueables** (Clásica, Fuego
  150, Hielo 400, Oro 800, Arcoíris 1500) aplicables en TODOS los modos.
- **Efecto visible en todo el juego**: iconos de efecto sobre AMBAS caras de
  la pala al aplicar giro (naranja=top, azul=corte, violeta=lateral) y estela
  coloreada. La física de giro (Magnus + rebote) ya era global en V2.141;
  V3.0 la hace VISIBLE sin tocar la dificultad.
- **Aislamiento total**: módulo `window.__PP_TRAIN` con escena, jueces y
  almacenamiento propios (`ppxr_train_v1`); física, árbitro, IA y los
  4 campeonatos no cambian.

## Entre V2.125 y V2.141 — resumen del tramo

- **V2.141 recuperada** del enlace WeTransfer oficial del dueño (zip de
  100,67 MB, SHA256 verificado) tras un revés del espacio de trabajo, y
  **auditada**: 30+ comprobaciones sobre núcleo, voces, arte y assets —
  todas superadas.
- **4 campeonatos publicados** con arte y audio propios dentro del zip:
  *La Locura* (v20, cargado eager), *Magia* (v28), *Salvaje Oeste* (v48:
  indios, dinamita en cadena, lingotes, cajones, megafonía, risas del
  forajido y del pueblo) y *Estación Orbital* (v5: intro con JUGAR y
  poderes AX-9).
- Todo el trabajo previo de voces, carteles, multijugador y audio del
  tramo v2 queda dentro de la V2.141 y, con ella, en la V3.0.

"""
s = s.replace(ancla, bloque + ancla)

io.open(P, 'w', encoding='utf-8').write(s)
print('README → V3.0 OK (título + intro + tabla + 2 secciones nuevas)')
