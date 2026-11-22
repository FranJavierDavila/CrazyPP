# AUDITORÍA DE FÍSICAS — «Guardianes de la Ecosfera» (CRAZY PING PONG)

**Task ID:** 7 · **Fecha:** 2026-11-12 · **Auditor:** agente de auditoría de físicas (solo lectura)
**Estado:** BORRADOR (no revisado por el coordinador; no se modificó ningún fichero del juego, no se ejecutó el juego, no hay commits)

## Alcance y método

Ficheros leídos (tamaños reales medidos con `stat`):

| Fichero | Bytes | Profundidad |
|---|---|---|
| `src/game/core/c02_cfg_escena.js` | 48.109 | DIMS completo (líneas 1–175) + grep de constantes |
| `src/game/core/c04_fisica_ccd.js` | 18.474 | ÍNTEGRO (373 líneas) |
| `src/game/core/c05_colisiones_ia_golpeo.js` | 56.247 | ÍNTEGRO (1.189 líneas, en 5 pasadas) |
| `src/game/core/c12_pingponggame.js` | 1.959.910 | Parcial por muestreo (~700 líneas de 18.311): bucle `animate`/dt, invocación de `stepPhysics`, `_bolaGuard`, `PerfManager`, `__solverHook` |
| `src/game/core/c09_red_netlink.js` | 113.445 | Parcial: `sendHit`, `onData`, `applyBallStream`, `netLocalHit`, `watchOwnCross`, `observeGhost`, `drainNetwork` |
| `src/game/core/c09b_red_nucleo.js` | 43.625 | Parcial (grep: transporte binario, validación, FSM de bola) |
| `src/game/core/c06_logros_stats_ia_rival.js` | 49.023 | Parcial: uso de `predictStrike` y `computeShotVelocityReal` |
| `scripts/test_fisica.mjs` | 9.353 | Cabecera y escenarios (1–100 de 202) |
| `scripts/fisica_golden.json` | 736 | ÍNTEGRO |

**Método:** solo lectura con Grep (ripgrep) de patrones concretos y Read con offset/limit. NO se ejecutó el juego ni los tests (regla de la auditoría). NO se tocó `game.html` ensamblado. Todas las citas son verificadas con número de línea. Convención de citación: `fichero:línea`.

---

## 1 · INTEGRACIÓN TEMPORAL

**Veredicto: SÓLIDO** (con un matiz de base temporal de la pala, ver abajo)

La bola avanza por subpasos fijos calculados dinámicamente, no por frames:

```js
// c05_colisiones_ia_golpeo.js:710-711
const n = Math.max(1, Math.min(96, Math.ceil(dt / MAX_SUBSTEP_DT)));
const h = dt / n;
```

con `MAX_SUBSTEP_DT = 1/480` (c04_fisica_ccd.js:1). Integración semi-implícita (Euler simpléctico de orden 1) por subpaso:

```js
// c05_colisiones_ia_golpeo.js:720-726
ball.vel.y += DIMS.gravity * h;
applyAerodynamics(ball.vel, ball.spin, h, ball.dragMul, ...);
ball.pos.addScaledVector(ball.vel, h);
```

**dt clamp y frames largos:** el frame XR distingue dos relojes — la bola integra tiempo REAL capado a 1/12 s (83 ms) y el resto (UI/red) a 1/30 s:

```js
// c12_pingponggame.js:14841-14843
const _rawDt = this.lastTime < 0 ? 0.016 : Math.max(0.0001, now - this.lastTime);
const dt = Math.min(_rawDt, 1 / 30);
const dtFis = Math.min(_rawDt, 1 / 12);
```

Frame de 30 ms → `n = ceil(0,03·480) = 15` subpasos de h≈2 ms. Frame de 83 ms (peor caso) → 40 subpasos, «dentro del tope 96» (comentario c12:14838). Tras una pausa no hay pico de dt: `this.lastTime = now` se actualiza todos los frames (c12:14858), congelada o no.

**Pausas:** la física no corre si la sesión no está activa (`presenting || net.online || __pp2DPlay`, c12:14867), ni durante congelaciones (`frozen = freezeT > 0`, c12:14874-14875; `holdLock`, `netFrozen`, `inHall`, prueba de campeonato activa — c12:15443-15444). La dilatación cinemática `_dilF` (r62, lenta hasta 0,34×) solo multiplica el dt de la bola, nunca IA/árbitro/HUD (c12:14851-14857, 15505).

**Anti-túnel continuo:** (a) CCD contra pala (ítem 2); (b) para geometría estática, cruces de plano por subpaso con `prevY`/`prevZ` guardados antes de integrar (c05:716-718, usados en collideTable:435 y collideNet:527-529); (c) tras un golpe de pala, mesa/red/suelo se APLAZAN al subpaso siguiente para evitar eventos dobles (`if (padHit) continue;` — c05:731, 746 y comentario v2.29 en c05:728-730); (d) rescate final anti-mundo (c05:607-616, ítem 5).

**Matiz (hallazgo real):** la pala se muestrea con el dt capado a 1/30, no con `dtFis`:

```js
// c12_pingponggame.js:15078
updatePaddleSim(ps, grip.position, tmpMountQ, now, dt);
```

`updatePaddleSim` divide el desplazamiento real del frame por ese dt (c04:231). En un frame de 50 ms el movimiento de 50 ms se divide por 0,0333 → velocidad de pala sobreestimada ×1,5 (luego clampeada por `paddleVelClamp` 16, c02:34), y eso alimenta directamente el impulso del golpe (c05:192, 202). Impacto pequeño (solo en frames de bajón, techo por clamp), pero es una inconsistencia de bases temporales entre bola (tiempo real) y pala (tiempo capado).

**Recomendación (R1):** pasar `dtFis` a `updatePaddleSim` (c12:15078) o normalizar dentro de c04 usando timestamps reales. Cambio de una línea, pero toca el golden de `paddleSim.swing120` — requiere refresco intencional del golden.

---

## 2 · CCD BOLA↔PALA (SDF)

**Veredicto: SÓLIDO**

Barrido conservador por SDF 1-Lipschitz en espacio local de la pala. El avance `t += dist/len` nunca puede saltarse la superficie porque `dist` es cota inferior de la distancia real:

```js
// c04_fisica_ccd.js:111-117
for (let i = 0; i < maxIter; i++) {
  dist = sdfBlade(ax + dx * t, ay + dy * t, az + dz * t, R, hT) - ballR;
  if (dist <= eps) return t;
  t += dist / len;                 // avance conservador: nunca se salta la superficie
  if (t > 1) return -1;
}
return dist < CCD_TUNE.glaze ? t : -1;   // casi rasante tras maxIter: contacto
```

Parámetros (c04:54-64): `eps: 1e-5` (0,01 mm), `maxIter: 32`, `glaze: 2e-4` (0,2 mm), `faceK: 0.7`. Contacto ya-penetrando → `t = 0` (c04:108). Segmento degenerado (`len < 1e-9`) → -1 (c04:109). El mango es una cápsula vertical y0=-0,21 / y1=-0,07 / r=0,05 con el mismo barrido (c04:56-58, 121-135).

**Clasificación cara/canto (faceK):** si el impacto llega a la cara (`|lhz| ≥ hT + rB·faceK`) se usa normal de cara firmada por posición; si no, gradiente analítico del SDF (canto exacto / esquina redondeada):

```js
// c05_colisiones_ia_golpeo.js:112-121
if (onHandle || Math.abs(lhz) >= hT + rB * CCD_TUNE.faceK) {
  tmpN.copy(ipNormal);
  if (lhz < 0) tmpN.negate();
} else {
  bladeNormalLocal(lx, dyy, lhz, Rb, hT, ccdNL); ...
}
```

`bladeNormalLocal` es el gradiente analítico exacto del cilindro (c04:139-151). Golpe descartado si las superficies ya se separan («spec F», c05:123: `if (vRelN >= 0) return false;`).

**Dónde se invoca:** en `stepPhysics` una vez por subpaso con las fracciones del subpaso como extremos de la pala — `collidePaddleSweep(ball, pad, i / n, (i + 1) / n, events)` (c05:744) — interpolando linealmente (nlerp) posición y base orientada entre la pose del frame anterior y la actual (c05:27-34, comentario «spec C/D» c05:16-22). Para la bola remota v1 sin integración local: `testPaddleContact` barre el frame completo (0→1) (c05:763-773, invocado desde c12:15490).

**¿Qué pasa si el sweep falla?** No existe un «fallback discreto» porque no hace falta: (a) la penetración preexistente se captura con `t=0` (c04:108); (b) si el barrido no encuentra contacto, la bola simplemente sigue integrando y las colisiones de mesa/red/suelo se evalúan ese mismo subpaso. El caso límite (golpe muy justo en el vuelo del saque) se cubre con la GRACE del saque (`ball.__serveGrace`, c05:76-86), no con un detector paralelo. `collidePaddle` (c05:1-3) es solo un envoltorio de compatibilidad (`kA = kB`).

**Matiz:** el barrido usa DOS poses interpoladas linealmente, no la hélice exacta de la rotación de la pala (nlerp entre bases, c05:27-34): documentado como decisión (v2.29, c04:23-25) y con poses reales del frame en geometría (sin suavizado, c04:49-51). El glaze de 0,2 mm puede validar un contacto rasante tras agotar maxIter — conservador en la dirección correcta (falso positivo solo a <0,2 mm).

---

## 3 · BOTE EN MESA CON GIRO

**Veredicto: SÓLIDO** — **no hay doble contabilidad**; las dos rutas son excluyentes.

Ruta activa (slip-coupled, FIS1) seleccionada por el interruptor maestro:

```js
// c05_colisiones_ia_golpeo.js:451-459
if (DIMS.physicsRealism >= 0.5) {
  bounceOnTable(vel, spin, impact);            // física real (config actual: physicsRealism: 1, c02:65)
} else {
  vel.y = impact * DIMS.tableRestitution;
  vel.x *= DIMS.tableFriction;  vel.z *= DIMS.tableFriction;
  applyBounceSpin(vel, spin);                  // ruta legada
}
```

Física del bote (c04:291-318): `vel.y = impact·tableRestitution` (0,88, c02:14); velocidad superficial de contacto `ux = vx + r·ωz·cm, uz = vz − r·ωx·cm` (c04:301-302); **agarre dependiente del impacto** interpolando `bounceGripMin 0,22 → bounceGripMax 0,60` saturando en `gripImpactRef = 4,5 m/s` (c04:303-304; c02:154-155; BOTE_TUNE c04:75-82); **tope de Coulomb** `|Δv| ≤ g·(1+e)·impact` (c04:310-311); **inercia de cascarón 2/5** (`cascaronInercia: 0.4`, c04:78) en el impulso tangencial `dvx = −ux·0,4·g` (c04:307-308); **acoplo 3/2** `Δωx = −(3/2r)·Δvz, Δωz = +(3/2r)·Δvx` (`cascaronAcoplo: 1.5`, c04:79, 314-317).

**¿Cuándo se usa cada ruta?** `bounceOnTable` en las tres físicas (real, IA, saque) cuando `physicsRealism >= 0.5`; `applyBounceSpin` (legada, con `DIMS.bounceSpinKick = 0,012`, c02:57) solo en las ramas legadas de `collideTable` (c05:458), `predictStrike` (c05:812) y `simulateServePath` (c05:1035). Con la configuración actual (c02:65 `physicsRealism: 1`) la legada está **dormida** y `bounceSpinKick` no contribuye: verificado por grep — `bounceSpinKick` solo aparece en c02:57 y c04:274-275. **No hay doble contabilidad del efecto** (ni bounceSpinKick + acoplo, ni acoplo aplicado dos veces); el riesgo solo existiría si alguien mezclara rutas, y el gate compartido lo impide.

**Matiz:** sobre el bote físico se superponen las «firmas tipificadas» del Súper Efecto (top/back/side), SOLO en `collideTable` real y SOLO en la mitad del rival (c05:469-488): deliberadamente ausentes en IA/solvers — la IA no predice la bola marcada (ver ítem 7). El multiplicador `coupleMul`/`efectoBoteMul` de la r51 fue RETIRADO en r57 (c05:438-446; c02:83-87), con lo que el bote físico puro es idéntico para jugador e IA salvo firma tipificada.

---

## 4 · AERODINÁMICA

**Veredicto: OK CON MATICES**

Una sola función compartida por física real y TODOS los simuladores (contrato declarado en c04:193-194):

```js
// c04_fisica_ccd.js:204-211
if (sp > 1e-6) {
  vel.multiplyScalar(Math.max(0, 1 - DIMS.airDragK * dm * sp * h));
}
if (spin.lengthSq() > 1e-4) {
  tmpM.crossVectors(spin, vel).multiplyScalar(DIMS.magnus * mm * h);
  vel.add(tmpM);
  spin.multiplyScalar(Math.max(0, 1 - DIMS.spinDecayAir * h));
}
```

- **Drag cuadrático:** Euler del modelo `dv/dt = −k·|v|·v` con `airDragK = 0,142` (c02:11-13; el factor `sp·h·k` mantiene el paso explícito estable: a 18 m/s y h=1/480, factor 0,9947). `Math.max(0, …)` evita inversión de velocidad con h grande. Coherente.
- **Magnus:** `a = Cm·(ω×v)` con `magnus = 0,0035` (c02:56) — constante empírica adimensionalizada para ω en rad/s; unidades de h en segundos en todos los callers (subpaso real h=dt/n en c05:721; predictores h=1/240 en c05:786/887/1009). Coherente.
- **spinDecayAir:** decaimiento exponencial `ω *= 1−0,3·h` (τ≈3,3 s, c02:60). Solo se aplica si hay giro (dentro del `if`), correcto.
- **dragMul / magnusMul (poderes):** `dragMul` viaja en `ball.dragMul` (bola-bomba, 0,30 según comentario c04:196-198) y `magnusMul` solo con bola marcada `ball.ppEfecto` → `DIMS.efectoMagnusMul = 2,2` (c05:721-722; c02:89). Sin poderes ambos son 1 → física idéntica (golden, c04:199-200).
- **Misma función en IA/predicción:** `stepPhysics` (c05:721), `predictStrike` (c05:798), `simulateBounceUntilTable` (c05:902) y `simulateServePath` (c05:1020) llaman exactamente `applyAerodynamics`. Sin réplicas a mano.

**Matices:**
1. **Los predictores no amplifican el Magnus de la bola marcada:** `predictStrike`/`simulateServePath` llaman sin `magnusMul` (predicen Magnus ×1) mientras la bola real vuela con ×2,2 (c05:721-722 vs c05:798/1020). La curva de la bola con Súper Efecto la subestima la IA en su punto de golpeo; está compensado por dificultad (efectoRivalErrMul ×2, c02:107) y el comentario de c04:199-200 indica que es deliberado («los simuladores no la marcan → 1»), pero conviene documentarlo como comportamiento oficial.
2. **Paso distinto:** predictores a h=1/240 vs física real hasta 1/480 — Euler con paso 2× mayor; con drag fuerte la desviación es pequeña pero no cero (el golden no cubre predictStrike, ver ítem 8/recomendación R2).

---

## 5 · COLISIONES CON ENTORNO

**Veredicto: OK CON MATICES**

Todo se resuelve en c05, por subpaso, en el orden pala → mesa → red → mundo (c05:750-756).

**Red** (`netTopY = 0,9125`, c02:6) — cruce del plano central con banda vertical:

```js
// c05_colisiones_ia_golpeo.js:527-533
const from = prevZ - nz;  const to = pos.z - nz;
if (from > 0 === to > 0) return;
if (Math.abs(pos.x) > DIMS.netHalfWidth) return;
if (pos.y <= DIMS.tableTopY || pos.y >= DIMS.netTopY + DIMS.ballRadius) return;
```

Dos regímenes: golpe a la malla (rebote amortiguado `vel.z *= -0,18`) y roce de cinta (`vel.z *= 0,35…`) — c05:533-545. Cruce de plano ⇒ sin túnel a cualquier velocidad.

**Mesa** (c05:424-522): bote superior con `prevY ≥ topR > pos.y` + márgenes laterales; bote en el vientre por debajo (c05:493-498, e=0,45); resolución de la losa/canto por mínima penetración con regla ITTF (canto = bote válido, evento con `edge:true`, c05:501-521).

**Suelo y paredes** (c05:548-617): suelo con **zona muerta** (impacto < 0,3 m/s la bola se posa sin evento ni sonido, c05:565-569 — mata el «bote infinito»); muros/techo de sala con rebote 0,4 (c05:582-605; `roomHalfX 3,05, roomBackZ 2,35, roomFrontZ −5,55, roomHeight 2,85`, c02:162-165; desactivables por prueba `ball.ignoreWalls`). **Rescate anti-atrapada:** |x|>30 ∨ |z|>30 ∨ y<−5 ∨ NaN → teleport a (0, 0,5, tableCenterZ) sin evento (c05:607-616).

**Bola guard** (`_bolaGuard`, llamada cada frame en c12:15754): c12:9916-10021 mantiene la bola en la mano en saque, garantiza visibilidad en el toss del rival (caduca a 2,5 s, c12:9961-9963) y en rally valida mundo finito + acotado:

```js
// c12_pingponggame.js:10005-10013
const enMundo = isFinite(p.x) && isFinite(p.y) && isFinite(p.z) &&
  p.y > -2 && p.y < 7 && Math.abs(p.x) < 7 && Math.abs(p.z - D.tableCenterZ) < 7.5;
if (!enMundo) { p.set(0, D.tableTopY + 0.5, ...); this.ball.vel.set(0,0,0); ... }
```

Telemetría `bola_guard` con clave de causa, rate-limitada a 1/5 s (c12:10023-10028).

**Doble bote en el mismo frame:** mitigado estructuralmente — subpasos de ~2 ms y aplazamiento de mesa/red tras golpe de pala (c05:746). Dos botes en el MISMO subpaso serían necesarios para duplicar un evento y el vuelo real entre botes es ~0,2 s ≈ 100 subpasos: riesgo residual despreciable.

**Matiz (asimetría real vs predicción):** el bote real acepta impactos hasta `tableHalfWidth + ballRadius·0,5` en X (c05:432), mientras predictStrike/simulateServePath usan `tableHalfWidth` exacto (c05:803, c05:1026): botes «de pelo» reales (≈5 mm fuera del borde) que la IA cree que no botaron. Menor, pero es una discrepancia deliberada no documentada.

---

## 6 · DETERMINISMO Y RED

**Veredicto: OK CON MATICES** (el diseño NO es lockstep-determinista; es autoridad-por-mitad con estado completo en los traspasos — divergencia flotante tolerada por diseño)

**v1 (JSON 30 Hz):** el golpe viaja con estado completo y el spin viaja en `s:[x,y,z]`:

```js
// c09_red_netlink.js:522-527
this.send({
  k: 'h', sv: isServe ? 1 : 0,
  p: NetLink.posToNet(g.ball.pos),
  v: NetLink.rawPos(g.ball.vel),
  s: [+g.ball.spin.x.toFixed(2), +g.ball.spin.y.toFixed(2), +g.ball.spin.z.toFixed(2)],
});
```

El receptor NO re-simula: aplica p/v/s directamente (c09:584-596 invitado; `drainNetwork` c09:804-806 anfitrión) o hace cinemática exacta del stream `p += v·age + ½g·age²` con espejado de spin (c09:762-770). Cuantización del spin a 0,01 rad/s (`toFixed(2)`, c09:526) — irrelevante al no haber re-simulación.

**v2 (binario, r79):** la bola rival se simula LOCALMENTE con la física real («fantasma», c12:15460-15477: `stepPhysics` sobre la bola con la FSM de autoridad; `applyBallStream` devuelve `false` con v2 activo, c09:753-754). Lo que se sincroniza: HIT (golpe propio «sagrado», p/v/s 3×f32), BALL_HANDOFF al cruzar la red con el estado EXACTO del subpaso (hook `_xNet` por subpaso, c12:15507-15511; `watchOwnCross` c09:1807-1824), TOSS del saque (c09:1795-1804), poses de pala (p+cuaternión, c09:560-566), eventos de bote espejados (c09:505-508, 777-791), estado de partido (applySync) y claims/acks de punto. Layout binario documentado:

```js
// c09b_red_nucleo.js:169-171
*   HIT(0x01)     kind u8 · shot u16 · tHit u32 · pos/vel/spin 3×f32
*   HANDOFF(0x02) shot u16 · tCross u32 · pos/vel/spin 3×f32
*   POSE(0x03) … F flags: bit0 lleva pose · bit1 lleva eventos.
```

**Riesgo de divergencia flotante:** existe MIENTRAS el fantasma vuela: cada cliente integra con su propio dt de frame (frecuencias de render distintas → micro-divergencia acumulativa en la posición del fantasma). El diseño la contiene en tres capas: (1) solo la sim del dueño de la mitad decide botes/puntos (FSM autoridad por mitad, c12:15460-15471); (2) cada HIT/HANDOFF sobrescribe el estado completo del fantasma (c09:1782-1785, 1815-1817); (3) autoridad provisional a los 300 ms si el traspaso se pierde (`observeGhost`/`maybeProvisional`, c09:1826-1840) y `RESYNC_STATE` del anfitrión como árbitro final (c09b:827-828). Validación anti-trampa con techos de velocidad y giro (`MAX_BALL_SPEED`/`MAX_SPIN`, c09b:686-688).

**Matiz:** la probabilidad de desacuerdo visual (fantasma botando en punto ligeramente distinto al que el dueño simula) es real entre handoffs; el golpe del jugador sobre el fantasma es local y sagrado (c12:15466-15471), con validación §12 en el rival — el sistema está pensado para eso. No hay rollbacks ni predicción con corrección suave del fantasma basada en el estado remoto (solo traspasos): aceptable para este género, pero conviene saberlo.

---

## 7 · IA Y PREDICCIÓN

**Veredicto: OK CON MATICES** (comparten EXACTAMENTE las ecuaciones; los matices son de paso de integración y márgenes, no réplicas a mano)

`predictStrike` replica el mismo pipeline: gravedad → `applyAerodynamics` → integrar → bote con el MISMO gate:

```js
// c05_colisiones_ia_golpeo.js:797-813
vel.y += DIMS.gravity * h;
applyAerodynamics(vel, spin, h);
pos.addScaledVector(vel, h);
...
if (DIMS.physicsRealism >= 0.5) {
  bounceOnTable(vel, spin, -vel.y);      // la IA predice con la MISMA física nueva
} else { ... applyBounceSpin(vel, spin); }
```

Ídem `simulateServePath` (c05:1019-1036) y el solver de la casa `computeShotVelocityReal` (vía `simulateBounceUntilTable`, c05:884-930 — mismo gate, mismo `applyAerodynamics`). **No hay ninguna réplica a mano de bounceOnTable o applyAerodynamics** (verificado por grep: las únicas llamadas están en c05:453/458, 807/812, 902, 1020/1030/1035 y c05:721).

**Consumo:** la IA llama `predictStrike` cada `predictInterval` (60–160 ms según nivel, c02:172-175) desde c06:632; `computeShotVelocityReal` en cada golpe de IA (c06:936) y en el Súper Imán (c05:404); `findServeVelocity` para saques (c12:1519, 16570) y la asistencia acotada (c05:1141-1167). Los 9 casos del saque y la CCD están expuestos para QA headless vía `window.__solverHook` (c12:16020-16029).

**Matices (drift numérico y de modelo, no de ecuaciones):**
1. **Paso 1/240 vs 1/480 real** (c05:786/887/1009 vs c04:1): el integrador es el mismo pero con paso 2× — desviación pequeña y de signo sistemático (los predictores «ven» algo menos de drag).
2. **Modelo de red distinto:** la física real amortigua la bola en la red (c05:533-545); los predictores la tratan como condición de fallo (devuelven `best`/`ok:false`, c05:819-820, 1050-1052). Aceptable (la IA no debe planificar tiros a la red).
3. **Margen de mesa** (c05:803/1026 exacto vs c05:432 con +r/2): ítem 5.
4. **Poderes invisibles a la predicción:** dragMul/magnusMul/firmas de bote no llegan a los simuladores (por diseño, ítems 3-4).
5. `predictStrike` clona pos/vel/spin por llamada y clona el candidato `best` en cada mejora dentro del bucle (c05:783-785, 829) — asignaciones solo en la ruta de IA (10-16 Hz), no en la caliente de 480 Hz.

---

## 8 · RENDIMIENTO

**Veredicto: OK CON MATICES**

**Cero asignaciones en la ruta caliente de c04:** scratches preasignados a nivel de módulo (tmpPrev, padPos, relVel, tmpN… c04:6-31) y scratches propios de la CCD (ccdPosA/B, ccdNrmA/B, ccdC0/C1…, c04:153-160); los barridos están especializados sin closures («CERO asignaciones», c04:103) y el bucle de subpasos de c05 no aloca. El solver real usa scratches propios `_svPos/_svVel/_svSpin/_svRes` (c05:880-883) y el transporte del apoyo `_rs*` (c05:639-643).

**Coste del CCD:** `maxIter = 32` (c04:60) por barrido; por subpaso y pala: 1 barrido de hoja y, si falla, 1 de mango (c05:64-70). Peor caso a 90 Hz con frames de 30 ms (15 subpasos): 15×(32+32) ≈ 960 evaluaciones de SDF por pala por frame, ~10-15 flops cada una → despreciable frente al presupuesto de 11,1 ms (90 Hz). El SDF del disco es de fórmula cerrada (c04:88-93).

**Asignaciones residuales (matiz):** (a) `updatePaddleSim` hace `velBuf.push({t,x,y,z})` + `shift` por pala y frame (c04:235, 237) — GC churn pequeño y constante; (b) cada evento de colisión clona posición (`pos.clone()` en c05:489/520/539/544/575/586/592/598/603 y c05:419) — solo en impactos; (c) predicción/solver aloca en su ruta (ítem 7.5); (d) `drainNetwork` crea un Vector3 por evento remoto (c09:784). Ninguna está en el bucle de 480 Hz; el claim estricto «cero por frame» es cierto SOLO para c04/c05-ruta-caliente, no para el juego completo.

**Budget 90 Hz Quest y PERF governor:** nunca recorta física — solo tres palancas gráficas, con sonda de calibración de rondas de 2,8 s (fovea +0,10 → rate 60 → escala −0,15, suelo 60 Hz estable, c12:17555-17591) y gobernador continuo con histéresis:

```js
// c12_pingponggame.js:17631-17633, 17641-17649
const bajando = avg < 56 || (avg < 60 && min < 48);
if (bajando && this._coolDown <= 0) { if (!rally || avg < 50) this._stepDown(); }
// _stepDown: fovea → tasa → escala (próxima sesión)
```

Perfiles por GPU (Quest 3: scale 1,40/fovea 0,35/90 Hz; Quest 2: 1,05/0,65/72, c12:17409-17413), techo FFR del dueño respetado (máx 0,65, c12:17475-17483), cambios de tasa aplazados fuera del rally (c12:17630-17633). La física integra tiempo real (ítem 1), así que una caída a 72/60 Hz no altera trayectorias — solo granularidad de subpasos.

**Golden:** `test_fisica.mjs` ejecuta la FUENTE REAL de c04+c02 en Node y compara SHA-256 por escenario (test_fisica.mjs:2-9, 24-28). Los 11 hashes: primitivas SDF/sweeps/normales, `paddleSim.swing120`, `aero.topspin480`, `aero.bomba480.dragMul`, `bounceOnTable.casos`, `applyBounceSpin.caso`, `paddlePerkFor.clasica`, `tuning.constantes` (fisica_golden.json:4-16). **No ejecutado en esta auditoría** (mandato read-only); coordinador reporta 0 desviaciones en la última ejecución.

---

## Balance general

| # | Ítem | Veredicto |
|---|---|---|
| 1 | Integración temporal (substeps 480 Hz, dt clamp, pausas) | SÓLIDO |
| 2 | CCD bola↔pala (SDF, faceK, mango, fallback) | SÓLIDO |
| 3 | Bote en mesa con giro (slip-coupled; doble contabilidad: NO) | SÓLIDO |
| 4 | Aerodinámica (drag/Magnus/decay, misma función en IA) | OK CON MATICES |
| 5 | Colisiones de entorno (red/mesa/suelo/muros, bola guard) | OK CON MATICES |
| 6 | Determinismo y red (v1 estado completo / v2 autoridad por mitad) | OK CON MATICES |
| 7 | IA y predicción (mismas ecuaciones; drift de paso y márgenes) | OK CON MATICES |
| 8 | Rendimiento (c04 cero-alloc real; governor no toca física) | OK CON MATICES |

Ningún ítem en RIESGO. Los tres «SÓLIDO» son el núcleo de contacto (integración, CCD, bote) y están doblemente blindados: golden de hashes + gates de rollback (`physicsRealism`, `paddlePerks`).

### Top-3 recomendaciones priorizadas

1. **R1 — Unificar la base temporal de la pala con la de la bola** (Hallazgo ítem 1): `updatePaddleSim(ps, …, dt)` usa el dt capado a 1/30 (c12:15078, 14842) mientras la bola integra `dtFis` hasta 1/12 (c12:14843). En frames >33 ms la velocidad de pala se sobreestima hasta el clamp y eso infla el impulso del golpe justo en los bajones de FPS. Fix de una línea + refresco intencional del golden (`paddleSim.swing120`).
2. **R2 — Cerrar la brecha física-real vs predictores y goldenizar c05:** alinear el margen de bote (c05:432 `+ballRadius·0,5` vs c05:803/1026 exacto) y valorar unificar el paso (1/240 vs 1/480); añadir al golden escenarios de `stepPhysics`/`collidePaddleSweep`/`predictStrike` (hoy el golden cubre solo primitivas de c04 — fisica_golden.json:4-16 —, la capa de integración completa queda sin red determinista; `__solverHook` ya expone las piezas, c12:16020-16029).
3. **R3 — Documentar (o corregir) la predicción de la bola marcada:** `predictStrike` predice Magnus ×1 mientras la bola con Súper Efecto vuela con ×2,2 (c05:798 vs c05:721-722). Si la subestimación es parte del balance del poder, dejarlo por escrito en DIMS/comentario; si no, propagar el flag a la predicción.

### Qué NO se auditó (declaración expresa)

- `game.html` ensamblado (11,5 MB): no abierto ni grepeado (regla del encargo); esta auditoría valida la fuente modular, no el artefacto de build.
- Ejecución: NO se ejecutó el juego, `test_fisica.mjs`, `test_fisica_perf.mjs` ni ningún benchmark (mandato); los datos del golden («0 desviaciones») se toman del coordinador.
- Módulos fuera del alcance físico: c01 (modelos), c03 (audio), c07/c08/c10/c11/c13 (escena/HUD/menú/champs/UI), c09c (red social), c11 (champloader). De c12 solo se leyeron las secciones del bucle de física, bola guard y PerfManager (~4 % de sus 18.311 líneas): el árbitro (rules), el arkanoid (`champs.testStep`), los poderes en detalle y el guardado/telemetría no se auditaron.
- De c09b solo el transporte/validación por grep; el reloj NTP (`_clock`), el jitter buffer del avatar y el reconciliador de claims no se leyeron línea a línea.
- Servicios externos (worker TURN, telemetría) y scripting de assets de `scripts/`.
