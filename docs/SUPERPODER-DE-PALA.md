# SUPERPODER DE PALA · Conocimiento del sistema

> Documento maestro del diseño aprobado por el dueño (FASE 39 · V3.6.37-SDK6,
> ronda 45). Toda la mecánica vive en el **núcleo** (`game.html`, generado desde
> `src/game/core/c12_pingponggame.js` + i18n en `c00_pre_three.js` + física en
> `c02/c04/c05/c06`): TODOS los campeonatos (locura, magia, oeste,
> estacion_orbital, valle_neon) y cualquier campeonato nuevo la heredan **sin
> escribir una línea** (norma en `public/championships/PLANTILLA-GUIA.md` §2.4).

## 1 · Reglas del juego (aprobadas)

| Regla | Valor |
|---|---|
| DÓNDE | **SOLO en los campeonatos** (Modalidad Campeonato, contra rivales). En un partido contra la máquina FUERA de los campeonatos no aparece nada (petición explícita del dueño; gate = `champs.active`). El HALL y la calibración siguen siendo zona neutra. |
| Concesión | **Cada 11 golpes del rally** (11, 22, 33…) = **+1 carga** de un poder **aleatorio** del registro `PODERES_PALA`. El rally largo premia con más cargas. Rally nuevo = cuenta nueva. |
| Matriz | Un poder distinto **NO sustituye**: **ENTRA en la matriz** (orden de llegada; el primero cogido ocupa la posición 0, el siguiente la 1…). Mismo poder → **acumula ×2, ×3** (tope 3; lleno = «toc» honesto). |
| Selección | **Joystick ⟷ de cualquier mando** cicla el seleccionado (en escritorio, ←/→). En todo momento **SOLO UN icono** se ve en la pala. **Flechas ‹ ›** como sprites PROPIOS a los lados del icono (disco oscuro + chevron oro + pulso — ronda 45: dentro del icono «no se nota»), **sin flecha izquierda en el índice 0, sin flecha derecha en el último** — y el joystick tampoco envuelve en los bordes. |
| Vida | Las cargas viven **solo en la partida en curso**; nueva partida = 0. |
| Uso | **Gatillo del mando LIBRE** (conmuta al cambiar de mano; respaldo en la pala si la pistola del Oeste ocupa la libre; escritorio = ratón) gasta 1 carga del poder **SELECCIONADO**. |
| MEGA PALA | 15 s por carga (pala ×1,30 visual + radio ×1,38 + canto oro + onda). Activa + gatillo = **alarga +15 s** (el tamaño nunca apila). |
| SÚPER EFECTO | Ventana propia: **8 segundos O 5 golpes con efecto**, lo que ocurra primero. Activo + gatillo = **recarga** la ventana. |
| SÚPER IMÁN | **8 segundos** de campo que atrae SUAVE la bola al **punto dulce**. **Cada impacto asistido válido consume 1 carga** (máx. **3 asistencias por activación**); el gatillo solo abre el campo (las cargas solo se gastan cuando el imán ayuda de verdad). Activo + gatillo = **refresca** la ventana. |
| Interruptor | **«Pala Mejorada»** en AJUSTES (`pp_pala_mejorada_v1`, por defecto ON) = llave maestra. Apagado = pala 100 % normal. |

## 2 · SÚPER EFECTO — las 4 reglas del dueño (implementadas)

1. **El jugador genera el efecto**: el spin sale del brush real del golpe
   (velocidad tangencial de la pala + giro de muñeca, `pad.omega` en c05).
2. **×2 al spin GENERADO** (`EFECTO_SPIN_MUL = 2`) — **nunca** a la rotación
   acumulada que ya traía la bola (la reversión −35 % del golpe sigue igual) —
   con **tope de seguridad 2 × spinMax** (`efectoSpinTope`, ≈2.100 rpm).
3. **El bote exagera el efecto**: la bola golpeada sale **MARCADA**
   (`ball.ppEfecto`) y hasta que la IA la devuelve (c06 limpia la marca):
   **Magnus ×1,5** en vuelo (`efectoMagnusMul`) y **acople de bote ×1,8**
   (`efectoBoteMul`) — topspin patea más hacia delante, sidespin desvía más,
   backspin frena más. El **tope de Coulomb** del bote sigue mandando: la
   desviación extra queda limitada y dependiente del spin (el rival hábil
   PUEDE contrarrestarlo). Golpe sin spin significativo
   (`|spin| < EFECTO_SPIN_MIN = 25`) no cuenta como golpe con efecto ni
   recibe bonificación.
4. **Duración limitada**: 8 s o 5 golpes con efecto, lo primero que ocurra.

> Predicción de la IA y solver del saque NO marcan la bola: siguen prediciendo
> con la física de siempre (la sorpresa es del jugador). El golden de física
> determinista no cambia (todos los multiplicadores son inactivos sin el poder).

### 2.b · SÚPER EFECTO NOTORIO (ronda 45 — «no lo noto»)

1. **HALO ROJO** sobre la bola marcada: sprite aditivo anclado a la bola cada
   frame (`_buildEfectoHalo`), visible mientras `ball.ppEfecto` (la IA limpia
   la marca al devolver).
2. **ANILLO DE BOTE amplificado**: cuando la bola marcada (con |spin| ≥ 25)
   bota en la mesa, anillo rojo one-shot de 0,38 s + barrido sonoro
   (`_efectoBoteFxShow`, disparado en `processEvents` caso `table`).
3. **Dificultad % al rival**: con la bola marcada viniendo, la IA sortea su
   error de puntería **×2** (`efectoRivalErrMul`) y va con **piernas ×0,85**
   (`efectoRivalVel`) — «dificultar en un %» el éxito del rival sin tocar la
   física de salida (honesto: se contrarresta con colocación).
4. **El mensaje enseña a aplicarlo**: «¡SÚPER EFECTO! · golpea con GIRO
   (arrastra la pala al golpear): spin ×2 · 8 s / 5 golpes» — el dueño no
   sabía que hay que barrer la pala para generar spin.

### 2.c · SÚPER IMÁN (ronda 45 — 3.er poder, spec completa del dueño)

**Objetivo**: campo magnético temporal alrededor de la pala del jugador que
atrae suavemente la pelota hacia el punto dulce. Aumenta la probabilidad de
impacto limpio **sin eliminar la habilidad ni falsear la física**.

**Principios implementados (todos)**: la pala sigue mandada por el movimiento
real de la mano/mando · la atracción centra el impacto pero NO dirige el
golpe · no se teletransporta la bola ni se mueve la pala · no se recuperan
bolas que ya superaron el plano de golpeo · velocidad/giro/energía los
gestiona el modelo de contacto de siempre · cada impacto asistido válido
consume 1 carga (máx. 3 por activación) · integración por SUBPASO con h fijo
(estable ante fluctuaciones de FPS).

| Parámetro (prototipo, a calibrar) | Valor inicial |
|---|---|
| Duración | 8 segundos (reloj de juego; respeta la pausa) |
| Impactos asistidos máximos | 3 |
| Intensidad | Media (= los valores de la tabla tal cual) |
| Radio de influencia | 0,45 m |
| Distancia de máxima asistencia | 0,12 m (plena dentro; lineal hasta el radio) |
| Aceleración lateral máxima | 3 m/s² |
| Incremento lateral máximo por aproximación | 0,35 m/s (acumulado real) |
| Tiempo máximo de predicción del impacto | 0,15 s (predicción lineal) |

> NO son propiedades físicas de un imán real: son parámetros de prototipo del
> dueño para calibrar con las velocidades reales del juego (DIMS.iman*).

## 3 · Feedback al jugador

1. **Icono anclado al mango** (sprite-billboard 4,8 cm, base de la mano, justo
   sobre el mando): PNG del poder seleccionado + **etiqueta ×N** (2-3 cargas)
   + **flechas ‹ ›** de la matriz.
2. **Voz NATIVA** por poder e idioma — Piper **es_ES-davefx** (la MISMA voz
   castellana de la megafonía del juego: «¡Potenciador de pala gigante!» /
   «¡Potenciador de súper efecto!») y **en_US-lessac** si se juega en inglés
   («Giant paddle booster!» / «Super spin booster!»). MP3 embebido data-URI,
   decode+caché. Adiós a la voz tongtong («horrible, no nativa» — petición
   del dueño, FASE 38).
3. **Jingle de carga** (tríada mayor + brillo) compartido; activación con
   arpegios PROPIOS por poder (oro square 420→1400 · cian sawtooth 340→1280).
4. **Canto de energía por poder**: oro ×1,055 (MEGA) / cian ×1,07 (EFECTO) /
   azul ×1,07 (IMÁN, 0x5aa2ff — familia del icono) — pueden convivir (son
   ortogonales). Onda de choque al liberar. Aviso sonoro
   descendente <2 s. Megáfono ES/EN con ×N y mensajes propios del efecto
   (`arc_efecto_go/fin`).
5. Pista de la norma una vez por navegador (`pp_mega_norm_hint`), ahora con
   matriz + joystick + «solo campeonatos».

## 4 · Arquitectura (extensible)

```
PODERES_PALA (c12, final del fichero)   ← REGISTRO: un poder = una entrada
  { id, nombre: () => T('poder_<id>'), voz, vozEn, png }
MEGA_DUR=15 · MEGA_TOPE=3 · MEGA_GOLPES=11 · MEGA_ICON_Y/Z/S · MEGA_ARROW_S=0.020
EFECTO_DUR=8 · EFECTO_GOLPES=5 · EFECTO_SPIN_MUL=2 · EFECTO_SPIN_MIN=25
IMAN_DUR=8 · IMAN_ASIST=3
DIMS: efectoSpinTope=2 · efectoMagnusMul=1.5 · efectoBoteMul=1.8
DIMS: efectoRivalErrMul=2.0 · efectoRivalVel=0.85 (efecto notorio)
DIMS: imanRadio=0.45 · imanPlena=0.12 · imanAcelMax=3 · imanDvMax=0.35 · imanTPred=0.15
PNG_PODER_* / VOZ_PODER_*               ← assets data-URI embebidos
```

| Pieza | Dónde | Qué hace |
|---|---|---|
| `updateMega(dt)` | c12 (bucle `animate`) | CARGA (11 golpes) · timers de MEGA y EFECTO · multiplicador del efecto en la pala · ciclo joystick · FX · icono. |
| `_megaCharge()` | c12 | Poder aleatorio; mismo→acumula (tope 3); distinto→ENTRA en la matriz y se selecciona; icono+voz+jingle+megáfono. |
| `_megaMatriz` / `_megaIdx` | c12 | La matriz `[{id, n}]` en orden de llegada + índice seleccionado. |
| `_megaCiclo/_megaCicla` | c12 | Joystick ⟷ (flanco + antirrebote 0,33 s, ambos mandos) y ←/→; SIN envolver en bordes. |
| `megaTrigger(i)` | c12 | Gatillo del mando libre: libera el poder SELECCIONADO (mega alarga · efecto recarga). |
| `_efectoTrigger/_efectoFin` | c12 | Ventana del súper efecto (8 s / 5 golpes) + FX cian + onda. |
| `_megaIconTex()` | c12 | PNG del poder seleccionado + etiqueta ×N (reservas canvas por poder). SIN flechas dentro (ronda 45). |
| `_megaVoz(id)` | c12 | Voz por poder e idioma (`__ppLang`), decode una vez + caché. |
| `_fxBuild(col)` | c12 | Canto+onda parametrizado (oro 0xffc84a / cian 0x54d8f0 / azul 0x5aa2ff). |
| `_imanTrigger/_imanFin/_imanImpacto` | c12 | Campo del imán: abre/refresca sin consumir; **cada impacto asistido gasta 1 carga** (máx. 3/activación); cierra por tiempo/cargas/tope. |
| `_buildMegaArrows/_megaArrowTex` | c12 | Flechas ‹ › como sprites PROPIOS junto al icono (disco oscuro + oro + pulso), visibilidad por índice. |
| `_buildEfectoHalo/_efectoBoteFxShow` | c12 | Halo rojo de la bola marcada + anillo de bote amplificado (one-shot 0,38 s). |
| `_megaNormReset()` | c12 | Recogida COMPLETA con dispose (conmutador OFF, hall, fin de partida). |
| Física | c02/c04/c05/c06 | `pad.ppEfectoMul` (brush ×2 + tope 2×spinMax) · `ball.ppEfecto` (Magnus ×1,5 + bote ×1,8 solo marcada) · c06 limpia la marca al devolver la IA · c06 castiga al rival con bola marcada (err ×2, piernas ×0,85). |
| `applyIman(ball, paddles, h)` | c05 (SUBPASO) | Atracción lateral al punto dulce: predicción ≤0,15 s · plena a ≤0,12 m · lineal hasta 0,45 m · a ≤3 m/s² · Δv ≤0,35 m/s por aproximación · solo bolas que se acercan y no pasaron el plano · marca `ball.ppImanTocada` (la consume el gancho 4.95 del animate). Golden intacto: todo detrás de `ball.ppIman`. |

**Añadir un superpoder nuevo** = ① entrada en `PODERES_PALA` + ② i18n
`poder_<id>` ES/EN + ③ voces ES/EN embebidas + ④ PNG embebido (+ su semántica
de activación en `megaTrigger`). La matriz, el ciclo, el reparto aleatorio y
TODOS los campeonatos lo cogen solos.

## 5 · QA y sellado

- Capa **AE** `scripts/qa_poderes_matriz_v3636.py` (en vivo): agujas de la
  matriz + súper efecto + gate de campeonatos + voces nativas + mecánica
  headless (carga 11/22/33/44 · matriz con 2 poderes · ciclo ⟷ sin envolver ·
  flechas en el icono · súper efecto 8 s / 5 golpes · spin ×2 con tope ·
  marca de bola y limpieza por la IA · SOLO campeonatos: fuera de ellos no
  carga ni el gatillo responde · conmutador + hall neutros). La capa AD
  (`qa_mega_cargas_v3635`) quedó **retirada del listado** (historial).
- `scripts/sella_r44.py` sella las capas E/F/G/H/I a 3.6.36-SDK6.
- Assets de la ronda: `scripts/_poder36/` (4 voces Piper + **icono REAL del
  dueño** `icono_efecto_real_64.png`, cuantizado a 64 colores con la receta
  del Crece) y `scripts/_poder36_insertar_assets.py` (inserción data-URI).
- Ronda 44-b: el icono PROVISIONAL de la casa se sustituyó por el
  `SuperPala_Efecto.png` del dueño (`scripts/_poder36_swap_icono_real.py`,
  comparación EXACTA del URI completo). Lección operativa: `deploy_pages.py`
  ensambla con `git archive HEAD` (solo commiteados) — **commit ANTES de
  deploy** o producción sirve el build viejo; y tras rodado, re-asentar
  `refs/heads/pages` a `origin/pages` (non-fast-forward, caso 133/142).

## 6 · Decisiones de diseño y por qué

- **Matriz en vez de sustitución** (cambio de la FASE 37, petición del dueño):
  «en caso de salir un potenciador distinto que NO elimine los actuales» — la
  tensión «úsalas o arriésgate» se sustituye por gestión de arsenal: cada
  poder conserva sus multiplicadores y el jugador elige cuándo y cuál.
- **Solo 1 icono visible** + flechas condicionales: la petición literal del
  dueño («en todo momento solo tenemos 1 visible en la pala»; «si estamos en
  el potenciador 0 no aparece flecha a la izquierda»).
- **SOLO campeonatos**: «los potenciadores SOLO aparecen en los campeonatos
  contra rivales, NO en una modalidad diferente con un partido contra la
  máquina fuera de los campeonatos» — gate en `megaEnabled()` (champs.active).
- **Voz nativa castellana + audio traducido al inglés**: la voz tongtong
  pronunciaba español «horrible»; davefx es la voz ES del juego entero. En
  inglés, el banco lessac con la frase traducida.
- **Spin ×2 solo generado, con topes**: amplifica lo que hace el jugador sin
  garantizar fallos del rival (Coulomb cap + tope 2×spinMax + Magnus limitado).
- **Predicción IA sin marca**: el rival sigue jugando con la física canónica —
  el efecto es ventaja real, no error del simulex.
