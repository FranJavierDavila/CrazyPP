# PLATAFORMA DE CAMPEONATOS — Auditoría y arquitectura (V2.125)

> Documento maestro generado de la auditoría real del código (13/10/2026).
> Es la especificación que usan tanto el equipo como las herramientas de
> generación automática. Si el núcleo cambia, este documento cambia.

## 1. Los tres estratos

| Estrato | Dónde | Qué contiene | Regla de oro |
|---|---|---|---|
| **NÚCLEO** | `public/game.html` (12.000 líneas) | Motor 3D, física, árbitro, menú HUB, audio (2 canales: música de menú + BSO de campeonato), ChampLoader, salas, ranking mundial | Los campeonatos NUNCA modifican el núcleo para existir |
| **SISTEMA COMÚN** | Clase `ChampLoader` (game.html L7317–7786) + `createChampRoom`/`createChampDecor` (L5772/5954) + índice `championships/championships.json` | Descubrimiento, carga, ciclo de vida, aislamiento de fallos, registro en menú | Cualquier cambio aquí debe validar los 3 campeonatos existentes |
| **CONTENIDO** | `public/championships/<id>/` — `manifest.json` + `index.js` + `assets/` | Temática, rival, superpoderes, pruebas, sala, música | Autónomo: una carpeta = un campeonato completo |

## 2. Contrato del ChampLoader (v2.125)

### Descubrimiento
1. `fetch('championships/championships.json')` (solo http/https; en `file://` se
   ignora en silencio — decisión v2.52).
2. Entradas: `"id"` o `{"id", "eager", "estado"}`. Regex anti-trayectoria
   `/^[a-z0-9_-]+$/i`.
3. **`estado` (v2.125)**: `"publicado"` (se lista y lanza), `"borrador"`,
   `"validacion"`, `"listo"` (se cargan bajo demanda pero NO aparecen en el
   menú), `"desactivado"` (no se carga). Por defecto: `"publicado"`.
4. Por cada campeonato publicado: fetch de `manifest.json` (título + storage +
   validación de contrato). Carpeta rota → se ignora sola y queda marcada con
   error visible en consola (`[champs] ...`).
5. `eager: true` → `preload()` al arrancar (sin `start()`). Solo para
   campeonatos que deben existir desde el primer frame (La Locura publica los
   datos de la BSO del núcleo).

### API que el núcleo entrega al módulo
```js
m.init({ game, id, stateName })   // ctx; el módulo valida window.__PP_CORE
```
**v2.125**: `ctx.manifest` lleva el manifest YA PARSEADO por el núcleo (los
módulos pueden seguir re-fetcheando su `cfg`/`level`, pero el fetch doble ya
no es obligatorio).

### Métodos del módulo que el núcleo consumirá si existen (todos opcionales)
`start` · `leave` · `update(dt)` · `onPoint(it)` · `onMatchOver(w)` ·
`aiMul()` · `serveTrigger(i)` · `reenter()` · `testActive()` · `testStep(dt)` ·
`gunArmed` · `paddleGunArmed` · `fireGun(i)` · `menuItems()` · `menuAction(a)` ·
`hint()` · `refresh()` · `resetRecords()` · `musicOff()` (nuevo en el
invariante de audio v2.125) · `replayMap/replayHover/replayLaunch` ·
`_split/splitFilterEvents/updateSplit`.

**Aislamiento**: toda delegación va en `try/catch` — un módulo roto NUNCA
tumba el frame; sus errores salen por consola como `[champs.X]`.

### Contrato de manifiesto (esquema v2.125)
Ver `championship.schema.json`. Mínimo obligatorio: `id`, `version`,
`contract` (1), `title{es,en}`, `description{es,en}`, `rival`, `storage`,
`assets`. Opcionales normalizados: `decor`, `room`, `powers[]`, `stages[]`,
`rewards`, `trophy`, `audio`, `procedural`, `notes[]`.

## 3. Superficie núcleo ↔ módulo (lo que los módulos PUEDEN tocar)

| Servicio | API estable | Notas |
|---|---|---|
| Física/estado | `window.__PP_CORE` (solo lectura: DIMS, stepPhysics, T, lang, aiPresets) | |
| Estado de partida | `game.rules.state = stateName` (el árbitro duerme) | Convención `'champtest'` |
| Audio | `game.audio`: `setArcWanted/setArcVol/setArcMute/setArcDuck/playOsc/playNoise/announce/rivalSfx` | Invariante UNA MELODÍA v2.122–2.125 |
| Música propia | Motor privado del módulo con `_musicEffVol()` siguiendo `arcVol/_arcDucked` (patrón magia/oeste v2.124) + guarda v2.125 `if (A.arcPlaying) return` | La BSO del núcleo (Locura) llama `mod.musicOff()` al arrancar |
| Sala | `game.champRoom.useVariant(v)` · bloques `room`/`decor` del export | createChampRoom viste 6 planos y restaura al salir |
| Ranking | `window.__PP_WORLD.submit(champId, {n,p,a})` | |
| Storage | prefijos `pp_champ_<id>_` (el reset global borra `pp_champ_*` entero) | Locura usa su legacy `pp_arcade_*` |
| Háptica | `game.haptic(hand, int, ms)` | Solo VR |

**Prohibido**: escribir en `game.ball` salvo `ignoreWalls/ignoreNet` (patrón
documentado), tocar `renderer.xr`, publicar globals nuevos tipo
`__PP_ARCADE_DATA` (es legacy de Locura; los nuevos campeonatos usan su
manifest).

## 4. Reglas estructurales ganadas (no romper jamás)

1. **UNA MELODÍA** (v2.122→v2.125): el invariante funciona en TODOS los
   sentidos y con los tres motores (menú ↔ BSO del núcleo ↔ BSO privada de
   módulo). `decodeAudioData` SIEMPRE en forma promesa y con copia
   (`ab.slice(0)`): la forma callback puede no dispararse jamás con la GPU
   saturada (bug constatado: la música del vagón moría en silencio).
2. **Espacio de coordenadas**: el jugador está en el origen del `rig`
   mirando a −Z. La red está en `DIMS.tableCenterZ` (−1,6). El campo propio
   es z ∈ [−1,50…+0,05] (convención confeti/mareo/tormenta).
3. **Texturas del artista**: los PNG deben traer alfa real. El Taller/validador
   comprueba esquinas y borde (ver `valida_activos.py`).
4. **Construye una vez, reusa toda la sesión** (regla Quest): pools, nada de
   asignar por frame.
5. **`championships.json` se GENERA** (`genera_indice.py`) — no se edita a mano.

## 5. Ciclo de vida de un campeonato

```
idea → (IA o asistente) → borrador → validación → listo → publicado ⇄ desactivado
                (carpeta con estado "borrador": el juego la ignora en el menú)
```
- Estados en `manifest.estado` (y espejo en la entrada del índice).
- Publicar = pasar `estado` a `"publicado"` + regenerar índice + validación.
- Desactivar = `"desactivado"` (la carpeta permanece; nada se borra).
- Nunca se sobrescribe un campeonato existente sin respaldo previo
  (`respaldo.py` crea snapshot verificado antes de cualquier migración).

## 6. Protección y restauración

- **Snapshot**: `python3 scripts/plataforma/respaldo.py "motivo"` →
  `respaldos/crazypp-<fecha>-<tag>.zip` (public/ + src/ + scripts/plataforma +
  configs) + SHA256SUMS dentro del propio zip + manifiesto externo.
- **Restaurar**: `python3 scripts/plataforma/restaurar.py respaldos/<zip>` —
  verifica SHA256, vuelca `public/` y deja el resto en `<zip>.restaurado/`.
- **Git**: cada versión publicada lleva tag `estable-vX.Y.Z`. La línea base
  v2.122 es el commit `3c0c2b9`.
- **Regresión**: `valida_regresion.py` — arranca el juego, lanza cada
  campeonato publicado, exige 0 errores JS y UNA sola melodía audible.

## 7. Herramientas (scripts/plataforma/)

| Script | Fase | Qué hace |
|---|---|---|
| `respaldo.py` / `restaurar.py` | A | Snapshot verificado / restauración |
| `valida_activos.py` | B | Alfa de PNG, formatos, tamaños, referencias del manifest |
| `valida_manifiesto.py` | B/E | Valida un manifest.json contra el esquema v2.125 |
| `genera_indice.py` | C | Regenera championships.json desde las carpetas |
| `migra_manifiestos.py` | D | Añade los campos normalizados a los 3 existentes (idempotente) |
| `crear_campeonato.py` | E | Asistente 7 fases → paquete completo + validación |
| `idea_llm.mjs` | F | Idea en texto → semilla completa (z-ai-web-dev-sdk) |
| `valida_regresion.py` | G | Batería automática de no-regresión |
