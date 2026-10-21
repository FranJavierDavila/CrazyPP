# PLANTILLA DE CAMPEONATOS · Guía de fabricación
### CRAZY PING PONG · Ronda 25 · Modelo unificado de los 5 campeonatos

> **Objetivo:** crear un campeonato nuevo = **subir arte + rellenar config + elegir
> comportamientos existentes (o añadir nuevos)**. Esta plantilla destila TODO lo que
> oeste, locura, magia, estacion_orbital y valle_neon tienen entre todos, unificando
> las 3 fuentes de verdad que convivían (manifest.stages / CFG.etapas / taller.retos)
> en una sola: **el manifest**.
>
> valle_neon fue la prueba de concepto (100% data-driven); esta plantilla lo
> generaliza y le añade lo que le faltaba a todos: coronación épica, RUTA LEYENDA,
> bolsa rotatoria de poderes, pistola opcional, mapa arte|canvas e i18n en manifest.

---

## 1 · Los 4 pasos para crear un campeonato

```bash
# 1) Prepara el arte con los nombres exactos de _plantilla/assets/LEEME-ARTE.txt
#    (mínimo viable: 6 paredes de sala + rival + estados + bso + insignia)

# 2) Genera el campeonato (crea carpeta, adapta manifest, copia arte y valida)
python3 scripts/gen_campeonato.py \
    --id bosque --titulo-es "Bosque Encantado" --rival-nombre "DRÍADA" \
    --dificultad media --arte ./mi-arte/

# 3) Valida cuando quieras (mismo informe que imprime el generador)
python3 scripts/qa_plantilla.py public/championships/bosque

# 4) Regístralo SOLO cuando esté validado en el headset
python3 scripts/gen_campeonato.py --id bosque --titulo-es "Bosque Encantado" --registrar
#    (estado 'borrador' = invisible en el menú; pásalo a 'listo'/'publicado' al final)
```

El generador: copia el módulo, sustituye el `MOD_ID`, adapta manifest
(id/storage/título/rival/dificultad/coronación), copia el arte por nombre
convencional, **desactiva la pistola sola si falta `pistol.glb`** y ejecuta el
validador al terminar. Sin sorpresas.

---

## 2 · Catálogo unificado de parámetros (manifest.json)

Cada bloque indica su **ORIGEN** (qué campeonato lo aportó). La plantilla completa
está en `_plantilla/manifest.json` con comentarios bloque a bloque.

### 2.1 Contrato base (championship.schema.json, contract 1 — ya existía)
| Bloque | Quées | Notas |
|---|---|---|
| `id` / `version` / `contract` | identidad | id = nombre de carpeta, inmutable |
| `estado` | `borrador→validacion→listo→publicado→desactivado` | solo `publicado` sale en el menú |
| `title` / `description` | i18n `{es,en}` | tienda y HUB |
| `rival` | `{id,name,kind,states[],oppLabel,personalidad}` | kind: `stock|clown|wizard|forajido` libre |
| `storage` | `pp_champ_<id>_*` | locura usa `pp_arcade_*` por legado |
| `audio` | `{music, musicVolume, sounds{}}` | mp3/ogg/wav |

### 2.2 Bloques unificados NUEVOS (lo que estaba disperso/hardcodeado)
| Bloque | Unifica | Detalle clave |
|---|---|---|
| `camino` | manifest.stages (valle) vs CFG.etapas (orbital) vs taller.retos | `patron: "duelo_prueba"` genera duelo1→prueba1→duelo2→prueba2→final |
| `camino.dificultad` | 4 curvas de IA distintas | `modo:"formula"` (valle: `difMul·(1+paso·i)+personalidad`, final `difFinal`) **o** `modo:"tabla"` (oeste: valores exactos por duelo) |
| `camino.leyenda` | RUTA LEYENDA NG+ (oeste R24) | `aiMulMul 1.15 · chanceSuma 0.06 (max 0.60) · cooldownResta 1.5 (min 6.0) · primerResta 1.0 · pruebaExtra +1` — desactivable |
| `camino.worldMetric` | wins (locura) / duelwins (magia+orbital+valle) / puntos (oeste) | métrica del ranking mundial `{n,p,a}`; a = `★` campeón / `🏆` trofeo / `✔` victoria |
| `rivalVisual` | createRival del SDK (2 modos) | `modo:"precarga"\|"perezoso"`, `alto 2.15`, `pos`, `material`, `flotacion`, `aspecto` |
| `pruebas` | constantes JS (ARK_CFG, IMP_CFG, LEVEL…) | params por kind; la plantilla trae `dianas` completa |
| `powerTrigger` | powerTrigger (locura) = WIZ_POWER (magia) = OESTE_POWER = orbital | `chance 0.32 · cooldown 13 · minRallyHits 1 · warn 2.0 · bolsa:"rotatoria"\|"antirepeticion" · primerCd 6 · garantiaS 22 · postCd 10..15` |
| `playerPower` | mega_pala (locura) | opcional |
| `playerGun` | pistola de locura/magia/orbital | `glb pistol.glb · cadencia 0.16 · alcance 6.0` — se autodesactiva si falta el GLB |
| `mapa` | 5 mapas distintos | `modo:"canvas"` (valle, sin arte) **o** `"arte"` + `nodos[]` en píxeles; anillo de rejugada estándar |
| `cartel` / `hud` | carteles y HUDs de los 5 | createCartel del SDK; HUD canvas de las pruebas |
| `coronacion` | `_championFlow` (oeste R24) + showChampConseguido (los 5) | panel épico con `stats: [puntos, duelos, fecha]` + insignia en la sala |
| `i18n` | TXT de magia/oeste | las claves mínimas viajan en el manifest |

### 2.3 Claves de progreso (derivadas del storage, las mismas para todos)
`stage · champ · fecha · puntos · duelwins · wins · rank · leyenda_1..5 · leyenda`

### 2.4 SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO + SÚPER IMÁN (en el NÚCLEO desde v3.6.34; ×3 v3.6.35; matriz + solo-campeonatos + súper efecto v3.6.36; imán + flechas propias + efecto notorio v3.6.37 — se hereda sola)
La mecánica del superpoder de la pala del JUGADOR **no se implementa en los
módulos**: vive en `game.html` y TODO campeonato (existente o nuevo) la
hereda sin escribir una línea. Los superpoderes SOLO existen en los
campeonatos (nunca en un partido contra la máquina fuera de ellos).

| Regla | Valor |
|---|---|
| Dónde | **SOLO en campeonatos** (Modalidad Campeonato); el HALL y la calibración son zona neutra |
| Carga | **cada 11 golpes del rally** (11, 22, 33…) = **+1 carga** de un poder ALEATORIO del registro `PODERES_PALA` — el rally largo premia con más cargas; rally nuevo = cuenta nueva |
| Matriz | PODER DISTINTO → **ENTRA en la matriz** (orden de llegada; NO sustituye); MISMO poder → **acumula ×2, ×3 (tope 3**; lleno = «toc» y nada). Joystick ⟷ de cualquier mando CICLA el seleccionado (flechas ‹ › como sprites PROPIOS a los lados del icono — disco + oro + pulso —, sin envolver en los bordes); SOLO UN icono visible en la pala |
| Vida | las cargas viven SOLO en la partida en curso; nueva partida = 0 |
| Aviso | icono (PNG) anclado al mango (etiqueta ×N + flechas de matriz) + **voz NATIVA por poder e idioma** (es_ES davefx / en_US lessac, MP3 embebido) + jingle propio + háptica — nada dentro de la hoja |
| Uso | **gatillo del mando LIBRE** libera 1 carga del poder SELECCIONADO: MEGA PALA = 15 s (pala ×1,30 + radio ×1,38 + canto oro; activo+gatillo = alarga +15 s); SÚPER EFECTO = ventana de **8 s o 5 golpes con efecto** (spin generado ×2 con tope 2×spinMax; Magnus ×1,5 y bote ×1,8 SOLO en la bola marcada; la bola marcada lleva **halo rojo** + anillo en su bote y el rival sufre error ×2 y piernas ×0,85; activo+gatillo = recarga); SÚPER IMÁN = campo de **8 s** que atrae la bola al punto dulce (radio 0,45 m · plena a 0,12 m · a ≤3 m/s² · Δv ≤0,35 m/s por aproximación · predicción ≤0,15 s; **cada impacto asistido válido gasta 1 carga**, máx. 3 por activación — el gatillo solo abre el campo); en `serve` el gatillo SACA |
| Interruptor | conmutador **«Pala Mejorada»** en AJUSTES (`pp_pala_mejorada_v1`): apagado = pala 100 % normal |
| Extender | poder nuevo = una entrada en `PODERES_PALA` (id + nombre i18n + voz ES/EN + PNG) + su semántica en `megaTrigger` — la matriz, el ciclo y el reparto aleatorio lo incluyen solo |

**Prohibido para los módulos**: tocar `DIMS.hitAssistRadius`, escalar
`g.paddleMounts`, pintar FX sobre la hoja del jugador ni definir
`megaTrigger` — el núcleo los restauraría y el FX duplicado se ve dos veces.
Los poderes del RIVAL (bolsa rotatoria, forajido, mago…) siguen siendo cosa
de cada módulo: la norma solo cubre la pala del jugador.

---

## 3 · Comportamientos (kinds de prueba)

### Implementados por la plantilla
| kind | Descripción | Origen |
|---|---|---|
| `duelo` | Partida real a N puntos contra el rival, curva por duelo, expresiones, poderes | los 5 |
| `dianas` | Dianas flotantes con 3 modos: `objetivos` / `movimiento` / `contrarreloj` (+`rules.objetivo/puntos/premio`) | valle generalizado |

### Puntos de extensión (portar cuando se necesite)
| kind | Portar desde | Esfuerzo estimado |
|---|---|---|
| `arkanoid` | `locura/index.js` → `ArcadeArkanoid` (ARK_CFG/ARK2_CFG + abanico + ladrillo negro) | medio |
| `orbe` | `magia/index.js` → `OrbeMagico` (rejilla 3D + montaje + pistola por capas) | alto |
| `impulso` | `estacion_orbital/index.js` → `ReactorImpulso` | alto |
| `escudo` | `estacion_orbital/index.js` → `EscudoCasco` | alto |
| `tren` | `oeste/index.js` → `TrenAction` (parallax + paradas + túnel) | alto |
| `asedio` | `oeste/index.js` → `AsedioAction` (oleadas + casas destruibles) | alto |
| `custom` | el tuyo | `stage.module` apunta a tu clase |

**Cómo añadir un kind nuevo** — en `_plantilla/index.js` (o en tu copia):

```js
class MiPrueba {
  constructor(ctrl, game, stage, cfg) { /* cfg = manifest.pruebas[stage.kind] + stage.rules */ }
  start() {}                    // cartel/instrucciones
  activa() { return true; }     // true durante el juego (el núcleo llama testStep)
  step(dt) {}                   // tu simulación (usa CORE.stepPhysics para física real)
  stop() {}                     // limpia escena/flags de la bola
  dispose() {}
}
PLANTILLA_PRUEBAS.mikind = MiPrueba;   // y en manifest: { "kind": "mikind" }
```

**Cómo añadir un superpoder nuevo:**

```js
PLANTILLA_PODERES.mipoder = {
  inicio(game, p, ctrl, ctx) {},   // aplica el efecto (p = entrada de manifest.powers)
  paso(dt, game, p, ctrl, ctx) {}, // cada frame mientras dura
  fin(game, p, ctrl, ctx) {},      // restauración EXACTA (regla de oro del proyecto)
};
```

---

## 4 · Convención de arte (resumen)

Nombres exactos en `assets/` (lista completa y medidas en `LEEME-ARTE.txt`):
`sala_{floor,ceil,back,front,left,right}.jpg` · `rival.webp` + un fichero por estado
(`idle.webp`, `duelo.webp`…) · `bso.mp3` · `superpoder.webp` · `insignia.png` ·
`power_N.png` · opcionales: `mapa.png` (solo modo `arte`), `intro.mp4`,
`pistol.glb`, `risas.mp3`, `decorN.png`.

Reglas: PNG con alfa = recorte exacto sin borde · rival 512×1024 cuerpo entero ·
medidas de sala canónicas 6.10×7.90 / 6.10×2.85 / 7.90×2.85 m.

---

## 5 · Validación y ciclo de vida

- **`qa_plantilla.py`** (sin navegador): contrato 1, rangos del modelo unificado,
  inventario de assets, contrato champ_sdk en index.js (16 métodos), patrón del
  camino, secretos. `--compat` para los campeonatos orgánicos pre-plantilla.
- Ciclo: `borrador` (invisible) → `validacion` → `listo` → **`publicado`** →
  `desactivado`. El registro en `championships.json` se hace con `--registrar`.
- Antes de publicar valen además los sellos del proyecto (sella_rXX + qa_todo),
  igual que cualquier ronda.

## 6 · Reglas de oro (no negociables)

1. **Sólo positivo**: un campeonato nuevo NUNCA toca el núcleo ni los otros 5.
2. **Restauración exacta**: todo poder/efecto tiene `fin()` que devuelve el estado byte-idéntico.
3. **Contract 1**: el módulo habla con el núcleo SOLO vía champ_sdk.js y el export del contrato.
4. **Quest first**: pools pre-creados, sin asignaciones por frame, dispose en leave.
5. **Sin secretos** en ningún fichero versionado (GitHub Push Protection lo vigila).
6. **Mega Pala = núcleo** (v3.6.34): la pala del JUGADOR y su superpoder son
   NORMATIVA del núcleo (rally 11+ → carga; gatillo → 8 s; conmutador «Pala
   Mejorada») — un módulo NUNCA escala `paddleMounts`, toca
   `DIMS.hitAssistRadius` ni define `megaTrigger` (ver 2.4).

## 7 · Auditoría de origen (qué aportó cada campeonato a esta plantilla)

| Campeonato | Aportaciones al modelo unificado |
|---|---|
| **oeste** | Coronación épica (panel+fecha+stats), RUTA LEYENDA NG+ completa, curva de IA por tabla, poderes de dos fases, métrica mundial por puntos |
| **locura** | Bolsa rotatoria de poderes + lanzamiento garantizado, powerTrigger canónico, playerPower (mega_pala), pistola láser, room `variants.final` |
| **magia** | Estrellas 1-3 por fracción de tiempo (0.25/0.08), trofeo 3D, i18n en el módulo (aquí elevada a manifest), `champIntroPause` |
| **estacion_orbital** | createRival modo perezoso, poderes `custom` con `module`, timings de poderes (primerCd/garantía/post), HUD de prueba |
| **valle_neon** | 100% data-driven (la prueba de concepto), `personalidad` del rival, activación de poderes `rally\|puntos` + `cadaCuantos`, mapa canvas, firma createMusic |
| **champ_sdk v1.4.0** | El contrato: getCore, congela, createSfx/Music/PowerSign/Rival/Cartel |
