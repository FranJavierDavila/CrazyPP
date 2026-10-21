# SUPERPODER DE PALA · Conocimiento del sistema

> Documento maestro del diseño aprobado por el dueño (FASE 37 · V3.6.35-SDK6,
> ronda 43). Toda la mecánica vive en el **núcleo** (`game.html`, generado desde
> `src/game/core/c12_pingponggame.js` + i18n en `c00_pre_three.js`): TODOS los
> campeonatos (locura, magia, oeste, estacion_orbital, valle_neon) y cualquier
> campeonato nuevo la heredan **sin escribir una línea** (norma en
> `public/championships/PLANTILLA-GUIA.md` §2.4).

## 1 · Reglas del juego (aprobadas)

| Regla | Valor |
|---|---|
| Concesión | **Cada 11 golpes del rally** (11, 22, 33…) = **+1 carga** de un poder **aleatorio** del registro `PODERES_PALA`. El rally largo premia con más cargas (la resistencia se premia sola, sin niveles). Rally nuevo = cuenta nueva. |
| Acumulación | **Mismo poder** → ×2, ×3 (tope 3; con la mano llena, «toc» honesto y nada). **Poder distinto** → lo **sustituye** (cargas a 1). |
| Vida | Las cargas viven **solo en la partida en curso**; nueva partida = 0. |
| Uso | **Gatillo del mando LIBRE** (el que no tiene la pala — conmuta solo al cambiar de mano) gasta 1 carga: **15 s** de MEGA PALA por carga. |
| Gasto múltiple | Gatillo con el poder **ACTIVO** y cargas → **alarga** +15 s por carga. El tamaño **nunca** se apila (el balance no se rompe). |
| Efecto MEGA PALA | Pala ×1,30 visual + radio de detección ×1,38 + canto de energía silueta ×1,055 + onda de choque + power-up sonoro + háptica. |
| Excepciones | En `serve` el gatillo **SACA** (cero conflicto). Si un campeonato ocupa la mano libre (pistola del Oeste armada), el gatillo de la pala queda de **respaldo**. El **HALL es zona neutra**. |
| Interruptor | **«Pala Mejorada»** en el menú principal → página AJUSTES (`pp_pala_mejorada_v1`, persistente, por defecto ON). Apagado = pala 100 % normal (recogida inmediata con dispose, mano vacía). |

## 2 · Feedback al jugador (el "chula y efectista")

1. **Icono del dueño anclado al mango**: sprite-billboard de 4,8 cm con el PNG
   elegido por el dueño (`SuperPala_Crece.png`, tres palas que crecen), posicionado
   en la **base de la mano, justo sobre el mando** (`MEGA_ICON_Y = -0.034`,
   `MEGA_ICON_Z = 0.004`) — «forma parte de la pala y no distrae».
2. **Etiqueta ×N**: al acumular 2-3 cargas, el icono lleva una etiqueta roja
   **×2/×3** dibujada en la textura (la idea «+2» del dueño).
3. **Voz animosa**: «¡Potenciador de pala gigante!» — TTS pre-generado (voz
   `tongtong`, recortada y normalizada, 2,4 s), **MP3 embebido como data-URI**
   (cero latencia, cero red, offline en el Quest).
4. **Jingle de carga** propio (tríada mayor 523→659→784→1568 + brillo) — firma
   distinta del arpegio de activación (420→860→1400) + háptica 0,5/120 ms.
5. **Megáfono ES/EN**: `¡POTENCIADOR DE PALA GIGANTE!` (con ` ×N` si acumula) y
   `TOPE ×3 · ¡gasta una con el gatillo libre!` cuando la mano está llena.
6. **Pista de la norma** una sola vez por navegador (`pp_mega_norm_hint`).
7. Mientras ACTIVA: icono fuera, cuenta atrás implícita con parpadeo final y
   aviso sonoro descendente; al agotarse, el icono **vuelve** con las cargas
   restantes.

## 3 · Arquitectura (extensible)

```
PODERES_PALA (c12, final del fichero)      ← REGISTRO: un poder = una entrada
  { id: 'mega', nombre: () => T('poder_mega'), voz: VOZ_PODER_MEGA }
MEGA_DUR=15 · MEGA_TOPE=3 · MEGA_GOLPES=11 · MEGA_ICON_Y/Z/S  ← constantes
PNG_PODER_MEGA / VOZ_PODER_MEGA            ← assets data-URI embebidos
```

| Pieza | Dónde | Qué hace |
|---|---|---|
| `updateMega(dt)` | c12 (bucle `animate`) | CARGA: `floor(rallyHits/11) > _megaRallyGrants` → `_megaCharge()`. ACTIVA: radio/escala/canto/onda/aviso. |
| `_megaCharge()` | c12 | Poder aleatorio; mismo→acumula (tope 3); distinto→sustituye; icono+voz+jingle+megáfono. |
| `megaTrigger(i)` | c12 | Gatillo del **mando libre** (respaldo en la pala si `gunArmed`); libera/alarga/aviso honesto. |
| `_megaIconTex(n)` | c12 | PNG del dueño + etiqueta ×N; respaldo canvas dorado si el PNG no cargó. |
| `_megaVoz()` | c12 | decode una vez + caché por AudioContext (patrón `_playRivalBuffer`). |
| `_megaPngCarga()` / `_megaIconRefresh()` | c12 | Carga async del PNG y redibujo de la textura al cambiar cargas. |
| `_megaNormReset()` | c12 | Recogida COMPLETA con dispose (regla Quest): conmutador OFF, hall, fin. |
| Estado | c12 constructor | `_megaLoads` (0..3) · `_megaPoder` (id) · `_megaRallyGrants` (por rally). |

**Añadir un superpoder nuevo** = ① entrada en `PODERES_PALA` + ② clave i18n
`poder_<id>` ES/EN + ③ voz MP3 embebida + ④ icono (extender `_megaIconTex` con
un branch por id). El reparto aleatorio y TODOS los campeonatos lo cogen solos.

## 4 · QA y sellado

- Capa **AD** `scripts/qa_mega_cargas_v3635.py` (92 checks en vivo): 10 sin
  carga · 11 ×1 · 22 ×2 · 33 ×3 · 44 tope · gatillo libre libera 15 s ·
  alarga +15 s · agotamiento · icono anclado · PNG decodificado · rally nuevo
  resetea · conmutador por el menú con persistencia · hall neutro. La capa AC
  (`qa_mega_norma_v3634`) quedó **retirada del listado** (historial conservado).
- `scripts/sella_r43.py` sella las capas E/F/G/H/I a 3.6.35-SDK6 + tamaños reales
  de los ZIPs.
- Assets de la ronda: `scripts/_poder35/` (voz TTS final + icono cuantizado a 64
  colores, 36,8 KB) y `scripts/_poder35_insertar_assets.py` (inserción de los
  data-URI en el núcleo).

## 5 · Decisiones de diseño y por qué

- **«Cada 11 golpes = +1 carga»** unifica los dos modelos que planteó el dueño
  (umbral fijo vs. premio por resistencia): un rally de 22 da 2 cargas — la
  resistencia se premia sin inventar niveles de poder.
- **Acumulación con tope ×3**: premia no gastar, elimina el miedo a perder la
  carga y crea la tensión «¿uso o espero a ×3?».
- **Sustitución por poder distinto**: tensión deliberada (úsalas o arriésgate);
  con un solo poder hoy, la regla espera a que el registro crezca.
- **Gatillo del mando libre**: es el que no hace nada en pleno rally → cero
  pulsaciones accidentales de la mano que balancea la pala; conmuta solo si se
  cambia la pala de mano; escritorio (sin XR) acepta el clic de ratón.
- **Icono anclado al mango** (y no flotando a un lado): petición explícita del
  dueño; las constantes `MEGA_ICON_Y/Z/S` lo ajustan en un solo sitio.
- **Voz TTS pre-generada embebida**: el speechSynthesis del navegador es
  robótico e impredecible en el Quest Browser; el MP3 suena igual siempre y no
  depende de red.
