# r99 · PLAN DE BRAZOS NATURALES — rig vr_arm.glb medido + poses de ping pong

**Proyecto:** Crazy Ping Pong · **Rol:** ingeniería de rigging · **Fecha:** 2026-11-20
**Base factual:** `scripts/plan_medir_rig_r99.mjs` → `scripts/plan_medidas_rig_r99.json` (51 KB, ambos brazos).
**Regla de oro cumplida:** cada número de este plan es una MEDICIÓN del GLB (apéndice A) o una
referencia del dueño (R1–R5), o está marcado **[HIPÓTESIS]** con su aguja de validación.
**No se ha tocado** `src/game/` ni `scripts/arnes_brazos_*.mjs`.

---

## 0 · Resumen ejecutivo — qué cambió respecto a lo que creíamos

| # | Hallazgo | Evidencia |
|---|---|---|
| H1 | **`hand_023` es la mano IZQUIERDA del personaje** y `hand(mirrored)_04` la DERECHA. La CPU (s=−1) agarra la pala con el brazo de x<0 → **B** (espejado). El enunciado "mano derecha = hand_023" era incorrecto; no cambia el driver (elige por `Srest.x·s>0`) pero sí los nombres en los comentarios. | bind: manos 10 cm al frente del pecho (modelo mira a +z); palma de hand_023 mira hacia el cuerpo con brazo colgado; `U_arm_021` x=+7 cm, espejado x=−7 |
| H2 | **La palma es −Z local de la mano en AMBOS brazos** (dot(across×along, −Z)=+0.9995 en A y −0.9995 en B: en B el producto cruzado apunta al dorso porque el eje pulgar→meñique invierte el sentido al espejar). La convención r95 es correcta. | apéndice A.2 |
| H3 | **El eje de flexión de los 4 dedos es ≈ +Y del marco padre** (dot con el eje del driver r95: 0.90–0.996, desvío ≤0.35 rad) — el curl r95 de los dedos es correcto. | apéndice A.4 |
| H4 | **El eje de flexión del PULGAR NO es +Y**: f1 = (0.157, 0.059, −0.986) ≈ −Z padre y f2 = (0, 0.226, −0.974). El driver r95 (curl +Y en el pulgar) está **86° fuera** (dot 0.058) → el pulgar gira de lado en vez de flexionar. | apéndice A.4 |
| H5 | **BUG: el meñique nunca se curlea.** `pinky__031` es el hijo 2 de `hand__027` (2 hijos: ring + pinky); el bucle `children[0]` de `_cargarArmasGLB` sólo baja por ring → el meñique queda en bind (estirado) en el agarre. | huesos: `hand__027` hijos=2, `pinky__031` padre=`hand__027` |
| H6 | **BUG: las raíces de los dedos (thumb__024, mid__034, index__037) no se curlean** (el bucle sólo rota `children[0]` y siguientes) y el meñique queda entero en bind → el agarre r95 mide **yemas a 2.4–3.5 cm GLB del mango** (4.4–7.9 cm adulto); con las poses r99 quedan a **0.81–0.91 cm GLB (1.8–2.1 cm adulto)**. | simulación `driver_r95_sim` vs `POSE_A_verif` en el JSON |
| H7 | **El mango debe cruzar la mano en la línea de los nudillos (crease), no en la muñeca**: centro de crease (4 nudillos, sin pulgar) = **(0.0868, ±0.024, −0.0022) m** del hueso mano en marco mano; el centroide "palma" con pulgar (0.0744, ±0.0152) arrastra el punto hacia el pulgar y deja el mango 3.4 cm GLB por detrás de los dedos → dedos que no envuelven. | apéndice A.6 |
| H8 | El bind trae **flexiones horneadas suaves** (dedos 0.08–0.49 rad, pulgar raíz 1.748 rad = oposición horneada) — coherente con R1 «manos abiertas, dedos estirados y ligeramente abiertos». Todas las poses r99 son **relativas al bind** (forma `q⊗bindQ`, igual que r95). | apéndice A.4 |

---

## 1 · Rig medido (lo esencial; completo en apéndice A)

- 42 huesos (+6 grupos). Cadena de cada dedo = **3 huesos** (raíz/MCP + PIP + DIP).
- Escala adulta del driver: `esc = 0.27 / 12.1985 cm = 0.02213`; antebrazo 0.2671 m; L1+L2 = **0.5371 m**.
- Ejes de la mano en el marco antebrazo: `dirMarcoPropio = (1,0,0)` (el antebrazo extiende su +X propio).
- Mano rel. antebrazo en bind (euler XYZ): A `[0.0536, −0.0141, −0.2267]` · B `[−0.0536, −0.0141, +0.2267]`
  (rollo ±0.227 rad horneado; el comentario r95 «rel. Z ±0,23» confirmado).
- `pulgarY`: A=−1, B=+1 — confirmado por el lado del pulgar en el marco antebrazo:
  b(A) = (0, −0.9907, −0.1358), b(B) = (0, +0.9907, −0.1358).
- Hombros (offsets vs Body_01, adulto): A (+0.1549, +0.0253, −0.0225) · B (−0.1549, +0.0253, −0.0225).

### 1.1 Geometría del agarre (deducida y verificada)

El mango de la pala cruza la palma ∥ a `hand-Y` (= `pulgarY·ejeHoja`), la hoja es el plano
span(`hand-Y`, `hand-Z`) con **normal de cara = ±`hand-X`** (la dirección de los dedos/antebrazo):
con el antebrazo hacia el rival, la cara `+X` (lado dedos/índice) mira al rival y el pulgar
presiona la cara −X («cara trasera») — exactamente la lámina del dueño (R2, R5).
En stance sintético (antebrazo hacia (0,−0.30,0.95), rival +z): cara = (0, −0.301, 0.954)
(0.306 rad de +z = la propia inclinación del antebrazo), ejeHoja a 0.775 rad de +Y
(tilt anatómico del bind; en juego la orientación la manda el plan de la pala — el valor es
informativo, no un defecto).

---

## 2 · Las 4 poses (números por hueso, radianes, RELATIVOS AL BIND)

Formato: `[MCP raíz, PIP, DIP]` por dedo. Ejes: **+Y marco padre** para los 4 dedos
(H3; desvío ≤0.35 rad — el control con ejes medidos da error igual o peor: 0.0014 vs 0.0061,
se queda +Y por compatibilidad con el arnés r95); **pulgar: bind intacto** en todas las poses
(su oposición ya está horneada, 1.748 rad en la raíz; cualquier curl medido lo aleja del mango —
el escaneo eligió bind en A y B). Los ejes medidos del pulgar quedan en el JSON por si una
pose futura necesita presionar (H4).

| Pose | thumb | index | mid | ring | pinky | Uso | Justificación |
|---|---|---|---|---|---|---|---|
| **POSE_REST** | [0,0,0] | [0,0,0] | [0,0,0] | [0,0,0] | [0,0,0] | fuera de juego | R1: bind = manos abiertas |
| **POSE_A agarre** | [0,0,0] | [1.2, 0.4, 0.4] | [1.45, 2.0, 1.3] | [0.5, 1.8, 1.3] | [0.5, 2.0, 1.5] | brazo de la pala (siempre) | R2 + escaneo: yemas a 0.81–0.91 cm GLB de la línea del mango (1.8–2.1 cm adulto); índice tumbado en el borde inferior (tip mano-local (4.70, −0.15, −4.35) cm: cara +X, borde −Z) |
| **POSE_B saque** | [0,0,0] | [0, 0.22, 0.16] | [0.2, 0.14, 0] | [0, 0.4, 0.24] | [0.2, 0.22, 0.16] | mano libre serviendo | R3 + escaneo de cuenco: puntas a **1.17–1.23 cm adulto** sobre el plano de palma (uniforme), pulgar en bind «relajado al lado» (bowl 2.1 cm) |
| **POSE_C balance** | [0.18, 0.12, 0.08] | [0.35, 0.55, 0.65] | [0.35, 0.55, 0.65] | [0.36, 0.57, 0.67] | [0.38, 0.59, 0.69] | mano libre en rally | R4 «semicurva»; muñeca neutra (bind) |

Verificación numérica de POSE_A (marco mano, cm GLB, ambos brazos espejo exacto):
`mid tip (3.10, ±0.31, −0.53) · dist mango 0.806` · `ring (3.57, ±1.57, −0.93) · 0.906` ·
`pinky (3.18, ±2.41, −0.54) · 0.860` · `thumb (4.88, ±4.00, −1.05) · 1.352` (bind, sombra del mango).
Comparativa con el driver r95 actual (misma métrica): mid 3.49 · index 3.39 · ring 2.56 ·
pinky 2.38 (bind, sin curl) · thumb 1.95 → **las poses r99 acercan todas las yemas 2.5–4×**.

### 2.1 Muñeca de POSE_B «palma arriba» (mano libre)

Construcción en mundo (cero ambigüedad de marco), con `_gF` = eje antebrazo (codo→muñeca):

```
Z_mano = −up, ortogonalizado contra _gF      // palma = −Z ⇒ palma arriba
Y_mano = Z_mano × X_mano                      // X_mano = _gF
quat_mano_deseada = makeBasis(X_mano, Y_mano, Z_mano)
```

Equivalente relativo al bind en el marco antebrazo (medido): quat
`(0.8784, −0.1006, −0.0522, −0.4642)`, eje (−0.9918, 0.1135, 0.0589), **ángulo 2.176 rad**,
eulerXYZ `[−2.1694, 0.0017, 0.2271]` con stance de antebrazo (−0.15, −0.05, 0.99)
(codo 90–110°, antebrazo horizontal al centro-frente, R3). Verificación: palma resultante a
**0.43°** de +Y mundo. POSE_C y REST: muñeca neutra = `relBind` intacta (el driver ya la
compone al continuar el antebrazo).

### 2.2 Muñeca del agarre (POSE_A, referencia pala-menos)

Delta relativo al bind en el marco antebrazo — la rotación que deja la hoja ⟂ antebrazo con
cara al rival y pulgar hacia la punta:

- **A:** quat (0.0402, −0.0037, 0.1132, 0.9927) · eje (0.3347, −0.0312, 0.9418) · **0.2411 rad** · euler [0.0808, 0.0017, 0.2271]
- **B:** quat (−0.0402, −0.0037, −0.1132, 0.9927) · eje espejo · mismo ángulo

En juego el quat de la mano del brazo de la pala lo construye el driver desde el plan de la
pala (basis `X=antebrazo ort, Y=pulgarY·ejeHoja, Z=X×Y`, líneas 19909-19946 — se conserva);
este delta es la referencia anatómica y sirve para el momento sin plan (menú/coda).

### 2.3 Interfaz de poses (propuesta exacta, cero allocs por frame)

```js
// r99 · estado en inst (una vez, en _cargarArmasGLB):
inst.posesObj = { rest: 1, agarre: 0, saque: 0, balance: 0 };   // pesos ACTUALES
inst.posesObjT = { rest: 1, agarre: 0, saque: 0, balance: 0 };  // pesos OBJETIVO
inst.setPose = (nombre, peso) => { inst.posesObjT[nombre] = THREE.MathUtils.clamp(peso, 0, 1); };

// r99 · updatePoses(dt) — un funde exponencial por pose (τ ≈ 125 ms), blend escalar:
//   w += (wT − w) · min(1, dt·8)   para las 4;  Σw normalizado a 1
//   curl[dedo][falange] = Σ_p w_p · R99_POSES[p][dedo][falange] + microSway
//   por hueso:  quat.copy(setFromAxisAngle(ejeFlex, curl)).multiply(bindQ)   (forma r95)
// R99_POSES = las 4 tablas del §2 (constantes módulo, medidas del JSON).
```

Los ángulos son escalares → el blend es un lerp escalar sin gimbal lock. La muñeca libre usa
slerp entre la quat de pose activa y la de bind con el mismo peso (temporales `_r99q1/_r99q2`).
El brazo de la pala aplica SIEMPRE POSE_A (la pala está en la mano también fuera de juego);
la mano libre conmuta `rest → saque → balance` según `rules.state`/`aiToss`.

---

## 3 · Brazo izquierdo (libre) — objetivos IK rig-local

DIMS (`c02_cfg_escena.js`): `tableTopY 0.76` · `mesaY = tableTopY+0.02 = 0.78` ·
`tableHalfLength 1.37` · `tableCenterZ −1.6` · borde CPU z = **−2.97** ·
`zCuerpo = centroZ + s·(1.37+0.42) = −3.39` (s=−1) · brazo total 0.5371 m →
anillo de alcance [0.150, 0.5365].

Hombro libre de la CPU (brazo A, +x) ≈ ancla del cuerpo + (0.155, 0.025, −0.023) con el yaw
del tronco ≈ **(x_ai+0.155, 1.355, −3.41)** con yaw 0.

| Momento | Target deseado (rig-local) | Dist. al hombro | Tras clamp de anillo | Codo |
|---|---|---|---|---|
| **Saque, espera** (bola aún no lanzada) | `(x_ai+0.10, mesaY+0.25 = 1.03, −2.67)` — 0.25 m sobre el borde, 0.30 m hacia el centro (petición literal del dueño) | **0.81 m > 0.537** | 0.5365 en la misma dirección ≈ `(x_ai+0.08, 1.13, −2.90)` | pole (−0.5,−1,0) actual; codo doblado por el radio 88 % |
| **Saque, bola en mano** (`!aiToss`) | `bola.pos − (0, 0.045, 0)` (como hoy, línea 19964-19966) | según bola | clamp como hoy | idem |
| **Rally (balance)** | `(x_ai+0.21, 0.98, zCuerpo+s·0.05 = −3.34)` — abajo-lado, pegado al cuerpo | **0.38 ✓** dentro del anillo | sin clamp | pole (−0.5,−1,0) actual ✓ «codo cerca del cuerpo» |

- **Geometría honesta [HIPÓTESIS→medido]:** el punto de saque pedido (0.25 sobre el borde,
  0.30 hacia el centro) está a 0.81 m del hombro — **inalcanzable** para L1+L2 = 0.537.
  El clamp del anillo lo trae a 0.536 en la misma dirección (la mano queda ~0.27 m más cerca
  del hombro que el ideal). Como en el instante real la mano va DEBAJO DE LA BOLA
  (`bola − 0.045`), el defecto sólo se ve en la espera; si molesta, la aguja R-7 (§6)
  valida bajar la espera a `mesaY+0.15`.
- **Nunca cruzar la línea media:** `if (x_target·Math.sign(hombroL.x) < 0.05) x_target = 0.05·Math.sign(hombroL.x);`
  (el hombro libre de la CPU es +x; para s=+1 el espejado cae solo).
- **Palma:** en saque el quat de la mano pasa a la basis palma-arriba (§2.1); en rally, neutra.

---

## 4 · Fluidez — mejoras concretas sin romper la IK

1. **Fundo de poses con τ=125 ms** (`dt·8`, §2.3): los cambios rest↔saque↔balance dejan de
   ser escalones; los curls son escalares, el funde es continuo y barato.
2. **Micro-sway procedural** (espera y rally; **cero en strike**):
   - dedos: `±0.02·sin(t·1.7 + faseDedo) + 0.015·sin(t·2.9 + 1.3·faseDedo)` rad por falange
     (total ≤0.035 rad — respira, no tiembla);
   - muñeca libre: rollo `±0.03·sin(t·0.9)` + pitch `±0.02·sin(t·1.3)` rad alrededor de `_gF`;
   - el cuerpo ya tiene su vaivén de 5 mm (línea 19805) — las manos lo acompañan.
3. **Tope de velocidad angular** en las 6 quats filtradas (`fqU/fqL/fqH` de ambos brazos):
   antes de `filtro.filtrar(qDeseada, dt)`, si `qDeseada.angleTo(filtro.prev) > ω_max·dt`,
   reemplazar por `slerp(prev, qDeseada, ω_max·dt/ángulo)` con
   `ω_max = 14` (strike) / `8` (golpeando) / `5` (reposo) rad/s. Mata los saltos del
   re-solve del piso duro del codo (líneas 19882-19889 y 20002-20003 re-solvean y el quat
   deseado puede saltar en un frame).
4. **Congelar el polo del codo durante strike** (líneas 19876-19879): si `enStrike`, no
   re-evaluar `ladoDeseado` (la histéresis r95 puede voltear el codo a mitad de swing).
5. **Easing de la coda ya existente** (20078-20090): sustituir el lerp lineal por
   `smoothstep` (`w = t·t·(3−2t)`) — mismo coste, salida sin acelerón final.
6. **Cero allocations:** todos los temporales nuevos con prefijo `_r99` junto a los `_g`
   existentes (líneas 21012-21021): `_r99q1, _r99q2, _r99v1, _r99v2, _r99m1`.

---

## 5 · Cambios propuestos en `src/game/core/c12_pingponggame.js`

*(sólo el implementador los aplica; aquí quedan diseñados con líneas exactas)*

### 5.1 `_cargarArmasGLB` — bloque de dedos (líneas 19699-19723) → sistema por nombre

```js
// r99 · DEDOS POR NOMBRE (el bucle children[0] de r95 dejaba el meñique EN
// BIND: pinky__031 es el hijo 2 de hand__027) + RAÍZ incluida + ejes medidos.
const _r99Nombres = ['thumb', 'mid', 'index', 'ring', 'pinky'];
const dedos = [];
for (const capa of capas) {
  const dc = [];
  for (const nombre of _r99Nombres) {
    let raiz = null;
    capa.mano.traverse((o) => {                       // raíz = 1er nodo del prefijo
      if (!raiz && o.name.startsWith(nombre)) raiz = o;
    });
    const fal = [raiz]; let h = raiz;                 // 3 huesos: MCP+PIP+DIP
    while (h.children.length) { h = h.children[0]; fal.push(h); }
    fal.forEach((hueso, iF) => dc.push({ hueso, dedo: nombre, falange: iF,
      bindQ: hueso.quaternion.clone(),
      ejeFlex: (nombre === 'thumb') ? R99_EJE_PULGAR[capa.lado][iF] : _ejeFlex }));
      // R99_EJE_PULGAR = { A: [(0.547,0.837,0), (0.157,0.059,−0.986), (0,0.226,−0.974)],
      //                     B: [(−0.547,0.837,0), (−0.157,0.059,0.986), (0,0.226,0.974)] }  // medido
      // los DEDOS conservan _ejeFlex=(0,1,0) (dot 0.90–0.996 medido, arnés r95 intacto)
  }
  dedos.push(dc);
}
// capturar además (una vez): inst.offCrease = { A: (0.0868,0.024,−0.0022), B: (0.0868,−0.024,−0.0022) }
// (marco mano, m adulto — medido) y R99_POSES (las 4 tablas del §2).
```

### 5.2 `updateAIArmGlb` — anclaje de la pala por la crease (líneas 19947-19956)

```js
// r99 · EL MANGO CRUZA LA MANO EN LA CREASE (nudillos), no en la muñeca:
//   centro = muñeca + handQ·offCrease + ejeHoja·(D_GRIP − dCrease)
//   offCrease = (0.0868, ±0.024, −0.0022) m (medido) · dCrease = 0.04 [HIPÓTESIS]
//   ⇒ ejeHoja·0.0903 en vez de D_GRIP·1.0 desde la muñeca.
_gQhand.copy(bp.mano.getWorldQuaternion(_r99qTmp));   // ya actualizada (19944-19946)
_gCentro99.copy(inst.offCrease[bp.lado]).applyQuaternion(_gQhand).add(_gA)
  .addScaledVector(_gD, 0.0903);
this.aiPaddleMesh.position.copy(_gCentro99);
this.clampPaddlePose(this.aiPaddleMesh.position, this.aiPaddleMesh.quaternion, false);
```

*(El objetivo del IK del brazo de la pala en 19838-19839 pasa a ser coherente con el mismo
offset: `_gE = centroDeseado − _gD·0.0903 − handX·0.0868`; el clamp de anillo 19844-19848
queda intacto y ahora sobra alcance porque la muñeca va 8.7 cm más atrás del centro.)*

### 5.3 `updateAIArmGlb` — mano izquierda (líneas 20019-20028) → poses + palma arriba

```js
// r99 · MUÑECA LIBRE POR POSE (adiós al rollo fijo 0.3·s de r95):
if (serviendo) {
  // basis palma-arriba en MUNDO (§2.1): Z=−up ort. al antebrazo, X=antebrazo, Y=Z×X
  _gZ99.copy(_gUp).negate();
  _gZ99.addScaledVector(_gF, -_gZ99.dot(_gF)).normalize();   // _gF = eje antebrazo
  _gY99.crossVectors(_gZ99, _gF).normalize();
  _gMx99.makeBasis(_gF, _gY99, _gZ99);
  _gQb.setFromRotationMatrix(_gMx99);                        // quat MUNDO deseada
} else {
  bl.mano.parent.getWorldQuaternion(_gQd);                   // continuación del antebrazo
  _gQb.copy(_gQd).multiply(bl.relBind);                      // muñeca neutra (bind)
}
// funde por peso de pose + micro-sway de §4.2 + filtro One Euro fqH (igual que hoy):
_gQbAlvo = _r99SlerpPose(bl, _gQb, dt);
bl.fqH.filtrar(_gQbAlvo, dt);
// ... (resto de líneas 20025-20028 idéntico: premultiply _gRigQ, local desde el padre)
```

El target del brazo libre (líneas 19957-19959) pasa a los valores del §3:
espera de saque `(x_ai+0.10, mesaY+0.25, borde+0.30·haciaCentro)`, rally
`(x_ai+0.21, 0.98, zCuerpo+s·0.05)`, con el clamp de línea media nuevo.

### 5.4 Aplicación de curls por pose (nuevo bloque tras la muñeca de cada brazo)

```js
// r99 · CURL DE DEDOS POR POSE (sustituye al curl único de la carga; rel. al bind):
//   blend = Σ_p w_p·POSE[p][dedo][falange] + microSway (espera/rally, §4.2)
//   hueso.quaternion.copy(setFromAxisAngle(ejeFlex, blend)).multiply(bindQ)
//   ejeFlex: (0,1,0) dedos · ejes medidos del pulgar (§5.1) · cero allocs (sólo copy)
```

### 5.5 Velocidad angular + polo congelado (líneas 19872-19894, 19876-19879, 19998-19999)

Como §4.3 y §4.4: wrapper `_r99TopeQ(filtro, qDeseada, dt, wMax)` antes de cada `filtrar`
(6 llamadas: 19897, 19905, 19942, 20007, 20015, 20024) y `if (!enStrike)` rodeando la
re-evaluación del polo.

---

## 6 · Plan de pruebas

### 6.1 Arnés numérico NUEVO `scripts/plan_arnes_poses_r99.mjs` (no tocar arnes_brazos_r95.mjs)

Réplica en Node de las constantes r99 + el bloque de dedos propuesto, con agujas:

- R-1 · la tabla de dedos incluye 15 huesos por brazo (5 dedos × 3) — pinky presente.
- R-2 · POSE_A: dist(tip→línea crease) de mid/ring/pinky ≤ 1.0 cm GLB en A y B.
- R-3 · POSE_A: índice tip en marco mano ≈ (4.70, ∓0.15, −4.35) ±0.3 (borde inferior, cara +X).
- R-4 · POSE_A: pulgar en bind (ángulo de su quat vs bind < 1e-6).
- R-5 · POSE_B: bowl de las 4 puntas ∈ [0.008, 0.018] m y pulgar bowl ∈ [0.015, 0.03].
- R-6 · muñeca palma-arriba: |palmaDir − (0,1,0)| ≤ 0.1 en stance (−0.15,−0.05,0.99).
- R-7 · delta muñeca agarre: ángulo 0.2411 ±0.01 rad, eje ±(0.335,−0.031,0.942).
- R-8 · anclaje crease: `|centro − (muñeca + handQ·offCrease + ejeHoja·0.0903)| < 1e-6`.
- R-9 · blending: setPose('saque',1) → curls iguales a la tabla saque ±1e-9 tras τ; mezcla
  0.5 agarre/0.5 saque = media aritmética de los ángulos.
- R-10 · tope angular: un salto de 1 rad en 8 ms queda limitado a ω_max·dt.
- R-11 · el arnés r95 SIGUE pasando (regresión): sus 6 agujas intactas.

### 6.2 Checkpoints de render (`scripts/capturas_r99/`)

1. **Reposo**: dedos estirados con curva bind suave — tips ≈ tipsBind del JSON.
2. **Agarre cercano (frente)**: 3 dedos envueltos tocando el mango (sin hueco visible entre
   yema y madera), índice sobre el borde inferior, pulgar apoyado al lado del índice, hoja
   ⟂ antebrazo con cara al rival. *Aguja visual: hueco dedo-mango < 3 mm adulto.*
3. **Agarre en strike**: mismos dedos que en 2 (R5 del dueño: «los dedos NO cambian») —
   sólo muñeca/brazo se mueven.
4. **Saque**: palma plana arriba (nivel de burbuja visual), bola descansando SIN hundirse
   (bola.y − palma.y ≈ r_bola + 0.005), mano no cruza el eje del cuerpo, codo 90–110°.
5. **Rally**: mano libre abajo-lado, codo pegado al torso, dedos semicurva, muñeca neutra.
6. **Funde**: capturar rest↔saque↔balance a 5 fps — sin saltos > 4 cm en las puntas
   (coherente con la coda r95).

---

## Apéndice A · Números medidos (fuente: plan_medidas_rig_r99.json)

### A.1 Escala y cadenas
`L1u=12.1985 cm · L2u=12.0693 cm · esc=0.02213 → L1=0.27 m · L2=0.2671 m`.
Largos de dedo (adulto): thumb 0.1105 · mid 0.1057 · index 0.0986 · ring 0.0945 · pinky 0.0757 m.
Jerarquía mano A: `hand_023 → thumb__024 → thumb_-_025 → thumb_--_026`; `hand_023 → mid__034 → mid_-_035 → mid_--_036`; `hand_023 → index__037 → index_-_038 → index_--_039`; `hand_023 → hand__027 → {ring__028 → ring_-_029 → ring_--_030; pinky__031 → pinky_-_032 → pinky_--_033}`.

### A.2 Palma (bind, mundo)
- A: across (pulgar→meñique) (0.3908,−0.8198,0.4186) · along (−0.0114,−0.4934,0.8697) ·
  **normal palmar = −Z mano = (−0.8027,−0.5195,−0.293)** (dot con across×along = +0.9995).
- B: **(0.8027,−0.5195,−0.293)** (dot con across×along = −0.9995 — espejo, ver H2).

### A.3 Ejes de la mano (bind mundo, A): X=(−0.0988,−0.3687,0.9243) · Y=(0.5882,−0.7709,−0.2446) · Z=(0.8027,0.5195,0.293). Antebrazo: dir mundo (0.0246,−0.5397,0.8415), dir marco propio (1,0,0).

### A.4 Ejes de flexión (marco PADRE, rotación positiva acerca la punta a la palma; verificación
+0.5 rad: dot>0 en TODAS las filas — apéndice completo en `brazos.A.deduccion`)

| dedo | falange | hueso | eje padre | dot vs driverY | desvío | bind (rad) |
|---|---|---|---|---|---|---|
| thumb | f0 | thumb__024 | (0.5467, 0.8373, 0) | 0.798 | 0.579 | 1.7483 |
| thumb | f1 | thumb_-_025 | **(0.157, 0.0586, −0.9859)** | **0.058** | **1.512** | 0.3031 |
| thumb | f2 | thumb_--_026 | **(0, 0.2256, −0.9742)** | 0.224 | 1.343 | 0.4502 |
| mid | f0 | mid__034 | (−0.0715, 0.9974, 0) | 0.988 | 0.072 | 0.2238 |
| mid | f1 | mid_-_035 | (−0.1762, 0.9759, −0.1289) | 0.963 | 0.220 | 0.1975 |
| mid | f2 | mid_--_036 | (0, 0.999, −0.0449) | 0.986 | 0.045 | 0.0807 |
| index | f0 | index__037 | (0.0006, 1, 0) | 0.996 | 0.001 | 0.1279 |
| index | f1 | index_-_038 | (−0.1153, 0.99, −0.0813) | 0.989 | 0.142 | 0.1364 |
| index | f2 | index_--_039 | (0, 0.9994, −0.0336) | 0.999 | 0.034 | 0.1788 |
| ring | f0 | ring__028 | (0.0943, 0.9501, −0.2973) | 0.916 | 0.317 | 0.3638 |
| ring | f1 | ring_-_029 | (0.0244, 0.9922, −0.1221) | 0.989 | 0.125 | 0.1926 |
| ring | f2 | ring_--_030 | (0, 0.9908, −0.1351) | 0.988 | 0.136 | 0.1431 |
| pinky | f0 | pinky__031 | (−0.1728, 0.9385, −0.2988) | 0.899 | 0.352 | 0.4877 |
| pinky | f1 | pinky_-_032 | (0.0797, 0.9963, 0.033) | 0.980 | 0.086 | 0.1584 |
| pinky | f2 | pinky_--_033 | (0, 0.9991, −0.0432) | 0.983 | 0.043 | 0.2335 |

Brazo B: espejo exacto (x,z invertidos por falange; tabla completa en `brazos.B.deduccion`).

### A.5 Tips en bind (marco mano, cm GLB, A — B espejo en y)
thumb (4.884, −4.002, −1.047) · mid (8.825, 1.492, 0.680) · index (8.660, −0.105, 0.059) ·
ring (7.950, 2.884, 0.656) · pinky (6.185, 4.073, 0.628).

### A.6 Offsets del hueso mano (marco mano, m adulto)
- Centro de palma (con pulgar): **(0.0744, ±0.0152, −0.0022)** — A y +, B y −.
- **Centro de crease (4 nudillos, sin pulgar): (0.0868, ±0.0240, −0.0022)** ← línea del mango.
- `D_GRIP = 0.1303` (r54) · `dCrease = 0.04` [HIPÓTESIS: piel del talón; aguja de render §6.2-2].

### A.7 Quats del agarre y palma-arriba
- Delta muñeca agarre: §2.2 (A y B). · Muñeca palma-arriba: §2.1.
- relBind mano: §1. · Stance: cara 0.306 rad de +z · ejeHoja 0.775 rad de +Y (informativo).

### A.8 Simulación del driver r95 (dist yema→mango, cm GLB, mano A)
thumb 1.95 · mid 3.49 · index 3.39 · ring 2.56 · pinky 2.38 (bind — sin curl).

---

*Fin del plan r99. Ficheros: `scripts/plan_medir_rig_r99.mjs` (medición, ejecutable),
`scripts/plan_medidas_rig_r99.json` (datos), `scripts/plan_brazos_r99.md` (este plan).*
